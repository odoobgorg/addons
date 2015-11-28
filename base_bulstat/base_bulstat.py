# -*- coding: utf-8 -*-
# Kostadin Kostadinov.

import logging
import string
import datetime
import re
_logger = logging.getLogger(__name__)

from openerp import api
from openerp.osv import osv,fields
from openerp.tools.misc import ustr
from openerp.tools.translate import _
from openerp.exceptions import UserError, ValidationError

class res_partner(osv.osv):
    _inherit = 'res.partner'
 
    _columns = {
           'bulstat':fields.char('Bulstat',size=64),
    }

    @api.one
    @api.constrains('bulstat')
    def _check_bulstat(self):
        #eik_checker(self.bulstat) 
        if not eik_checker(self.bulstat):
            raise ValidationError("BULSTAT isn't valid")	

def eik_checker(eik):
    """
    Check Bulgarian EIK/BULSTAT codes for validity
    full information about algoritm is available here
    http://bulstat.registryagency.bg/About.html
    """

    def get_checksum(weights, digits):
        checksum = sum([weight * digit for weight, digit in zip(weights, digits)])
        return checksum % 11

    def check_eik_base(eik):
        checksum = get_checksum(range(1, 9), eik)
        if checksum == 10:
            checksum = get_checksum(range(3, 11), eik)
        return eik[-1] == checksum % 10

    def check_eik_extra(eik):
        digits = eik[8:13]
        checksum = get_checksum([2, 7, 3, 5], digits)
        #raise ValidationError("BULSTAT isn't valid checksum:"+str(eik[8:13]) +" "+str(checksum))
        if checksum == 10:
            checksum = get_checksum([4, 9, 5, 7], digits)
        return digits[-1] == checksum % 10

    try:
        eik = map(int, eik)
    except ValueError:
        return False

    if not (len(eik) in [9, 13] and check_eik_base(eik)):
        return False

    if len(eik) == 13 and not check_eik_extra(eik):
        return False
		
    return True
