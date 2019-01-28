# -*- coding: utf-8 -*-
import json

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale as WebsiteSale
from odoo.http import request


class UpdateVariantsInCart(WebsiteSale):

    @http.route(['/shop/cart/<model("product.product"):product>/variants'], type='http', auth="public", csrf=False,
                website=True)
    def productVariants(self, product, **post):
        pricelist = request.website.get_current_pricelist()
        return request.render("update_variants_in_cart.variantUpdateForm", {
            'product': product.with_context(pricelist=int(pricelist)),
            'previous_line_id': post.get('previous_line_id', False)
        })

    @http.route(['/shop/cart/update/variant'], type='http', auth="public", website=True)
    def updateVariant(self, **post):
        order_line_id = post.get('previous_line_id', False)
        product_id = post.get('variant_id', False)
        quantity = post.get('quantity', False)

        value = request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id),
                                                                            set_qty=float(quantity))

        if int(order_line_id) != value.get('line_id', False):
            request.env['sale.order.line'].sudo().browse(int(order_line_id)).unlink()
        return json.dumps({'status': True, 'value': value})
