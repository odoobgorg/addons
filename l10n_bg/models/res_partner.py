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

    def generate_place_of_deal(self, res, cr, uid, record, context, cities):
        city = record.city
        if record.country_id:
            city += str(record.country_id)
        if city not in cities:
            res.append((record.id, self._display_address(cr, uid, record, without_company=True, context=context)))
            cities.append(city)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []

        if context.get('show_city'):
            cities = []
            res_parent_id = False

            users = self.pool.get('res.users')
            current_user = users.browse(cr, uid, uid, context=context)

            for record in self.browse(cr, uid, ids, context=context):
                if not record.city:
                    continue
                set_city = False
                set_parent_city = False
                if record.id == current_user.partner_id.id:
                    set_city = True
                    if current_user.parent_id.id:
                        set_parent_city = True
                elif record.id == current_user.company_id.partner_id.id:
                    set_city = True
                elif record.parent_id.id == current_user.company_id.partner_id.id:
                    set_city = True

                if set_city:
                    self.generate_place_of_deal(res, cr, uid, record, context, cities)
                if set_parent_city:
                    self.generate_place_of_deal(res, cr, uid, current_user.parent_id, context, cities)
                    res_parent_id = current_user.parent_id.id

            if res_parent_id:
                for record in self.browse(cr, uid, ids, context=context):
                    if res_parent_id == record.parent_id.id:
                        self.generate_place_of_deal(res, cr, uid, record, context, cities)
        else:
            types_dict = dict(self.fields_get(cr, uid, context=context)['type']['selection'])
            for record in self.browse(cr, uid, ids, context=context):
                name = record.name or ''
                if record.parent_id and not record.is_company:
                    if not name and record.type in ['invoice', 'delivery', 'other']:
                        name = types_dict[record.type]
                    name = "%s, %s" % (record.parent_name, name)
                if context.get('show_address_only'):
                    name = self._display_address(cr, uid, record, without_company=True, context=context)
                if context.get('show_address'):
                    name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n', '\n')
                name = name.replace('\n\n', '\n')
                if context.get('show_email') and record.email:
                    name = "%s <%s>" % (name, record.email)
                if context.get('html_format'):
                    name = name.replace('\n', '<br/>')
                res.append((record.id, name))

        return res

    def _display_address(self, cr, uid, address, without_company=False, context=None):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        if context.get('show_city'):
            address_format = "%(city)s, %(country_name)s"
        else:
            address_format = address.country_id.address_format or \
                             "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"

        args = {
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
        }

        for field in self._address_fields(cr, uid, context=context):
            args[field] = getattr(address, field) or ''

        if context.get('show_city'):
            args['state_code'] = ''
            args['state_name'] = ''
            args['country_code'] = ''
            args['company_name'] = ''
        elif without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format

        return address_format % args

    def _commercial_fields(self, cr, uid, context=None):
        """ Returns the list of fields that are managed by the commercial entity
        to which a partner belongs. These fields are meant to be hidden on
        partners that aren't `commercial entities` themselves, and will be
        delegated to the parent `commercial entity`. The list is meant to be
        extended by inheriting classes. """
        return ['vat', 'credit_limit', 'bg_egn', 'bg_mol', 'bg_uic']

    def _display_name_compute(self, cr, uid, ids, name, args, context=None):
        context = dict(context or {})
        context.pop('show_address', None)
        context.pop('show_address_only', None)
        context.pop('show_email', None)
        context.pop('show_city', None)

        return dict(self.name_get(cr, uid, ids, context=context))
