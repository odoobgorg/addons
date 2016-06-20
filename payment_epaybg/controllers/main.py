# -*- coding: utf-8 -*-

import json
import logging
import pprint
import werkzeug
import base64

from openerp import http, SUPERUSER_ID
from openerp.http import request

from openerp.addons.payment.models.payment_acquirer import ValidationError
from hashlib import sha1
import hmac

_logger = logging.getLogger(__name__)


class EpaybgController(http.Controller):
    _return_url = '/shop/confirmation'
    # _return_url = '/payment/epaybg/return/'
    _notify_url = '/payment/epaybg/notification/'

    def epaybg_validate_data(self, **post):

        res = False
        new_post = dict(post, cmd='_notify-validate')
        cr, uid, context = request.cr, request.uid, request.context
        reference = post.get('item_number')
        tx = None
        if reference:
            tx_ids = request.registry['payment.transaction'].search(cr, uid, [('reference', '=', reference)], context=context)
            if tx_ids:
                tx = request.registry['payment.transaction'].browse(cr, uid, tx_ids[0], context=context)
        paypal_urls = request.registry['payment.acquirer']._get_paypal_urls(cr, uid, tx and tx.acquirer_id and tx.acquirer_id.environment or 'prod', context=context)
        validate_url = paypal_urls['paypal_form_url']
        urequest = urllib2.Request(validate_url, werkzeug.url_encode(new_post))
        uopen = urllib2.urlopen(urequest)
        resp = uopen.read()
        if resp == 'VERIFIED':
            _logger.info('Paypal: validated data')
            res = request.registry['payment.transaction'].form_feedback(cr, SUPERUSER_ID, post, 'paypal', context=context)
        elif resp == 'INVALID':
            _logger.warning('Paypal: answered INVALID on data verification')
        else:
            _logger.warning('Paypal: unrecognized paypal answer, received %s instead of VERIFIED or INVALID' % resp.text)
        return res

    @http.route([
        '/payment/epaybg/notification',
    ], type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_notification(self, **post):
        _logger.info('Beginning epaybg_notification form_feedback with post data %s', pprint.pformat(post))  # debug
        # encoded, checksum = post.get('encoded'), post.get('checksum')
        # if not encoded or not checksum:
        #     return ''

        # epay_decoded_result = self.epay_decoded_result(encoded)
        # tx_id = int(epay_decoded_result['INVOICE'])

        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', context=request.context)

        info_data = False

        # tx = request.registry['payment.transaction'].browse(request.cr, SUPERUSER_ID, tx_id, context=request.context)
        #
        # hmac = self._epaybg_generate_merchant_checksum(
        #     tx.acquirer_id.epaybg_merchant_account.encode('utf-8'), encoded)
        # if hmac != checksum:
        #     error_msg = _('epaybg: Not valid CHECKSUM (%s) with hmac (%s)') % (checksum, hmac)
        #     _logger.info(error_msg)
        #     raise ValidationError(error_msg)
        #
        # epay_decoded_pformat = pprint.pformat(epay_decoded_result)
        #
        # if not tx:
        #     # XXX if not recognise this invoice
        #     status = 'NO'
        #
        #     # error = _('Epaybg: feedback error')
        #     tx.write({
        #         'state': 'error',
        #         'state_message': epay_decoded_pformat
        #     })
        # elif epay_decoded_result['STATUS'] == 'PAID':
        #     # XXX if OK for this invoice
        #     status = 'OK'
        #
        #     tx.write({
        #         'state': 'done',
        #         'acquirer_reference': epay_decoded_pformat,
        #     })
        # else:
        #     # XXX if error for this invoice
        #     status = 'ERR'
        #
        #     tx.write({
        #         'state': 'error',
        #         'acquirer_reference': epay_decoded_pformat,
        #     })
        #
        # info_data = "INVOICE=%s:STATUS=%s\n" % (tx_id, status)
        # _logger.critical(info_data)

        return info_data
