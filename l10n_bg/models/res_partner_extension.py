from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


# _logger.error(country_id)

class ResPartnerPlaceOfDeal(models.Model):
    _inherit = 'res.partner'

    def name_get_test(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'city'], context=context)
        res = []
        for record in reads:
            name = record['name']
            city = record['city']
            country_id = record['country_id']

            if country_id:
                country_obj = self.pool.get('res.country').browse(cr, uid, country_id, context=context)
                country = country_obj.country_id.name
                _logger.error(country)

            if city:
                name = city
            res.append((record['id'], name))
        return res
