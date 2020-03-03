# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from . import models

from odoo.service import common
from odoo.exceptions import Warning

def pre_init_check(cr): 
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '12.0':
        raise Warning(
            'Module support Odoo series 12.0 found {}.'.format(server_serie))
    return True