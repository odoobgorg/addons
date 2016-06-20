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
        request.registry['payment.transaction'].form_feedback(request.cr, SUPERUSER_ID, post, 'epaybg', context=request.context)

        _logger.critical("START epaybg_notification")
        epay_decoded_result = request.registry['payment.transaction'].epay_decoded_result(self, post.get('encoded'))
        _logger.critical(epay_decoded_result)
        _logger.critical("END epaybg_notification")

        tx_id = epay_decoded_result['INVOICE']
        status = epay_decoded_result['STATUS']

        info_data = "INVOICE=%s:STATUS=%s\n" % (tx_id, status)
        _logger.critical(info_data)

        return info_data
