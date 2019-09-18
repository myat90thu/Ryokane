from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

class SalesOrderDoubleApproval(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('to_approve', 'To Approve'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

    @api.multi
    def _make_url(self, record_id, model_name, menu_id, action_id):
        ir_param = self.env['ir.config_parameter'].sudo()
        base_url = ir_param.get_param('web.base.url')
        if base_url:
            base_url += \
                '/web?#id=%s&action=%s&model=%s&view_type=form&menu_id=%s' \
                % (record_id, action_id, model_name, menu_id)
        return base_url

    @api.multi
    def action_confirm(self):
        for so in self:
            if so.state not in ['draft']:
                continue
            if so.type_name == 'Quotation':
                ir_param = so.env['ir.config_parameter'].sudo()
                is_double_enabled = \
                    bool(ir_param.get_param(
                        'sales_order_double_approval.double_verification'))
                if is_double_enabled:
                    validation_amount = \
                        float(ir_param.get_param(
                            'sales_order_double_approval.'
                            'customer_salesorder'))
                    user_has_approval_right = \
                        self.env.user.has_group(
                            'sales_order_double_approval.'
                            'supplier_salesorder')
                    if so.amount_total < validation_amount \
                            or user_has_approval_right:
                        return super(SalesOrderDoubleApproval, self).action_confirm()
                    else:
                        authorized_group = \
                            self.env.ref('sales_order_double_approval.'
                                         'double_verification_sales_right')
                        authorized_users = self.env['res.users'].\
                            search([('groups_id', '=', authorized_group.id)])
                        menu_id = \
                            self.env.ref('sale.sale_order_menu').id
                        action_id = \
                            self.env.ref('sale.menu_sale_order').id
                        salesorder_url =\
                            self._make_url(so.id, so._name,
                                           menu_id, action_id)
                        if authorized_users:
                            for au_user in authorized_users:
                                email_body = ''' <span style='font-style: 16px;
                                 font-weight: bold;'>Dear, %s</span>
                                  ''' % ( au_user.name) + '''
                                   <br/><br/>''' + ''' <span style='font-style:
                                    14px;'> A Sales Order from <span
                                     style='font-weight: bold;'>%s</span> is
                                     awaiting for your Approval to be Validated
                                     </span>''' % (self.env.user.name) + '''
                                      <br/>''' + '''<span style='font-style:
                                      14px;'>Please, access it form below
                                      button</span>
                                      <div style="margin-top:40px;"> <a href=
                                      "''' + salesorder_url + '''"
                                      style="background-color: #1abc9c;
                                      padding: 20px; text-decoration: none;
                                       color: #fff; border-radius: 5px;
                                       font-size: 16px;
                                       "class="o_default_snippet_text">
                                       View Invoice</a></div><br/><br/>'''
                                email_id = \
                                    self.env['mail.mail'].\
                                        create(
                                        {'subject': 'Customer Sales Order is '
                                                    'Waiting for Approval',
                                         'email_from':
                                             self.env.user.partner_id.email,
                                         'email_to': au_user.partner_id.email,
                                         'message_type': 'email',
                                         'body_html': email_body,
                                         })
                                email_id.send()
                        so.write({'state': 'to_approve'})


    @api.multi
    def make_saleorder_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_salesorder = self.filtered(lambda inv: inv.state != 'sale')
        if to_open_salesorder.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it"
                              " to validate the Vendor Bill."))
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True

    @api.multi
    def make_saleorder_cancel(self):
        for so in self:
            return so.action_cancel()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    double_verification = fields.Boolean(string="Double Sales Order Approval")
    customer_salesorder \
        = fields.Float(string="Customer Sales Order Minimum Amount")
    supplier_salesorder \
        = fields.Float(string="Supplier Sales Order Minimum Amount")

    @api.model
    def set_values(self):
        ir_param = self.env['ir.config_parameter'].sudo()
        ir_param.set_param('sales_order_double_approval.double_verification',
                           self.double_verification)
        ir_param.set_param('sales_order_double_approval.'
                           'customer_salesorder',
                           self.customer_salesorder)
        ir_param.set_param('sales_order_double_approval.'
                           'supplier_salesorder',
                           self.supplier_salesorder)
        super(ResConfigSettings, self).set_values()


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_param = self.env['ir.config_parameter'].sudo()
        double_verification = \
            ir_param.get_param('sales_order_double_approval.double_verification')
        customer_salesorder \
            = ir_param.get_param('sales_order_double_approval.'
                                 'customer_salesorder')
        supplier_salesorder \
            = ir_param.get_param('sales_order_double_approval.'
                                 'supplier_salesorder')
        res.update(
            double_verification=bool(double_verification),
            customer_salesorder=
            float( customer_salesorder),
            supplier_salesorder=
            float( supplier_salesorder),
        )
        return res














