# -*- coding: utf-8 -*-
{
    'name': 'Multistore Website',
	'category': 'Website',
    'version': '1.1',
	'summary': """
	Multistore Website for Odoo  
    """,
    'author': 'Atharva System',
	'support': 'support@atharvasystem.com',
	'website' : 'http://www.atharvasystem.com',
	'license' : 'OPL-1',
	'description': """
	Multistore website,
	Multi Website,
	Real Multi Website,
	Multiple website,
	Multi Store,
	Multi Domain,
	Multi Websites,
	Manage many websites from one database,
	multiwebsite
	multiple sites,
	multi site, 
	Odoo Multi website, 
	Odoo Multi Domain, 
	Multi Stores Management,
	multi-website,
	website multi theme,
	website_multi_theme
	odoo website multi theme,
	different theme per website
    """,
    'depends': ['website_event_track','website_sale_options','website_blog','website_crm','website_sale_delivery'],
    'data': [ 
            'views/view.xml',
            'views/templates.xml',
        	'views/recaptcha_assets.xml',
        	'views/recaptcha_templates.xml',
        	'data/data.xml',
            'security/ir.model.access.csv',
    ],
	'images': ['static/description/multistore_website.png'],
	'live_test_url': 'https://www.atharvasystem.com/contact.html',
    'price': 165.00,
    'currency': 'EUR',
	'installable': True,
	'application': True,
}
