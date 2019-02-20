# coding=utf-8
from odoo import _, api, fields, models
import odoo.exceptions
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.exceptions import UserError
import logging
import mercadopago
from datetime import datetime
import json
import pprint

from werkzeug import urls, utils
from odoo.http import request
from .mercadopago_request import MecradoPagoPayment


_logger = logging.getLogger(__name__)

class MercadoPagoPaymentMethods(models.Model):
    _name = "mercadopago.payment.methods"

    name = fields.Char(string="Name")
    uni_id = fields.Char(string="Id")
    payment_type = fields.Selection([('credit_card','Credit Card'),
                                     ('debit_card', 'Debit Card'),
                                     ('ticket', 'Ticket'),
                                     ('atm', 'ATM'),
                                     ],string="Payment Type Ids")
    type = fields.Selection([('credit_card','Credit Card'),
                                     ('debit_card', 'Debit Card'),
                                     ('other', 'Others'),
                                     ],string="Type")

class PaymentMercadoPago(models.Model):
    _inherit = 'payment.acquirer'

    global _mercadopago_sandbox_url, _mercadopago_production_url
    _mercadopago_sandbox_url = ""
    _mercadopago_production_url = ""
    # _card_token_dict = {}

    @api.model
    def _get_credit_card_payment(self):
        return self.env['mercadopago.payment.methods'].sudo().search([('type', '=', 'credit_card')]).ids

    @api.model
    def _get_debit_card_payment(self):
        return self.env['mercadopago.payment.methods'].sudo().search([('type', '=', 'debit_card')]).ids

    @api.model
    def _get_other_payment(self):
        return self.env['mercadopago.payment.methods'].sudo().search([('type', '=', 'other')]).ids


    provider = fields.Selection(selection_add=[('mercadopago', 'MercadoPago')])
    mercadopago_client_id = fields.Char(string='Client Id', required_if_provider='mercadopago', groups='base.group_user')
    mercadopago_client_secret = fields.Char(string='Client Secret', required_if_provider='mercadopago', groups='base.group_user')
    mercadopago_use_ipn = fields.Boolean(string='Use IPN', groups='base.group_user')
    mercadopago_ipn_url = fields.Char(string='IPN URL', groups='base.group_user', compute='_get_ipn_url')
    mercadopago_enable_MercadoEnvio = fields.Boolean(string='Enable MercadoEnvio', groups='base.group_user')
    auto_confirm = fields.Selection([('confirm_order_draft_acquirer', 'Authorize & capture the amount, confirm the SO, create	the	payment	and	save the invoice in	draft state on acquirer confirmation'),("confirm_order_confirm_inv","Authorize & capture the amount, confirm the SO and auto-validate the invoice on acquirer confirmation")],
                                    default="confirm_order_draft_acquirer")
    available_payment_method = fields.Selection([('all', 'All Available Payment Methods Available'),
                                                 ('custom', 'Customized Available Payment Methods')],
                                                default="all",
                                                string="Available Payment Methods")
    credit_card_payment_methods_ids = fields.Many2many('mercadopago.payment.methods', 'credit_card_mercadopago_payment_rel',  'mercadopago_payment_id', 'credit_card_payment_id', domain=[('type', '=', 'credit_card')], string="Credit Cards", default=_get_credit_card_payment)
    debit_card_payment_methods_ids = fields.Many2many('mercadopago.payment.methods', 'debit_card_mercadopago_payment_rel', 'mercadopago_payment_id', 'debit_card_payment_id', domain=[('type', '=', 'debit_card')], string="Debit Cards", default=_get_debit_card_payment)
    other_payment_methods_ids = fields.Many2many('mercadopago.payment.methods', 'other_mercadopago_payment_rel', 'mercadopago_payment_id', 'other_payment_id', domain=[('type', '=', 'other')], string="Cash/Bank Transfer", default=_get_other_payment)
    mercadopago_test_public_key = fields.Char(string='Test Public Key')
    mercadopago_test_access_token = fields.Char(string="Test Access Token")
    mercadopago_prod_public_key = fields.Char(string="Public Key")
    include_installments = fields.Boolean(string='Include Installments in S2S')
    financing_costs_url = fields.Char(string="Financing Costs URL")

    @api.depends('mercadopago_use_ipn')
    def _get_ipn_url(self):
        for rec in self:
            if rec.mercadopago_use_ipn:
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                rec.mercadopago_ipn_url = base_url + '/ipn/notification'
            else:
                rec.mercadopago_ipn_url = False


    def _set_excluded_payment_methods(self, acquirer):
        excluded_type = []
        excluded_method = []
        incl_methods = []
        incl_methods.extend(self.credit_card_payment_methods_ids.ids)
        incl_methods.extend(self.debit_card_payment_methods_ids.ids)
        incl_methods.extend(self.other_payment_methods_ids.ids)
        excl_methods = self.env['mercadopago.payment.methods'].search([('id', 'not in', incl_methods)])
        for method in excl_methods:
            excluded_method.append({'id' : method.uni_id})
        # print("----------method------",excluded_method)
        atm = self.other_payment_methods_ids.search([('payment_type', '=', 'atm')])
        ticket = self.other_payment_methods_ids.search([('payment_type', '=', 'ticket')])
        if not self.credit_card_payment_methods_ids:
            excluded_type.append({'id' : 'credit_card'})
        if not self.debit_card_payment_methods_ids:
            excluded_type.append({'id' : 'debit_card'})
        if not atm:
            excluded_type.append({'id' : 'atm'})
        if not ticket:
            excluded_type.append({'id' : 'ticket'})
        # print("-------type-------",excluded_type)
        return {'excluded_type' : excluded_type, 'excluded_method' : excluded_method}

    def _get_mercadopago_pref(self, values, order, base_url, excluded_payment_methods):
        # Initializing mercadoPago Payment
        mp = mercadopago.MP(self.mercadopago_client_id, self.mercadopago_client_secret)

        accessToken = mp.get_access_token()
        # print("---------accessToken-----------",accessToken)
        # print("-------values--------",values)
        # print("-------order--------",order)
        if excluded_payment_methods.get('excluded_method'):
            excluded_payment_method = excluded_payment_methods.get('excluded_method')
        else:
            excluded_payment_method = []
        if excluded_payment_methods.get('excluded_type'):
            excluded_payment_type = excluded_payment_methods.get('excluded_type')
        else:
            excluded_payment_type = []
        r_url = "/mercadopago" + values.get('return_url')
        return_url = urls.url_join(base_url, r_url)
        preference_data = {"items": [{'id' : order.name,
                                      'title' : order.name,
                                      'quantity' : 1,
                                      'currency_id' : values.get('currency').name,
                                      'unit_price' : values.get('amount'),
                                      }],
                           "payer" : {'name' : values.get('partner_name'),
                                       'email' : values.get('partner_email'),
                                       'date_created' : order.create_date,
                                       'phone' : {'area_code' : "",
                                                  'number' : values.get('partner_phone')},
                                       'address' : {'zip_code' : values.get('billing_partner_zip'),
                                                    'street_name' : values.get('billing_partner_address'),}
                                       },
                           "back_urls" : {'pending' : return_url,
                                          'success' : return_url,
                                          'failure' : return_url},
                                          'auto_return' : 'approved',
                           "external_reference" : order.name,
                               "payment_methods" : {'excluded_payment_methods' :excluded_payment_method,
                                                    'excluded_payment_types' : excluded_payment_type,
                                                   },
                           }
        preference_result = mp.create_preference(preference_data)
        # print("-----preference_result-----", preference_result)
        if preference_result.get('response').get('status') == 400:
            raise UserError(_('There seems to be some problem while creating MercadoPago Preference'))
        request.session['pref_id'] = preference_result.get('response').get("id")

        # 2/0
        return preference_result

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(PaymentMercadoPago, self)._get_feature_support()
        res['authorize'].append('mercadopago')
        res['tokenize'].append('mercadopago')
        return res


    def _get_fu_urls(self, environment):
        """ MercadoPago URLs """
        if environment == 'prod':
            return {'mercadopago_form_url': _mercadopago_production_url}
        else:
            return {'mercadopago_form_url':_mercadopago_sandbox_url}

    @api.multi
    def mercadopago_form_generate_values(self, values):
        self.ensure_one()
        global _mercadopago_sandbox_url, _mercadopago_production_url
        # print("--------mercadopago_form_generate_values----------")
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        order = request.website.sale_get_order()
        excluded_payment_methods = self._set_excluded_payment_methods(self)
        # print("------excluded_payment_methods----",excluded_payment_methods)
        temp_mercadopago_tx_values = {}
        if order:

            mercadopago_pref = self._get_mercadopago_pref(values, order, base_url, excluded_payment_methods)
            _mercadopago_sandbox_url = mercadopago_pref.get('response').get('sandbox_init_point')
            _mercadopago_production_url = mercadopago_pref.get('response').get('init_point')

            temp_mercadopago_tx_values = {'tx_return_url' : mercadopago_pref.get('response').get("back_urls").get('success')}
        return temp_mercadopago_tx_values


    @api.model
    def mercadopago_s2s_form_process(self, data):
        # print("----------data---------",data, self)
        # print("----_card_token_dict------",_card_token_dict)
        self = self.env['payment.acquirer'].sudo().search([('provider', '=', 'mercadopago')])
        # print ('-------self------',self)
        # print("-----data------",data)

        mercado_obj = MecradoPagoPayment(self)
        values = {'cc_number': data.get('cc_number'),
                  'cc_holder_name': data.get('cc_holder_name'),
                  'cc_expiry': data.get('cc_expiry'),
                  'cc_cvc': data.get('cc_cvc'),
                  'cc_brand': data.get('cc_brand'),
                  'acquirer_id': self.id,
                  # 'acquirer_id': int(data.get('acquirer_id')),
                  'partner_id': int(data.get('partner_id')),
                  'docNumber' : data.get('docNumber'),
                  'docType' : data.get('docType'),
                  'customer_email' : data.get('customer_email'),
                  'installments' : data.get('installments')}
        # 2/0
        PaymentMethod = self.env['payment.token'].sudo().create(values)
        return PaymentMethod

    @api.multi
    def mercadopago_s2s_form_validate(self, data):
        error = dict()
        # print("--mercadopago_s2s_form_validate-----",data)
        mandatory_fields = ["cc_number", "cc_cvc", "cc_holder_name", "cc_expiry", "cc_brand"]
        # Validation
        for field_name in mandatory_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'
        # if data['cc_expiry'] and datetime.now().strftime('%y%M') > datetime.strptime(data['cc_expiry'],
        #                                                                              '%M / %y').strftime('%y%M'):
        #     return False
        # print("------error-----",error)
        return False if error else True

    @api.multi
    def mercadopago_get_form_action_url(self):
        self.ensure_one()
        return self._get_fu_urls(self.environment)['mercadopago_form_url']


