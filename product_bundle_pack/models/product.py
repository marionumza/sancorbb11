# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


class ProductPack(models.Model):
    _name = 'product.pack'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    qty_uom = fields.Float(string='Quantity', required=True, defaults=1.0)
    bi_product_template = fields.Many2one(comodel_name='product.template', string='Product pack')
    bi_image = fields.Binary(related='product_id.image_medium', string='Image', store=True)
    price = fields.Float(related='product_id.lst_price', string='Product Price')
    uom_id = fields.Many2one(related='product_id.uom_id' , string="Unit of Measure", readonly="1")
    name = fields.Char(related='product_id.name', readonly="1")

class ProductProduct(models.Model):
    _inherit = 'product.template'

    is_pack = fields.Boolean(string='Is Product Pack')
    cal_pack_price = fields.Boolean(string='Calculate Pack Price')
    pack_ids = fields.One2many(comodel_name='product.pack', inverse_name='bi_product_template', string='Product pack')

    @api.model
    def create(self,vals):
        total = 0
        res = super(ProductProduct,self).create(vals)
        if res.cal_pack_price:
            if 'pack_ids' in vals or 'cal_pack_price' in vals:
                    for pack_product in res.pack_ids:
                            qty = pack_product.qty_uom
                            price = pack_product.product_id.list_price
                            total += qty * price
        if total > 0:
            res.list_price = total
        return res


    @api.multi
    def write(self,vals):
        total = 0
        res = super(ProductProduct, self).write(vals)
        if self.cal_pack_price:
            if 'pack_ids' in vals or 'cal_pack_price' in vals:
                    for pack_product in self.pack_ids:
                            qty = pack_product.qty_uom
                            price = pack_product.product_id.list_price
                            total += qty * price
        if total > 0:
            self.list_price = total
        return res


class StockMove(models.Model):
    _inherit="stock.move"

    @api.multi
    def _action_done(self):
        _logger.info("+++++++++++++++++++++>++++++++++")
        """ Makes the move done and if all moves are done, it will finish the picking.
		@return:
		"""
        context = self.env.context.copy() or {}
        super(StockMove, self)._action_done()

        ids = self

        for id in ids:
            data = self.browse(id.id)
            erp_product_id = data.product_id.id

            #product = self.env['product.product'].browse(erp_product_id)
            available_qty = data.product_id.qty_available
            incoming_qty = data.product_id.incoming_qty
            outgoing_qty = data.product_id.outgoing_qty
            virtual_available = data.product_id.virtual_available
            quantity = data.product_qty

            product_pack = self.env['product.product'].search([('is_pack', '=', True)])

            for product in product_pack:

                contains = False

                if product.pack_ids:
                    l = [(id_pack.product_id.qty_available/id_pack.qty_uom, id_pack.product_id.id)
                         for id_pack in product.pack_ids if id_pack.qty_uom > 0]
                    if l:
                        less = l[0][0]

                        for i in l:

                            less = min(less, i[0])

                            if i[1] == erp_product_id:
                                contains = True

                # for id_pack in product.pack_ids:
                #
                #     _logger.info("QUNATITYYYYYYY+++++++++++++++++++++>%r", [id_pack.qty_uom])
                #
                #     if id_pack.qty_uom > 0:
                #
                #         less = min(less, id_pack.product_id.qty_available/id_pack.qty_uom)
                #
                #         if id_pack.product_id.id == erp_product_id:
                #             contains = True

                if contains:

                    wizard = self.env['stock.change.product.qty'].create({
                        'product_id': product.id,
                        'new_quantity': float(less),
                        'location_id': data.location_id.id,
                        })
                    wizard.change_product_qty()
