# -*- coding: utf-8 -*-

from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.http import request
import odoo
from odoo import fields, http, _
from odoo.exceptions import UserError, AccessError
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.http_routing.models.ir_http import slug
import werkzeug
import pytz
import babel.dates
from collections import OrderedDict
import itertools
from odoo.addons.website_event.controllers.main import WebsiteEventController
from datetime import datetime, timedelta
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_form.controllers.main import WebsiteForm
import json
import os

from odoo.addons.auth_signup.controllers.main import AuthSignupHome

class AuthSignupHomes(AuthSignupHome):

    @http.route()
    def web_auth_signup(self, *args, **kw):
    	res = super(AuthSignupHomes, self).web_auth_signup(*args, **kw)
    	if request.uid != odoo.SUPERUSER_ID:
    		request.env['res.users'].sudo().search([('id','=',request.uid)]).write({'website_ids':[(6,0,[request.context.get('website_id')])]})
    	return res
    
class WebsiteEvent(WebsiteEventController):


    def _add_event(self, event_name=None, context=None, **kwargs):
        if not event_name:
            event_name = _("New Event")
        date_begin = datetime.today() + timedelta(days=(14))
        vals = {
            'name': event_name,
            'date_begin': fields.Date.to_string(date_begin),
            'date_end': fields.Date.to_string((date_begin + timedelta(days=(1)))),
            'seats_available': 1000,
            'website_ids' :[(6,0,[request.context.get('website_id')])]
        }
        return request.env['event.event'].with_context(context or {}).create(vals)
        
    @http.route()
    def event(self, event, **post):
        res = super(WebsiteEvent,self).event(event,**post)
        if event and event.website_ids and request.context.get('website_id') not in event.website_ids.ids:
            return request.render('website.404')
        return res
        
    @http.route()        
    def event_register(self, event, **post): 
        res = super(WebsiteEvent,self).event_register(event,**post)
        if event and event.website_ids and request.context.get('website_id') not in event.website_ids.ids:
            return request.render('website.404')
        return res
               
    @http.route()        
    def event_page(self, event, page, **post):
        res = super(WebsiteEvent,self).event_page(event,page,**post)
        if event and event.website_ids and request.context.get('website_id') not in event.website_ids.ids:
            return request.render('website.404')
        return res    
        
class WebsiteBlog(WebsiteBlog):

    def nav_list(self, blog=None):
        website_id = request.context.get('website_id')
        dom = []
        if  blog and blog.website_ids and website_id and website_id in blog.website_ids.ids:
             dom = ['&',('website_ids','in',[request.context.get('website_id')])]
             dom +=  [('blog_id', '=', blog.id)]
        post_ids =  request.env['blog.post'].search(dom) and request.env['blog.post'].search(dom).ids or []
        if not request.env.user.has_group('website.group_website_designer'):
            dom += [('post_date', '<=', fields.Datetime.now())]
        groups = request.env['blog.post']._read_group_raw(
            [('id','in',post_ids)],
            ['name', 'post_date','website_ids'],
            groupby=["post_date"], orderby="post_date desc")
        for group in groups:
            (r, label) = group['post_date']
            start, end = r.split('/')
            group['post_date'] = label
            group['date_begin'] = start
            group['date_end'] = end

            locale = request.context.get('lang') or 'en_US'
            start = pytz.UTC.localize(fields.Datetime.from_string(start))
            tzinfo = pytz.timezone(request.context.get('tz', 'utc') or 'utc')

            group['month'] = babel.dates.format_datetime(start, format='MMMM', tzinfo=tzinfo, locale=locale)
            group['year'] = babel.dates.format_datetime(start, format='YYYY', tzinfo=tzinfo, locale=locale)

        return OrderedDict((year, [m for m in months]) for year, months in itertools.groupby(groups, lambda g: g['year']))

    @http.route()
    def blog(self, blog=None, tag=None, page=1, **opt):
        res = super(WebsiteBlog,self).blog(blog,tag,page,**opt)
        if blog and blog.website_ids and request.context.get('website_id') not in blog.website_ids.ids:
            return request.render('website.404')
        return res
        
    @http.route()
    def blog_post_create(self, blog_id, **post):
        new_blog_post = request.env['blog.post'].create({
            'blog_id': blog_id,
            'website_published': False,
            'website_ids' :[(6,0,[request.context.get('website_id')])]
        })
        return werkzeug.utils.redirect("/blog/%s/post/%s?enable_editor=1" % (slug(new_blog_post.blog_id), slug(new_blog_post)))
                
