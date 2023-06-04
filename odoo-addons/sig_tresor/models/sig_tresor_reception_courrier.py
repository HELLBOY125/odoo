# -*- coding:utf-8 -*-
# !C:/Users/VEONE/odoo-env python

import base64
import logging
import mimetypes
import sys

# from extractor import Extractor

from odoo import fields, models, api, os

_logger = logging.getLogger(__name__)


class SigTresorReceptionCourrier(models.Model):
    """
cette classe permet de traiter les courriers entrants et sortants
"""
    _name = 'sig.tresor.reception.courrier'
    _inherit = ['mail.thread']  # , 'ir.needaction_mixin', 'mail.alias.mixin'
    _description = 'réception du courrier workflow de demande d\'agrément'
    _rec_name = "description"
    _order = 'date_reception desc'

    # recuperer l'employé lié à l'ulisateur connecté
        
    def _employee_get(self):
        resource_id = self.env['resource.resource'].search([('user_id', '=', self.env.user.id)])
        employee_id = self.env['hr.employee'].search([('resource_id', '=', resource_id.id)])
        # employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_id

    # recuperer l'id du group autorisation_exercer_group
        
    def get_group_id_autorisation_exercer(self):
        return self.env.ref('sig_tresor.autorisation_exercer_group').id

    # recuperer len() chef ModuleNotFoundError service d'autorisation d'exercer
        
    def get_chef_sae(self):
        group_id = self.get_group_id_autorisation_exercer()
        print('group_id >>> %s ', group_id[0])
        query = 'SELECT g.uid, p.name FROM res_groups_users_rel AS g INNER JOIN res_users u ON g.uid=u.id INNER JOIN res_partner AS p ON u.partner_id=p.id INNER JOIN hr_employee AS e ON e.user_id=u.id  WHERE g.gid = %s AND  e.id IN (SELECT manager_id FROM hr_department)'
        self.env.cr.execute(query, (group_id[0],))
        user_id = self.env.cr.fetchone()
        print('user_id >>> %s ', user_id[0])
        self.assigne_a = user_id[0]
        return user_id

