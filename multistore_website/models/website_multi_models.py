from odoo import api, models, fields, _
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class BlogPost(models.Model):
    _inherit = 'blog.post'
    
    website_ids = fields.Many2many('website', string='Websites')
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(BlogPost, self).search(args,offset,limit,order,count)

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'
    
    website_ids = fields.Many2many('website', string='Websites')
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(PaymentAcquirer, self).search(args,offset,limit,order,count)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    website_ids = fields.Many2many('website', string='Websites')
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(DeliveryCarrier, self).search(args,offset,limit,order,count)


                        
class BlogBlog(models.Model):
    _inherit = 'blog.blog'
    
    website_ids = fields.Many2many('website', string='Websites')

    
    def get_current_website_blog(self):
        website_id = self.env['website'].get_current_website()
        blogs = False
        if website_id:
            blogs = [ '|',('website_ids','=',False),('website_ids','in',request.website.id)]
        return blogs    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(BlogBlog, self).search(args,offset,limit,order,count)  

    @api.multi
    def all_tags(self, min_limit=1):
        tags=request.env['blog.tag'].search([]) and request.env['blog.tag'].search([]).ids  or []

        req = """
            SELECT
                p.blog_id, count(*), r.blog_tag_id
            FROM
                blog_post_blog_tag_rel r
                    join blog_post p on r.blog_post_id=p.id
            WHERE
                p.blog_id in %s
            GROUP BY
                p.blog_id,
                r.blog_tag_id
            ORDER BY
                count(*) DESC
        """
        self._cr.execute(req, [tuple(self.ids)])
        tag_by_blog = {i.id: [] for i in self}
        for blog_id, freq, tag_id in self._cr.fetchall():
            if freq >= min_limit:
                if(tag_id in tags):
                    tag_by_blog[blog_id].append(tag_id)

        BlogTag = self.env['blog.tag']
        for blog_id in tag_by_blog:
            tag_by_blog[blog_id] = BlogTag.browse(tag_by_blog[blog_id])
        return tag_by_blog
        
class BlogTag(models.Model):
    _inherit = 'blog.tag'
    
    website_ids = fields.Many2many('website', string='Websites')
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(BlogTag, self).search(args,offset,limit,order,count)

class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'
    
    website_ids = fields.Many2many('website', string='Websites')

class Users(models.Model):
    _inherit = 'res.users'   
    website_ids = fields.Many2many('website', string='Websites')
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(Users, self).search(args,offset,limit,order,count)

class SaleOrder(models.Model):
    _inherit = 'sale.order' 
      
    website_ids = fields.Many2many('website', string='Websites')
    


        
        
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(SaleOrder, self).search(args,offset,limit,order,count)
                                                          
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    website_ids = fields.Many2many('website', string='Websites')

    
    def get_current_website_product(self, args, offset=0, limit=None, order=None, count=False):
        website_id = self.env['website'].get_current_website()
        products = False
        if website_id:
            products = self.search(['|',('website_ids','=',False),('website_ids','in',request.website.id)])
        return products
   
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(ProductTemplate, self).search(args,offset,limit,order,count)

class Events(models.Model):
    _inherit = 'event.event'
    
    website_ids = fields.Many2many('website', string='Websites')

    
    def get_current_website_event(self, args, offset=0, limit=None, order=None, count=False):
        website_id = self.env['website'].get_current_website()
        events = False
        if website_id:
            events = self.search(['|',('website_ids','=',False),('website_ids','in',request.website.id)])
        return events
   
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(Events, self).search(args,offset,limit,order,count)       


class EventCategory(models.Model):
    _inherit = 'event.type'

    website_ids = fields.Many2many('website', string='Websites')


    def get_current_website_event_category(self, args, offset=0, limit=None, order=None, count=False):
        website_id = self.env['website'].get_current_website()
        events = False
        if website_id:
            events = self.search(['|',('website_ids','=',False),('website_ids','in',request.website.id)])
        return events
   
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if request and request.context and request.context.get('website_id'):
            args = args + ['|',('website_ids','=',False),('website_ids','in',[request.context.get('website_id')])]
        return super(EventCategory, self).search(args,offset,limit,order,count)      

