# -*- coding: utf-8 -*-

{
    'name': 'Epay.bg Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Epay.bg Implementation',
    'version': '1.0',
    'description': """Epay.bg Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/epaybg.xml',
        'views/payment_acquirer.xml',
        'data/epaybg.xml',
    ],
    'installable': True,
    'sequence': 2,
    'application': True,
}
