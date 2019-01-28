# -*- coding: utf-8 -*-
# Copyright 2018 Pierre Faniel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    # has_google_tag_manager is used only in UI at the moment
    has_google_tag_manager = fields.Boolean('Google Tag Manager Key')
    google_tag_manager_key = fields.Char('Google Tag Manager Key', help='Container ID')