class Website(models.Model):
    _inherit = 'website'


    def get_pricelist_available(self, show_visible=False):

        """ Return the list of pricelists that can be used on website for the current user.
        Country restrictions will be detected with GeoIP (if installed).
        :param bool show_visible: if True, we don't display pricelist where selectable is False (Eg: Code promo)
        :returns: pricelist recordset
        """
        website = request and hasattr(request, 'website') and request.website or None
        if not website:
            if self.env.context.get('website_id'):
                website = self.browse(self.env.context['website_id'])
            else:
                # In the weird case we are coming from the backend (https://github.com/odoo/odoo/issues/20245)
                website = len(self) == 1 and self or self.search([], limit=1)
        isocountry = request and request.session.geoip and request.session.geoip.get('country_code') or False
        partner = self.env.user.partner_id
        order_pl = partner.last_website_so_id and partner.last_website_so_id.state == 'draft' and partner.last_website_so_id.pricelist_id
        partner_pl = partner.property_product_pricelist
        if order_pl and request.website and request.website.id not in order_pl.website_ids.ids:
            order_pl = request.env['sale.order'].search([('partner_id','=',partner.id)],order="id desc",limit=1)        
        pricelists = website._get_pl_partner_order(isocountry, show_visible,
                                                   website.user_id.sudo().partner_id.property_product_pricelist.id,
                                                   request and request.session.get('website_sale_current_pl') or None,
                                                   website.pricelist_ids,
                                                   partner_pl=partner_pl and partner_pl.id or None,
                                                   order_pl=order_pl and order_pl.id or None)


        return self.env['product.pricelist'].browse(pricelists)

    @api.multi
    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        company = request.website.company_id
        partner = self.env.user.partner_id
        pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id
        available_pricelists = [] 
        if not  pricelist_id:
            available_pricelists = self.get_pricelist_available()
            for price in available_pricelists:
                pricelist_id = price.id
                break
        _logger.info("price_lisr %s, AVAIL %s",pricelist_id,available_pricelists)
        pricelist_id =1 
        res = super(Website, self).sale_get_order(force_create, code, update_pricelist, force_pricelist)
        if request.context.get('website_id') and not request.session.get('sale_order_id'):            
                self = self.with_context(force_company=company.id)
                force_create = 1
                pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
                so_data = self._prepare_sale_order_values(partner, pricelist)
                so_data.update({'website_ids':[(6,0,[request.context.get('website_id')])]})
                sale_order = self.env['sale.order'].sudo().create(so_data)
                order_id = self.env['sale.order'].sudo().search([('id','=',sale_order.id)])
                if order_id and order_id.website_ids and request.context.get('website_id') in order_id.website_ids.ids:
                    request.session.update({'sale_order_id':order_id.id})
                order_id = self.env['sale.order'].sudo().search([('id','=',request.session.get('sale_order_id'))])
                if order_id and order_id.website_ids and request.context.get('website_id') in order_id.website_ids.ids:
                    return order_id
        if request.context.get('website_id') and request.session.get('sale_order_id'):
            order_id = self.env['sale.order'].sudo().search([('id','=',request.session.get('sale_order_id'))])
            if order_id and order_id.website_ids and request.context.get('website_id') not in order_id.website_ids.ids:
                force_create = 1
                self = self.with_context(force_company=company.id)
                pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
                so_data = self._prepare_sale_order_values(partner, pricelist)
                so_data.update({'website_ids':[(6,0,[request.context.get('website_id')])]})
                sale_order = self.env['sale.order'].sudo().create(so_data)
                order_id = self.env['sale.order'].sudo().search([('id','=',request.session.get('sale_order_id'))])
                if order_id and order_id.website_ids and request.context.get('website_id') in order_id.website_ids.ids:
                    return order_id
            if request.context.get('website_id') and not(order_id):
                force_create = 1
                
                pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
                so_data = self._prepare_sale_order_values(partner, pricelist)
                sale_order = self.env['sale.order'].sudo().create(so_data)
                order_id = self.env['sale.order'].sudo().search([('id','=',sale_order.id)])
                order_id.write({'website_ids':[(6,0,[request.website.id])]})
                if order_id and order_id.website_ids and request.context.get('website_id') in order_id.website_ids.ids:
                    request.session.update({'sale_order_id':order_id.id})
                order_id = self.env['sale.order'].sudo().search([('id','=',request.session.get('sale_order_id'))])
                if order_id and order_id.website_ids and request.context.get('website_id') in order_id.website_ids.ids:
                    return order_id

            return order_id
                  





        
class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_website_so_id = fields.Many2one(company_dependent=True)
