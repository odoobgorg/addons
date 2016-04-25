# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class res_partner(osv.osv):
    _inherit = "res.partner"

    _columns = {
        'bg_egn': fields.char(string=_('EGN'), size=10, help=_('EGN')),
        'bg_uic': fields.char(string=_('UIC'), size=13, help=_('UIC by Bulgarian register agency')),
        'bg_mol': fields.char(string=_('MOL'), size=100, help=_('MOL')),
    }

    _sql_constraints = [
        ('bg_uic_uniq', 'unique("bg_uic")', 'The company register number must be unique !')
    ]

    @api.one
    @api.constrains('bg_egn')
    def _check_egn(self):
        if not self.egn_checker(self.bg_egn):
            _logger.error(self.bg_egn)
            raise Exception("EGN isn't valid.")

    def egn_checker(self, egn):

        if not egn:
            return True

        def get_checksum(weights, digits):
            checksum = sum([weight * digit for weight, digit in zip(weights, digits)])
            return checksum % 11

        def check_egn(egn):
            digits = egn[0:10]
            checksum = get_checksum([2, 4, 8, 5, 10, 9, 7, 3, 6], digits)
            return digits[-1] == checksum % 10

        try:
            egn = map(int, list(egn))
        except ValueError:
            return False

        if not (len(egn) in [10] and check_egn(egn)):
            return False

        return True

    @api.one
    @api.constrains('bg_uic')
    def _check_uic(self):
        if not self.bg_uic_checker(self.bg_uic):
            raise ValidationError(_("BULSTAT/EIK isn't valid"))

    def bg_uic_checker(self, uic):

        if not uic:
            return True

        def get_checksum(weights, digits):
            checksum = sum([weight * digit for weight, digit in zip(weights, digits)])
            return checksum % 11

        def check_uic_base(uic):
            checksum = get_checksum(range(1, 9), uic)
            if checksum == 10:
                checksum = get_checksum(range(3, 11), uic)
            return uic[-1] == checksum % 10

        def check_uic_extra(uic):
            digits = uic[8:13]
            checksum = get_checksum([2, 7, 3, 5], digits)
            if checksum == 10:
                checksum = get_checksum([4, 9, 5, 7], digits)
            return digits[-1] == checksum % 10

        try:
            uic = map(int, list(uic))
        except ValueError:
            _logger.error(uic)
            return False

        if not (len(uic) in [9, 13] and check_uic_base(uic)):
            _logger.error(uic)
            return False

        if len(uic) == 13 and not check_uic_extra(uic):
            _logger.error(uic)
            return False

        return True
