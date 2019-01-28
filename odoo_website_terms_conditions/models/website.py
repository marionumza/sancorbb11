# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo import http, SUPERUSER_ID, tools, _
from odoo.http import request

class website_terms_conditions(models.Model):
    _name = 'website.terms.conditions'
    
    title  =  fields.Char('Title')
    name  =  fields.Char('Label Name')
    terms_conditions  =  fields.Text('Terms & Conditions')


class website(models.Model):
    _inherit = 'website'

    def get_website_terms_conditions(self):  
        terms_ids=self.env['website.terms.conditions'].search([])
        return terms_ids               
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    