# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2017 BulkTP
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
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

import odoo


class WebsiteForm(odoo.addons.website_form.controllers.main.WebsiteForm):

    def insert_record(self, request, model, values, custom, meta=None):
        record_id = super(WebsiteForm, self).insert_record(request, model, values, custom, meta)

        # Ivastanin: If to override fault forms
        if values.get('email_from'):
            template_id = request.env['ir.model.data'].sudo().get_object_reference('website_contact_notify', 'website_contact_notify_mail')[1]
            mail_id = request.env['mail.template'].sudo().browse(template_id).send_mail(int(record_id), force_send=True)

        return record_id
