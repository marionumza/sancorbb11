# -*- coding: utf-8 -*-
from odoo import http

# class WebsiteMassMailingExtends(http.Controller):
#     @http.route('/website_mass_mailing_extends/website_mass_mailing_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_mass_mailing_extends/website_mass_mailing_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_mass_mailing_extends.listing', {
#             'root': '/website_mass_mailing_extends/website_mass_mailing_extends',
#             'objects': http.request.env['website_mass_mailing_extends.website_mass_mailing_extends'].search([]),
#         })

#     @http.route('/website_mass_mailing_extends/website_mass_mailing_extends/objects/<model("website_mass_mailing_extends.website_mass_mailing_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_mass_mailing_extends.object', {
#             'object': obj
#         })