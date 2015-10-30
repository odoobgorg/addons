# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Bulgarian UIC Number Validation',
    'version': '1.0',
    'category': 'Hidden/Dependency',
    'description': """
This is the module to manage the Registration Number for Bulgaria in OpenERP
============================================================================
Bulgarian uic by Trade agency.
    """,
    'depends': ['account'],
    'website': 'https://www.odoo.com/page/accounting',
    'data': ['base_bg_uic_view.xml'],
    'installable': True,
    'auto_install': False,
}
