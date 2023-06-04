# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)

import logging

from datetime import datetime, time
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class HolidaysAllocation(models.Model):
    """ Allocation Requests Access specifications: similar to leave requests """
    _inherit = "hr.leave.allocation"

    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True, default=lambda self: self.env.company,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})