# coding=utf-8
from odoo import api, fields, models, _

class MercadopagoResPartner(models.Model):
    _inherit = "res.partner"

    mercadopago_customer = fields.Char(string="MercadoPago Customer Id", store=True)