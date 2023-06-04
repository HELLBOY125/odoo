# -*- coding: utf-8 -*-
# Part Of AS CONSULTING

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.exceptions import UserError
from pkg_resources._vendor.pyparsing import line

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    @api.depends('amount', 'amount_retention')
    def _compute_amount(self):
        if self.amount and self.amount_retention:
            self.amount_after_retention = self.amount - self.amount_retention
        else:
            self.amount_after_retention = 0
    
    account_retention_id = fields.Many2one('account.retention', string="Retenue à la source",  readonly=True, states={'draft': [('readonly', False)]})
    amount_base_retention = fields.Monetary(string='Base de la retenue', readonly=True, states={'draft': [('readonly', False)]})
    amount_retention = fields.Monetary(string='Montant de la retenue', readonly=True, states={'draft': [('readonly', False)]})
    amount_after_retention = fields.Monetary(compute='_compute_amount', string='Montant Net', readonly=True)
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountPayment, self)._onchange_partner_id()
        if self.partner_id:
            """ Charger la retenue à la source de client/Fournisseur """
            self.account_retention_id = self.partner_id.retention_id and self.partner_id.retention_id.id or False
        return res
    
    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        res = super(AccountPayment, self)._onchange_amount()
        if self.amount:
            self.amount_base_retention = self.amount
            if self.account_retention_id:
                self._onchange_account_retention_id()
        return res

    
    @api.onchange('account_retention_id')
    def _onchange_account_retention_id(self):
        """ Calculer le montant de la retenue à la source """
        if self.account_retention_id:
            if self.amount_base_retention >= self.account_retention_id.amount:
                retention_amount = self.amount_base_retention * self.account_retention_id.percent
                self.amount_retention = retention_amount
            else:
                warning = {
                    'title': _("Avertissement sur la retenue à la source"),
                    'message': "La retenu à la source " + self.account_retention_id.name + " s'applique sur un montant >=" + str(self.account_retention_id.amount) + ". Veuillez choisir la retenue qui convient à votre paiement !"
                }
                return {'warning': warning}
            
    
    def get_move_line_bank(self, payment_id, move_lines):
        """ Retourner l'écriture de paiement """
        if payment_id.partner_type == 'customer':
            if payment_id.payment_type == 'inbound':
                for line in move_lines:
                    if line[2]['account_id'] == payment_id.journal_id.default_debit_account_id.id:
                        return line
                    else:
                        continue
                return False
            if payment_id.payment_type == 'outbound':
                for line in move_lines:
                    if line[2]['account_id'] == payment_id.journal_id.default_credit_account_id.id:
                        return line
                    else:
                        continue
                return False
        else: #  payment_id.partner_type == 'supplier'
            if payment_id.payment_type == 'outbound':
                for line in move_lines:
                    if line[2]['account_id'] == payment_id.journal_id.default_debit_account_id.id:
                        return line
                    else:
                        continue
                return False
            if payment_id.payment_type == 'inbound':
                for line in move_lines:
                    if line[2]['account_id'] == payment_id.journal_id.default_credit_account_id.id:
                        return line
                    else:
                        continue
                return False
            
                
    def update_move_line_bank_retenu(self, payment_id, payment_move_line):
        """ Mettre à jour l'écriture de paiement pour intégrer l'écriture de la retenue à la source """
        if not payment_move_line:
            return False
        
        if payment_id.partner_type == 'customer':
            if payment_id.payment_type == 'inbound':
                amount_without_retention = payment_move_line['debit'] - payment_id.amount_retention
                payment_move_line['debit'] = amount_without_retention
            if payment_id.payment_type == 'outbound':
                amount_without_retention = payment_move_line['credit'] - payment_id.amount_retention
                payment_move_line['credit'] = amount_without_retention
        else: # payment_id.partner_type == 'supplier':
            if payment_id.payment_type == 'inbound':
                amount_without_retention = payment_move_line['debit'] - payment_id.amount_retention
                payment_move_line['debit'] = amount_without_retention
            if payment_id.payment_type == 'outbound':
                amount_without_retention = payment_move_line['credit'] - payment_id.amount_retention
                payment_move_line['credit'] = amount_without_retention
        return True
    
    
    def prepare_move_line_retenu(self, payment_id):
        """ Créer l'écriture de retenue à la source """
        debit = credit = 0.0
        if payment_id.partner_type == 'customer':
            if payment_id.payment_type == 'inbound':
                debit = payment_id.amount_retention
                account_id = payment_id.account_retention_id.debit_account_id.id
            if payment_id.payment_type == 'outbound':
                credit = payment_id.amount_retention
                account_id = payment_id.account_retention_id.credit_account_id.id
        else: # payment_id.partner_type == 'supplier':
            if payment_id.payment_type == 'inbound':
                debit = payment_id.amount_retention
                account_id = payment_id.account_retention_id.debit_account_id.id
            if payment_id.payment_type == 'outbound':
                credit = payment_id.amount_retention
                account_id = payment_id.account_retention_id.credit_account_id.id
        
        move_line_value = (0, 0, {
            'name': "Retenue à la source " + payment_id.account_retention_id.name,
            'amount_currency': 0.0,
            'currency_id': payment_id.journal_id.currency_id.id,
            'debit': debit,
            'credit': credit,
            'date_maturity': payment_id.payment_date,
            'partner_id': payment_id.partner_id.commercial_partner_id.id,
            'account_id': account_id,
            'payment_id': payment_id.id,
        })
        return move_line_value
    
                
    
    def _prepare_payment_moves(self):
        move_values = super(AccountPayment, self)._prepare_payment_moves()
        print ('move_lines prepare ********', move_values)
        for move_value in move_values:
            if move_value and move_value['line_ids']:
                payment_id = move_value['line_ids'][0][2]['payment_id']
                payment = self.env['account.payment'].browse(payment_id)
                if payment.account_retention_id:
                    payment_move_line = self.get_move_line_bank(payment, move_value['line_ids'])
                    self.update_move_line_bank_retenu(payment, payment_move_line[2])
                    move_retention_line = self.prepare_move_line_retenu(payment)
                    move_values[0]['line_ids'].append(move_retention_line)
        return move_values
    

class payment_register(models.TransientModel):
    _inherit = 'account.payment.register'
    
    account_retention_id = fields.Many2one('account.retention', string="Retenue à la source")
    
    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.

        :param invoices: The invoices/bills to pay. In case of multiple
            documents, they need to be grouped by partner, bank, journal and
            currency.
        :return: The payment values as a dictionary.
        '''
        values = super(payment_register, self)._prepare_payment_vals(invoices)
        
        amount = self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, self.journal_id, self.payment_date)
        amount_retention = 0
        if self.account_retention_id:
            if amount >= self.account_retention_id.amount:
                amount_retention = amount * self.account_retention_id.percent
        values.update({
            'account_retention_id': self.account_retention_id and self.account_retention_id.id or False,
            'amount_retention': amount_retention
        })
        return values
        
        
        
            
    

    
    