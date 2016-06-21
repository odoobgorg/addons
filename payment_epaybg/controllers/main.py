# -*- coding: utf-8 -*-

# import json
import logging
import pprint
# import werkzeug
# import base64
import os

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class EpaybgController(http.Controller):
    # _return_url = '/shop/confirmation'
    _return_url = '/shop/payment/validate'

    @http.route([
        '/payment/epaybg/notification',
    ], type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_form_feedback(self, **post):
        _logger.info('START epaybg_form_feedback with post data %s', pprint.pformat(post))  # debug

        cr, uid, context = request.cr, request.uid, request.context
        request.registry['payment.transaction']._epaybg_form_get_tx_from_data(cr, uid, post, context=None)

        import time
        time.sleep(3)

        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', context=context)

        epay_decoded_result = request.registry['payment.transaction'].epay_decoded_result(post.get('encoded'))
        status = epay_decoded_result['STATUS'].rstrip(os.linesep)
        tx_id = epay_decoded_result['INVOICE'].rstrip(os.linesep)

        if status in ['PAID', 'DENIED', 'EXPIRED']:
            epay_status = 'OK'
        else:
            epay_status = 'ERR'

        info_data = "INVOICE=%s:STATUS=%s,\n" % (tx_id, epay_status)

        _logger.info('END epaybg_form_feedback with info data %s', info_data)  # debug
        return info_data
