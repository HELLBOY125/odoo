# -*- coding: utf-8 -*-
# Part Of AS CONSULTING

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, format_date, get_lang
from pickle import FALSE


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    @api.model
    def _default_applicate_timbre(self):
        ''' Application de timbre par défaut sur les factures de vente et les facture d'achat '''
        journal = self._get_default_journal()
        if journal.type == 'sale':
            return journal.company_id.applicate_out_timbre
        elif journal.type == 'purchase':
            return journal.company_id.applicate_in_timbre
        else:
            return False
        
    
    applicate_timbre = fields.Boolean(string="Appliquer Timbre Fiscal", default=_default_applicate_timbre, states={'draft': [('readonly', False)]})
    
    
    def get_line_timbre_values(self, tax_id, purchase_tax_id, move_type):
        """ Retourner le dictionnaire de la ligne de facture/avoir de timbre selon le type de facture/avoir """
        value = {
            'name': "Timbre",
            'move_id': self.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'recompute_tax_line': True,
        }
        
        if move_type == 'out_invoice':
            value.update({'quantity': 1.0,
                          'tax_ids': [(6, 0, [tax_id.id])],
                          'account_id': self.journal_id.default_credit_account_id.id})
        elif move_type == 'out_refund':
            value.update({'quantity': -1.0,
                          'tax_ids': [(6, 0, [tax_id.id])],
                          'account_id': self.journal_id.default_debit_account_id.id})
        elif move_type == 'in_invoice':
            value.update({'quantity': -1.0,
                          'tax_ids': [(6, 0, [purchase_tax_id.id])],
                          'account_id': self.journal_id.default_debit_account_id.id})
        if move_type == 'in_refund':
            value.update({'quantity': 1.0,
                          'tax_ids': [(6, 0, [purchase_tax_id.id])],
                          'account_id': self.journal_id.default_credit_account_id.id})   
        else:
            pass
        
        return value
            
    @api.onchange('applicate_timbre')
    def _onchange_applicate_timbre(self):
        """ Gestion de timbre fiscal """
        tax_id = self.company_id.account_tax_id
        purchase_tax_id = self.company_id.asc_account_purchase_tax_id
        if self.applicate_timbre:
            exist_line = False
            for line in self.invoice_line_ids:
                if line.name == 'Timbre':
                    if self.type in ('out_invoice', 'out_refund'):
                        line.tax_ids = [tax_id.id]
                    elif self.type in ('in_invoice', 'in_refund'):
                        line.tax_ids = [purchase_tax_id.id]
                    line.recompute_tax_line = True
                    self._onchange_invoice_line_ids()
                    exist_line = True
                else:
                    continue
            if not exist_line:
                vals = self.get_line_timbre_values(tax_id, purchase_tax_id, self.type)
                self.env['account.move.line'].new(vals)
                self._onchange_invoice_line_ids()
        else:
            taxe_timbre_id = False
            if self.type in ('out_invoice', 'out_refund'):
                taxe_timbre_id = tax_id
            elif self.type in ('in_invoice', 'in_refund'):
                taxe_timbre_id = purchase_tax_id
            else:
                pass
            for line in self.invoice_line_ids:
                if taxe_timbre_id.id in line.tax_ids.ids:
                    line.tax_ids = False
                    line.recompute_tax_line = True
                    self._onchange_invoice_line_ids()
                    break
                else:
                    continue
        
    
