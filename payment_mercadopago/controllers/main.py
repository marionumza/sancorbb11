# coding=utf-8
import logging
import pprint
import werkzeug

from odoo import http, _
from odoo.http import request
import odoo.exceptions
from odoo.exceptions import UserError
from werkzeug import urls, utils
import json
from datetime import datetime

_logger = logging.getLogger(__name__)

from ..models.mercadopago_request import MecradoPagoPayment
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleInherited(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        order = request.website.sale_get_order()
        if order.partner_id == request.env.ref('base.public_partner'):
            _logger.info("<MercadoPago> has detected Customer as Public User. Redirecting to User form to get Customer details.")
            return request.redirect('/shop/address')

        return super(WebsiteSaleInherited, self).payment(**post)

    @http.route('/shop/payment/token', type='http', auth='public', website=True)
    def payment_token(self, pm_id=None, **kwargs):
        """ Method that handles payment using saved tokens

        :param int pm_id: id of the payment.token that we want to use to pay.
        """
        # print("-------testing for flow in payment_token--------")
        # print("--------payment_token-------",kwargs)
        order = request.website.sale_get_order()
        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'mercadopago')])
        if kwargs.get('payment_method') == 'cash' or kwargs.get('payment_method') == 'bank_transfer' and kwargs.get('payment_type_bank') or acquirer_id and acquirer_id.save_token == "none":
            # print("Inside if with transaction :")
            tx = request.env['payment.transaction'].sudo().search([('sale_order_id' , '=', order.id)])
            # print("------transaction : ",tx)
            request.session['sale_transaction_id'] = tx.id
            return request.redirect('/shop/payment/validate?success=True')
        else:
            # do not crash if the user has already paid and try to pay again
            if not order:
                return request.redirect('/shop/?error=no_order')

            assert order.partner_id.id != request.website.partner_id.id

            try:
                pm_id = int(pm_id)
            except ValueError:
                return request.redirect('/shop/?error=invalid_token_id')

            # We retrieve the token the user want to use to pay
            token = request.env['payment.token'].sudo().browse(pm_id)
            # print("----token----",token)
            if not token:
                return request.redirect('/shop/?error=token_not_found')

            # we retrieve an existing transaction (if it exists obviously)
            tx = request.website.sale_get_transaction() or request.env['payment.transaction'].sudo()
            # print("---------tx----------",tx)
            # we check if the transaction is Ok, if not then we create it
            tx = tx.sudo()._check_or_create_sale_tx(order, token.acquirer_id, payment_token=token, tx_type='server2server')
            # we set the transaction id into the session (so `sale_get_transaction` can retrieve it )
            request.session['sale_transaction_id'] = tx.id
            # we proceed the s2s payment
            # print("--------33333333333-----tx from website sale--------", tx)
            # print("--------33333333333-----kwargs from website sale--------", kwargs)
            res = {k: v for k, v in kwargs.items() if "cc_cvc" in k and v is not ''}
            res_installment = {k: v for k, v in kwargs.items() if "installments" == k and v is not ''}
            # print("=======res_installment",res_installment)
            installments = ""
            if res_installment :
                installments = list(res_installment.values())[0]
            else:
                installments = '1'
            if res:
                # print("-------------tx from website sale--------", res)
                tx = tx.with_context(cc_cvc=list(res.values())[0], installment=installments)
            res = tx.confirm_sale_token()
            # print("---------res in payment_token---------",res)
            if res == 'pay_sale_tx_fail' and tx.acquirer_id.provider == 'mercadopago':
                return request.redirect("/mercadopago/reject_payment"   )
            if res == 'pay_sale_tx_state' and tx.acquirer_id.provider == 'mercadopago':
                # print("trying to redirect to payment failed page.")
                msg = request.session.get('state_message')
                request.session['state_message'] = False
                return request.redirect("/mercadopago/reject_payment?state_msg="+msg)
            # we then redirect to the page that validates the payment by giving it error if there's one
            if res is not True:
                # print("We got some issues here. res is False already. Deal with it somehow")
                return request.redirect('/shop/payment/validate?success=False&error=%s' % res)
            return request.redirect('/shop/payment/validate?success=True')

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            tx = request.env['payment.transaction'].sudo().search([('sale_order_id', '=', order.id)], limit=1, order='id desc')
            return request.render("website_sale.confirmation", {'order': order, 'msg' : tx.state_message})
        else:
            return request.redirect('/shop')


