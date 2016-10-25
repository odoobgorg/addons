# -*- coding: utf-8 -*-
# © 2015 Aserti Global Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "X-Forwarded-For IPs in log",
    "summary": "Displays source IPs in log when behind a reverse proxy",
    "version": "10.0.1.0.0",
    "category": "Tools",
    "website": "https://odoo-community.org/,http://www.odoobg.net",
    "author": "Aserti Global Solutions, Lumnus LTD, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
    ],
    "uninstall_hook": "restore_address_string"
}
