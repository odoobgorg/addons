# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 BGO software (<http://bgosoftware.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Bulgaria - Accounting',
    'version': '2.0',
    'category': 'Localization/Account',
    'description': """
This is the base module to manage the accounting chart for Bulgaria in OpenERP (Odoo).
This module is in development. Please be patient.
    """,
    'author': 'BGO Team 2016',
    'website': 'http://bgosoftware.com',
    'images': ['static/description/icon.png', 'images/main_screenshot.png'],
    'depends': ['account',
                'base_vat',
               ],
    'demo': [],
    'data': [
        'views/account_chart.xml',
        'views/account_chart_template.yml',
        'views/account_tax_template.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/fiscal_position_template.xml',
        'views/account_invoice_view.xml',
        'views/report_invoice.xml',
        'views/report_header.xml',
        'views/report_footer.xml',
        'views/report_invoice_amount_to_text.xml',
        'views/account_tax.xml',
        'views/account_fiscal_position.xml',
    ],
    'sequence': 1,
    'installable': True,
    'doc': ['doc/index.rst'],
    "application": True,
}
