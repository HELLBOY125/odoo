# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from lxml import etree
import re


class Employee(models.Model):
    _inherit = 'hr.employee'

    # Main page
    matricule = fields.Char(string='Matricule', required=True)
    identification_id = fields.Char(string='Identification No', groups="hr.group_hr_user", tracking=True,size=8)
    mobile_phone = fields.Char(string="Mobile pro", help='Mobile professionnel')
    work_phone = fields.Char(string="Téléphone pro", help='Téléphone professionnel')
    work_email = fields.Char(string="Email pro", help='Email professionnel')
    company_country_id = fields.Many2one(related='company_id.country_id')
    employee_type_id = fields.Many2one('hr.employee.type', string="Type de l'employé")
    linked_company = fields.Many2one('res.partner', string="Société liée", domain=[('is_company', '=', True)])

    # Informations personnelles
    bank_account_ids = fields.One2many(comodel_name='res.partner.bank', inverse_name='employee_id',
                                       string='Comptes Bancaires', tracking=True)
    delivred_date_identification = fields.Date(string="Délivrée le")
    matricule_cnss = fields.Char(string="Matricule CNSS/CNRPS", size=10)
    state_id = fields.Many2one('res.country.state', string="Lieu de naissance",
                               domain=lambda self: [('country_id', '=', self.env.ref('base.tn').id)])
    householder = fields.Selection([('yes', 'Oui'), ('no', 'Non'), ],
                                   string="Chef de famille", default="no")
    # Informations personnelles
    mobile = fields.Char(related='address_home_id.mobile', string="Mobile", readonly=False)
    military_service = fields.Selection([('yes', 'Oui'), ('no', 'Non'), ],
                                        string="Service militaire", default="no")
    num_securite_sociale = fields.Char(string="N° sécurité sociale")
    num_permis_conduire = fields.Char(string="N° Permis de conduire")
    work_location_id = fields.Many2one('hr.work.location', string="Lieu de travail")
    new_km_home_work = fields.Float(string="Km Domicile - Bureau", groups="hr.group_hr_user", tracking=True)
    national_fund = fields.Selection([('cnss', 'CNSS'), ('cnrps', 'CNRPS'), ],
                                     string="Caisse nationale", default="cnss")

    partner_ids = fields.One2many(comodel_name='res.partner', inverse_name='employee_id', string="Benéficiares",compute='get_beneficaire')
    is_conventionne = fields.Boolean(string="Conventionné",default=True)
    _sql_constraints = [('matricule_unique', 'unique(matricule)', _('Matricule existe déja !'))]

    def get_beneficaire(self):
        for rec in self:
            partner_ids=False
            if self.user_id:
                partner_ids =self.user_id.partner_id.child_ids.ids if self.user_id.partner_id.child_ids else False
            rec.partner_ids=partner_ids

    @api.constrains('identification_id')
    def _check_unique_identification_id(self):
        for record in self:
            new_value = record.identification_id
            if new_value:
                existing_records = record.env['hr.employee'].search([('identification_id', '=', new_value)])
                if len(existing_records) > 1:
                    raise ValidationError("Le N° d'identification existe déja !")

    @api.constrains('work_email')
    def _check_work_email(self):
        for record in self:
            new_value = record.work_email
            if new_value:
                existing_records = record.env['hr.employee'].search([('work_email', '=', new_value)])
                if len(existing_records) > 1:
                    raise ValidationError("Email professionnel existe déja !")
                if not (re.match(r"[^@]+@[^@]+\.[^@]+", new_value)):
                    raise ValidationError("Email invalid ! Merci de bien vouloir vérifier le format d'émail SVP")

    @api.constrains('matricule')
    def _check_matricule(self):
        my_acc = ""
        for record in self:
            if record.matricule:
                my_acc = record.matricule
                if not record.matricule.isalnum():
                    raise ValidationError("Le matricule ne doit pas contenir des caractères spéciaux !")
                if len(record.matricule) > 20:
                    raise ValidationError("Le longeur du matricule ne doit pas être supérieur à 20 !")

    @api.constrains('num_securite_sociale')
    def _check_num_securite_sociale(self):
        for record in self:
            if record.num_securite_sociale:
                if not record.num_securite_sociale.isdecimal():
                    raise ValidationError("Le N° de  sécurité sociale ne doit contenir que des chiffres !")
                if len(record.num_securite_sociale) > 20:
                    raise ValidationError(
                        "Le longeur du N° de sécurité sociale ne doit pas être supérieur à 20 chiffres!")

    @api.constrains('num_permis_conduire')
    def _check_num_permis_conduire(self):
        for record in self:
            if record.num_permis_conduire:
                if len(record.num_permis_conduire) > 20:
                    raise ValidationError(
                        "Le longeur du N° de permis de conduire ne doit pas dépasser 20 Lettres / Chiffres !")

    @api.constrains('matricule_cnss')
    def _check_matricule_cnss_cnrps(self):
        for record in self:
            new_value = record.matricule_cnss
            if new_value:
                if not (re.match(r"^[0-9]+$", new_value)):
                    raise ValidationError("Le matricule de CNSS/CNRPS ne doit pas contenir que des numéros!")

            if record.matricule_cnss:
                if len(record.matricule_cnss) > 10:
                    raise ValidationError(
                        "Le matriculre de CNSS ou CNRPS ne doit pas dépasser 10 Chiffres !")

    @api.onchange('department_id')
    def _onchange_department(self):
        current_emp = False
        res = super(Employee, self)._onchange_department()
        for record in self:
            current_emp = self.env['hr.employee'].browse(record._origin.id)
            if record.parent_id.id == current_emp.id:
                record.parent_id = False
        return res

    @api.model
    def _fields_view_get_address(self, arch):
        arch = super(Employee, self)._fields_view_get_address(arch)
        doc = etree.fromstring(arch)

    def update_account_bank(self, vals):
        body = "\n"

        if vals.get('bank_account_ids'):
            for val in vals.get('bank_account_ids'):
                if val[2] != False and val[2].get('acc_number'):
                    body += "N° du compte : " + str(val[2].get('acc_number')) + "\n"

                if val[2] != False and val[2].get('bank_id'):
                    bank_id = val[2].get('bank_id')
                    bank_name = self.env['res.bank'].browse(bank_id).name
                    body += "Banque : " + str(bank_name) + "\n"

                if val[2] != False and val[2].get('active_account'):
                    body += "Active : " + str(val[2].get('active_account')) + "\n"

                if val[2] != False and val[2].get('created_date'):
                    body += "Date d'utilisation : " + str(val[2].get('created_date')) + "\n"
        return body

    @api.model
    def create(self, vals):
        res = super(Employee, self).create(vals)
        if res.is_conventionne:
            if res.user_id:
                if res.user_id.partner_id:
                   res.user_id.partner_id.ref=res.matricule
                   res.user_id.partner_id.type_partner='conventionne'
                   res.user_id.partner_id.type_conventionne='physique'
        body = self.update_account_bank(vals)
        res.message_post(body=body, subject="Modifications")
        return res

    def write(self, vals):
        res = super(Employee, self).write(vals)
#         if res.is_conventionne:
#             if res.user_id:
#                 if res.user_id.partner_id:
#                    res.user_id.partner_id.ref=res.matricule
#                    res.user_id.partner_id.type_partner='conventionne'
#                    res.user_id.partner_id.type_conventionne='physique'
        # body = self.update_account_bank(vals)
        # self.message_post(body=body, subject="Modifications")
        return res

    def name_get(self):
        result = []
        name=''
        for emp in self:
            if emp.matricule and emp.name:
                name = emp.matricule + ' ' + emp.name
            else:
                name= emp.name
            result.append((emp.id, name))
        return result
    
  
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('matricule', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        emp_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(emp_ids).with_user(name_get_uid))

class EmployeeWorkLocation(models.Model):
    _name = 'hr.work.location'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Lieu", required=True)
    description = fields.Text(string='Description')


class EmployeeType(models.Model):
    _name = 'hr.employee.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Type d'employé"

    name = fields.Char(string="Type de l'employé", required=True)
    description = fields.Text(string="Description")