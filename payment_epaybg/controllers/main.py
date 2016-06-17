# -*- coding: utf-8 -*-

import json
import logging
import pprint
import werkzeug
import base64

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)


class EpaybgController(http.Controller):
    _return_url = '/shop/confirmation'
    # _return_url = '/payment/epaybg/return/'
    _cancel_url = '/payment/epaybg/cancel/'
    _notify_url = '/payment/epaybg/notification/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from epaybg. """
        return_url = post.pop('return_url', '')
        if not return_url:
            custom = json.loads(post.pop('custom', False) or '{}')
            return_url = custom.get('return_url', '/')
        return return_url

    def _epaybg_generate_merchant_decoded(self, encoded):
        return base64.b64decode(encoded)

    def _epaybg_generate_merchant_checksum(self, merchant_account, encoded):
        return hmac.new(merchant_account, encoded, sha1).hexdigest()

    def epay_decoded_result(self, encoded):
        result = self._epaybg_generate_merchant_decoded(encoded)
        words = result.split(":")
        dict1 = {}
        if len(words) > 0:
            for word in words:
                w = word.split("=")
                if len(w) > 0:
                    dict1[w[0]] = w[1]
        return dict1

    @http.route([
        '/payment/epaybg/return',
    ], type='http', auth='none', csrf=False)
    def epaybg_return(self, **post):
        _logger.info('Beginning epaybg_return form_feedback with post data %s', pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', context=request.context)
        return werkzeug.utils.redirect(return_url)

    @http.route('/payment/epaybg/cancel', type='http', auth="none", csrf=False)
    def epaybg_cancel(self, **post):
        """ When the user cancels its epaybg payment: GET on this route """
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        _logger.info('Beginning epaybg cancel with post data %s', pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        return werkzeug.utils.redirect(return_url)

    @http.route([
        '/payment/epaybg/notification',
    ], type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_notification(self, **post):
        _logger.info('Beginning epaybg_notification form_feedback with post data %s', pprint.pformat(post))  # debug
        encoded, checksum = post.get('encoded'), post.get('checksum')
        if not encoded or not checksum:
            return ''
        epay_decoded_result = self.epay_decoded_result(encoded)
        tx_id = int(epay_decoded_result['INVOICE'])

        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', context=request.context)

        tx = request.registry['payment.transaction'].browse(request.cr, SUPERUSER_ID, tx_id, context=request.context)

        hmac = self._epaybg_generate_merchant_checksum(
            tx.acquirer_id.epaybg_merchant_account.encode('utf-8'), encoded)
        if hmac != checksum:
            error_msg = _('epaybg: Not valid CHECKSUM (%s) with hmac (%s)') % (checksum, hmac)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        if not tx:
            # XXX if not recognise this invoice
            status = 'NO'

            # error = _('Epaybg: feedback error')
            tx.write({
                'state': 'error',
                'state_message': epay_decoded_result
            })
        elif epay_decoded_result['STATUS'] == 'PAID':
            # XXX if OK for this invoice
            status = 'OK'

            tx.write({
                'state': 'pending',
                'acquirer_reference': epay_decoded_result,
            })
        else:
            # XXX if error for this invoice
            status = 'ERR'

            tx.write({
                'state': 'pending',
                'acquirer_reference': epay_decoded_result,
            })

        info_data = "INVOICE=%s:STATUS=%s\n" % (tx_id, status)
        _logger.critical(info_data)

        return info_data
