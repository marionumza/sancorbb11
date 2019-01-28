# -*- coding: utf-8 -*-
# 2018 Moogah

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    child_name = fields.Char(string="Nombre de hijo/hija")
    birthdate = fields.Date(string="Fecha de nacimiento")
