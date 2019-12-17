from odoo import _, api, fields, models

class salestarget(models.Model):
    _inherit = 'sale.target'
    salesperson_id= fields.Many2one('res.users', string='Salesperson', track_visibility='onchange', default=lambda self: self.env.user)
    sales_target=fields.Float(string="Sales Target")
    sales_target_type=fields.Selection([('personal', 'Individual'),('team', 'Team')],string="Target Type", required=True)
    sales_target_process=fields.Float(string="Sales Target Process",_compute='_compute_sales_target_process',readonly=True)
    
    date_From = fields.Date(string="From:", required=True)
    date_to = fields.Date(string="To:", required=True)


    def _compute_sales_target_process(self):
            for saleorder in self:
                if sales_target_type == "personal":
                    saleorder.salesperson_id.sales_target_process+= saleorder.amount_untaxed
                else:
                    saleorder.team_id.sales_target_process+= saleorder.amount_untaxed
class salestargetforuser(models.Model):
    _inherit = 'res.users'

    sales_target_process=fields.Float(string='Sales Target', required=True,readonly=True)

class salestargetforteams(models.Model):
    _inherit = 'crm.team'

    sales_target_process=fields.Float(string='Sales Target', required=True,readonly=True)