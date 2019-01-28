# -*- coding: utf-8 -*-
# 2018 Moogah

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"
    _name = "res.partner"

    first_name = fields.Char(string="First Name",translate=True)
    last_name = fields.Char(string="Last Name",translate=True)
    street_number = fields.Char(string="Street Number", translate=True)
    street3 = fields.Text(string="Aditional Info", translate=True)
    neighborhood = fields.Char(string="Neighborhood", translate=True)
    floor = fields.Char(string="Floor", translate=True)
    apartment = fields.Char(string="Apartment", translate=True)
    main_id_category_id = fields.Many2one('res.partner.id_category', string="ID Document Type",  translate=True)
    main_id_number = fields.Char(string="Main ID Number", translate=True)
    afip_responsability_type_id = fields.Many2one('afip.responsability.type', string="Tax Responsibility Type", translate=True)
    localidad = fields.Char(string="Localidad", translate=True)
    partido = fields.Char(string="Partido", translate=True)
    who_receive = fields.Char(strng="quien recibe")

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        res['afip_responsability_type_id'] = self.env['afip.responsability.type'].search([],limit=1).id

        return res

    @api.multi
    def _display_address(self, without_company=False):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = self.country_id.address_format or \
            self._get_default_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
            'company_name': self.commercial_company_name or '',
            'street_number': self.street_number or '',
            'neighborhood': self.neighborhood or '',
            'floor': self.floor or '',
            'apartment': self.apartment or '',
            'localidad': self.localidad or '',
            'partido': self.partido or '',
            'zip': self.zip or '',
        }
        for field in self._address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    street3 = fields.Text(related="partner_id.street3",string="Aditional Info", translate=True)
    neighborhood = fields.Char(related="partner_id.neighborhood",string="Neighborhood", translate=True)
    floor = fields.Char(related="partner_id.floor",string="Floor", translate=True)
    apartment = fields.Char(related="partner_id.apartment",string="Apartment", translate=True)
    localidad = fields.Char(related="partner_id.localidad",string="Localidad", translate=True)
    partido = fields.Char(related="partner_id.partido",string="Partido", translate=True)
    zip = fields.Char(related="partner_id.zip",string='Zip', change_default=True)
    city = fields.Char(related="partner_id.city",string='City')
    state_id = fields.Many2one(related="partner_id.state_id",string='State')
    country_id = fields.Many2one(related="partner_id.country_id",string='Country')
    who_receive = fields.Char(related="partner_shipping_id.who_receive",string="Quien Recibe")

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for so in self:
            sp = self.env['stock.picking'].search([('sale_id.id', '=', so.id)])
            for pick in sp:
                pick.write({'who_receive': so.who_receive})
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    who_receive = fields.Char(string="Quien Recibe")
