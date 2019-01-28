# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Website Product Labels & Stickers on Odoo Shop",
    "version" : "11.0.0.2",
    "category" : "eCommerce",
    "depends" : ['website','website_sale'],
    "author": "BrowseInfo",
    "summary": 'This module helps to put different stickers/tag for product which shows on website as Ribbon',
    "description": """
    Assign & Customize Product Labels on website, Product tag on website, Prodoct Stickers on website, Website product Label, Website product Stickers. Website product Ribbon, Stickers as ribbon, Product Label as Ribbon.
    Website eCommerce Product Ribbons
    """,
    "website" : "www.browseinfo.in",
    "price": "19",
    'currency': "EUR",
    "data": [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/product_label.xml',
        'views/template.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "images":['static/description/Banner.png']
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
