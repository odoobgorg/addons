# -*- coding: utf-8 -*-

{
    'name': 'epaybg Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: epaybg Implementation',
    'version': '1.0',
    'description': """epaybg Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/epaybg.xml',
        'views/payment_acquirer.xml',
        'data/epaybg.xml',
    ],
    'installable': True,
    'sequence': 2,
    'application': 2,
}
