# -*- coding: utf-8 -*-
# 2018 Moogah

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width = fields.Float(string="Width",help="The Width in cms",translate=True)
    height = fields.Float(string="Height",help="The Height in cms",translate=True)
    length = fields.Float(string="Length",help="The Length in cms",translate=True)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    width = fields.Float(string="Width",help="The Width in cms",translate=True)
    height = fields.Float(string="Height",help="The Height in cms",translate=True)
    length = fields.Float(string="Length",help="The Length in cms",translate=True)
