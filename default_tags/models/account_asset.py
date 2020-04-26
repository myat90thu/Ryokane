# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_move(self, line):
        category_id = line.asset_id.category_id
        account_analytic_id = line.asset_id.account_analytic_id
        analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(line.amount, company_currency, line.asset_id.company_id, depreciation_date)
        asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
        partner = self.env['res.partner']._find_accounting_partner(line.asset_id.partner_id)
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': partner.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] ,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': partner.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] ,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        move_vals = {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        return move_vals
