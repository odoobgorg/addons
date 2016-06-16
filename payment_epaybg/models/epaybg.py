# -*- coding: utf-'8' "-*-"

import base64
import json
from hashlib import sha1
import hmac
import logging
import urlparse

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

    def epaybg_form_generate_values(self, cr, uid, id, values, environment, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        # tmp
        import datetime
        from dateutil import relativedelta
        # tmp_date = datetime.date.today() + relativedelta.relativedelta(days=1)
        tmp_date = datetime.datetime.now() + relativedelta.relativedelta(days=1)

        return_url = '%s' % urlparse.urljoin(base_url, EpaybgController._return_url)

        item_number = False
        if values['reference']:
            tx_id = self.pool['payment.transaction'].search(cr, uid, [('reference', '=', values['reference'])],
                                                            context=context)
            if tx_id and len(tx_id) == 1:
                item_number = str(tx_id[0])

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

    # def _epaybg_form_get_tx_from_data(self, cr, uid, data, context=None):
    #     reference, pspReference = data.get('merchantReference'), data.get('pspReference')
    #     if not reference or not pspReference:
    #         error_msg = _('epaybg: received data with missing reference (%s) or missing pspReference (%s)') % (reference, pspReference)
    #         _logger.info(error_msg)
    #         raise ValidationError(error_msg)
    #
    #     # find tx -> @TDENOTE use pspReference ?
    #     tx_ids = self.pool['payment.transaction'].search(cr, uid, [('reference', '=', reference)], context=context)
    #     if not tx_ids or len(tx_ids) > 1:
    #         error_msg = _('epaybg: received data for reference %s') % (reference)
    #         if not tx_ids:
    #             error_msg += _('; no order found')
    #         else:
    #             error_msg += _('; multiple order found')
    #         _logger.info(error_msg)
    #         raise ValidationError(error_msg)
    #     tx = self.pool['payment.transaction'].browse(cr, uid, tx_ids[0], context=context)
    #
    #     # verify shasign
    #     shasign_check = self.pool['payment.acquirer']._epaybg_generate_merchant_sig(tx.acquirer_id, 'out', data)
    #     if shasign_check != data.get('merchantSig'):
    #         error_msg = _('epaybg: invalid merchantSig, received %s, computed %s') % (data.get('merchantSig'), shasign_check)
    #         _logger.warning(error_msg)
    #         raise ValidationError(error_msg)
    #
    #     return tx

    def epay_decoded_result(self, encoded):
        result = AcquirerEpaybg._epaybg_generate_merchant_decoded(encoded)
        words = result.split(":")
        dict1 = {}
        if len(words) > 0:
            for word in words:
                w = word.split("=")
                if len(w) > 0:
                    dict1[w[0]] = w[1]
        _logger.critical(dict1)
        return dict1

    def _epaybg_form_get_tx_from_data(self, cr, uid, data, context=None):
        encoded, checksum = data.get('encoded'), data.get('checksum')
        if not encoded or not checksum:
            error_msg = _('epaybg: received data with missing encoded (%s) or missing checksum (%s)') % (
                encoded, checksum)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        tx = False
        epay_result = self.epay_decoded_result(encoded)
        if epay_result['INVOICE']:
            tx = self.pool['payment.transaction'].browse(cr, uid, int(epay_result['INVOICE']), context=context)

        _logger.critical(tx)

        return tx

    def _epaybg_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []

        # # reference at acquirer: pspReference
        # if tx.acquirer_reference and data.get('pspReference') != tx.acquirer_reference:
        #     invalid_parameters.append(('pspReference', data.get('pspReference'), tx.acquirer_reference))
        # # seller
        # if data.get('skinCode') != tx.acquirer_id.epaybg_merchant_kin:
        #     invalid_parameters.append(('skinCode', data.get('skinCode'), tx.acquirer_id.epaybg_merchant_kin))
        # # result
        # if not data.get('authResult'):
        #     invalid_parameters.append(('authResult', data.get('authResult'), 'something'))

        return invalid_parameters

    def _epaybg_form_validate(self, cr, uid, tx, data, context=None):
        status = data.get('authResult', 'PENDING')
        if status == 'AUTHORISED':
            tx.write({
                'state': 'done',
                'acquirer_reference': data.get('pspReference'),
            })
            _logger.critical('_epaybg_form_validate')
            _logger.critical(tx)
            return True
        elif status == 'PENDING':
            tx.write({
                'state': 'pending',
                'acquirer_reference': data.get('pspReference'),
            })
            _logger.critical('_epaybg_form_validate')
            _logger.critical(tx)
            return True
        else:
            error = _('epaybg: feedback error')
            _logger.info(error)
            tx.write({
                'state': 'error',
                'state_message': error
            })
            _logger.critical('_epaybg_form_validate')
            _logger.critical(tx)
            return False