# -*- coding: utf-8 -*-

import json
import logging
import pprint
import werkzeug
import base64

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class EpaybgController(http.Controller):
    _return_url = '/shop/confirmation'
    _notify_url = '/payment/epaybg/notification/'

    @http.route([
        '/payment/epaybg/notification',
    ], type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_notification(self, **post):
        _logger.info('Beginning epaybg_notification form_feedback with post data %s', pprint.pformat(post))  # debug

        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', context=request.context)

        epay_decoded_result = request.registry['payment.transaction'].epay_decoded_result(post.get('encoded'))

        if epay_decoded_result['STATUS'] in ['PAID', 'DENIED', 'EXPIRED']:
            status = 'OK'
        else:
            status = 'ERR'

        info_data = "INVOICE=%s:STATUS=%s\n" % (epay_decoded_result['INVOICE'], status)

        return info_data
