# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount

            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

            if loan.total_paid_amount == loan.total_amount and loan.balance_amount == 0.0 and loan.state == 'approve':
                loan.paid = True
            else:
                loan.paid = False

    name = fields.Char(string="Titre de prêt", default="/", readonly=True, help="Titre de prêt", tracking=True)
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date", tracking=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employé", required=True, help="Employé")
    department_id = fields.Many2one(comodel_name='hr.department', related="employee_id.department_id", readonly=True,
                                    string="Département", help="Employé", tracking=True)
    installment = fields.Integer(string="Nombre des tranches", default=1, help="Nombre des tranches", tracking=True)
    payment_date = fields.Date(string="Date de paiement", required=True, default=fields.Date.today(),
                               help="Date de paiement", tracking=True)
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Détails du prêt", index=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Société', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(comodel_name='res.currency', string='Devise', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one(comodel_name='hr.job', related="employee_id.job_id", readonly=True, string="Poste",
                                   help="Poste")
    loan_amount = fields.Float(string="Montant du prêt", required=True, help="Montant du prêt", tracking=True)
    total_amount = fields.Float(string="Total", store=True, readonly=True, compute='_compute_loan_amount',
                                help="Total")
    balance_amount = fields.Float(string="Montant en balance", store=True, compute='_compute_loan_amount',
                                  help="Montant en balance")
    total_paid_amount = fields.Float(string="Total payé", store=True, compute='_compute_loan_amount',
                                     help="Total payé")
    loan_percent = fields.Float(string="Pourcentage du prêt")

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting_approval_1', 'Envoyé'),
        ('approve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('cancel', 'Annulé'),
    ], string="État", default='draft', track_visibility='onchange', copy=False)

    paid = fields.Boolean(string="Payé", help="Paid", default=False)


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
        res = super(HrLoan, self).create(values)
        return res

    @api.onchange('employee_id', 'loan_amount', 'installment')
    def check_loan(self):
        if self.employee_id and self.loan_amount and self.installment:
            loan_percent = self.env['ir.config_parameter'].get_param('ohrms_loan.loan_percent')
            wage = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)]).wage
            installment_amount = (self.loan_amount / self.installment)
            amount_percent = (wage * float(loan_percent)) / 100
            if installment_amount > amount_percent:
                return {
                    'warning': {
                        'title': 'ATTENTION !',
                        'message': 'Ce prêt dépasse le plafond autorisé ' + str(loan_percent) + ' %'}
                }

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
        return True

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for data in self:
            if not data.loan_lines:
                raise ValidationError(_("Please Compute installment"))
            else:
                self.write({'state': 'approve'})

    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Payé", help="Payé")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        for rec in self:
            rec.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', rec.id)])
