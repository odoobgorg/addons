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

    # def _epaybg_generate_merchant_sig(self, acquirer, inout, values):
    #     """ Generate the shasign for incoming or outgoing communications.
    #
    #     :param browse acquirer: the payment.acquirer browse record. It should
    #                             have a shakey in shaky out
    #     :param string inout: 'in' (openerp contacting ogone) or 'out' (epaybg
    #                          contacting openerp). In this last case only some
    #                          fields should be contained (see e-Commerce basic)
    #     :param dict values: transaction values
    #
    #     :return string: shasign
    #     """
    #     assert inout in ('in', 'out')
    #     assert acquirer.provider == 'epaybg'
    #
    #     if inout == 'in':
    #         keys = "paymentAmount currencyCode shipBeforeDate merchantReference skinCode merchantAccount sessionValidity shopperEmail shopperReference recurringContract allowedMethods blockedMethods shopperStatement merchantReturnData billingAddressType deliveryAddressType offset".split()
    #     else:
    #         keys = "authResult pspReference merchantReference skinCode merchantReturnData".split()
    #
    #     def get_value(key):
    #         if values.get(key):
    #             return values[key]
    #         return ''
    #
    #     sign = ''.join('%s' % get_value(k) for k in keys).encode('ascii')
    #     key = acquirer.epaybg_skin_hmac_key.encode('ascii')
    #
    #     return base64.b64encode(hmac.new(key, sign, sha1).digest())

    def _epaybg_generate_merchant_checksum(self, key, secret):
        # return base64.b64encode(hmac.new(key, secret, sha1).digest())
        return hmac.new(key, secret, sha1)

    def epaybg_form_generate_values(self, cr, uid, id, values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        # tmp
        import datetime
        from dateutil import relativedelta
        # tmp_date = datetime.date.today() + relativedelta.relativedelta(days=1)
        tmp_date = datetime.datetime.now() + relativedelta.relativedelta(days=1)

        item_number = False
        if values['reference']:
            item_number = self.pool['payment.transaction'].search(cr, uid, [('reference', '=', values['reference'])],
                                                                  context=context)
            if item_number and len(item_number):
                item_number = item_number[0]

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

        _logger.info("Start Epay Params:")
        _logger.info(params)
        _logger.info("End Epay Params:")

        # encoded = base64.b64encode("\n".join(["%s=%s" % (k, v) for k, v in params.items()]))
        encoded = base64.b64encode("\n".join(["%s=%s" % (k, v) for k, v in params.items()]).encode('utf-8').strip())

        return_url = '%s' % urlparse.urljoin(base_url, EpaybgController._return_url)

        values.update({
            'encoded': encoded,
            'checksum': self._epaybg_generate_merchant_checksum(str(acquirer.epaybg_merchant_account), encoded),
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

    def _epaybg_form_get_tx_from_data(self, cr, uid, data, context=None):
        reference, pspReference = data.get('merchantReference'), data.get('pspReference')
        if not reference or not pspReference:
            error_msg = _('epaybg: received data with missing reference (%s) or missing pspReference (%s)') % (
            reference, pspReference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use pspReference ?
        tx_ids = self.pool['payment.transaction'].search(cr, uid, [('reference', '=', reference)], context=context)
        if not tx_ids or len(tx_ids) > 1:
            error_msg = _('epaybg: received data for reference %s') % (reference)
            if not tx_ids:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        tx = self.pool['payment.transaction'].browse(cr, uid, tx_ids[0], context=context)

        # verify shasign
        shasign_check = self.pool['payment.acquirer']._epaybg_generate_merchant_sig(tx.acquirer_id, 'out', data)
        if shasign_check != data.get('merchantSig'):
            error_msg = _('epaybg: invalid merchantSig, received %s, computed %s') % (
            data.get('merchantSig'), shasign_check)
            _logger.warning(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _epaybg_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []

        # reference at acquirer: pspReference
        if tx.acquirer_reference and data.get('pspReference') != tx.acquirer_reference:
            invalid_parameters.append(('pspReference', data.get('pspReference'), tx.acquirer_reference))
        # seller
        if data.get('skinCode') != tx.acquirer_id.epaybg_merchant_kin:
            invalid_parameters.append(('skinCode', data.get('skinCode'), tx.acquirer_id.epaybg_merchant_kin))
        # result
        if not data.get('authResult'):
            invalid_parameters.append(('authResult', data.get('authResult'), 'something'))

        return invalid_parameters

    def _epaybg_form_validate(self, cr, uid, tx, data, context=None):
        status = data.get('authResult', 'PENDING')
        if status == 'AUTHORISED':
            tx.write({
                'state': 'done',
                'acquirer_reference': data.get('pspReference'),
                # 'date_validate': data.get('payment_date', fields.datetime.now()),
                # 'paypal_txn_type': data.get('express_checkout')
            })
            return True
        elif status == 'PENDING':
            tx.write({
                'state': 'pending',
                'acquirer_reference': data.get('pspReference'),
            })
            return True
        else:
            error = _('epaybg: feedback error')
            _logger.info(error)
            tx.write({
                'state': 'error',
                'state_message': error
            })
            return False
