# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# © 2016 Lumnus LTD - Kaloyan Naumov, adding City for pre-selection
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request
# from odoo.addons.website_sale.controllers.main import website_sale


# class WebsiteSale(website_sale):
class WebsiteSale(http.Controller):
    def checkout_values(self, data=None):
        result = super(WebsiteSale, self).checkout_values(data)
        try:
            result["checkout"].setdefault(
                "country_id",
                request.website.company_id.country_id.id)
            result["checkout"].setdefault(
                "city",
            request.website.company_id.city)
        except KeyError:
            pass
        return result