class MercadoPagoController(http.Controller):

    @http.route(['/mercadopago/shop/payment/validate'], type='http', auth='public')
    def mercadopago_payment_transaction(self, **post):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        r_url = "/shop/payment/validate?success=True"
        if request.session.get('pref_id') == post.get('preference_id'):
            tx = request.env['payment.transaction'].sudo().browse(
                int(request.session.get('sale_transaction_id') or request.session.get('website_payment_tx_id', False)))
            # print("-------tx-----------",tx)
            post.update({'sale_transaction_id' : tx.id})
            request.env['payment.transaction'].sudo().form_feedback(post, 'mercadopago')
        # 2/0
        return utils.redirect(r_url)

    @http.route(['/payment/mercadopago/deposit'],type='json', auth='public')
    def mercadopago_payment_deposit(self, **kwargs):
        # print("-----------post",kwargs)
        # print("------request",request, request.session)
        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'mercadopago')])
        order = request.env['sale.order'].sudo().search([('id', '=', request.session.get('sale_order_id'))])
        mp = MecradoPagoPayment(acquirer_id)
        # 2/0
        # print("Order---------",order)
        # print("Order---------",order.partner_id.email)
        if kwargs.get('payment_method'):
            tx = request.env['payment.transaction'].sudo().browse(
                int(request.session.get('sale_transaction_id') or request.session.get('website_payment_tx_id', False)))
            # print("--------tx from mercadopago payment deposit------",tx, order)
            if not tx:
                # print("Create it please!")
                tx = tx.sudo()._check_or_create_sale_tx(order, acquirer_id, payment_token=False,
                                                        tx_type='form')
            else:
                tx = tx
            # 2/0
            kwargs.update({'sale_transaction_id' : tx.id})
            payment_resp = mp.marcadopago_payment_manual(tx, kwargs)
            # print("payment_resp----------",payment_resp)
            # print("transaction : ",tx)
            if payment_resp.get('status') == 400:
                return utils.redirect("/mercadopago/reject_payment")
            if payment_resp:
                if tx and payment_resp.get('transaction_details').get('external_resource_url'):
                    tx.write({'state_message': payment_resp.get('transaction_details').get('external_resource_url')})
                else:
                    return utils.render("payment_mercadopago.reject_payment_template")
                    # print("state msg", tx.state_message)
                kwargs.update({'id' : payment_resp.get('id'),
                               'external_resource_url' : payment_resp.get('external_resource_url'),
                               'mp_payment_type_id' : payment_resp.get('payment_type_id'),
                               'status' : payment_resp.get('status'),
                               'status_detail' : payment_resp.get('status_detail'),
                               }
                              )
                request.env['payment.transaction'].sudo().form_feedback(kwargs, 'mercadopago')
                # tx.sale_order_id.with_context(send_email=True).action_confirm()
                # tx._generate_and_pay_invoice()
                return {"result": True, "id" : acquirer_id.id, "3d_secure" : False}
            else:
                return request.render("payment_mercadopago.reject_payment_template")
        return utils.redirect('/shop')

    @http.route(['/payment/mercadopago/s2s/create_json_3ds'], type='json', auth='public', csrf=False)
    def mercadopago_s2s_create_json_3ds(self, verify_validity=False, **kwargs):
        # print("------mercadopago_s2s_create_json_3ds-----",kwargs)
        # 2/0
        # print("Token will be generated!")
        acquirer_id = request.env['payment.acquirer'].sudo().browse(int(kwargs.get('acquirer_id')))
        if acquirer_id.save_token in ("always", "ask"):
            token = acquirer_id.s2s_process(kwargs)
            if not token:
                res = {'result': False, }
                return res

            res = {'result': True, 'id': token.id, 'short_name': token.short_name, '3d_secure': False,
                   'verified': False, }

            if verify_validity != False:
                token.validate()
                res['verified'] = token.verified
        else:
            # print("Token won't be generated in this case")
            # print("------kwargs : ",kwargs)
            if kwargs.get('cc_number'):
                kwargs['cc_number'] = kwargs['cc_number'].replace(' ', '')
                mercado_obj = MecradoPagoPayment(acquirer_id)
                card_token = mercado_obj._get_card_token(acquirer_id, kwargs)
                kwargs['card_token'] = card_token.get('id')
                # print("---card_token----- : ",card_token)
                order = request.env['sale.order'].sudo().search([('id', '=', request.session.get('sale_order_id'))])
                tx = request.env['payment.transaction'].sudo().browse(int(
                    request.session.get('sale_transaction_id') or request.session.get('website_payment_tx_id',
                                                                                      False)))
                # print("--------tx from mercadopago payment deposit------",tx, order)
                if not tx:
                    # print("Create it please!")
                    tx = tx.sudo()._check_or_create_sale_tx(order, acquirer_id, payment_token=False, tx_type='form')
                else:
                    tx = tx
                # 2/0
                kwargs.update({'sale_transaction_id': tx.id})
                payment_resp = mercado_obj.mercadopago_payment_no_token(tx, kwargs)
                _logger.info('MercadoPago: entering form_feedback with post data %s', pprint.pformat(payment_resp))
                if payment_resp:
                    kwargs.update({'id': payment_resp.get('id'),
                                   'external_resource_url': payment_resp.get('external_resource_url'),
                                   'status': payment_resp.get('status'),
                                   'status_detail': payment_resp.get('status_detail'), })
                    request.env['payment.transaction'].sudo().form_feedback(kwargs, 'mercadopago')
                    # tx.sale_order_id.with_context(send_email=True).action_confirm()
                    # tx._generate_and_pay_invoice()
                # print("kwargs after form feedback", kwargs)
                res = {"result": True,
                        "id": acquirer_id.id,
                        "3d_secure": False}
        print("RES is : ",res)
        return res

    # @http.route(['/payment/mercadopago/s2s/create'], type='http', auth='public')
    # def mercadopago_s2s_create(self, **post):
    #     acquirer_id = int(post.get('acquirer_id'))
    #     acquirer = request.env['payment.acquirer'].browse(acquirer_id)
    #     acquirer.s2s_process(post)
    #     return utils.redirect(post.get('return_url', '/'))

    @http.route(['/mercadopago/reject_payment'], type='http', auth='public', website=True)
    def reject_payment(self, **data):
        # print("------controller calling--------",data,request.session.get('state_message'))
        msg = data.get('state_msg')
        return request.render("payment_mercadopago.reject_payment_template", {'msg':msg})

    @http.route(['/ipn/notification'], type='http', auth='public')
    def mercadopago_ipn_notification(self, *args,**kwargs):
        return_data = {}
        print("Request has been received!")
        print("Args : ",args)
        # kwargs =    request.jsonrequest
        print("kwargs : ",kwargs)
        if kwargs and kwargs.get('id'):
            request.env['log.payment.notifications'].sudo().create({'name': "IPN " + str(datetime.now()),
                                                                    'received_date' : datetime.now(),
                                                                    'notification_type' : "ipn",
                                                                    'notification_id' : kwargs.get('id')})
        p_id = ""
        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'mercadopago')], limit=1)
        mp = MecradoPagoPayment(acquirer_id)
        if acquirer_id.mercadopago_use_ipn:
            if kwargs.get('id'):
                p_id = kwargs.get('id')
            elif kwargs.get('resource'):
                p_id = kwargs.get('resource').split('/')[-1]
            # elif kwargs.get('merchant_order'):
            #     p_id = kwargs.get('merchant_order')
            print("-------p_id-------",p_id)
            response = {}
            if kwargs and kwargs.get('topic') == 'payment' and p_id:
                payment = mp.get_payment_update(p_id)
                response = mp.get_merchant_orders(payment.get('data').get('order').get('id'))
            elif kwargs and kwargs.get('topic') == 'merchant_order' and p_id:
                payment = mp.get_payment_update(p_id)
                print ("===========", payment)
                response = mp.get_merchant_orders(payment.get('data').get('order').get('id'))
                print ("--------------", response)
            else:
                _logger.info("Sorry, Something went wrong before getting details of %s with id of %s"% (kwargs.get('topic'), p_id))
            # if response.get('status') in (200, 201) and kwargs.get('topic') == 'payment' and response.get('data'):
            #     merchant_orders = mp.get_merchant_orders(response.get('data').get('order').get('id'))
            # elif response.get('status') in (200, 201) and kwargs.get('topic') == 'merchant_order' and response.get('data'):
            #     merchant_orders = response
            if response and response.get('status') in (200, 201):
                return_data['payment'] = response.get('data').get('payments')
                return_data['shipment'] = response.get('data').get('shipments')
            print("Response : ",response)
            print ('>>>>>>>>>>>>>>>>>', response.get('data').get('payments'))
            if response:
                payments = response.get('data').get('payments') or []
                for payment in payments:
                    payment_respose = mp.get_payment_update(str(payment.get('id')))
                    self.process_payment(payment_respose)
            else:
                _logger.info("Payment has not been processed,\n We did not get any merchant order from MercadoPago with reference of Id : %s"% p_id)
            if return_data:
                return return_data
            else:
                return False
        else:
            return False

    @http.route(['/hooks/payment_info'], type='json', auth='public')
    def mercadopago_hooks_payment_create(self, *args, **kwargs):
        print(request.jsonrequest)
        hook_data = request.jsonrequest
        if hook_data and hook_data.get('action') and hook_data.get('action') and hook_data.get('data'):
            request.env['log.payment.notifications'].sudo().create({'name': "WebHook " + str(datetime.now()),
                                                                    'received_date': datetime.now(),
                                                                    'notification_type': "webhook",
                                                                    'notification_id': hook_data.get('data').get('id'),
                                                                    'notification_data' : hook_data.get('data')})
        if hook_data and hook_data.get('action') == "payment.created":
            payment_transaction = request.env['payment.transaction'].sudo().search([('acquirer_reference', '=', hook_data.get('data').get('id'))])
            if payment_transaction:
                return True
            else:
                acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'mercadopago')], limit=1)
                mp = MecradoPagoPayment(acquirer_id)
                mp_d = mp.get_payment_update(hook_data.get('data').get('id'))
                mp_data = mp.get_merchant_orders(mp_d.get('order').get('id'))
                if mp_data:
                    for payment in mp_data.get('payments'):
                        self.process_payment(payment)
                    return {'payments' : mp_data.get('payments'),
                            'shipments' : mp_data.get('shipments')}
                else:
                    return False
        elif hook_data and hook_data.get('action') == "payment.updated":
            payment_transaction = request.env['payment.transaction'].sudo().search([('acquirer_reference', '=', hook_data.get('data').get('id'))])
            if payment_transaction:
                acquirer_id = request.env['payment.acquirer'].sudo().search([('provider', '=', 'mercadopago')])
                mp = MecradoPagoPayment(acquirer_id)
                mp_d = mp.get_payment_update(hook_data.get('data').get('id'))
                mp_data = mp.get_merchant_orders(mp_d.get('order').get('id'))
                if mp_data:
                    for payment in mp_data.get('payments'):
                        self.process_payment(payment)
                    return {'payments': mp_data.get('payments'),
                            'shipments': mp_data.get('shipments')}
                else:
                    return False
            else:
                _logger.info("Payment Transaction with reference to id=%s is not available in Odoo"% hook_data.get('data').get('id'))
                return False

        return True

    def process_payment(self, response):
        # print ('+_+__+_', response)
        _logger.info(
            'Payment status has been changed for MercadoPago Payment of Sale Order : %s to %s, now changing payment status in Odoo.',
            response.get('data').get('description'), response.get('data').get('status'))
        tx = request.env['payment.transaction'].sudo().search([('acquirer_reference', '=', response.get('data').get('id'))])
        if not tx:
            raise odoo.exceptions.MissingError(
                'Transaction does not exist or has been deleted for MercadoPago Payment reference : %s' % response.get(
                    'data').get('id'))

        status = "pending" if response.get('data').get('status') in ("in_process", "pending") else response.get(
            'data').get('status')
        status = "done" if response.get('data').get('status') == "approved" else status
        # print("tx : ",tx, status)
        if tx.state == status:
            _logger.info('Payment status is already in same state.')
            return True
        tx.write({'state': status})
        if response.get('data').get('status') == "approved" and tx.state in ('authorized', 'done'):
            _logger.info("Payment has been done, now confirming Sale Order as well paying invoice.")
            tx.sale_order_id.with_context(send_email=True).action_confirm()
            tx._generate_and_pay_invoice()
        return True
