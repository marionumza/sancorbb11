# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Cash on Delivery',
    'summary': 'This apps helps to add Cash on Delivery as Payment method on Odoo eCommerce',
    'description': """Website Payment Cash on Delivery
    Website Cash on Delivery
    eCommerce Cash on Delivery
    e-Commerce Cash on Delivery
    Odoo shop Cash on Delivery

    Website payment Cash on Delivery
    eCommerce payment Cash on Delivery
    e-Commerce payment Cash on Delivery
    Odoo shop payment Cash on Delivery

    Website payment COD
    eCommerce payment COD
    e-Commerce payment COD
    Odoo shop payment COD
    cash on delivery on website
    cash on delivery on eCommerce
    cash on delivery on e-Commerce
    cash on delivery on Odoo Shop
    cash on delivery on Shop Odoo

    cash on delivery payment on website
    cash on delivery payment on eCommerce
    cash on delivery payment on e-Commerce
    cash on delivery payment on Odoo Shop
    cash on delivery payment on Shop Odoo


    COD payment on website
    COD payment on eCommerce
    COD payment on e-Commerce
    COD payment on Odoo Shop
    COD payment on Shop Odoo

    cash on delivery payment method on website
    cash on delivery payment method on eCommerce
    cash on delivery payment method on e-Commerce
    cash on delivery payment method on Odoo Shop
    cash on delivery payment method on Shop Odoo


    COD payment method on website
    COD payment method on eCommerce
    COD payment method on e-Commerce
    COD payment method on Odoo Shop
    COD payment method on Shop Odoo


""" , 
    'category': 'eCommerce',
    'version': '11.0.0.1',
    'price': '39',
    'currency': "EUR",
    'author': 'BrowseInfo',
    'depends': ['sale', 'account', 'website','website_sale','payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/cod_view.xml',
        'views/template.xml',
        'views/cod_collection_report.xml',
        'views/report_cod_collection.xml',
        'data/payment_acquirer_data.xml',
        
    ],
    'application': True,
    'installable': True,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
