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
# from openerp.tools.amount_to_text_bg import *
from amount_to_text_bg import *

import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('amount_total')
    def _compute_text(self):
        self.amount_in_word = amount_to_text_bg(self.amount_total, self.currency_id.name)

    amount_in_word = fields.Char(readonly=True,
                                 default=False,
                                 copy=False,
                                 compute='_compute_text'
                                 )

    comment_template1_id = fields.Many2one('base.comment.template',
                                           string='Comment Template 1')
    comment_template2_id = fields.Many2one('base.comment.template',
                                           string='Comment Template 2')
    note1 = fields.Html('Comment 1')
    note2 = fields.Html('Comment 2')

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

    place_of_deal_id = fields.Many2one(comodel_name='res.partner', store=True, required=False,
                                       string="Place of deal",
                                       default=lambda self: self.env.user.partner_id)

    place_of_deal = fields.Char(store=True, required=False)

    @api.onchange('place_of_deal_id')
    def _set_place_of_deal(self):
        place = self.place_of_deal_id
        #_logger.info("Place of deal partner_id: %s" % place.id)
        if place:
            self.place_of_deal = self.place_of_deal_id.city
            if self.place_of_deal_id.country_id.name:
                self.place_of_deal += ", "
                self.place_of_deal += self.place_of_deal_id.country_id.name
            #_logger.info("Place of deal: %s" % self.place_of_deal)

    # @api.model
    # def tax_line_move_line_get(self):
    #     _logger.critical("TEST: %s" % self.tax_line_ids)
    #     res = []
    #     for tax_line in self.tax_line_ids:
    #         if tax_line.amount:
    #             _logger.critical("amount: %s" % tax_line.amount)
    #             res.append({
    #                 'tax_line_id': tax_line.tax_id.id,
    #                 'type': 'tax',
    #                 'name': tax_line.name,
    #                 'price_unit': tax_line.amount,
    #                 'quantity': 1,
    #                 'price': tax_line.amount,
    #                 'account_id': tax_line.account_id.id,
    #                 'account_analytic_id': tax_line.account_analytic_id.id,
    #                 'invoice_id': self.id,
    #             })
    #     return res
