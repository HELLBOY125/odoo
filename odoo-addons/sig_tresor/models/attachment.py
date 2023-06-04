# -*- coding: utf-8 -*-

from odoo import models, fields


class IrAttachment(models.Model):

    _inherit = 'ir.attachment'

    document_sfd = fields.Boolean('Documents SFD', default=False)