class WebsiteSale(WebsiteSale):

        
    @http.route()
    def add_product(self, name=None, category=0, **post):
        product = request.env['product.product'].create({
            'name': name or _("New Product"),
            'public_categ_ids': category,
            'website_ids' :[(6,0,[request.context.get('website_id')])]
        })
        return "/shop/product/%s?enable_editor=1" % slug(product.product_tmpl_id)
        
    @http.route()
    def product(self, product, category='', search='', **kwargs):
        res = super(WebsiteSale,self).product(product,category,search,**kwargs)
        if product and product.website_ids and request.context.get('website_id') not in product.website_ids.ids:
            return request.render('website.404')         
        return res   

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSale,self).shop(page,category,search,ppg,**post)
        if category and category.website_ids and request.context.get('website_id') and request.context.get('website_id') not in category.website_ids.ids:
            return request.render('website.404')        
        categs = request.env['product.public.category'].search([
            ('parent_id', '=', False),
            '|',
            ('website_ids', '=', False),
            ('website_ids', 'in', [request.website.id]),
        ])
        res.qcontext.update({
            'categories': categs,
        })
        return res 

  
              
class Home(Home):
    
    '''@http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        request.params['login_success'] = False
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        values = request.params.copy()

        if 'g-recaptcha-response' in kw and \
           not request.website.is_captcha_valid(kw['g-recaptcha-response']):
            values['error'] = _("Required: Invalid/Missing reCaptcha.")
            response = request.render('web.login', values)
            response.headers['X-Frame-Options'] = 'DENY'

            if 'login' not in values and request.session.get('auth_login'):
                values['login'] = request.session.get('auth_login')
            return response
        return super(Home, self).web_login(redirect=redirect, **kw)'''


class AuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if 'g-recaptcha-response' in kw and \
           not request.website.is_captcha_valid(kw['g-recaptcha-response']):
            qcontext['error'] = _("Required: Invalid/Missing reCaptcha.")
            return request.render('auth_signup.signup', qcontext)
        return super(AuthSignupHome, self).web_auth_signup(*args, **kw)


class WebsiteForm(WebsiteForm):

    @http.route()
    def website_form(self, model_name, **kwargs):
        if kwargs.get('g-recaptcha-response'):
            if request.website.is_captcha_valid(kwargs['g-recaptcha-response']):
                del kwargs['g-recaptcha-response']
                return super(WebsiteForm, self).website_form(model_name, **kwargs)
            else:
                return super(WebsiteForm, self).website_form(None, **kwargs)
        return super(WebsiteForm, self).website_form(model_name, **kwargs)
        
        
class Website(Website):

            
    @http.route()
    def theme_customize(self, enable, disable, get_bundle=False):
        res = super(Website,self).theme_customize(enable,disable,get_bundle)
        ids = self.get_view_ids(enable)
        disable_ids = self.get_view_ids(disable)
        for view in request.env['ir.ui.view'].with_context(active_test=True).browse(ids):
            website_record = request.env['customize.active.website'].search([('view_id','=',view.id)])
            if not website_record:
                request.env['customize.active.website'].create({'view_id':view.id,'website_ids': [(6, None, [request.context.get('website_id')])]})                    
            else:
                if website_record and website_record.website_ids:
                    website_record.write({'website_ids' :[(4,request.context.get('website_id'),None)]})
                if not website_record.website_ids:
                   website_record.write({'website_ids' :[(6,0,[request.context.get('website_id')])]})
            if website_record and website_record.view_id:
                website_record.view_id.write({'active':True}) 
        for view in request.env['ir.ui.view'].with_context(active_test=True).browse(disable_ids):
            website_record = request.env['customize.active.website'].search([('view_id','=',view.id)])
            if website_record:
                if request.context.get('website_id'):
                    website_record.write({'website_ids' :[(3,request.context.get('website_id'),)]})

        return res
