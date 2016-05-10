from openerp import models, fields, api


class BaseCommentTemplate(models.Model):
    _name = "base.comment.template"
    _description = "Base Comment template"

    name = fields.Char('Comment summary', required=True)
    position = fields.Selection([('comment_1', 'Reason for not charging VAT'),
                                 ('comment_2', 'Method of payment')],
                                'Position',
                                required=True,
                                default='comment_1',
                                help="Position on document")
    text = fields.Html('Comment', translate=True, required=True)

    @api.multi
    def get_value(self, partner_id=False):
        self.ensure_one()
        lang = None
        if partner_id:
            lang = self.env['res.partner'].browse(partner_id).lang
        return self.with_context({'lang': lang}).text
