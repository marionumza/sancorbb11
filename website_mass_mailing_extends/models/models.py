# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partners(models.Model):
    _inherit = 'res.partner'

    children_id = fields.One2many('children.children', 'partner_ids', 'Childrens', store=True)

class children(models.Model):
     _name = 'children.children'

     day = fields.Char()
     month = fields.Char()
     year = fields.Char()
     partner_ids = fields.Many2one('res.partner', 'Partner', store=True)

