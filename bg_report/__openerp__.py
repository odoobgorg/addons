# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'BG Report',
    'version': '1.0',
    'sequence': 14,
    'summary': 'Sale Layout, page-break, subtotals, separators, report',
    'description': """
Manage your reports
=========================
    """,
    'website': 'http://bgosoftware.com',
    'depends': ['account'],
    'category': 'Localization/Account',
    'data': [
        'views/account_invoice_view.xml',
        'views/report_invoice.xml',
        'views/report_header.xml',
        'views/report_footer.xml',
        'views/report_invoice_amount_to_text.xml',
        'views/taxes.xml',
        #'views/account_fiscal_position.xml',
    ],
    'installable': True,
    'auto_install': False,
}
