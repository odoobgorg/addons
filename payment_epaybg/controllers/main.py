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

    @http.route([
        '/payment/epaybg/notification',
    ], type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_notification(self, **post):
        _logger.info('Beginning epaybg_notification form_feedback with post data %s', pprint.pformat(post))  # debug
        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', context=request.context)

        _logger.critical("START epaybg_notification")
        epay_decoded_result = request.registry['payment.transaction'].epay_decoded_result(post.get('encoded'))
        _logger.critical(epay_decoded_result)
        _logger.critical("END epaybg_notification")

        tx_id = epay_decoded_result['INVOICE']
        status = epay_decoded_result['STATUS']

        info_data = "INVOICE=%s:STATUS=%s\n" % (tx_id, status)
        _logger.critical(info_data)

        return info_data
