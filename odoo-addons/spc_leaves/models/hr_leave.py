# -*- coding: utf-8 -*-.

import re
from datetime import date, datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.resource.models.resource import float_to_time
from odoo.tools.translate import _
from odoo.tools.float_utils import float_round


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    time_type = fields.Selection(
        related='holiday_status_id.time_type',
        store=True,
    )
    unpaid = fields.Boolean(
        related='holiday_status_id.unpaid',
        store=True,
    )
    

    is_outgoing = fields.Boolean("Is outgoing")
    document_certificate_id = fields.Binary(string="Certificat médical")
    document_certificate_file_name = fields.Char("document_certificate File Name")
    solde_leave= fields.Char(string="Solde de congé",compute="get_solde_leave")
    
    @api.onchange('employee_id','holiday_status_id')
    def onchange_solde_leave(self):
        name=''
        data_days={}
        virtual_remaining_leaves=0.0
        max_leaves=0.0
        if self.employee_id and self.holiday_status_id:
            data_days = self.holiday_status_id.get_employees_days([self.employee_id.id])[self.employee_id.id]
            result = data_days.get(self.holiday_status_id.id, {})
            max_leaves = result.get('max_leaves',0)
            virtual_remaining_leaves = result.get('virtual_remaining_leaves',0)
            if self.holiday_status_id.allocation_type != 'no':
                name = "%(name)s (%(count)s)" % {
                    'name': self.holiday_status_id.name if self.holiday_status_id else '',
                    'count': _('%g remaining out of %g') % (
                        float_round(virtual_remaining_leaves, precision_digits=2) or 0.0,
                        float_round(max_leaves, precision_digits=2) or 0.0,
                    ) + (_(' hours') if self.holiday_status_id.request_unit == 'hour' else _(' days'))
                }
        self.solde_leave=name
     
     
    @api.depends('employee_id','holiday_status_id')    
    def get_solde_leave(self):
        name=''
        for rec in self:
            data_days={}
            virtual_remaining_leaves=0.0
            max_leaves=0.0
            if rec.employee_id and rec.holiday_status_id:
                data_days = self.holiday_status_id.get_employees_days([self.employee_id.id])[self.employee_id.id]
                result = data_days.get(self.holiday_status_id.id, {})
                max_leaves = result.get('max_leaves',0)
                virtual_remaining_leaves = result.get('virtual_remaining_leaves',0)
                if rec.holiday_status_id.allocation_type != 'no':
                    name = "%(name)s (%(count)s)" % {
                        'name': self.holiday_status_id.name if self.holiday_status_id else  '' ,
                        'count': _('%g remaining out of %g') % (
                            float_round(virtual_remaining_leaves, precision_digits=2) or 0.0,
                            float_round(max_leaves, precision_digits=2) or 0.0,
                        ) + (_(' hours') if self.holiday_status_id.request_unit == 'hour' else _(' days'))
                    }
        rec.solde_leave=name    
    @api.model
    def default_get(self, fields_list):
        defaults = super(HrLeave, self).default_get(fields_list)
        defaults = self._default_get_request_parameters(defaults)

        LeaveType = self.env['hr.leave.type'].with_context(employee_id=defaults.get('employee_id'), default_date_from=defaults.get('date_from', fields.Datetime.now()))
        lt = LeaveType.search([('valid', '=', True)], limit=1)
       
        if self._context.get('default_is_outgoing'):
            defaults['holiday_status_id'] = self.env.ref('spc_leaves.holiday_status_outing_authorization').id
#             print(self.is_outgoing)
        elif self._context.get('default_is_not_outgoing'):
            defaults['holiday_status_id'] != self.env.ref('spc_leaves.holiday_status_outing_authorization').id
        else:
            defaults['holiday_status_id'] =None
                
        defaults['state'] = 'confirm' if lt and lt.validation_type != 'no_validation' else 'draft'
        return defaults
    
    
   
    @api.onchange('holiday_status_id')
    def check_holiday_is_outgoing(self):
        
            
            if self.holiday_status_id  == self.env.ref('spc_leaves.holiday_status_outing_authorization'):
                self.request_unit_hours = True
                
          
#     @api.onchange('holiday_status_id') 
#     def check_holiday_is_outgoing_auto(self):
#         holidays=self.env['hr.leave'].sudo().search([])
#         for holiday in holidays:
#              
#             if holiday.holiday_status_id.name == self.env.ref('spc_leaves.holiday_status_outing_authorization').name:
#                 holiday.is_outgoing = True
#                  
#             else: 
#                 
#                 holiday.is_outgoing = False
#                 
                
