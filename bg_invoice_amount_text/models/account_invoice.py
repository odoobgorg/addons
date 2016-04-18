from openerp import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('amount_total')
    def _compute_text(self):
        self.amount_in_word = amount_to_text_bg(self.amount_total, self.currency_id.name)

    amount_in_word = fields.Char(string=u'Словом: ',
                                 readonly=True,
                                 default=False, copy=False, compute='_compute_text'
                                 )
