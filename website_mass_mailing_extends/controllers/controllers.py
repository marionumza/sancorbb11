# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import route, request
from odoo.addons.website_mass_mailing.controllers.main import MassMailController
import logging
_logger = logging.getLogger(__name__)

class WebsiteMassMailingExtends(MassMailController):

    @route('/website_mass_mailing/subscribe', type='json', website=True, auth="public")
    def subscribe(self, list_id, email, days, month, year, **post):
        _logger.info("+++++++++++++++++++++>>>>>>>>>>>>>>++++++++++")
        Partner = request.env['res.partner'].sudo()
        id_partner = Partner.create({'name': email, 'email': email})
        _logger.info(id_partner.id)
        Children = request.env['children.children'].sudo()
        i = 0
        while i < len(days):
            Children.create({'day': days[i], 'month': month[i], 'year': year[i], 'partner_ids': id_partner.id})
            i = i+1
        return super(WebsiteMassMailingExtends, self).subscribe(list_id, email)