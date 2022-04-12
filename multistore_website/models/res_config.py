# -*- coding: utf-8 -*-

import logging
import requests
from odoo import api, fields, models
_logger = logging.getLogger(__name__)
from odoo.http import request
import os


    
class Themefonts(models.Model):
    _name = "website.themefonts"

    name = fields.Char("Font Name")
    path = fields.Text("Font Less File Path")

class Website(models.Model):
    _inherit = "website"



    def _get_default_theme_domain(self):
        category_id =self.env.ref('base.module_category_theme')
        domain =False
        if category_id: 
            domain = [
            '|',('category_id', '=', category_id.id), ('category_id.parent_id', '=',category_id.id)
        ]
        domain = domain + [('state','=','installed')]
        return domain
    recaptcha_site_key = fields.Char('reCAPTCHA site Key')
    recaptcha_private_key = fields.Char('reCAPTCHA Private Key')
    enable_recaptcha_login = fields.Boolean('Enable reCAPTCHA on Login')
    enable_recaptcha_signup = fields.Boolean('Enable reCAPTCHA on Signup')
    enable_recaptcha_contactus = fields.Boolean('Enable reCAPTCHA on Contactus')
    website_theme_logo = fields.Binary(string='Logo', store=True)
    website_theme_logo_filename = fields.Char(string='Logo Filename')
    website_theme_id = fields.Many2one('ir.module.module' , domain = _get_default_theme_domain)
         
    @api.multi
    def is_captcha_valid(self, cresponse):
        params = {'secret': self.recaptcha_private_key, 'response': cresponse}
        try:
            response = requests.get(
                'https://www.google.com/recaptcha/api/siteverify', params=params)
        except Exception:
            _logger.warning("Could not connect to Google reCAPTCHA server.")
        res = response.json()
        return True if res.get('success') else False

    def logo_image_url(self, record):
        sudo_record = record.sudo()
        return '/web/image/%s/%s/%s/%s' %(record._name, str(record.id), 'website_theme_logo', record.website_theme_logo_filename)


    def updated_file(self):
        website_ids = self.env['website'].search([])
        theme_module = self.env['ir.module.module'].search(self._get_default_theme_domain())
        for module in theme_module:
            if theme_module!='theme_default':
                views = self.env['ir.ui.view'].search([('type','=','qweb'),('key','ilike',module.name+'%')])
                views.write({'use_for_theme':True,'website_id':False,'active':False})                    
        for website in website_ids:
            if website.website_theme_id:            
                theme_module = website.website_theme_id and website.website_theme_id.name
                if theme_module!='theme_default': 
                    views = self.env['ir.ui.view'].search(['&','&',('key','ilike',theme_module+'%'),('type','=','qweb'),('active','!=',True)])
                    for view in views:
                        if view.customize_show==True:            
                            view.write({'active' : False,'website_id' : website.id})
                        else:
                            view.write({'active': True,'website_id' : website.id}) 
                    
          

    def get_updayed_less(self):
        if request.website.theme_color:
            chosen_color = request.website.theme_color
            filePath = "/multistore_website/static/src/less/option_website_"+ str(request.website.id) +"_.less";
            return filePath
        return False
        
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _default_website(self):
        return self.env['website'].search([], limit=1)

    website_id = fields.Many2one(
        'website', string="website", default=_default_website, required=True)
    recaptcha_site_key = fields.Char(
        string='Site Key', related='website_id.recaptcha_site_key')
    recaptcha_private_key = fields.Char(
        string='Private Key', related='website_id.recaptcha_private_key')
    enable_recaptcha_login = fields.Boolean(
        string='Enable reCAPTCHA on Login', related='website_id.enable_recaptcha_login')
    enable_recaptcha_signup = fields.Boolean(
        string='Enable reCAPTCHA on Signup', related='website_id.enable_recaptcha_signup')
    enable_recaptcha_contactus = fields.Boolean(
        string='Enable reCAPTCHA on Contactus', related='website_id.enable_recaptcha_contactus')
    website_theme_logo = fields.Binary(string='Logo', related='website_id.website_theme_logo', store=True)
    website_theme_logo_filename = fields.Char(string='Logo Filename', related='website_id.website_theme_logo_filename')
    website_theme_id = fields.Many2one('ir.module.module' , domain = [('state','=','installed'),('category_id','!=',False),('category_id.name','ilike','Theme'),('category_id.parent_id.name','ilike','Theme')],related='website_id.website_theme_id')
