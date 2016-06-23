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
    _return_url = '/payment/epaybg/feedback'

    def epaybg_validate_data(self, **post):
        _logger.info('Start epaybg_validate_data with post data %s', pprint.pformat(post))  # debug

        info_data = None
        encoded, checksum = post.get('encoded'), post.get('checksum')
        if encoded and checksum:
            epay_decoded_result = request.registry['payment.transaction'].epay_decoded_result(encoded)
            status = str(epay_decoded_result['STATUS'].rstrip(os.linesep))
            tx_id = int(epay_decoded_result['INVOICE'].rstrip(os.linesep))

            cr, uid, context = request.cr, request.uid, request.context
            has_tx_id = request.registry['payment.transaction'].search(cr, uid, [('id', '=', tx_id)], context=context)

            if has_tx_id:

                if status == 'PAID':
                    epaybg_state = 'done'
                elif status in ['DENIED', 'EXPIRED']:
                    epaybg_state = 'cancel'
                else:
                    epaybg_state = 'error'

                tx = request.registry['payment.transaction'].browse(cr, uid, tx_id, context=context)
                epay_status = 'ERR'
                if tx.state in ['done', 'cancel']:
                    epay_status = 'OK'

                if tx.state != epaybg_state:
                    res = request.registry['payment.transaction'].form_feedback(cr, SUPERUSER_ID, post, 'epaybg', context)
                    _logger.warning(res)

            else:
                epay_status = 'NO'

            info_data = "INVOICE=%s:STATUS=%s\n" % (tx_id, epay_status)

        _logger.info('END epaybg_validate_data with info data %s', info_data)  # debug
        return info_data

    @http.route('/payment/epaybg/notification/', type='http', auth='none', methods=['POST'], csrf=False)
    def epaybg_notification(self, **post):
        return self.epaybg_validate_data(**post)

    @http.route(['/payment/epaybg/feedback'], type='http', auth="public", website=True)
    def epaybg_confirmation(self, **post):
        _logger.info('START epaybg_confirmation')

        cr, uid, context = request.cr, request.uid, request.context
        sale_order_id = request.session.get('sale_last_order_id')
        request.website.sale_reset(context=context)
        if sale_order_id:
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
        else:
            return request.redirect('/shop')

        _logger.info('END epaybg_confirmation')
        return request.website.render("website_sale.confirmation", {'order': order})

