# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class POSConfig(models.Model):
    _inherit = 'pos.config'

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')


class POSOrderLine(models.Model):
    _inherit = 'pos.order.line'

    analytic_tag_ids = fields.Many2many('account.analytic.tag', related="order_id.session_id.config_id.analytic_tag_ids", string='Analytic Tags')


# class AccountBankStatement(models.Model):
#     _inherit = 'account.bank.statement'
#
#     analytic_tag_ids = fields.Many2many('account.analytic.tag', related="order_id.session_id.config_id.analytic_tag_ids", string='Analytic Tags')
#
#
# class AccountBankStatementLine(models.Model):
#     _inherit = 'account.bank.statement.line'
#
#     analytic_tag_ids = fields.Many2many('account.analytic.tag', related="statement_id.analytic_tag_ids", string='Analytic Tags')
#

class POSOrder(models.Model):
    _inherit = 'pos.order'

    analytic_tag_ids = fields.Many2many('account.analytic.tag', related="session_id.config_id.analytic_tag_ids", string='Analytic Tags')

    @api.onchange('analytic_tag_ids')
    def onchange_tag(self):
        config = self.env['pos.config'].search([])
        self.update({
                'analytic_tag_ids': [(6, 0, config.analytic_tag_ids.ids)]
            })

    @api.onchange('lines')
    def _onchange_pos_order_line(self):
        if self.analytic_tag_ids:
            self.lines.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
            })

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        res = super(POSOrder, self)._action_create_invoice_line(line,invoice_id)
        if not res['analytic_tag_ids']:
            res.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
            })
        return res

    @api.multi
    def action_pos_order_invoice(self):
        res = super(POSOrder, self).action_pos_order_invoice()
        invoice = self.env['account.invoice'].search([('id','=', res['res_id'])])
        if not invoice.analytic_tag_id:
            invoice.update({
                'analytic_tag_id': [(6, 0, self.analytic_tag_ids.ids)]
            })
        for x in invoice.tax_line_ids:
            if not x.analytic_tag_ids:
                x.update({
                    'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]
                })
        return res


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def action_pos_session_close(self):
        # Close CashBox
        for session in self:
            company_id = session.config_id.company_id.id
            ctx = dict(self.env.context, force_company=company_id, company_id=company_id)
            ctx_notrack = dict(ctx, mail_notrack=True)
            for st in session.statement_ids:
                if abs(st.difference) > st.journal_id.amount_authorized_diff:
                    # The pos manager can close statements with maximums.
                    if not self.user_has_groups("point_of_sale.group_pos_manager"):
                        raise UserError(_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
                if (st.journal_id.type not in ['bank', 'cash']):
                    raise UserError(_("The journal type for your payment method should be bank or cash."))
                st.with_context(ctx_notrack).sudo().button_confirm_bank()
                move_lines = self.env['account.move.line'].search([('statement_id', '=', st.id)])
                for move_line in move_lines:
                    move_line.update({
                        'analytic_tag_ids': session.config_id.analytic_tag_ids
                    })
                    dimension_tags_allowed = []

                    tag_ids = move_line.analytic_tag_ids.ids
                    for dimension in move_line.account_id.analytic_dimension_ids:
                        dimension_tags = dimension.analytic_dimension_id.analytic_tag_ids.ids
                        dimension_tags_allowed += dimension_tags
                        occurance = False
                        for x in set(dimension_tags):
                            if tag_ids.count(x) > 0:
                                occurance = True
                        if occurance is False:
                            if dimension.default_value:
                                tag_ids.append(dimension.default_value.id)
                            else:
                                raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))

                    allowed_tag_val = []
                    for tag in tag_ids:
                        if tag in dimension_tags_allowed:
                            allowed_tag_val.append(tag)
                    move_line.update({
                        'analytic_tag_ids': [(6, 0, allowed_tag_val)]
                    })
                    if not move_line.analytic_tag_ids and move_line.display_type != 'line_section':
                        raise ValidationError(_("Please choose a valid Tag/Dimension!!!"))
        self.with_context(ctx)._confirm_orders()
        self.write({'state': 'closed'})
        return {
            'type': 'ir.actions.client',
            'name': 'Point of Sale Menu',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('point_of_sale.menu_point_root').id},
        }
