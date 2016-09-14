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

import models

import logging

_logger = logging.getLogger(__name__)


def post_init_l10n_bg(cr, registry):
    from openerp import SUPERUSER_ID
    _logger.info("Post hook bg start")
    if l10n_bg_install_lang(registry, cr, SUPERUSER_ID, 'bg_BG'):
        _logger.info("BG Lang created/updated")

    if l10n_bg_change_customer_invoice_data(registry, cr, SUPERUSER_ID):
        _logger.info("Customer invoice updated")
    _logger.info("Post hook bg end")


def l10n_bg_install_lang(registry, cr, uid, lang):
    res_lang = registry['res.lang']
    lang_ids = res_lang.search(cr, uid, [('code', '=', lang)])
    if not lang_ids:
        lang_ids.append(res_lang.load_lang(cr, uid, lang))

    res_lang_data = {
        'date_format': '%d.%m.%Y г.',
        'thousands_sep': '.',
        'decimal_point': '.',
    }
    for lang_id in lang_ids:
        res_lang.write(cr, uid, lang_id, res_lang_data, context={})

    ir_values_obj = res_lang.pool.get('ir.values')
    default_value = ir_values_obj.get(cr, uid, 'default', False, ['res.partner'])
    if not default_value:
        ir_values_obj.set(cr, uid, 'default', False, 'lang', ['res.partner'], lang)

    return True


def l10n_bg_change_customer_invoice_data(registry, cr, uid):
    account_journal = registry['account.journal']
    account_journal_ids = account_journal.search(cr, uid, [('code', '=', 'INV')])

    if account_journal_ids:
        ir_sequence_data = {
            'prefix': '',
            'suffix': '',
            'padding': 10,
            'number_increment': 1,
            'use_date_range': False,
            'active': True,
            'implementation': 'no_gap',
        }

        for account_journal in account_journal.browse(cr, uid, account_journal_ids, context={}):
            ir_sequence = registry['ir.sequence']
            ir_sequence_ids = ir_sequence.search(cr, uid, [('name', '=', account_journal.name)])

            if ir_sequence_ids:
                for ir_sequence_id in ir_sequence_ids:
                    ir_sequence.write(cr, uid, ir_sequence_id, ir_sequence_data, context={})
                    _logger.info("account journal %s, ir sequence %s" % (account_journal.id, ir_sequence_id))

    return True
