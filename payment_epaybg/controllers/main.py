# -*- coding: utf-8 -*-

import json
import logging
import pprint
import werkzeug
# import base64
import os

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class EpaybgController(http.Controller):
    _return_url = '/payment/epaybg/feedback'

    def _get_return_url(self):
        return '/shop/payment/validate'
        # return '/shop/confirmation'

    def epaybg_validate_data(self, **post):
        _logger.info('Start epaybg_validate_data with post data %s', pprint.pformat(post))  # debug

        info_data = None
        encoded, checksum = post.get('encoded'), post.get('checksum')
        if encoded and checksum:
            epay_decoded_result = request.registry['payment.transaction'].epay_decoded_result(encoded)
            # status = str(epay_decoded_result['STATUS'].rstrip(os.linesep))
            tx_id = int(epay_decoded_result['INVOICE'].rstrip(os.linesep))

            cr, uid, context = request.cr, request.uid, request.context
            request.registry['payment.transaction'].form_feedback(cr, SUPERUSER_ID, post, 'epaybg', context)
            tx = request.registry['payment.transaction'].browse(request.cr, SUPERUSER_ID, tx_id, context=context)

            epay_status = 'ERR'
            if not tx:
                epay_status = 'NO'
            elif tx.state in ['done', 'cancel']:
                epay_status = 'OK'

            info_data = "INVOICE=%s:STATUS=%s\n" % (tx_id, epay_status)

        _logger.info('END epaybg_validate_data with info data %s', info_data)  # debug
        return info_data

    @http.route('/payment/epaybg/notification/', type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_notification(self, **post):
        return self.epaybg_validate_data(**post)

    @http.route('/payment/epaybg/feedback', type='http', auth="none", csrf=False)
    def epaybg_feedback(self, **post):
        _logger.info('Beginning Epay.bg feedback with post data %s', pprint.pformat(post))  # debug
        return_url = self._get_return_url()
        import time
        time.sleep(1)
        return werkzeug.utils.redirect(return_url)
