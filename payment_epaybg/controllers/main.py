# -*- coding: utf-8 -*-

import json
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class EpaybgController(http.Controller):
    _return_url = '/shop/confirmation'

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

        tx = request.registry['payment.transaction'].browse(request.cr, SUPERUSER_ID, tx_id, context=request.context)

        if not tx:
            # XXX if not recognise this invoice
            info_data = "INVOICE=%s:STATUS=NO\n" % tx_id
        elif epay_decoded_result['STATUS'] == 'PAID':
            # XXX if OK for this invoice
            info_data = "INVOICE=%s:STATUS=OK\n" % tx_id
        elif epay_decoded_result['STATUS'] == 'DENIED' or epay_decoded_result['STATUS'] == 'EXPIRED':
            # XXX if error for this invoice
            info_data = "INVOICE=%s:STATUS=ERR\n" % tx_id

        _logger.critical("start info_data")
        _logger.critical(info_data)
        _logger.critical("end info_data")

        # tx_id = post.get('merchantReference') and request.registry['payment.transaction'].search(request.cr, SUPERUSER_ID, [('reference', 'in', [post.get('merchantReference')])], limit=1, context=request.context)
        # if post.get('eventCode') in ['AUTHORISATION'] and tx_id:
        #     tx = request.registry['payment.transaction'].browse(request.cr, SUPERUSER_ID, tx_id, context=request.context)
        #     states = (post.get('merchantReference'), post.get('success'), tx.state)
        #     if (post.get('success') == 'true' and tx.state == 'done') or (post.get('success') == 'false' and tx.state in ['cancel', 'error']):
        #         _logger.info('Notification from epaybg for the reference %s: received %s, state is %s', states)
        #     else:
        #         _logger.warning('Notification from epaybg for the reference %s: received %s but state is %s', states)

        return info_data

    def epay_decoded_result(self, encoded):
        result = AcquirerEpaybg._epaybg_generate_merchant_decoded(encoded)
        words = result.split(":")
        dict1 = {}
        if len(words) > 0:
            for word in words:
                w = word.split("=")
                if len(w) > 0:
                    dict1[w[0]] = w[1]
        return dict1
