# coding=utf-8

import requests
import mercadopago
import json
from datetime import datetime
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
class MecradoPagoPayment():

    def __init__(self, acquirer):
        self.url = "https://api.mercadopago.com"
        # _logger.info(acquirer.mercadopago_client_secret)
        mp_token = mercadopago.MP(acquirer.mercadopago_client_id, acquirer.mercadopago_client_secret)
        if acquirer.environment == "test":
            access_token = acquirer.mercadopago_test_access_token
        else:
            access_token = mp_token.get_access_token()

        # print("-----mp-----",mp)
        self.mp = mercadopago.MP(access_token)
        self.accessToken = access_token

    def _get_card_token(self,acquirer, values):
        if not values:
            raise ValidationError(_('Card Details seems to be missing. Please check it.'))
        if acquirer.environment == "test":
            if not acquirer.mercadopago_test_public_key:
                raise ValidationError(_('Please provide Test Public Key in MercardoPago payment acquirer provided by MercadoPago.'))
            public_key = acquirer.mercadopago_test_public_key
        else:
            if not acquirer.mercadopago_prod_public_key:
                raise ValidationError(_('Please provide Public Key in MercardoPago payment acquirer provided by MercadoPago.'))
            public_key = acquirer.mercadopago_prod_public_key

        if values:
            expiration_month = str(values['cc_expiry'][:2])
            expiration_year = datetime.strptime(str(values['cc_expiry'][-2:]), '%y').strftime('%Y')

        data = {"card_number": values['cc_number'],
                "expiration_month": expiration_month,
                "security_code": values['cc_cvc'],
                "expiration_year": expiration_year,
                "cardholder": {"identification": {"number": values['docNumber'],
                                                  "type": values['docType'],
                                                  },
                               "name": values['cc_holder_name']
                               },
                }

        # print("--------data--------",data)
        # print("-----url data------",self.url, public_key)
        card_token = requests.post("%s/v1/card_tokens?public_key=%s"% (self.url, public_key), headers={"content-type":"application/json"}, data=json.dumps(data))
        # print("-----card token------",card_token, card_token.json())
        if card_token:
            if acquirer.save_token and acquirer.save_token == "none":
                pass
        # print("---------card_token-------",card_token)
        if not card_token:
            raise ValidationError(_('Unable to generate Card Token from MercadoPago API. Please contact administration'))
        return card_token.json()

    def _create_mercadopago_customer(self, partner, acquirer):
        # if acquirer.environment == "test":
        #     mp = self.mp
        # else:
        #     mp = mercadopago.MP(self.accessToken)
        # print("----mp----",mp)
        # create_url = self.url + "/v1/customers"
        mp = self.mp
        first_name = ''
        last_name = ''
        if partner.name:
            split_name = partner.name.split(" ")
            if split_name[0]:
                first_name = partner.name.split(" ")[0]
            if len(split_name) >1:
                last_name = partner.name.split(" ")[1]
        data = {"first_name" : first_name,
                "last_name" : last_name,
                "address" : {"street_name" : partner.street if partner.street else ""+ partner.street2 if partner.street2 else "",
                             "zip_code" : partner.zip},
                "email" : partner.email,
                "phone" : {"area_code" : "",
                           "number" : partner.phone}
                }
        # print("-----data----",data)
        create_response = mp.post("/v1/customers", data)
        # print("------create_response-------",create_response)
        return create_response.get('response')

    def _set_customer_card(self, mercadopago_profile_id, acquirer, card_token):
        if mercadopago_profile_id and card_token.get('id'):
            # if acquirer.environment == "test":
            #     access_token = "TEST-4525870278296149-082019-d9ace4366816503b329ff0a4dea12b84-347469609"
            # else:
            #     access_token = self.accessToken
            mp = self.mp
            create_card = mp.post("/v1/customers/"+mercadopago_profile_id+"/cards", {'token' : card_token.get('id')})
            # print("------create_card--------",create_card)
            return create_card.get("response")

    def mercadopago_payment(self, transaction):
        if transaction:
            # if transaction.acquirer_id.environment == "test":
            #     access_token = "TEST-4525870278296149-082019-d9ace4366816503b329ff0a4dea12b84-347469609"
            # else:
            #     access_token = self.accessToken
            # mp = mercadopago.MP(access_token)
            mp = self.mp
            # print("-------mp-----",mp)
            first_name = ''
            last_name = ''
            if transaction.partner_id.name:
                split_name = transaction.partner_id.name.split(" ")
                if split_name[0]:
                    first_name = transaction.partner_id.name.split(" ")[0]
                if len(split_name) > 1:
                    last_name = transaction.partner_id.name.split(" ")[1]
                installments = ""
                if transaction.payment_token_id.mercadopago_installments:
                    installments = transaction.payment_token_id.mercadopago_installments
                else:
                    installments = '1'

            payment_data = {"transaction_amount" : transaction.amount,
                            "description" : transaction.reference,
                            "token" : transaction.payment_token_id.acquirer_ref,
                            "installments" : int(installments),
                            "payment_method_id" : transaction.payment_token_id.mercadopago_profile.split(":")[-1],
                            "payer" : {"first_name" : first_name,
                                       "last_name" : last_name,
                                       "address" : {"street_name" : transaction.partner_id.street if transaction.partner_id.street else ""+ transaction.partner_id.street2 if transaction.partner_id.street2 else "",
                                                    "zip_code" : transaction.partner_id.zip},
                                       "email" : transaction.partner_id.email,
                                        },
                            "capture" : True
                            }
            # print("---------payment_data--------",payment_data)

            payment_response = mp.post("/v1/payments", payment_data)
            # print("---------payment_response--------",payment_response)
            return payment_response.get('response')

        else:
            raise ValidationError(_('Transaction is missing. Cannot proceed to pay on blank transaction.'))

    def marcadopago_payment_manual(self,transaction, data):
        # print("-------transaction-----",transaction)
        # print("-------data-----",data)
        mp = self.mp
        if transaction:
            if data.get('payment_method') == "cash":
                payment_type = 'atm'
                payment_method= 'redlink'
            elif data.get('payment_method') == "bank_transfer" and data.get('payment_type_bank'):
                payment_type = 'ticket'
                payment_method=data.get('payment_type_bank')
            # print("inside mercadopago manual payment : ", payment_method)
            # 2/0
            first_name = ''
            last_name = ''
            if transaction.partner_id.name:
                split_name = transaction.partner_id.name.split(" ")
                if split_name[0]:
                    first_name = transaction.partner_id.name.split(" ")[0]
                if len(split_name) > 1:
                    last_name = transaction.partner_id.name.split(" ")[1]
            payment_data = {"transaction_amount": transaction.amount,
                            "description": transaction.reference,
                            "installments": 1,
                            "payment_method_id": payment_method,
                            "payer": {"first_name": first_name,
                                      "last_name": last_name,
                                      "address": {"street_name": transaction.partner_id.street if transaction.partner_id.street else "" + transaction.partner_id.street2 if transaction.partner_id.street2 else "",
                                                  "zip_code": transaction.partner_id.zip
                                                  },
                                      "email": transaction.partner_id.email,
                                      },
                            "capture": True
                            }
            # print("---------payment_data--------", payment_data)
            payment_response = mp.post("/v1/payments", payment_data)
            return payment_response.get('response')

        else:
            raise ValidationError(_('Transaction is missing. Cannot proceed to pay on blank transaction.'))

    def mercadopago_payment_no_token(self, transaction, kwargs):
        if transaction:
            # if transaction.acquirer_id.environment == "test":
            #     access_token = "TEST-4525870278296149-082019-d9ace4366816503b329ff0a4dea12b84-347469609"
            # else:
            #     access_token = self.accessToken
            # mp = mercadopago.MP(access_token)
            mp = self.mp
            # print("-------mp-----",mp)
            first_name = ''
            last_name = ''
            # print("kwargs ",kwargs)
            if kwargs:
                if not kwargs.get('installments'):
                    raise ValidationError(_('Installments are missing.'))
                if not kwargs.get('card_token'):
                    raise ValidationError(_('Card Token from MercadoPago is missing. Cannot proceed to make payment.'))
            if transaction.partner_id.name:
                split_name = transaction.partner_id.name.split(" ")
                if split_name[0]:
                    first_name = transaction.partner_id.name.split(" ")[0]
                if len(split_name) > 1:
                    last_name = transaction.partner_id.name.split(" ")[1]
                installments = ""
                if kwargs.get('installments'):
                    installments = kwargs.get('installments')
                else:
                    installments = '1'

            payment_data = {"transaction_amount" : transaction.amount,
                            "description" : transaction.reference,
                            "token" : kwargs.get('card_token'),
                            "installments" : int(installments),
                            "payment_method_id" : kwargs.get('cc_brand'),
                            "payer" : {"first_name" : first_name,
                                       "last_name" : last_name,
                                       "address" : {"street_name" : transaction.partner_id.street if transaction.partner_id.street else ""+ transaction.partner_id.street2 if transaction.partner_id.street2 else "",
                                                    "zip_code" : transaction.partner_id.zip},
                                       "email" : transaction.partner_id.email,
                                        },
                            "capture" : True
                            }
            # print("---------payment_data--------",payment_data)
            payment_response = mp.post("/v1/payments", payment_data)
            return payment_response.get('response')

        else:
            raise ValidationError(_('Transaction is missing. Cannot proceed to pay on blank transaction.'))

    def get_payment_update(self, data):
        if data:
            mp = self.mp
            response = mp.get('/v1/payments/'+data)
            # print("response : ",response    )
            if response and response.get('status') in (200, 201):
                return {'status' : response.get('status'),
                        'data' : response.get('response')}

            else:
                return {'status' : response.get('status'),
                        'data' : response.get('response')}

    def get_merchant_orders(self, data):
        mp = self.mp
        merchant_order = mp.get("/merchant_orders/" + data)
        return  {'status' : merchant_order.get('status'),
                 'data' : merchant_order.get("response")}

    def search_mercadopago_payment(self, transaction):
        mp = self.mp
        filters = {"external_reference" : transaction.sale_order_id.name}
        print("Token : ",self.accessToken)
        search_payments = requests.get("%s/v1/payments/search?access_token=%s"% (self.url, self.accessToken), filters)
        # search_payments = mp.search_payment(filters)
        results = search_payments.json()
        return results.get('results')
