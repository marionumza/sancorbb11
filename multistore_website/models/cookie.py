from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify


class website(models.Model):
    _inherit = 'website'
    
    enable_cookie = fields.Boolean(string="Enable Cookie")
    cookie_message = fields.Char(string="Message")
    cookie_button_text = fields.Char(string="Accept Button Text")
    enable_decline_button = fields.Boolean(string="Enable Decline")
    decline_button_text = fields.Char(string ="Decline Button Text")
    policy_text = fields.Char(string="Policy Text")
    policy_url = fields.Char(string="Policy Url")
    enable_shop = fields.Boolean(string="Enable Shop")
    cookie_position = fields.Selection([('top_cookie', 'Top'),
        ('top_left_cookie', 'Top Left'),
        ('top_right_cookie', 'Top Right'),
        ('bottom_cookie', 'Bottom'),
        ('bottom_right_cookie','Bottom Right'),
        ('bottom_left_cookie','Bottom Left'),
    ],default='top_cookie',
    help="Set Position of Cookie")
    
class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_cookie = fields.Boolean(string="Do you want to enable Cookie?", related='website_id.enable_cookie')
    cookie_message = fields.Char(string="Message", related="website_id.cookie_message")
    policy_text = fields.Char(string="Policy Text", related="website_id.policy_text")
    cookie_button_text = fields.Char(string="Button Text", related="website_id.cookie_button_text")
    policy_url = fields.Char(string="Policy Url", related="website_id.policy_url")
    enable_shop = fields.Boolean(string="Do you want to enable Shop?", related='website_id.enable_shop')
    enable_decline_button = fields.Boolean(string="Enable Decline", related='website_id.enable_decline_button')
    decline_button_text = fields.Char(string ="Decline Button Text", related='website_id.decline_button_text')
        
