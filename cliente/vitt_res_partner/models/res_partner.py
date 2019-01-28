# -*- coding: utf-8 -*-
# 2018 Moogah

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResPartnerIdCategory(models.Model):
    _name = "res.partner.id_category"
    _order = "name"

    def _default_validation_code(self):
        return _("\n# Python code. Use failed = True to specify that the id "
                 "number is not valid.\n"
                 "# You can use the following variables :\n"
                 "#  - self: browse_record of the current ID Category "
                 "browse_record\n"
                 "#  - id_number: browse_record of ID number to validate")

    code = fields.Char(
        string="Code", size=16, required=True,
        help="Abbreviation or acronym of this ID type. For example, "
             "'driver_license'")
    name = fields.Char(
        string="ID name", required=True, translate=True,
        help="Name of this ID type. For example, 'Driver License'")
    active = fields.Boolean(string="Active", default=True)
    validation_code = fields.Text(
        'Python validation code',
        help="Python code called to validate an id number.",
        default=_default_validation_code)

    sequence = fields.Integer(
        default=10,
        required=True,
    )
    afip_code = fields.Integer(
        'AFIP Code',
        required=True,
        translate=True
    )
    arciba_doc_code = fields.Char(size=1,string=" ARCIBA Doc. Code",translate=True)
    ecommerce_avail = fields.Boolean(string="Available for eCommerce")

class AfipresponsabilityType(models.Model):
    _name = 'afip.responsability.type'
    _description = 'AFIP Responsability Type'
    _order = 'sequence'

    name = fields.Char(
        'Name',
        translate=True,
        size=64,
        required=True
    )
    sequence = fields.Integer(
        'Sequence',
        translate=True,
    )
    code = fields.Char(
        'Code',
        translate=True,
        size=8,
        required=True
    )
    active = fields.Boolean(
        'Active',
        translate=True,
        default=True
    )

    _sql_constraints = [('name', 'unique(name)', 'Name must be unique!'),
                        ('code', 'unique(code)', 'Code must be unique!')]
