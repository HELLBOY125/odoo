# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api


class CourrierSortant(models.Model):
   _name = 'courrier.sortant'
   _inherit = ['mail.thread', 'mail.activity.mixin']
   _description = "Les courriers sortants"
   _order = 'date_courrier desc'

   def _default_employee(self):
        return self.env.user.employee_id.department_id

   
   name = fields.Char(string="Réference", readonly=True)
   state = fields.Selection([
      ('to_service', "Agent Service"),
      ('to_sousdirect', "Responsable Service"),
      ('to_soumdirect', "Responsable BO"),
      ('draft', "Service courrier"),
      ('traiter','Traité'),
   ], default='to_service', string="État", track_visibility='onchange')

   type_id = fields.Many2one('type.courrier.sortant', 'Type de courrier',required=True)
   date_send = fields.Date(string="Date d'envoi")
   urgent_id = fields.Many2one('courrier.urgence', 'Urgence')
   date_courrier = fields.Date(string='Date de traitement', default=fields.Date.today(), required=True)
   objet = fields.Text(string="Résumé")
   department_id = fields.Many2one('hr.department', string="Département",default=_default_employee)
   street = fields.Char(string="Rue")
   street2 = fields.Char(string="Street2")
   city = fields.Char(string="Ville")
   country_id = fields.Many2one('res.country', 'Pays', ondelete='restrict')
   state_id = fields.Many2one('res.country.state', 'State', domain="[('country_id', '=', country_id)]")
   zip = fields.Char(string="Code postale", size=24, change_default=True)
   website = fields.Char(string="Site Web", help="Website of Partner or Company")

   mode_reception_id = fields.Many2one('courrier.mode', "Mode d'envoi", required=True)
   partner_name =fields.Char('Nom')
   type_destinataire =fields.Char(string="Type destinataire")
   function = fields.Char(string="Poste occupé")
   phone = fields.Char(string="Tél.",default="00 000 000")
   email = fields.Char(string="courrier")
   is_company = fields.Boolean(help="Check if the contact is a company, otherwise it is a person")
   title = fields.Many2one('res.partner.title', 'Civilité')
   contact_id = fields.Many2one('res.partner', string="Contact")
   user_id = fields.Many2one('res.users', 'Expéditeur')
   user_ids = fields.Many2many('res.users', 'courrier_sortant_res_users_rel', 'courrrier_sortant_id', 'user_id',string="Agent destinataire")
   state_color_courrier = fields.Boolean(string="Merci de cocher cet case si vous voulez mettre le courrier toujours noir !")
   attachement_ids = fields.Many2many('ir.attachment', string="Attachements")
   courrier_id = fields.Binary('Courrier')
   current_user = fields.Boolean(store=True)
   autre_destinataire = fields.Selection([('cnm', "CNM"), ('dg', "Direction Générale")], string="Autre destinataire", default='dg')
   autre_destinataire_autre = fields.Char(string="Autre destinataire")
   existe_autre_destinataire = fields.Selection(string='Autre destinataire ?', selection=[('Yes', 'Oui'), ('No', 'Non')], default='No')
   notes = fields.Html(string="Notes")
   courrier_entrant_id = fields.Many2one(comodel_name='courrier.entrant', string="Courrier entrant", tracking=True)
   courrier_traite = fields.Boolean("Courrier Traité",readonly=True)
   date_traitement = fields.Date("Date de traitement", readonly=True)
   steg_department_id = fields.Many2one('steg.department', string="Département STEG")


   def to_sousdirect(self):
      self.sudo().state = 'to_sousdirect'

   def to_service(self):
      self.sudo().state = 'to_service'

   def draft(self):
      self.state = 'draft'

   def to_soumsecretariat(self):
      self.state = 'to_soumsecretariat'

   def to_soumdirect(self):
      self.state = 'to_soumdirect'
   
   def action_courrier_traite(self):
        """Mettre le champ courrier traité à True pour signaler le traitement de courrier"""
        self.courrier_traite =True
        self.date_traitement = fields.Date.today()
        self.state='traiter'    
      
      

   @api.onchange('existe_autre_destinataire')
   def _onchange_existe_autre_destinataire(self):
      if self.existe_autre_destinataire == 'Yes':
         self.autre_destinataire = ''

   @api.model
   def create(self, vals):
        my_date = datetime.now()
        current_year = my_date.year
        type_courrier = self.env['type.courrier.sortant'].search([('id', '=', vals['type_id'])],limit=1)
        code_courrier = type_courrier.code_sortant
        code_seq = 'CS.' + code_courrier
        ir_sequence_id = self.env['ir.sequence'].search([('code', '=', code_seq)])
        if ir_sequence_id:
            seq_prefix = ir_sequence_id.next_by_code(code_seq)
            vals.update({'name': seq_prefix})
        else:
            val_seq = {"name": "CS-" + code_courrier,
                     "code": code_seq,
                     "prefix": "CS/" + str(code_courrier) + "/" + "%(current_year)s" + "/",
                     "use_date_range": True,
                     "padding": 5,
                     "number_increment": 1,
                     }
            self.env['ir.sequence'].sudo().create(val_seq)
            vals['name'] = self.env['ir.sequence'].next_by_code(code_seq)
        result = super(CourrierSortant, self).create(vals)
        return result

   def write(self, vals):
        if 'type_id' in vals:
            type_courrier = self.env['type.courrier.sortant'].search([('id', '=', vals['type_id'])],limit=1)
            code_courrier = type_courrier.code_sortant
            code_seq = 'CS.' + code_courrier
            ir_sequence_id = self.env['ir.sequence'].search([('code', '=', 'code_seq')])
            if ir_sequence_id:
                seq_prefix = ir_sequence_id.next_by_code(code_seq)
                vals.update({'name': seq_prefix})
            else:
                val_seq = {"name": "CE-" + code_courrier,
                           "code": code_seq,
                           "prefix": "CE/" + str(code_courrier) + "/" + "%(current_year)s" + "/",
                           "use_date_range": True,
                           "padding": 5,
                           "number_increment": 1,
                           }
                self.env['ir.sequence'].sudo().create(val_seq)
                vals.update({'name': self.env['ir.sequence'].next_by_code(code_seq)})
        result = super(CourrierSortant, self).write(vals)
        return result