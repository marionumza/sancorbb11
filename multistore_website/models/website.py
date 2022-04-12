
from odoo.http import request
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from lxml import etree


class CustomizeModel(models.Model):
    _name = 'customize.active.website'
    
    view_id = fields.Many2one('ir.ui.view','View Id',domain=['&',("use_for_theme", "=", True),('type','=','qweb'),
                "|", ("active", "=", True), ("active", "=", False)])
    website_ids = fields.Many2many('website','customize_view_relation','view_id','dest_id')
    
    
    def get_assets(self,view_id=0):
        assets = []
        views = False
        if request.context.get('website_id'):
            views = self.env['customize.active.website'].sudo().search([('website_ids','in',[request.context.get('website_id')])])
            for v in views:
                for asset_call_node in etree.fromstring(v.view_id["arch"]).xpath("//link"):
                    if(asset_call_node.get('type')=='text/less'):
                    	assets.append(asset_call_node.get('href'))
        return views and assets

        
class Iruiview(models.Model):
    _inherit = 'ir.ui.view'

    use_for_theme = fields.Boolean('Use for Theme', default=False)

    '''@api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
        	args = args + [('use_for_theme','!=',True)]
        return super(Iruiview, self).search(args,offset,limit,order,count)'''
