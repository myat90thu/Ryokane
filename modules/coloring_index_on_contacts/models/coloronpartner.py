import base64
import collections
import datetime
import hashlib
import pytz
import threading
import re

from email.utils import formataddr

import requests
from lxml import etree
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat

class partnercolor(models.Model):
    _inherit=['res.partner']
    _name='res.partner'

    partner_state= fields.Boolean(string='confirmed customer', default=False,compute='_compute_color_type') 

    @api.depends('ref')
    def _compute_color_type(self):
        for partner in self:
            if partner.ref:
                partner.partner_state = True
            else:
                partner.partner_state = False

class crmpartnercolor(models.Model):
    _inherit=['crm.lead']
    _name='crm.lead'

    color = fields.Integer(string='Color index',default=2, compute='_compute_color_type')

    @api.depends('partner_id')
    def _compute_color_type(self):
        for record in self:
            if record.partner_id.partner_state and record.partner_id.customer and record.partner_id.is_company:
                record.color= 10
            elif not record.partner_id.partner_state and record.partner_id.customer and record.partner_id.is_company:
                record.color=3
            else:
                record.color=1