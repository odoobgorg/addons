# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Bulgaria Accounting, Open Source Accounting and Invoiceing Module
#    Copyright (C) 2016 BGO software LTD, Lumnus LTD, Prodax LTD
#    (http://www.bgosoftware.com, http://www.lumnus.net, http://www.prodax.bg)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(translate=True)
    bg_egn = fields.Char(string=_('EGN'), store=True, size=10, help=_('EGN'))
    bg_uic = fields.Char(string=_('BULSTAT'), store=True, size=13, help=_('BULSTAT by Bulgarian register agency'))
    bg_mol = fields.Char(string=_('MOL'), translate=True, store=True, size=100, help=_('MOL'))
    zip = fields.Char(translate=True)
    city = fields.Char(translate=True)
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)

    @api.one
    @api.constrains('bg_egn')
    def _check_egn(self):

        if not self.bg_egn:
            return True

        if self.country_id.id != 23:
            _logger.info("We check only BG contacts. %s, %s" % (self.display_name, self.country_id.name))
            return True

        if not self.egn_checker(self.bg_egn):
            _logger.error(self.bg_egn)
            raise Exception("EGN isn't valid.")

    @staticmethod
    def egn_checker(egn):

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
        if not self.bg_uic:
            return True

        if self.country_id.id != 23:
            _logger.info("We check only BG contacts. %s, %s" % (self.display_name, self.country_id.name))
            return True

        if not self.bg_uic_checker(self.bg_uic):
            raise ValidationError(_("BULSTAT/EIK isn't valid"))

    @staticmethod
    def bg_uic_checker(uic):

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

    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + \
            ['bg_egn', 'bg_mol', 'bg_uic']
