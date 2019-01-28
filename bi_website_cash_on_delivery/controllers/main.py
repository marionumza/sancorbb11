# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http, tools, SUPERUSER_ID, _
from odoo.http import request

_logger = logging.getLogger(__name__)

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteCODPayment(http.Controller):

    _accept_url = '/cod/payment/feedback'
    _return_url = '/shop/payment/confirmation'

    @http.route([
        '/cod/payment/feedback',
    ], type='http', auth='none', csrf=False)
    def cod_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        
        request.env['payment.transaction'].sudo().form_feedback(post, 'cod')
        return werkzeug.utils.redirect(post.pop('return_url', '/'))
    
    
    @http.route('/shop/payment/cod', type='json', auth="public", methods=['POST'], website=True)
    def codline(self, payment_id, **post):
        #cr, uid, context = request.cr, request.uid, request.context
        #print('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
        #request.redirect('bi_website_cash_on_delivery.cod_notify')
        
        '''payment_acquirer_obj = request.env['payment.acquirer'].sudo().search([('id','=', payment_id)]) 
        
        order = request.website.sale_get_order()
        product_obj = request.env['product.product'].browse()
        extra_fees_product = request.env['ir.model.data'].get_object_reference('bi_website_cash_on_delivery', 'product_product_fees')[1]
        product_ids = product_obj.sudo().search([('product_tmpl_id.id', '=', extra_fees_product)])
        
        order_line_obj = request.env['sale.order.line'].sudo().search([])
        
        
        flag = 0
        for i in order_line_obj:
            if i.product_id.id == product_ids.id and i.order_id.id == order.id:
                flag = flag + 1
        
        if flag == 0:
            order_line_obj.sudo().create({
                    'product_id': product_ids.id,
                    'name': 'Extra Fees',
                    'price_unit': payment_acquirer_obj.delivery_fees,
                    'order_id': order.id,
                    'product_uom':product_ids.uom_id.id,
                
                })
        
        
        print('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooo',product_ids)'''
        #order.write({'amount_total': order.amount_total + payment_acquirer_obj.fees_dom_fixed})
        
        #return {
          #  'type': 'ir.actions.client',
          #  'tag': 'reload',
        #}
            
        return True
    
    @http.route('/shop/payment/default', type='json', auth="public", methods=['POST'], website=True)
    def payment_default(self, payment_id, **post):  	
        
        cr, uid, context = request.cr, request.uid, request.context
        
        return request.redirect('/shop/payment/validate')


class WebsiteCODPayment(WebsiteSale):

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        
        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            tx = request.env['payment.transaction'].browse(transaction_id)

        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')


        # if payment.acquirer is cod payment provider
        if tx.acquirer_id.provider == 'cod':
            
            payment_acquirer_obj = request.env['payment.acquirer'].sudo().search([('id','=', tx.acquirer_id.id)]) 
        
            order = request.website.sale_get_order()
            product_obj = request.env['product.product'].browse()
            extra_fees_product = request.env['ir.model.data'].get_object_reference('bi_website_cash_on_delivery', 'product_product_fees')[1]
            product_ids = product_obj.sudo().search([('product_tmpl_id.id', '=', extra_fees_product)])
            
            order_line_obj = request.env['sale.order.line'].sudo().search([])
            
            
            flag = 0
            for i in order_line_obj:
                if i.product_id.id == product_ids.id and i.order_id.id == order.id:
                    flag = flag + 1
            
            if flag == 0:
                order_line_obj.sudo().create({
                        'product_id': product_ids.id,
                        'name': 'Extra Fees',
                        'price_unit': payment_acquirer_obj.delivery_fees,
                        'order_id': order.id,
                        'product_uom':product_ids.uom_id.id,
                    
                    })
                         
            
            #order.force_quotation_send()
            order.with_context(send_email=True).action_confirm()
            request.website.sale_reset()
            return request.render("website_sale.confirmation", {'order': order})
            
            
        if (not order.amount_total and not tx) or tx.state in ['pending', 'done', 'authorized']:
            if (not order.amount_total and not tx):
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
                order.with_context(send_email=True).action_confirm()
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            order.action_cancel()

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        return request.redirect('/shop/confirmation')        
        
            	
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
