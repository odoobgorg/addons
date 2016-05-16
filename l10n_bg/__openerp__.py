# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Bulgaria Accounting, Open Source Accounting and Invoiceing Module
#    Copyright (C) 2016 BGO software LTD, Lumnus LTD, Prodax LTD
#    (http://www.bgosoftware.com, http://www.lumnus.net, http://www.prodax.bg)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
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
This module holds the Bulgarian Chart of Accounts and Invoicing in Odoo v9. It adds all the needed attributes to the invoice,
the tax templates and the fiscal positions, as per the Bulgarian law.
This module is still in development. If you would like to assist the testing, please do. Issue are tracked under:
https://github.com/odoobgorg/addons/issues
    """,
    'author': 'BGO Software, Lumnus LTD, Prodax LTD',
    'website': 'http://bgosoftware.com, http://www.lumnus.net, http://www.prodax.bg',
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
        'views/comment_view.xml',
        'views/report_invoice_comments.xml',
        'views/base_comment_template.xml',
        'security/ir.model.access.csv',
    ],
    'sequence': 1,
    'installable': True,
    'doc': ['doc/index.rst'],
    "application": True,
}
