# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import except_orm
from odoo import exceptions


class SalaryAdvancePayment(models.Model):
    _name = "salary.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Demande d'avance"

    name = fields.Char(string='Nom', readonly=True, default=lambda self: '/')
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True, help="Employee")
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today(), help="Submit date")
    reason = fields.Text(string='Raison', help="Reason")
    currency_id = fields.Many2one('res.currency', string='Devise', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    advance = fields.Float(string='Avance', required=True)
    payment_method = fields.Many2one('account.journal', string='Méthode de paiement')
    exceed_condition = fields.Boolean(string='Exceed than Maximum',
                                      help="The Advance is greater than the maximum percentage in salary structure")
    department = fields.Many2one('hr.department', string='Département')
    state = fields.Selection([('draft', 'Brouillon'),
                              ('submit', 'Envoyé'),
                              ('waiting_approval', 'En attente de validation'),
                              ('approve', 'Approuvé'),
                              ('cancel', 'Annulé'),
                              ('reject', 'Rejeté')], string='État', default='draft', track_visibility='onchange')
    debit = fields.Many2one('account.account', string='Compte Débit')
    credit = fields.Many2one('account.account', string='Compte Crédit')
    journal = fields.Many2one('account.journal', string='Journal')
    employee_contract_id = fields.Many2one('hr.contract', string='Contrat')
    paid = fields.Boolean(string="Payé", help="Payé")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            department_id = self.employee_id.department_id.id
            company_id = self.employee_id.company_id.id
            domain = [('employee_id', '=', self.employee_id.id)]
            employee_contract_id = self.env['hr.contract'].search(domain)[0].id
            return {'value': {'department': department_id, 'company_id': company_id,
                              'employee_contract_id': employee_contract_id},
                    'domain': {'employee_contract_id': domain}
                    }

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        domain = [('company_id.id', '=', company.id)]
        result = {
            'domain': {
                'journal': domain,
            },

        }
        return result

    def submit_to_manager(self):
        self.state = 'submit'

    def cancel(self):
        self.state = 'cancel'

    def reject(self):
        self.state = 'reject'

    def draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('salary.advance.seq') or ' '
        res_id = super(SalaryAdvancePayment, self).create(vals)
        return res_id

    def approve_request(self):
        """This Approve the employee salary advance request.
                   """
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise except_orm('AVERTISSEMENT!', "L'avance peut être demandée une fois par mois")
        if not self.employee_contract_id:
            raise except_orm('Error!', 'Define a contract for the employee')
        struct_id = self.employee_contract_id.struct_id
        adv = self.advance
        amt = self.employee_contract_id.wage

        if not self.advance:
            raise except_orm('AVERTISSEMENT', "Vous devez saisir le montant de l'avance sur salaire")
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'done'), ('date_from', '<=', self.date),
                                                     ('date_to', '>=', self.date)])
        if payslip_obj:
            raise except_orm('AVERTISSEMENT', "Salaire de ce mois déjà calculé")

        for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]):
            slip_moth = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date), '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise exceptions.Warning(
                        _('La demande peut être faite après " %s" jours du mois de salaire précédent') % struct_id.advance_date)
        self.state = 'waiting_approval'

    def approve_request_acc_dept(self):
        """This Approve the employee salary advance request from accounting department.
                   """
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise except_orm('AVERTISSEMENT!', "L'avance peut être demandée une fois par mois")

        if not self.advance:
            raise except_orm('AVERTISSEMENT', "Vous devez saisir le montant de l'avance sur salaire")

        self.state = 'approve'
