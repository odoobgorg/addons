from openerp import models, fields, api, _
# from openerp.tools.amount_to_text_bg import *
from amount_to_text_bg import *


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

    place_of_deal_id = fields.Many2one(comodel_name='res.partner', store=True, required=False, string="Place of deal",
                                       default=lambda self: self.env.user.partner_id)
