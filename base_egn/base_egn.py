# -*- coding: utf-8 -*-
# Kostadin Kostadinov.

import logging
import string
import datetime
import re
_logger = logging.getLogger(__name__)

from openerp import api, models
from openerp.osv import osv, fields
from openerp.tools.misc import ustr
from openerp.tools.translate import _
from openerp.exceptions import UserError, ValidationError

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'egn': fields.char('EGN',size=10),
    }
    @api.one
    @api.constrains('egn')
    def _check_egn(self):		
            if not egn_checker(self.egn):
                _logger.info("Egn Problem")
                raise Exception("EGN isn't valid.")

def egn_checker(egn):
    _logger.info(egn)
    def get_checksum(weights, digits):
        checksum = sum([weight * digit for weight, digit in zip(weights, digits)])
        _logger.info(str(digits) + "get checksum:" + str(checksum))
        return checksum % 11

    def check_egn(egn):
        digits = egn[0:10]
        checksum = get_checksum([2, 4, 8, 5, 10, 9, 7, 3, 6], digits)
        #raise ValidationError("isn't valid checksum:"+str(egn[1:10]) +" "+str(checksum))
        _logger.info(str(egn) + " " + str(checksum))
        return digits[-1] == checksum % 10

    
    try:
        egn = map(int, list(egn))
    except ValueError:
        return False
    
    if not (len(egn) in [10] and check_egn(egn)):
        return False
		
    return True