#         
#     def get_chef_sae(self):
#         group_id = self.get_group_id_autorisation_exercer()
#         print('group_id >>> %s ', group_id[0])
#         query = 'SELECT g.uid, p.name FROM res_groups_users_rel AS g INNER JOIN res_users u ON g.uid=u.id INNER JOIN res_partner AS p ON u.partner_id=p.id INNER JOIN hr_employee AS e ON e.user_id=u.id  WHERE g.gid = %s AND  e.id IN (SELECT manager_id FROM hr_department)'
#         self.env.cr.execute(query, (group_id[0],))
#         user_id = self.env.cr.fetchone()
#         print('user_id >>> %s ', user_id[0])
#         self.assigne_a = user_id[0]
#         return user_id

        
    def get_email_next_validator(self, group_id):
        print('group_id >>> %s ', group_id)
        query = 'SELECT g.uid, p.name, u.login, e.name FROM res_groups_users_rel AS g INNER JOIN res_users u ON g.uid=u.id INNER JOIN res_partner AS p ON u.partner_id=p.id INNER JOIN hr_employee AS e ON e.user_id=u.id  WHERE g.gid = %s AND  e.id IN (SELECT manager_id FROM hr_department)'
        self.env.cr.execute(query, (group_id,))
        user_id = self.env.cr.fetchone()
        print('email >>> %s ', user_id[2])
        self.email_next_validate = user_id[2]
        self.name_next_validate = user_id[3]

        
    def get_email_agent_sae(self, user_id_):
        print('user_id >>> %s ', user_id_.id)
        query = 'SELECT g.uid, p.name, u.login, e.name FROM res_groups_users_rel AS g INNER JOIN res_users u ON g.uid=u.id INNER JOIN res_partner AS p ON u.partner_id=p.id INNER JOIN hr_employee AS e ON e.user_id=u.id  WHERE g.uid= %s'
        self.env.cr.execute(query, (user_id_.id,))
        user_id = self.env.cr.fetchone()
        print('email agent >>> %s ', user_id[2])
        self.email_next_validate = user_id[2]
        self.name_next_validate = user_id[3]

        
    def get_numero_identification_courrier(self):
        seq_id = 'sig.tresor.reception.courrier'
        code = self.env['ir.sequence'].next_by_code(seq_id)
        print('code >> %s ' % code)
        if self.etape == 'recep_enr_dossier':
            self.numero_identification_secretariat = code
        if self.etape == 'etude_forme':
            self.numero_identification_secretariat_complement_dossier = code
        if self.etape == 'etude_fond':
            self.numero_identification_secretariat_courrier_bceao = code
        return code

    description = fields.Text("Description", states={'draft': [('required', True)]})
    type_courrier_id = fields.Many2one('sig.tresor.type.courrier', 'Type courrier')
    # fields of réception dossier demande d'agreement du sfd ou demandeur par le service courrier
    date_reception = fields.Date("Date de réception", default=fields.Date.today)
    numero_identification = fields.Char("N° d'identification")
    courrier = fields.Binary("Joindre le courrier")
    nom_courrier = fields.Char('Nom courrier')
    initiateur = fields.Many2one("res.users", string="Initiateur")
    # fields of réception dossier demande d'agreement par le sécrétariat
    date_reception_secretariat = fields.Date("Date de réception Sécretariat", default=fields.Date.today)
    numero_identification_secretariat = fields.Char("N° d'identification")

    # fields of réception complément dossier par le service courrier
    type_courrier_complément_dossier_id = fields.Many2one('sig.tresor.type.courrier', 'Type courrier')
    date_reception_complement_dossier = fields.Date("Date de réception", default=fields.Date.today)
    numero_identification_complement_dossier = fields.Char("N° d'identification")
    complement_dossier = fields.Binary("Joindre le courrier")
    nom_complement_dossier = fields.Char('Nom courrier')

    # fields of réception complément dossier  d'agreement par le sécrétariat
    date_reception_secretariat_complement_dossier = fields.Date("Date de réception Sécretariat", default=fields.Date.today)
    numero_identification_secretariat_complement_dossier = fields.Char("N° d'identification")

    # fields of réception courrier bceao par le service courrier
    type_courrier_courrier_bceao_id = fields.Many2one('sig.tresor.type.courrier', 'Type courrier')
    date_reception_courrier_bceao = fields.Date("Date de réception", default=fields.Date.today)
    numero_identification_courrier_bceao = fields.Char("N° d'identification")
    courrier_bceao = fields.Binary("Joindre le courrier")
    nom_courrier_bceao = fields.Char('Nom courrier')

    # fields of réception courrier bceao par le sécrétariat
    date_reception_secretariat_courrier_bceao = fields.Date("Date de réception Sécretariat", default=fields.Date.today)
    numero_identification_secretariat_courrier_bceao = fields.Char("N° d'identification")

    # fields of imputation dossier demande d'agreement à un agent par son chef de service SAE
    assigne_a = fields.Many2one("res.users", string="Imputer à",
                                domain=lambda self: [
                                    ("groups_id", "=", self.env.ref("sig_tresor.autorisation_exercer_group").id)],
                                states={'imput_dossier_au_chief_sae': [('required', True)]})
    courrier_id = fields.Many2one("res.users")
    secretariat_id = fields.Many2one("res.users")
    directrice_id = fields.Many2one("res.users")
    sda_id = fields.Many2one("res.users")
    chef_sae_id = fields.Many2one("res.users")
    agent_sae_id = fields.Many2one("res.users")
    instruction_directrice = fields.Text("Instruction")

    # field to follow progress of workflow agreement,  will be updated automatically
    etape = fields.Selection([('recep_enr_dossier', 'Réception et enregistrement du dossier'),
                              ('etude_forme', 'Etude de forme du dossier'),
                              ('etude_fond', 'Etude de fond du dossier'),
                              ('saisine_bceao', 'Saisine de la BCEAO')],
                             string="Étape", default='recep_enr_dossier')

    # field to follow progress of workflow agreement reception courrier,  will be updated automatically
    state = fields.Selection([('draft', 'Courrier'),
                              ('enr_dossier', 'Sécretariat'),
                              ('trans_dossier_a_directrice', 'Direction'),
                              ('imput_dossier_au_sda', 'SDA'),
                              ('imput_dossier_au_chief_sae',
                               'Chef du Service SAE'),
                              ('imput_dossier_a_agent_sae',
                               'Agent du Service SAE')],
                             string="État", default='draft')

    user = fields.Many2one('res.users', 'Utilisateur courant', default=lambda self: self.env.user)
    verif_conformite_dossier_id = fields.Many2one("sig.tresor.verif.conformite.dossier", "Vérif. conformite dossier")
    # verif_conformite_dossier_ids = fields.One2many("sig.tresor.verif.conformite.dossier", 'reception_courrier_id', "Vérif. conformite dossier")
    etude_fond_dossier_id = fields.Many2one("sig.tresor.etude.fond.dossier", "Etude de fond du dossier")
    saisine_bceao_id = fields.Many2one("sig.tresor.saisine.bceao", "Saisine de la BCEAO")
    email_next_validate = fields.Char("Email prochaine validation")
    name_next_validate = fields.Char("Nom prochaine validation")

        
    def action_draft(self):
        self.state = 'draft'

        
    def action_enr_dossier(self):
        self.state = 'enr_dossier'
        self.initiateur = self.env.user.id  # initiateur
        self.courrier_id = self.env.user.id
        self._write_courrier()
        self.get_numero_identification_courrier()
        # envoi mail au service secretariat
        group_id = self.env.ref('sig_tresor.secretariat_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_recep_enr_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")
            self.write({'state': 'enr_dossier', 'initiateur': self.env.user.id, 'courrier_id': self.env.user.id})

        # uploader courrier transmis par le demandeur dans alfresco
        if self.etape == 'recep_enr_dossier':
            self._upload_file_to_alfresco(self.nom_courrier, self.courrier)
        if self.etape == 'etude_forme':
            self._upload_file_to_alfresco(self.nom_complement_dossier, self.complement_dossier)
        if self.etape == 'etude_fond':
            self._upload_file_to_alfresco(self.nom_courrier_bceao, self.courrier_bceao)

        
    def action_trans_dossier_a_directrice(self):
        self.state = 'trans_dossier_a_directrice'
        self.secretariat_id = self.env.user.id
        self.instruction_directrice = ''
        group_id = self.env.ref('sig_tresor.direction_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_recep_enr_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

        
    def action_imput_dossier_au_sda(self):
        self.state = 'imput_dossier_au_sda'
        self.directrice_id = self.env.user.id
        group_id = self.env.ref('sig_tresor.sous_direction_agrement_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_recep_enr_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

        
    def action_imput_dossier_au_chief_sae(self):
        self.state = 'imput_dossier_au_chief_sae'
        self.sda_id = self.env.user.id
        self.get_chef_sae()
        group_id = self.env.ref('sig_tresor.autorisation_exercer_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_recep_enr_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

        
    def action_imput_dossier_a_agent_sae(self):
        self.state = 'imput_dossier_a_agent_sae'
        self.chef_sae_id = self.env.user.id
        self.agent_sae_id = self.assigne_a
        if self.etape == 'recep_enr_dossier':
            self.verif_conformite_dossier_id.create({'reception_courrier_id': self.id, 'description': self.description, 'assigne_a': self.agent_sae_id.id})
        if self.etape == 'etude_forme':
            browsed_verif_conformite_dossier = self.env['sig.tresor.verif.conformite.dossier'].browse(
                self.verif_conformite_dossier_id)  # récupère l'objet en fonction de l'id
            print('verif_conformite_dossier %s ' % browsed_verif_conformite_dossier)
            if browsed_verif_conformite_dossier:  # if l'objet trouvé, on fait la mise à jour de state et étape
                updated_verif_conformite_dossier = self.env['sig.tresor.verif.conformite.dossier'].write(
                    {'assigne_a': self.assigne_a})
                print('upadted verif_conformite_dossier %s ' % updated_verif_conformite_dossier)
        if self.etape == 'etude_fond':
            browsed_etude_fond_dossier = self.env['sig.tresor.etude.fond.dossier'].browse(
                self.etude_fond_dossier_id)  # récupère l'objet en fonction de l'id
            print('etude_fond_dossier %s ' % browsed_etude_fond_dossier)
            if browsed_etude_fond_dossier:  # if l'objet trouvé, on fait la mise à jour de state et étape
                updated_etude_fond_dossier = self.env['sig.tresor.etude.fond.dossier'].write(
                    {'assigne_a': self.assigne_a})
                print('upadted etude_fond_dossier %s ' % updated_etude_fond_dossier)

        self.get_email_agent_sae(self.assigne_a)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_recep_enr_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")


    #     
    # def action_cancelled(self):
    #     self.state = 'cancelled'

    def _compute_content(self):
        for record in self:
            record.nom_courrier = record._get_content()

    def _get_content(self):
        self.ensure_one()
        self.check_access('read', raise_exception=True)
        return self.reference.sudo().content() if self.reference else None

        
    def _write_courrier(self):
        print('OK')
        self.state = 'enr_dossier'
        self.initiateur = self.env.user.id  # initiateur
        self.courrier_id = self.env.user.id
        print(self.state)
        print(self.initiateur)
        print(self.courrier_id)

       
    def _upload_file_to_alfresco(self, fname, f):
        """
        Upload file to alfresco
        :param fname:
        :param f:
        :return:
        """
        path = 'B100 REGLEMENTATIONS DES SYSTEMES FINANCIERS DECENTRALISES/B110 Dossiers de demande d’agrément/TEST'
        cmis_obj = self.env['cmis.backend']
        # récupérer chemin
        # fpath = os.path.join(os.path.dirname(os.path.abspath(__file__))) + "\\" + fname
        root = os.path.dirname(os.path.abspath(__file__))
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/docs/' + fname)
        print("root %s" % root)
        print("path %s" % fpath)
        try:
            # récupérer le type de contenu du doc uploadé
            ftype = mimetypes.MimeTypes().guess_type(fname)[0]
            if ftype:
                print('type %s ' % ftype)
                index_content = ftype.split('/')[-1]
                print("index content %s " % index_content)
            # créer le doc en local et ecrire le contenu du fichier binary ulplodé
            with open(fpath, 'wb+') as file:
                file.write(base64.b64decode(f))
                file.close()
        except (IOError, OSError):
                _logger.info("_file_write writing %s", fpath, exc_info=True)

        # récupérer le contenu du fichier
        try:
            # fcontent = base64.b64decode(open(fpath, 'rb').read())
            # fcontent = open(fpath, 'rb')
            fsize = os.path.getsize(fpath)
            fencoding = "'ISO-8859-1'"
            # fencoding = "'ascii'"
            # fencoding = "'utf-8'"
            fcontent = open(fpath, 'r', encoding=fencoding, errors="ignore")  # , encoding=fencoding latin-1
            # with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            #     fcontent = f.read()

            print("fencoding %s" % fencoding)
            print("content \n %s" % fcontent)
            print("size %s" % fsize)

            if fsize > 0:
                idcontent = cmis_obj.browse(1).check_directory_of_write_new(path, fname, fcontent, ftype,
                                                                            fencoding)  # 'utf-8'
                print("idcontent %s " % idcontent)
        except (IOError, OSError):
            _logger.info("_read_file reading %s", fpath, exc_info=True)

    # Just use the ORM layer for those simple queries. There are some easy methods for this
    # (e.g. for typical CRUD-> create, read, update, delete):
    #
    # Create -> create(vals)
    #
    # # creates a user in db and
    # # returns this user as python object (RecordSet)
    # created_user = self.env['res.users'].create({'name': 'New User'})

    # Browse -> browse(list_of_ids)
    #
    # # reads the whole database rows and
    # # returns python objects (RecordSet)
    # browsed_users = self.env['res.users'].browse([1,2])

    # Search -> search(domain)
    #
    # # search database with Odoo's domain syntax
    # # returns python objects if something were found
    # domain = [('name', '=', 'New User')]
    # searched_users = self.env['res.users'].search(domain)

