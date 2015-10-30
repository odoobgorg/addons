# -*- encoding: utf-8 -*-
##############################################################################
#
# @author - Rosen Vladimirov, Terraros Commerce <vladimirov.rosen@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp
from openerp import SUPERUSER_ID, tools, api, models
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

class res_company(osv.osv):
	_name = 'res.company'
	_inherit = "res.company"
	_columns = {
		'bg_uic': fields.related('partner_id', 'bg_uic', string=_('UIC'), type="char", size=13, required=True, help=_('UIC by Bulgarian register agency')),
	}