#     
#     
    
                
    
    
    ####################################################
    # ORM Overrides methods
    ####################################################

    def name_get(self):
        res = []
        for leave in self:
            holiday_status = leave.name or leave.holiday_status_id.name or ''
            if self.env.context.get('short_name'):
                
                if leave.leave_type_request_unit == 'hour':
                    res.append((leave.id, _("%s : %.2f hours") % (holiday_status, leave.number_of_hours_display)))
                else:
                    res.append((leave.id, _("%s : %.2f days") % (holiday_status, leave.number_of_days)))
            else:
                
                if leave.holiday_type == 'company':
                    target = leave.mode_company_id.name
                elif leave.holiday_type == 'department':
                    target = leave.department_id.name
                elif leave.holiday_type == 'category':
                    target = leave.category_id.name
                else:
                    target = leave.employee_id.name
                if leave.leave_type_request_unit == 'hour':
                    res.append(
                        (leave.id,
                        _("%s on %s : %.2f hours") %
                        (target, holiday_status, leave.number_of_hours_display))
                    )
                else:
                    res.append(
                        (leave.id,
                        _("%s on %s: %.2f days") %
                        (target, holiday_status, leave.number_of_days))
                    )
        return res
    
    
    
    

    
    
    
    
       
    #check the difference between the hours
    @api.constrains('request_hour_from', 'request_hour_to')
    def _check_leaves_constrains_hours(self):
        for holiday in self:
            if holiday.holiday_status_id.name == self.env.ref('spc_leaves.holiday_status_outing_authorization').name:
                if holiday.request_hour_from and holiday.request_hour_to:
                    hour_f = abs(float(holiday.request_hour_from))
                    hour_t = abs(float(holiday.request_hour_to))
                    result = hour_t - hour_f
                    nb_hour_auth = self.env['ir.config_parameter'].sudo().get_param('spc_leaves.nb_hours_authorization_month', default=0)

                    if result > float(nb_hour_auth):

                        raise ValidationError(_("La durée d'une autorisation de sortie ne doit pas dépasser"+" "+str(int(float(nb_hour_auth)))+" " +"heures"))

                    elif result == 0 or holiday.number_of_hours_display == 0:

                        raise ValidationError("La durée d'une autorisation de sortie doit être définie")

    #calculate the difference between hours

#     @api.depends('number_of_days')
#     def _compute_number_of_hours_display(self):
#         for holiday in self:
#             if holiday.holiday_status_id.name == self.env.ref('spc_leaves.holiday_status_outing_authorization').name:
#                 if holiday.request_hour_from and holiday.request_hour_to:
#                     hour_f = abs(holiday.request_hour_from) - 0.5 if holiday.request_hour_from < 0 else abs(holiday.request_hour_from)
#                     hour_t = abs(holiday.request_hour_to) - 0.5 if holiday.request_hour_to < 0 else abs(holiday.request_hour_to)
#                     result = hour_t - hour_f
#                     holiday.number_of_hours_display = result
             
    #onchange holiday.request_date_to
#     @api.onchange('request_date_from')
#     def _onchange_duration_hours(self):
#         for holiday in self:
#             if holiday.holiday_status_id.name == self.env.ref('spc_leaves.holiday_status_outing_authorization').name:
#                 holiday.request_date_to = holiday.request_date_from

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HrLeave, self).create(vals_list)
        res.check_holiday_is_outgoing()
        # I added the parent_id var to avoid our problem of rules (hr_user) [Read]
        parent_id = self.env['hr.employee'].browse(res.employee_id.id).sudo().parent_id.user_id

        if parent_id:
            template_id = self.env.ref('spc_leaves.email_template_leave_for_approve')
            template_id.send_mail(res.id, force_send=True)
        return res
# 
# 
#     
#     def action_validate(self):
#         record_id = self.id
#         res = super(HrLeave, self).action_validate()
#         
#         template_id = self.env.ref('spc_leaves.email_template_leave_approve')
#         template_id.send_mail(self.id, force_send=True)
#         return True
    def action_approve(self):
        res = super(HrLeave, self).action_approve()
        template_id = self.env.ref('spc_leaves.email_template_leave_approve')
        template_id.send_mail(self.id, force_send=True)
        return res 
#     
    def action_refuse(self):
        record_id = self.id
        res = super(HrLeave, self).action_refuse()
        template_id = self.env.ref('spc_leaves.email_template_leave_rejection')
        template_id.send_mail(record_id, force_send=True)
        return res
    
