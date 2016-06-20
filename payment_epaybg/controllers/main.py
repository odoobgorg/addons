# -*- coding: utf-8 -*-

# import json
import logging
import pprint
# import werkzeug
# import base64

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class EpaybgController(http.Controller):
    # _return_url = '/shop/confirmation'
    _return_url = '/payment/epaybg/return/'

    @http.route([
        '/payment/epaybg/return',
    ], type='http', auth='none', csrf=False)
    def epaybg_return(self, **post):
        _logger.info('Beginning Epaybg form_feedback with post data %s', pprint.pformat(post))  # debug
        # if post.get('authResult') not in ['CANCELLED']:
        #     request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'adyen', context=request.context)
        return_url = post.pop('return_url', '')
        # if not return_url:
        #     custom = json.loads(post.pop('merchantReturnData', '{}'))
        #     return_url = custom.pop('return_url', '/')
        return werkzeug.utils.redirect(return_url)

    @http.route([
        '/payment/epaybg/notification',
    ], type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_notification(self, **post):
        _logger.info('START epaybg_notification form_feedback with post data %s', pprint.pformat(post))  # debug

        epay_decoded_result = request.registry['payment.transaction'].epay_decoded_result(post.get('encoded'))

        tx_id = epay_decoded_result['INVOICE']

        if epay_decoded_result['STATUS'] in ['PAID', 'DENIED', 'EXPIRED']:
            status = 'OK'
        else:
            status = 'ERR'

        info_data = "INVOICE=%s:STATUS=%s\n" % (tx_id, status)

        cr, uid, context = request.cr, request.uid, request.context
        tx_ids = request.registry['payment.transaction'].search(cr, uid, [('id', '=', tx_id), ('state', '=', 'done')], context=context)

        if not tx_ids:
            request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', context=request.context)

        _logger.info('END epaybg_notification form_feedback with info data %s', info_data)  # debug
        return info_data
