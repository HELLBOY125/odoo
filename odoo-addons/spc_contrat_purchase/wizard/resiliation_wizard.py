# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date




    
class ResiliationWizard(models.TransientModel):
    _name = 'resiliation.wizard'
    _description = 'Résiliation du convention'

    date_resiliation = fields.Date(string="Date",required="1") 
    reason_resiliation = fields.Many2one('agreement.resiliation',string="Motif de résiliation",required="1") 
    
  
            
    def validate(self):
        res_ids = self._context.get('active_ids')
        convention = self.env['purchase.agreement'].browse(res_ids)
        for wizard in self:
            convention.date_resiliation=wizard.date_resiliation
            convention.reason_resiliation =wizard.reason_resiliation
            convention.state='end'
        return {'type': 'ir.actions.act_window_close'}
     
    
     