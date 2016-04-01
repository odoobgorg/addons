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
           'bg_uic':fields.char(string=_('UIC'),size=13,help=_('UIC by Bulgarian register agency')),
           'bg_mol':fields.char(string=_('MOL'),size=100,help=_('MOL')),
    }
    
    _sql_constraints = [
        ('bg_uic_uniq', 'unique("bg_uic")', 'The company register number must be unique !')
    ]

    @api.one
    @api.constrains('bg_uic')
    def _check_bulstat(self):
        #eik_checker(self.bulstat) 
        if not bg_uic_checker(self.bg_uic):
            raise ValidationError(_("BULSTAT isn't valid"))	

def bg_uic_checker(_bg_uic):
    """
    Check Bulgarian EIK/BULSTAT codes for validity
    full information about algoritm is available here
    http://bulstat.registryagency.bg/About.html
    """

    def get_checksum(weights, digits):
        checksum = sum([weight * digit for weight, digit in zip(weights, digits)])
        return checksum % 11

    def check_uic_base(_bg_uic):
        checksum = get_checksum(range(1, 9), _bg_uic)
        if checksum == 10:
            checksum = get_checksum(range(3, 11), _bg_uic)
        return _bg_uic[-1] == checksum % 10

    def check_uic_extra(_bg_uic):
        digits = _bg_uic[8:13]
        checksum = get_checksum([2, 7, 3, 5], digits)
        #raise ValidationError("BULSTAT isn't valid checksum:"+str(eik[8:13]) +" "+str(checksum))
        if checksum == 10:
            checksum = get_checksum([4, 9, 5, 7], digits)
        return digits[-1] == checksum % 10

    try:
        _bg_uic = map(int, list(_bg_uic))
    except ValueError:
        return False

    if not (len(_bg_uic) in [9, 13] and check_uic_base(_bg_uic)):
        return False

    if len(_bg_uic) == 13 and not check_uic_extra(_bg_uic):
        return False
		
    return True
