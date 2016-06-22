# -*- coding: utf-'8' "-*-"

import base64
import json
from hashlib import sha1
import hmac
import logging
import urlparse
import pprint

from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons.payment_epaybg.controllers.main import EpaybgController
from openerp.osv import osv, fields
from openerp.tools import float_round
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class AcquirerEpaybg(osv.Model):
    _inherit = 'payment.acquirer'

    def _get_epaybg_urls(self, cr, uid, environment, context=None):
        """ epaybg URLs """
        if environment == 'prod':
            return {
                'epaybg_form_url': 'https://epay.bg/'
            }
        else:
            return {
                'epaybg_form_url': 'https://demo.epay.bg/'
            }

    def _get_providers(self, cr, uid, context=None):
        providers = super(AcquirerEpaybg, self)._get_providers(cr, uid, context=context)
        providers.append(['epaybg', 'epaybg'])
        return providers

    _columns = {
        'epaybg_merchant_account': fields.char('Merchant Account', required_if_provider='epaybg'),
        'epaybg_merchant_kin': fields.char('Kin Code', required_if_provider='epaybg'),
    }

    def _epaybg_generate_merchant_encoded(self, params):
        return base64.b64encode("\n".join(["%s=%s" % (k, v) for k, v in params.items()]).encode('utf-8').strip())

    def _epaybg_generate_merchant_checksum(self, merchant_account, encoded):
        return hmac.new(merchant_account, encoded, sha1).hexdigest()

    def _epaybg_generate_merchant_decoded(self, encoded):
        return base64.b64decode(encoded)

    def epaybg_form_generate_values(self, cr, uid, id, values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        # tmp
        import datetime
        from dateutil import relativedelta
        # tmp_date = datetime.date.today() + relativedelta.relativedelta(days=1)
        tmp_date = datetime.datetime.now() + relativedelta.relativedelta(days=1)

        return_url = False
        item_number = False
        if values['reference']:
            tx_id = self.pool['payment.transaction'].search(cr, uid, [('reference', '=', values['reference'])],
                                                            context=context)
            if tx_id and len(tx_id) == 1:
                item_number = str(tx_id[0])
                return_url = '%s' % urlparse.urljoin(base_url, EpaybgController._return_url)

        item_name = '%s: %s /%s' % (
            acquirer.company_id.name,
            values['reference'],
            values.get('partner_email'),
        )

        if item_name and len(item_name) > 100:
            item_name = item_name[:100]

        currency_code = values['currency'] and values['currency'].name or ''

        params = {"MIN": acquirer.epaybg_merchant_kin or '', "INVOICE": item_number,
                  "AMOUNT": float_round(values['amount'], 2) or '', "EXP_TIME": tmp_date.strftime("%d.%m.%Y %H:%M"),
                  "DESCR": item_name or '', "CURRENCY": currency_code}

        encoded = self._epaybg_generate_merchant_encoded(params)

        values.update({
            'encoded': encoded,
            'checksum': self._epaybg_generate_merchant_checksum(acquirer.epaybg_merchant_account.encode('utf-8'),
                                                                encoded),
            'urlOK': return_url,
            'urlCancel': return_url,
        })

        return values

    def epaybg_get_form_action_url(self, cr, uid, id, context=None):
        acquirer = self.browse(cr, uid, id, context=context)
        return self._get_epaybg_urls(cr, uid, acquirer.environment, context=context)['epaybg_form_url']


class TxEpaybg(osv.Model):
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    def epaybg_generate_merchant_checksum(self, merchant_account, encoded):
        return hmac.new(merchant_account, encoded, sha1).hexdigest()

    def epaybg_generate_merchant_decoded(self, encoded):
        return base64.b64decode(encoded)

    def epay_decoded_result(self, encoded):
        result = self.epaybg_generate_merchant_decoded(encoded)
        words = result.split(":")
        dict1 = {}
        if len(words) > 0:
            for word in words:
                w = word.split("=")
                if len(w) > 0:
                    dict1[w[0]] = w[1]
        return dict1

    def _epaybg_form_get_tx_from_data(self, cr, uid, data, context=None):
        _logger.info('START _epaybg_form_get_tx_from_data')
        encoded, checksum = data.get('encoded'), data.get('checksum')
        if not encoded or not checksum:
            error_msg = _('Epaybg: received data with missing encoded (%s) or missing checksum (%s)') % (encoded, checksum)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        epay_decoded_result = self.epay_decoded_result(encoded)
        tx_id = int(epay_decoded_result['INVOICE'])

        # find tx
        tx_ids = self.pool['payment.transaction'].search(cr, uid, [('id', '=', tx_id)], context=context)
        if not tx_ids or len(tx_ids) > 1:
            error_msg = _('Epaybg: received data for encoded %s') % encoded
            if not tx_ids:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        tx = self.pool['payment.transaction'].browse(cr, uid, tx_ids[0], context=context)

        # verify hmac
        hmac = self.epaybg_generate_merchant_checksum(tx.acquirer_id.epaybg_merchant_account.encode('utf-8'), encoded)
        if hmac != checksum:
            error_msg = _('Epaybg: invalid checksum, received %s, computed %s') % (data.get('checksum'), hmac)
            _logger.warning(error_msg)
            raise ValidationError(error_msg)

        _logger.info('END _epaybg_form_get_tx_from_data')
        return tx

    def _epaybg_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []
        return invalid_parameters

    def _epaybg_form_validate(self, cr, uid, tx, data, context=None):
        _logger.info('START _epaybg_form_validate')

        encoded, checksum = data.get('encoded'), data.get('checksum')
        epay_decoded_result = self.epay_decoded_result(encoded)

        import os
        status = epay_decoded_result['STATUS'].rstrip(os.linesep)
        tx_id = int(epay_decoded_result['INVOICE'].rstrip(os.linesep))

        if status == 'PAID':
            epaybg_status = 'done'
        elif status == 'DENIED' or status == 'EXPIRED':
            epaybg_status = 'cancel'
        else:
            epaybg_status = 'error'

        result = False
        if tx and tx.state != epaybg_status:
            _logger.info('OLD transaction state %s', tx.state)
            epay_decoded_pformat = pprint.pformat(epay_decoded_result)
            if status == 'PAID':
                tx.write({
                    'state': 'done',
                    'acquirer_reference': tx_id,
                    'state_message': epay_decoded_pformat,
                })
                result = True
            elif status == 'DENIED' or status == 'EXPIRED':
                tx.write({
                    'state': 'cancel',
                    'acquirer_reference': tx_id,
                    'state_message': epay_decoded_pformat,
                })
                result = True
            else:
                tx.write({
                    'state': 'error',
                    'acquirer_reference': tx_id,
                    'state_message': epay_decoded_pformat,
                })
                result = False
            _logger.info('New transaction state %s', tx.state)

        _logger.info('END _epaybg_form_validate with result: %s', result)
        return result
