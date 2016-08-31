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
from amount_to_text_bg import *
# from openerp.tools import amount_to_text_en

import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    comment_template1_id = fields.Many2one('base.comment.template', string=_('Comment Template 1'))
    comment_template2_id = fields.Many2one('base.comment.template', string=_('Comment Template 2'))
    note1 = fields.Html(_('Comment 1'))
    note2 = fields.Html(_('Comment 2'))
    comment = fields.Text(translate=True)
    amount_in_word = fields.Char(readonly=True, default=False, copy=False, compute='_compute_text')
    place_of_deal = fields.Char(compute='_compute_place_of_deal', store=True, translate=True)
    proforma_number = fields.Char(store=True, readonly=True, copy=False)

    @api.one
    @api.depends('amount_total')
    def _compute_text(self):
        # self.amount_in_word_en = amount_to_text_en.amount_to_text(self.amount_total, lang='en', currency='')
        self.amount_in_word = amount_to_text_bg(self.amount_total, self.currency_id.name)

    @api.onchange('comment_template1_id')
    def _set_note1(self):
        comment = self.comment_template1_id
        if comment:
            self.note1 = comment.get_value(self.partner_id.id)

    @api.onchange('comment_template2_id')
    def _set_note2(self):
        comment = self.comment_template2_id
        if comment:
            self.note2 = comment.get_value(self.partner_id.id)

    def _set_place_of_deal(self):
        place_of_deal = ''
        if self.company_id.partner_id:
            place_of_deal = "%s, %s" % (self.company_id.partner_id.city, self.company_id.partner_id.country_id.name)
        return place_of_deal

    @api.onchange('place_of_deal')
    def onchange_place_of_deal(self):
        if not self.place_of_deal:
            self.place_of_deal = self._set_place_of_deal()
            _logger.info("Place of deal created (onchange): %s" % self.place_of_deal)

    @api.model
    def create(self, vals):
        if 'proforma_number' not in vals:
            vals['proforma_number'] = self.env['ir.sequence'].next_by_code('account.invoice.proforma')
            _logger.info("Proforma number created: %s" % vals['proforma_number'])
        else:
            _logger.critical("Proforma number already exists: %s" % vals['proforma_number'])

        if 'place_of_deal' not in vals:
            company = self.env['res.company'].browse(vals['company_id'])
            if company.partner_id:
                vals['place_of_deal'] = "%s, %s" % (company.partner_id.city, company.partner_id.country_id.name)
                _logger.info("Place of deal created (on model create): %s" % vals['place_of_deal'])

        return super(AccountInvoice, self).create(vals)
