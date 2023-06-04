# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class HrContract(models.Model):
    _inherit = 'hr.contract'

    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True, required=True,
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    date_embauche = fields.Date("Date d'embauche", default=fields.Date.today)
    date_depart = fields.Date("Date départ")
    # type_id = fields.Many2one('hr.contract.type', string="Type de contrat", required=True)

    description_job = fields.Html(string="Fonction et attributions", translate='html_translate', sanitize_attributes=False)

    @api.onchange('job_id')
    def onchange_job_id(self):
        if self.job_id:
            self.description_job = self.job_id.job_description

    @api.constrains('date_start', 'date_embauche','date_depart','trial_date_end','date_end')
    def _check_dates_debut_contrat_embauche_depart(self):
        if self.date_embauche and self.date_start and self.date_embauche > self.date_start:
            raise ValidationError(_("La date d'embauche doit être antérieure à la date de début du contrat."))
        elif self.date_depart and self.date_depart < self.date_start:
            raise ValidationError(_('La date de début de contrat doit être antérieure à la date de départ.'))
        elif self.trial_date_end and self.trial_date_end < self.date_start:
            raise ValidationError(_('La date de début de contrat doit être antérieure à la date fin de la période d’essai.'))
        elif self.date_depart and self.trial_date_end and self.trial_date_end > self.date_depart:
            raise ValidationError(_('La date fin de la période d’essai doit être antérieure à la date de départ.'))
        elif self.date_end and self.date_depart and self.date_end > self.date_depart:
            raise ValidationError(_('La date fin de contrat doit être antérieure à la date de départ.'))
        elif self.date_end and self.trial_date_end and self.trial_date_end > self.date_end:
            raise ValidationError(_('La date fin de la période d essai doit être antérieure à la date de fin de contrat.'))
        
    def _get_old_contract_employee(self,emp):
        old_contract = False
        list_sorted = False
        if emp:
            contracts = emp.contract_ids
            list_sorted = sorted(contracts, key=lambda old_contract: old_contract.date_start, reverse=False)
            old_contract = list_sorted[0]
        return old_contract
        
    @api.model
    def create(self, vals):
        print('-----------------------------------', vals)
        emp = False
        len_res = 0
        line_company = False
        old_contract_start_date = False
        res = super(HrContract, self).create(vals)
        emp = self.env['hr.employee'].browse(vals.get('employee_id'))
        if emp.resume_line_ids:
            len_res = len(emp.resume_line_ids)
            if len_res > 0:
                line_company = self.env['hr.resume.line'].search([('current_comp_id', '>', 0),
                                                                  ('employee_id', '=', emp.id)])
                old_contract_start_date = self._get_old_contract_employee(emp).date_start
                if line_company and old_contract_start_date:
                    line_company.sudo().write(
                        {'date_start': old_contract_start_date})
        return res
    
    def update_default_company_resume_line(self, employee_id):
        len_res = 0
        old_contract_start_date = False
        line_company = False
        
        len_res = len(employee_id.resume_line_ids)
        if len_res:
            line_company = self.env['hr.resume.line'].search([('current_comp_id', '>', 0), 
                                                              ('employee_id', '=', employee_id.id)])
            old_contract_start_date = self._get_old_contract_employee(employee_id).date_start
            if line_company and old_contract_start_date:
                line_company.sudo().update(
                    {'date_start': old_contract_start_date})       
        
    def write(self, vals):
        
        super(HrContract, self).write(vals)
        
        len_res = 0
        old_contract_start_date = False
        line_company = False
        
        new_employee_id = False
        old_employee_id = False
        date_start = False
        
        old_employee_id = self.employee_id
        
        if 'employee_id' in vals:
            new_employee_id = self.env['hr.employee'].browse(vals['employee_id'])
        if 'date_start' in vals:
            date_start = vals['date_start']
        else:
            date_start = self.date_start
       
        if new_employee_id:
            len_res = len(new_employee_id.resume_line_ids)
            if len_res:
                line_company = self.env['hr.resume.line'].search([('current_comp_id', '>', 0), 
                                                                  ('employee_id', '=', new_employee_id.id)])
                old_contract_start_date = self._get_old_contract_employee(new_employee_id).date_start
                
                if line_company and old_contract_start_date:
                    
                    line_company.sudo().update(
                        {'date_start': old_contract_start_date})
                       
        elif old_employee_id:
            len_res = len(old_employee_id.resume_line_ids)
            if len_res:
                line_company = self.env['hr.resume.line'].search([('current_comp_id', '>', 0), 
                                                                  ('employee_id', '=', old_employee_id.id)])
                old_contract_start_date = self._get_old_contract_employee(old_employee_id).date_start
                
                if line_company and old_contract_start_date:

                    line_company.sudo().update(
                        {'date_start': old_contract_start_date})
            
        return
        
        
class ContractType(models.Model):
    _inherit = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'

    # name = fields.Char(string='Contract Type', required=True, translate=True, size=10)
    # sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    # company_id = fields.Many2one('res.company')

    @api.constrains('name')
    def check_name(self):
        if self.name:
            pattern = r"^[a-zA-Z0-9]+$"
            if not re.match(pattern,self.name):
                raise models.ValidationError(
                    _("Le type de contrat ne doit pas contenir des caractères spéciaux "))
