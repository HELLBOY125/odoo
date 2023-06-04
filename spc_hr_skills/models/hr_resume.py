# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re
from odoo.osv import expression
from builtins import int


class Employee(models.Model):
    _inherit = 'hr.employee'

    #
    def _get_contracts_list_employee(self):
        list = []
        for rec in self:
            contracts_sorted = rec.id.contract_ids.sort(reverse=False)
            list.append(contracts_sorted)
        return list

    @api.model_create_multi
    def create(self, vals_list):
        len_res = 0
        current_company = False
        list_sorted = []
        list_sorted = self._get_contracts_list_employee()

        res = super(Employee, self).create(vals_list)

        len_res = len(res.resume_line_ids)
        current_company_id = res.resume_line_ids[len_res - 1].id
        employee_id = self.env['hr.employee'].browse(res.id)

        employee_id.resume_line_ids[len_res - 1].sudo().update(
            {'current_comp_id': current_company_id})

        return res


#     def write(self, vals):
# #         if vals.get('contract_ids'):
#         print("write function get vals")
#         print(vals)

#     @api.model_create_multi
#     def create(self, vals_list):
#         res = super(Employee, self).create(vals_list)
#         for employee in res:
#             for line in res.resume_line_ids:
#                 line.write({'date_start': employee.birthday})
#         return res


class HrResumeLine(models.Model):
    _inherit = 'hr.resume.line'
    _description = "Resumé line of an employee"

    date_end_rl = fields.Date(compute='_get_current_end_date', store=True)
    duration_experience = fields.Char(string="Durée expérience", compute='_difference_date_experience', store=True)
    current_comp_id = fields.Integer(string="Current comp id")

    # Education fields
    university_id = fields.Many2one(comodel_name='res.partner', string="Université", domain=[('is_university', '=', True)])
    diploma_id = fields.Many2one('hr.employee.diploma', string="Diplôme")
    cursus = fields.Char(string="Cursus")
    attachments_ids = fields.One2many(comodel_name='ir.attachment', inverse_name='hr_resume_line_id',
                                      string="Pièces jointes")

    @api.depends('date_end')
    def _get_current_end_date(self):
        current_date_today = date.today()
        for record in self:

            if record.date_end:
                record.date_end_rl = record.date_end
            else:

                record.date_end_rl = current_date_today

    @api.constrains('date_start', 'date_end', 'employee_id')
    def _check_date(self):

        current_date_today = date.today()

        domains = [[
            ('date_start', '<', rec.date_end_rl),
            ('date_end_rl', '>', rec.date_start),

            ('employee_id', '=', rec.employee_id.id),
            ('line_type_id', '=', rec.line_type_id.id),
            ('id', '!=', rec.id),
        ] for rec in self.filtered('employee_id')]

        domain = expression.AND([expression.OR(domains)])

        if self.search_count(domain):
            raise ValidationError(_('Vous ne pouvez pas avoir deux expériences  durant la même période.'))

    @api.constrains('date_start', 'date_end')
    def _check_dates_debut_experience_date_fin(self):

        for rec in self:
            if rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError(_("La date de début de l'expérience doit être antérieure à la date de fin."))

    @api.depends('date_start', 'date_end')
    def _difference_date_experience(self):
        date_end = False
        total_month = ""
        total_duration = ""
        for rec in self:
            if rec.date_end:
                date_end = rec.date_end
            else:
                date_end = date.today()
            if date_end and rec.date_start:
                date_start_exp = datetime.strptime(str(rec.date_start), '%Y-%m-%d')
                date_end_exp = datetime.strptime(str(date_end), '%Y-%m-%d')

                r = relativedelta(date_end_exp, date_start_exp) + relativedelta(months=+1)

                if r.years == 1:
                    total_duration = str(r.years) + " an "
                elif r.years > 1:
                    total_duration = str(r.years) + " ans "

                if r.months > 0:
                    total_month = str(r.months) + " mois"

                if r.years > 0 and r.months > 0:
                    total_duration += "et " + total_month
                elif r.months >= 1 and not r.years:
                    total_duration = total_month

                rec.duration_experience = total_duration


class HrEmployeeDiploma(models.Model):
    _name = 'hr.employee.diploma'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Diplôme", required=True)
    title = fields.Char(string="Titre")
