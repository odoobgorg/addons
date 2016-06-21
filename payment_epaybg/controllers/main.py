# -*- coding: utf-8 -*-

# import json
import logging
import pprint
import werkzeug
# import base64
import os

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class EpaybgController(http.Controller):
    # _return_url = '/shop/payment/validate'
    _notify_url = '/payment/epaybg/notification/'
    _return_url = '/payment/epaybg/feedback/'
    _cancel_url = '/payment/epaybg/cancel/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from epaybg. """
        return_url = post.pop('return_url', '')
        if not return_url:
            custom = json.loads(post.pop('custom', False) or '{}')
            return_url = custom.get('return_url', '/')
        return return_url

    def epaybg_validate_data(self, **post):
        _logger.info('START epaybg_form_feedback with post data %s', pprint.pformat(post))  # debug
        epay_decoded_result = request.registry['payment.transaction'].epay_decoded_result(post.get('encoded'))
        status = epay_decoded_result['STATUS'].rstrip(os.linesep)
        tx_id = epay_decoded_result['INVOICE'].rstrip(os.linesep)
        if status == 'PAID':
            epay_status = 'OK'
        elif status in ['DENIED', 'EXPIRED']:
            epay_status = 'OK'
        else:
            epay_status = 'ERR'
        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', request.context)
        info_data = "INVOICE=%s:STATUS=%s\n" % (tx_id, epay_status)
        _logger.info('END epaybg_form_feedback with info data %s', info_data)  # debug
        return info_data

    @http.route('/payment/epaybg/notification/', type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_notification(self, **post):
        _logger.info('Beginning epaybg_notification form_feedback with post data %s', pprint.pformat(post))  # debug
        return self.epaybg_validate_data(**post)

    @http.route('/payment/epaybg/feedback', type='http', auth="none", methods=['GET'], csrf=False)
    def epaybg_feedback(self, **post):
        _logger.info('Beginning epaybg_feedback form_feedback with post data %s', pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        self.epaybg_validate_data(**post)
        return werkzeug.utils.redirect(return_url)

    @http.route('/payment/epaybg/cancel', type='http', auth="none", csrf=False)
    def epaybg_cancel(self, **post):
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        _logger.info('Beginning epaybg_cancel with post data %s', pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        return werkzeug.utils.redirect(return_url)
