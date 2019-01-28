# -*- coding: utf-8 -*-

import json
import logging
from werkzeug.exceptions import Forbidden, NotFound

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.exceptions import ValidationError
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression

from odoo import models
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class ResPartnerId_category(models.Model):
    _inherit = 'res.partner.id_category'

    def get_website_sale_cat_ids(self):
        return self.sudo().search([])


class WebsiteSaleExtension(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            pre_values.update({'name': pre_values['first_name'] + ' ' + pre_values['last_name']}) #NEW
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            # NEW
            if order.amount_total > 1000:
                if not 'main_id_category_id' in pre_values.keys():
                    errors["main_id_category_id"] = 'missing'
                    error_msg.append(_('Some required fields are empty.'))
                else:
                    if not pre_values['main_id_category_id']:
                        errors["main_id_category_id"] = 'missing'
                        error_msg.append(_('Some required fields are empty.'))
                if not 'main_id_number' in pre_values.keys():
                    errors["main_id_number"] = 'missing'
                    error_msg.append(_('Tipo Documento: Es necesario ingresar una opción.'))
                else:
                    if not pre_values['main_id_number']:
                        errors["main_id_number"] = 'missing'
                        error_msg.append(_('Some required fields are empty.'))
            if pre_values['main_id_number']:
                if len(pre_values['main_id_number']) < 6 or len(pre_values['main_id_number']) > 8 or not pre_values['main_id_number'].isdigit():
                    errors["main_id_number"] = 'missing'
                    error_msg.append(_('Nro de Documento: Este campo solo permite un valor numérico de 6 a 8 dígitos'))
            if pre_values['street_number']:
                if not pre_values['street_number'].isdigit():
                    errors["street_number"] = 'missing'
                    error_msg.append(_('Numero de Calle: Solo se admite el ingreso de números, maximo 5 dígitos'))
            if pre_values['zip']:
                if not pre_values['zip'].isdigit() or len(pre_values['zip']) > 4:
                    errors["zip"] = 'missing'
                    error_msg.append(_('Código Postal: Solo se permite el ingreso de 4 números'))


            if pre_values['first_name']:
                if len(pre_values['first_name']) < 2:
                    errors["first_name"] = 'missing'
                    error_msg.append(_('Nombre: Se deben ingresar 2 letras o más'))
            if pre_values['last_name']:
                if len(pre_values['last_name']) < 2:
                    errors["last_name"] = 'missing'
                    error_msg.append(_('Apellido: Se deben ingresar 2 letras o más'))
            if pre_values['phone']:
                if not pre_values['phone'].isdigit() or len(pre_values['phone']) < 8:
                    errors["phone"] = 'missing'
                    error_msg.append(_('Télefono: Ingresar solo números, minimo 8 digitos'))
            if pre_values['street']:
                if len(pre_values['street']) < 3:
                    errors["street"] = 'missing'
                    error_msg.append(_('Calle: Se deben ingresar 3 letras o más'))
            if pre_values['street2']:
                if len(pre_values['street2']) < 3:
                    errors["street2"] = 'missing'
                    error_msg.append(_('Error de Formato en entre calle/esquina 3 letras o mas'))
            if pre_values['who_receive']:
                if len(pre_values['who_receive']) < 3:
                    errors["who_receive"] = 'missing'
                    error_msg.append(_('Quien Recibe: Se debe ingresar un nombre con 3 letras o más'))


            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)

                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/checkout')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }

        #NEW VALUES
        main_id_category_ids = request.env['res.partner.id_category']
        render_values.update({'main_id_category_ids': main_id_category_ids.get_website_sale_cat_ids()})



        return request.render("website_sale.address", render_values)
