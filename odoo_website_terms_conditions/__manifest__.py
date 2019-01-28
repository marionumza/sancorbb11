# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    "name" : "Website Terms & Conditions",
    "version" : "11.0.0.1",
    "category" : "eCommerce",
    "price": 10,
    "currency": 'EUR',
    "depends" : ['website','website_sale'],
    "author": "BrowseInfo",
    "summary": 'Using this apps able to add terms and condition on shop which user to agree before checkout',
    "description": """
Add Customizable Terms and Conditions on your Odoo Website.
Using this apps able to add terms and condition on shop which user to agree before checkout
add terms and condition on checkout page
        
    """,
    "website" : "www.browseinfo.in",
    "data": [
        'security/ir.model.access.csv',
        'views/terms_conditions.xml',
        'views/template.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
