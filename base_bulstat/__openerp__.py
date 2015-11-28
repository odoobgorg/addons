# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Bulstat Number Validation',
    'version': '1.0',
    'category': 'Hidden/Dependency',
    'description': """
EIK/BULSTAT validation for Partner's EIK/BULSTAT numbers.
=========================================
    """,
    'depends': ['account'],
    'website': 'https://www.odoo.com/page/accounting',
    'data': ['base_bulstat_view.xml'],
    'installable': True,
    'auto_install': False,
}
