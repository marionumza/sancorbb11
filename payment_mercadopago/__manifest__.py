# coding=utf-8
{
    'name': 'MercadoPago Payment Acquirer',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: MercadoPago Integration',
    'version': '1.11',
    'author' : 'Moogah',
    'website' : 'http://www.moogah.com',
    'description': """MercadoPago Payment Acquirer""",
    'depends': ['payment', 'sale_payment', 'website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_views.xml',
        'views/payment_mecradopago_templates.xml',
        'views/res_partner_modifications.xml',
        'views/log_payment_notification_view.xml',
        'data/payment_acquirer_data.xml',
        'data/ir_cron_transaction.xml',
    ],
    'installable': True,
    'price': 360,
    'currency': 'USD',    
}