class PaymentTransactionMercadoPago(models.Model):
    _inherit = "payment.transaction"

    mercadopago_response = fields.Text("MercadoPago Cron Response")

    def _generate_and_pay_invoice(self):
        self.sale_order_id._force_lines_to_invoice_policy_order()
        ctx_company = {'company_id': self.sale_order_id.company_id.id,
                       'force_company': self.sale_order_id.company_id.id}
        created_invoice = self.sale_order_id.with_context(**ctx_company).action_invoice_create()
        created_invoice = self.env['account.invoice'].browse(created_invoice).with_context(**ctx_company)

        if created_invoice:
            print("------auto_confirm-----",self.acquirer_id)
            # print("------auto_confirm-----",self.acquirer_id.auto_confirm)
            if self.acquirer_id.auto_confirm == "confirm_order_draft_acquirer":
                # To keep invoice created for particular SO to draft state.
                _logger.info('<%s> transaction completed, auto-generated invoice %s (ID %s) for %s (ID %s)',
                             self.acquirer_id.provider, created_invoice.name, created_invoice.id,
                             self.sale_order_id.name, self.sale_order_id.id)

                # created_invoice.action_invoice_open()
                self.sale_order_id.write({'invoice_status': 'invoiced'})
                if not self.acquirer_id.journal_id:
                    default_journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
                    if not default_journal:
                        _logger.warning(
                            '<%s> transaction completed, could not auto-generate payment for %s (ID %s) (no journal set on acquirer)',
                            self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
                    self.acquirer_id.journal_id = default_journal
                    created_invoice.with_context(tx_currency_id=self.currency_id.id).pay_and_reconcile(
                        self.acquirer_id.journal_id, pay_amount=created_invoice.amount_total)
                    if created_invoice.payment_ids:
                        created_invoice.payment_ids[0].payment_transaction_id = self
            #     Creating Payment record related to particular Invoice generated from MercadoPago paayment Gateway.
                pay_journal = self.env['account.journal'].browse([self.acquirer_id.journal_id.id])
                print("------pay_journal-----",pay_journal)

                payment_type = created_invoice.type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
                if payment_type == 'inbound':
                    payment_method = self.env.ref('account.account_payment_method_manual_in')
                    journal_payment_methods = pay_journal.inbound_payment_method_ids
                else:
                    payment_method = self.env.ref('account.account_payment_method_manual_out')
                    journal_payment_methods = pay_journal.outbound_payment_method_ids
                if payment_method not in journal_payment_methods:
                    raise UserError(_('No appropriate payment method enabled on journal %s') % pay_journal.name)

                communication = created_invoice.type in ('in_invoice', 'in_refund') and created_invoice.reference or created_invoice.number or ""
                if created_invoice.origin:
                    communication = '%s (%s)' % (communication, created_invoice.origin)

                payment_values = {'invoice_ids': [(6, 0, created_invoice.ids)],
                                  'amount': created_invoice.amount_total or created_invoice.residual,
                                  'payment_date': fields.Date.context_today(self),
                                  'communication': communication,
                                  'partner_id': created_invoice.partner_id.id,
                                  'partner_type': created_invoice.type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
                                  'journal_id': self.acquirer_id.journal_id.id,
                                  'payment_type': payment_type,
                                  'payment_method_id': payment_method.id,
                                  }
                if self.env.context.get('tx_currency_id'):
                    payment_values['currency_id'] = self.env.context.get('tx_currency_id')

                payment = self.env['account.payment'].create(payment_values)
                print("-----payment has been created with id of : ",payment)


            else:
                _logger.info('<%s> transaction completed, auto-generated invoice %s (ID %s) for %s (ID %s)',
                             self.acquirer_id.provider, created_invoice.name, created_invoice.id,
                             self.sale_order_id.name, self.sale_order_id.id)

                created_invoice.action_invoice_open()
                print("-----self.acquirer_id.journal_id------",self.acquirer_id.journal_id)
                if not self.acquirer_id.journal_id:
                    default_journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
                    if not default_journal:
                        _logger.warning(
                            '<%s> transaction completed, could not auto-generate payment for %s (ID %s) (no journal set on acquirer)',
                            self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
                    self.acquirer_id.journal_id = default_journal
                created_invoice.with_context(tx_currency_id=self.currency_id.id).pay_and_reconcile(
                    self.acquirer_id.journal_id, pay_amount=created_invoice.amount_total)
                self.sale_order_id.write({'invoice_status' : 'invoiced'})
                if created_invoice.payment_ids:
                    created_invoice.payment_ids[0].payment_transaction_id = self
        else:
            _logger.warning('<%s> transaction completed, could not auto-generate invoice for %s (ID %s)',
                                self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)

    @api.multi
    def mercadopago_s2s_do_transaction(self, **data):
        self.ensure_one()
        print("-------mercadopago_s2s_do_transaction-------",self.payment_token_id.acquirer_ref)
        transaction = MecradoPagoPayment(self.acquirer_id)
        res = transaction.mercadopago_payment(self)
        print("-------res---------",res)
        return self._mercadopago_s2s_validate_tree(res)

    @api.multi
    def _mercadopago_s2s_validate_tree(self, tree):
        print("-------_mercadopago_s2s_validate_tree--------",tree)
        self.ensure_one()
        if self.state not in ('draft', 'pending', 'refunding'):
            _logger.info('MercadoPago: trying to validate an already validated tx (ref %s)', self.reference)
            return True
        status = ""
        collection_id = ""
        status_detail = ""
        if tree and tree.get('collection_status'):
            status = tree.get('collection_status')
            collection_id = tree.get('collection_id')
        if tree and tree.get('status'):
            status = tree.get('status')
            collection_id = tree.get('id')
        # status = tree.get('collection_status')
        if tree and tree.get('status') and tree.get('status_detail'):
            collection_id = tree.get('id')
            status = tree.get('status')
            status_detail = tree.get('status_detail')

        # print("---------Status--------",status)
        if status == 'approved':
            # print("it has been approved and rest is being done")
            new_state = 'refunded' if self.state == 'refunding' else 'done'
            self.write({'state': new_state,
                        'date_validate': fields.datetime.now(),
                        'acquirer_reference': collection_id, })
            self.execute_callback()
            if self.payment_token_id:
                self.payment_token_id.verified = True
            return True

        elif status == 'pending':
            self.write({'state' : 'pending',
                        'acquirer_reference': collection_id,})
            # self.execute_callback()
            if self.payment_token_id:
                self.payment_token_id.verified = True

            return True

        elif status == "in_process":
            self.write({'state': 'pending',
                        'acquirer_reference': collection_id, })
            return True

        elif status == "rejected":
            state_message = ""
            status_detail = tree.get('status_detail')
            # print("--------status_detail--------",tree.get('status_detail'))
            if status_detail == "cc_rejected_call_for_authorize":
                state_message = "Aww Snap! There seems to be some problem with Payment. Please call authorize person."
            elif status_detail == "cc_rejected_insufficient_amount":
                state_message = "Insufficient Funds."
            elif status_detail == "cc_rejected_bad_filled_security_code":
                state_message = "Security Code entered is incorrect for this Card."
            elif status_detail == "cc_rejected_bad_filled_date":
                state_message = "Card has been Expired, Please provide Valid Card."
            elif status_detail == "cc_rejected_bad_filled_other":
                state_message = "It seems some information in Payment form has been provided incorrectly.\n\t Please check it and try again."
            else:
                state_message = "Aww Snap! We are sorry that your payment has been rejected. Please try again after sometimes."
            self.write({'state': 'cancel', 'acquirer_reference': collection_id,
                'state_message': state_message, })

            # r =  request.redirect("/mercadopago/reject_payment", state_message)
            # response = request.render("payment_mercadopago.reject_payment_template", state_message)
            # print("----------response---------", response)

            return True

        else:
            error = ""
            if tree:
                if tree.get('error') and tree.get('error').get('message'):
                    error = tree['error']['message']
            else:
                error = "Payment process was disrupted."
            _logger.warn(error)
            self.sudo().write({'state': 'error', 'state_message': error, 'acquirer_reference': tree.get('id'),
                               'date_validate': fields.datetime.now(), })

            return False

    def confirm_sale_token(self):
        """ Confirm a transaction token and call SO confirmation if it is a success.

        :return: True if success; error string otherwise """
        self.ensure_one()
        # print("------------inside confirm_sale_token---------",self, self.payment_token_id)
        # print("------------context inside confirm_sale_token---------",self._context)
        # print("------------payment token inside confirm_sale_token---------",self.payment_token_id, self.partner_id, self.sale_order_id.partner_id)
        if self.payment_token_id and self.partner_id == self.sale_order_id.partner_id:
            # print("Inside if going to check for context with :", self._context, self._context.get('cc_cvc'), self._context.get('installment'))
            if self._context and self._context.get('cc_cvc') and self._context.get('installment'):
                # print("----payment token inside confirm_sale_token------", self.payment_token_id, self.payment_token_id.mercadopago_profile)
                acquirer = self.payment_token_id.acquirer_id
                cc_details = str(self.payment_token_id.mercadopago_profile).split(':')
                values = {'cc_number' : cc_details[0] if cc_details[0] else "",
                          'cc_expiry' : cc_details[1] if cc_details[1] else "",
                          'cc_holder_name' : cc_details[2] if cc_details[2] else "",
                          'docNumber' : cc_details[3] if cc_details[3] else "",
                          'docType' : cc_details[4] if cc_details[4] else "",
                          'cc_cvc' : self._context.get('cc_cvc'),
                          'acquirer_id' : acquirer.id,
                          'partner_id' : self.payment_token_id.partner_id.id,
                          'customer_email' : cc_details[5] if cc_details[5] else ""}
                mercado_obj = MecradoPagoPayment(acquirer)
                card_token = mercado_obj._get_card_token(acquirer, values)
                if card_token and card_token.get('id'):
                    token = self.payment_token_id
                    token.write({'acquirer_ref' : card_token.get('id'),
                                 'mercadopago_installments' : self._context.get('installment')})

            try:
                s2s_result = self.s2s_do_transaction()
                # print("--------s2s_result-------",s2s_result)
            except Exception as e:
                _logger.warning(
                    _("<%s> transaction (%s) failed: <%s>") %
                    (self.acquirer_id.provider, self.id, str(e)))
                return 'pay_sale_tx_fail'

            valid_state = 'authorized' if self.acquirer_id.capture_manually else 'done'
            # print("------valid_state------",valid_state, self.state)
            if not s2s_result or self.state != valid_state:
                _logger.warning(
                    _("<%s> transaction (%s) invalid state: %s") %
                    (self.acquirer_id.provider, self.id, self.state_message))
                request.session['state_message'] = self.state_message
                return 'pay_sale_tx_state'

            try:
                return self._confirm_so()
            except Exception as e:
                _logger.warning(
                    _("<%s> transaction (%s) order confirmation failed: <%s>") %
                    (self.acquirer_id.provider, self.id, str(e)))
                return 'pay_sale_tx_confirm'
        return 'pay_sale_tx_token'


    @api.model
    def _mercadopago_form_get_tx_from_data(self, data):
        # print("----------data-----------",data)
        reference = data.get('sale_transaction_id')
        if not reference:
            error_msg = _(
                'MercadoPago: invalid reply received from provider, missing reference. Additional message: %s' % data.get(
                    'error', {}).get('message', ''))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.search([('id', '=', reference)])
        if not tx:
            error_msg = (_('MercadoPago: no order found for reference %s') % reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = (_('MercadoPago: %s orders found for reference %s') % (len(tx), reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx[0]

    @api.multi
    def _mercadopago_form_validate(self, data):
        # print("--------_mercadopago_form_validate data--------", data)
        # 2 / 0
        res = self._mercadopago_s2s_validate_tree(data)
        # print("-----res-------",res)
        return res

    def _cron_pending_payment_mercadopago(self):
        # print("Cron pending Payemt MercadoPago")
        transactions = self.env['payment.transaction'].sudo().search([('provider', '=', 'mercadopago'),('state', 'not in', ['done', 'cancel', 'refunded']), ('acquirer_reference', '!=', False)])
        # print("Transaction : ",transactions)
        if transactions:
            for transaction in transactions:
                if not transaction.acquirer_reference:
                    _logger.info("There is no MercadoPago Payment Id provide for %s"% transaction.reference)
                else:
                    payments = []
                    mp = MecradoPagoPayment(transaction.acquirer_id)
                    # print("mp >>>>>>>>>>",mp)
                    mp_payment = mp.get_payment_update(transaction.acquirer_reference)
                    if mp_payment and mp_payment.get('status') in (200, 201):
                        print("inside if mp payment")
                        if transaction.acquirer_id.environment == "prod":
                            merchant_order = mp.get_merchant_orders(mp_payment.get('data').get('order').get('id'))
                            payments.append(merchant_order.get('data').get('payments'))
                            # print ("00000000000000000000000000000000000", payments)
                        else:
                            merchant_order = mp_payment
                            payments.append(merchant_order.get('data'))
                        # print("merchant_order : ",merchant_order)
                        if merchant_order and merchant_order.get('status') in (200, 201):
                            print("getting payment done, I guess!!")
                            # print("Payments are : ",payments)
                            for payment in payments:
                                if len(payment) > 1:
                                    for pay in payment:
                                        payment_respose = mp.get_payment_update(str(pay.get('id')))
                                        self.process_payment(payment_respose)
                                else:
                                    payment_respose = mp.get_payment_update(str(payment[0].get('id')))
                                    _logger.info("\npayment response is %s", payment_respose)
                                    self.process_payment(payment_respose)
                        else:
                            _logger.info(
                                "Payment has not been processed,\n We did not get any merchant order from MercadoPago with reference of Id : %s" % transaction.acquirer_reference)

    def _cron_recover_abandoned_payment_mercadopago(self):
        _logger.info("Checking for Abandoned Payments from MercadoPago. Trying to recover Payment Transactions.")
        transactions_draft = self.env['payment.transaction'].sudo().search([('provider', '=', 'mercadopago'), ('state', 'in', ['draft']),('acquirer_reference', '=', False)])

        transactions = []

        date = datetime.now().date()

        for t in transactions_draft:

            delta_time = t.create_date.date - date

            _logger.info("DEBUGTRANSACTIONS%r", delta_time, t.create_date.date, date)

            if delta_time <= 7:
                transactions.append(t)



        print("Transactions from Cron that are abandoned : ", transactions)


        # if transactions:
        #     for transaction in transactions:
        #         mp = MecradoPagoPayment(transaction.acquirer_id)
        #         search_payments = mp.search_mercadopago_payment(transaction)
        #         if search_payments:
        #             for payment in search_payments:
        #                 # print("~~~~~~~~~",payment)
        #                 transaction.write({'acquirer_reference':payment.get('id')})
        #                 # data = {'data' : payment}
        #                 # self.process_payment(data)
        #         else:
        #             _logger.info("No Payments found for %s Order"% transaction.sale_order_id.name)
        # else:
        #     _logger.info("No Abandoned transaction found against MercadoPago Payment Gateway.")

    def process_payment(self, response):
        _logger.info(
            'Payment status has been changed for MercadoPago Payment of Sale Order : %s to %s, now changing payment status in Odoo.',
            response.get('data').get('description'), response.get('data').get('status'))
        print("!!!!!!!!!!",response.get('data').get('id'))
        txs = self.env['payment.transaction'].sudo().search([('acquirer_reference', '=', response.get('data').get('id')),('state', 'not in',['done', 'cancel', 'refunded'])])
        # print ("<<<<<<<<<<<<<<<<<", txs)
        if not txs:
            _logger.info(response.get('data').get('id'))
            # raise odoo.exceptions.MissingError(
            #     'Transaction does not exist or has been deleted for MercadoPago Payment reference : %s' % response.get(
            #         'data').get('id'))
        else:
            for tx in txs:
                # status = "pending" if response.get('data').get('status') in ("in_process", "pending") else response.get(
                #     'data').get('status')
                # status = "done" if response.get('data').get('status') == "approved" else status
                status = response.get('data').get('status')
                # print (">>>>>>>>>>>>>",status)
                if status == 'approved':
                    # print("it has been approved and rest is being done")
                    new_state = 'refunded' if tx.state == 'refunding' else 'done'
                    tx.write({'state': new_state, 'date_validate': fields.datetime.now()})

                elif status == 'pending':
                    tx.write({'state': 'pending'})

                elif status == "in_process":
                    tx.write({'state': 'pending'})
                    return True

                elif status == "rejected":
                    # print ("--------------------", status)

                    state_message = ""
                    if response and response.get('data') and response.get('data').get('status_detail'):
                        status_detail = response.get('data').get('status_detail')
                        # print("--------status_detail--------",tree.get('status_detail'))
                    if status_detail == "cc_rejected_call_for_authorize":
                        state_message = "Aww Snap! There seems to be some problem with Payment. Please call authorize person."
                    elif status_detail == "cc_rejected_insufficient_amount":
                        state_message = "Insufficient Funds."
                    elif status_detail == "cc_rejected_bad_filled_security_code":
                        state_message = "Security Code entered is incorrect for this Card."
                    elif status_detail == "cc_rejected_bad_filled_date":
                        state_message = "Card has been Expired, Please provide Valid Card."
                    elif status_detail == "cc_rejected_bad_filled_other":
                        state_message = "It seems some information in Payment form has been provided incorrectly.\n\t Please check it and try again."
                    else:
                        state_message = "Aww Snap! We are sorry that your payment has been rejected. Please try again after sometimes."
                    tx.write({'state': 'cancel', 'state_message': state_message})
                    # print ("===============",tx.state)
                # print(response)
                elif status == "refunded":
                    tx.write({'state' : 'refunded'})
                elif status == "cancelled":
                    tx.write({'state' : 'cancel', 'state_message' : response.get('data').get('status_detail')})
                tx.write({'mercadopago_response' : pprint.pformat(response.get('data'))})
                print("tx.stage = ",tx.state)
                try:
                    if response.get('data').get('status') and tx.state in ('authorized', 'done'):
                        _logger.info("Transcation Status : %s", tx.state)
                        _logger.info("Payment has been done, now confirming Sale Order as well paying invoice.")
                        tx.sale_order_id.with_context(send_email=True).action_confirm()
                        _logger.info("Transcation Status : %s, Order status: %s", tx.state, tx.sale_order_id.state)
                        tx._generate_and_pay_invoice()
                        self._cr.commit()

                    elif response.get('data').get('status') and tx.state == "pending":
                        _logger.info("Payment status received as Pending. Confirming Sale Order.")
                        tx.sale_order_id.action_quotation_send()
                        self._cr.commit()

                    elif response.get('data').get('status') and tx.state == "cancel":
                        _logger.info("Transaction was cancelled, moving sale order to cancel state.")
                        tx.sale_order_id.action_cancel()
                        self._cr.commit()
                except:
                    _logger.info("Some error : %s ", tx.sale_order_id.name)
                    #tx.sale_order_id.with_context(send_email=True).action_confirm()
            return True



class MercadoPagoPaymentToken(models.Model):
    _inherit = "payment.token"

    mercadopago_profile = fields.Char(string='MercadoPago Profile ID', help='This contains the unique reference '
                                                                            'for this partner/payment token combination in the Authorize.net backend')
    provider = fields.Selection(string='Provider', related='acquirer_id.provider')
    save_token = fields.Selection(string='Save Cards', related='acquirer_id.save_token')
    mercadopago_installments = fields.Char(string='Installements', default='1')

    @api.model
    def mercadopago_create(self, values):
        # print("-----values-from mercadopago_create------- ",values)
        if values.get('cc_number'):
            values['cc_number'] = values['cc_number'].replace(' ', '')
            acquirer = self.env['payment.acquirer'].browse(values['acquirer_id'])
            expiry = str(values['cc_expiry'][:2]) + str(values['cc_expiry'][-2:])
            partner = self.env['res.partner'].browse(values['partner_id'])
            mercado_obj = MecradoPagoPayment(acquirer)
            mercadopago_profile_id = ""
            if acquirer.save_token:
                # print("-------values----",values)
                # 2/0
                pass
            card_token = mercado_obj._get_card_token(acquirer, values)
            # print("----card_token----", card_token)

            # if partner.mercadopago_customer:
            #     print("There it exists as : ",partner.mercadopago_customer)
            #     mercadopago_profile_id = partner.mercadopago_customer
            # else:
            #     new_customer = mercado_obj._create_mercadopago_customer(partner, acquirer)
            #     if new_customer:
            #         partner.sudo().write({
            #             'mercadopago_customer': new_customer.get('id'),
            #         })
            #         if new_customer.get('id'):
            #             mercadopago_profile_id = new_customer.get('id')
            #     # print("---else mercadopago_customer-------",partner.mercadopago_customer)
            # print("--mercadopago_profile_id----",mercadopago_profile_id)
            # print("--mercadopago_profile_id----",card_token)
            # print("--mercadopago_profile_id----",card_token.get("id"))
            # if mercadopago_profile_id and card_token.get('id'):
            #     if acquirer.save_token == 'always':
            #         customer_card = mercado_obj._set_customer_card(mercadopago_profile_id, acquirer, card_token)
            # 2/0
            doctype = ""
            if not values['docType']:
                doctype = "Otro"
            else:
                doctype = values['docType']

            card_info = values['cc_number'] + ":" + values["cc_expiry"] + ":" + values['cc_holder_name'] + ":" + values['docNumber'] + ":" + doctype + ":" + values['customer_email'] + ":" + values['cc_brand']
            if card_token and card_token.get("id"):
                # print("Inside if----------------")
                return {'mercadopago_profile' : card_info,
                        'name': 'XXXXXXXXXXXX%s - %s' % (values['cc_number'][-4:], values['cc_holder_name']),
                        'acquirer_ref': card_token.get("id"),
                        'mercadopago_installments' : values.get('installments'),
                        }
            else:
                raise ValidationError(_('The Customer Profile creation in MercadoPago failed.'))

        else:
            return values

        #     transaction = AuthorizeAPI(acquirer)
        #     res = transaction.create_customer_profile(partner, values['cc_number'], expiry, values['cc_cvc'])
        #     if res.get('profile_id') and res.get('payment_profile_id'):
        #         return {'authorize_profile': res.get('profile_id'),
        #             'name': 'XXXXXXXXXXXX%s - %s' % (values['cc_number'][-4:], values['cc_holder_name']),
        #             'acquirer_ref': res.get('payment_profile_id'), }
        #     else:
        #         raise ValidationError(_('The Customer Profile creation in Authorize.NET failed.'))
        # else:
        #     return values



