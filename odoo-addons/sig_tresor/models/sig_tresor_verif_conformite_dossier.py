# -*- coding:utf-8 -*-
import logging
import re

import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class SigTresorVerifConformiteDossier(models.Model):
    _name = 'sig.tresor.verif.conformite.dossier'
    _inherit = ['mail.thread']  # , 'ir.needaction_mixin'
    _description = 'vérif conformite dossier workflow de demande d\'agrément'
    _rec_name = 'description'
    _order = 'create_date desc'

    # def __init__(self):
    #     self.assigne_a = self.reception_courrier_id

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
        print(':::: user_id :::: %s ' % user_id[0])
        self.assigne_a = user_id[0]
        return user_id[0]

          
    def get_numero_identification_courrier(self):
        # methode 1
        # code = self.env['ir.sequence'].get('sig.tresor.verif.conformite.dossier') or '/'
        # print('code >> %s ' % code)
        # methode 2
        seq_id = 'sig.tresor.verif.conformite.dossier'
        code = self.env['ir.sequence'].next_by_code(seq_id)
        print('code >> %s ' % code)
        if self.res_verif_conformite_dossier == 'oui':
            self.numero_recepisse = code
        else:
            self.numero_note_observation = code
        return code

          
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

    description = fields.Text("description")
    reception_courrier_id = fields.Many2one("sig.tresor.reception.courrier", 'Réception du courrier',
                                            domain=lambda self: [
                                                ("verif_conformite_dossier_id", "=",
                                                 False), ("etape", "=",
                                                          "recep_enr_dossier")], states={
            'draft': [('required', True)]})  # odoo NULL= False , , ondelete='cascade'
    assigne_a = fields.Many2one("res.users", string="Imputer à",
                                domain=lambda self: [
                                    ("groups_id", "=", self.env.ref("sig_tresor.autorisation_exercer_group").id)],
                                states={'dossier_conforme': [
                                    ('required', True)]})  # , default=reception_courrier_id.assigne_a

    courrier_id = fields.Many2one("res.users")
    secretariat_id = fields.Many2one("res.users")
    directrice_id = fields.Many2one("res.users")
    sda_id = fields.Many2one("res.users")
    chef_sae_id = fields.Many2one("res.users")
    agent_sae_id = fields.Many2one("res.users")

    # field to follow progress of workflow agreement verif conformite dossier,  will be updated automatically
    state = fields.Selection([('draft', 'Enregistrer SFD'),
                              ('enr_info', 'Etude de forme'),
                              ('dossier_conforme', 'Agent du Service SAE'),
                              ('redac_trans_courrier_au_chief_sae',
                               'Chef de Service SAE'),
                              ('trans_courrier_au_sda', 'SDA'),
                              ('trans_courrier_au_directeur',
                               'Directrice'),
                              ('imput_courrier_au_secretariat',
                               'Sécretariat'),
                              ('num_trans_au_service_courrier',
                               'Courrier'),
                              ('trans_courrier_au_demandeur',
                               'Terminé')],
                             string="État", default='draft')

    # fields of step verif conformité dossier agreement request
    identifiant = fields.Char("Identifiant", states={'draft': [('required', True)]})
    sfd = fields.Char("SFD", states={'draft': [('required', True)]})
    denomination = fields.Char("Dénomination", states={'draft': [('required', True)]})
    legal_form_id = fields.Many2one('sig.tresor.legal.form', 'Forme Juridique',
                                    states={'draft': [('required', True)]})
    mutual_specificity_id = fields.Many2one('sig.tresor.mutual.specificity', 'Spécificité Mutuelle',
                                            states={'draft': [('required', True)]})
    district_id = fields.Many2one('sig.tresor.district', 'District', states={'draft': [('required', True)]})
    region_id = fields.Many2one('sig.tresor.region', 'Région', states={'draft': [('required', True)]})
    departement_id = fields.Many2one('sig.tresor.departement', 'Département', states={'draft': [('required', True)]})
    commune_id = fields.Many2one('sig.tresor.commune', 'Sous-Préfecture/Commune',
                                 states={'draft': [('required', True)]})
    village_id = fields.Many2one('sig.tresor.village',
                                 'Quartier / Village',
                                 states={'draft': [('required', True)]})
    bp = fields.Char("Boite Postale", states={'draft': [('required', True)]})
    mobile = fields.Char("Tél. Portable", states={'draft': [('required', True)]})
    tel = fields.Char("Tél. Fixe", states={'draft': [('required', True)]})
    site_internet = fields.Char("Site internet")
    email = fields.Char("Adresse Email", states={'draft': [('required', True)]})
    no_rccm = fields.Char("N° RCCM", states={'draft': [('readonly', False)]})
    type = fields.Selection([('normal', 'Agrément conventionnel'), ('islamic', 'Finance Islamique')],
                            string="Type d'agrément",
                            default='normal')
    dirigeant_ids = fields.One2many("sig.tresor.dirigeant", 'verif_conformite_dossier_id', "Dirigeant")

    # fields of step approval checking conformity folder agreement request
    res_verif_conformite_dossier = fields.Selection([
        ('oui', 'Oui'),
        ('non', 'Non')],
        string="Dossier Conforme ?", default='non')

    type_courrier_id = fields.Many2one('sig.tresor.type.courrier', 'Type Courrier',
                                       states={'num_trans_au_service_courrier': [('required', True)]})
    # fields of step transmission projet récépissé au chef sae par l'agent sae si dossier conforme
    projet_recepisse = fields.Binary("Projet de récépissé")
    date_trans_projet_recepisse = fields.Date("Date transmission", default=fields.Date.today)
    date_accuse_reception_projet_recepisse_agent_sae = fields.Date("Date d'accusé de réception",
                                                                   default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet récépissé au sda par le chef sae si dossier conforme
    date_trans_projet_recepisse_par_chef_sae = fields.Date("Date de transmission",
                                                           default=fields.Date.today)
    date_accuse_reception_projet_recepisse_par_chef_sae = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet récépissé au directeur par sda si dossier conforme
    date_trans_projet_recepisse_par_sda = fields.Date("Date de transmission",
                                                      default=fields.Date.today)
    date_accuse_reception_projet_recepisse_par_sda = fields.Date("Date d'accusé de réception",
                                                                 default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet récépissé au sécretariat par directrice si dossier conforme
    date_trans_projet_recepisse_par_directrice = fields.Date("Date de transmission",
                                                             default=fields.Date.today)
    date_accuse_reception_projet_recepisse_par_directrice = fields.Date("Date d'accusé de réception",
                                                                        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step numérottation et transmission récépissé au courrier par le secretariat si dossier conforme
    date_entree_processus = fields.Date("Date d'entrée", default=fields.Date.today)
    numero_recepisse = fields.Char("N° d'identification")

    # fields of step transmission du récépissé au courrier par le courrier si dossier conforme
    date_notif_recepisse_au_demandeur = fields.Date("Date de notification",
                                                    default=fields.Date.today)
    recepisse = fields.Binary("Joindre le récépissé")

    # fields of step transmission projet de courrier de notif. de non conformité au chef sae si dossier conforme non
    projet_courrier_notif_non_conformite = fields.Binary("Joindre projet")
    date_trans_projet_courrier_notif_non_conformite = fields.Date(
        "Date transmission", default=fields.Date.today)
    date_accuse_projet_courrier_notif_non_conformite_par_agent_sae = fields.Date(
        "Date d'accusé de réception projet", default=fields.Date.today)

    # fields of step transmission projet de courrier de notif. de non conformité au sda par le chef sae si dossier conforme non
    date_trans_projet_courrier_notif_non_conformite_par_chef_sae = fields.Date(
        "Date de transmission",
        default=fields.Date.today)
    date_accuse_projet_courrier_notif_non_conformite_par_chef_sae = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)

    # fields of step transmission projet de courrier de notif. de non conformité au directeur par sda si dossier conforme non
    date_trans_projet_courrier_notif_non_conformite_par_sda = fields.Date(
        "Date de transmission",
        default=fields.Date.today)
    date_accuse_projet_courrier_notif_non_conformite_par_sda = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet de courrier de notif. de non conformité au sécretariat par directrice si dossier conforme non
    date_trans_projet_courrier_notif_non_conformite_par_dir = fields.Date(
        "Date de transmission",
        default=fields.Date.today)
    date_accuse_projet_courrier_notif_non_conformite_par_dir = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission note d'observation au service courrier par le secretariat
    # si dossier conforme non
    date_reception_note_observation = fields.Date(
        "Date réception", default=fields.Date.today)
    numero_note_observation = fields.Char(
        "N° d'identification")


    # fields of step transmission note d'observation au demandeur par le service courrier
    # si dossier conforme non
    date_notif_note_observation_au_demandeur = fields.Date(
        "Date de notification", default=fields.Date.today)
    date_reponse_note_observation_du_demandeur = fields.Date(
        "Date de réponse")  # , default=(datetime.datetime.now().date() + datetime.timedelta(days=30))
    note_observation = fields.Binary("Note d'observation")

    # others fields
    is_show_no_rccm = fields.Boolean(string="Masquer RCCM")
    is_show_traitement_dossier_conforme = fields.Boolean(string="Dossier Conforme", default=False)
    is_show_traitement_dossier_non_conforme = fields.Boolean(string="Dossier Non Conforme", default=False)
    label_button_oui = fields.Char("OUI")
    label_required = fields.Char("*")
    region_id_ = fields.Integer(store=False)
    email_next_validate = fields.Char("Email prochaine validation")
    name_next_validate = fields.Char("Nom prochaine validation")

    # comment écrire_sql_constraints dans odoo
    # _sql_constraints = [('name_of_field_unique', 'unique(name_of_field)',
    #                      'Error Message')]
    _sql_constraints = [
        ('identifiant_uniq',
         'unique(identifiant)',
         _('L\'identifiant doit être unique!')),
    ]

    # hide or show number rccm by legal_form_id
    @api.onchange('legal_form_id')
    def onchange_legal_form_id(self):
        if self.legal_form_id:
            if self.legal_form_id.is_required_no_rccm:
                self.is_show_no_rccm = True
            else:
                self.is_show_no_rccm = False
            res = {}
            res['domain'] = {'mutual_specificity_id': [('legal_form_id', '=', self.legal_form_id.id)]}
            logging.info('LISTE DES SPECIFICITES MUTUELLES DE LA FORME JURIDIQUE CHOISIE')
            logging.info(res)
            return res

    # charger les régions en fonction du district_id sélectionné
    @api.onchange('district_id')
    def onchange_district_id(self):
        """

        :return:
        """
        if self.district_id:
            res = {}
            res['domain'] = {'region_id': [('district_id', '=', self.district_id.id)]}
            logging.info('LISTE DES REGIONS DU DISTRICT CHOISI')
            logging.info(res)
            return res

    # charger les départements en fonction du region_id sélectionné
    @api.onchange('region_id')
    def onchange_region_id(self):
        if self.region_id:
            self.region_id_ = self.region_id.id
            print("region selected %s" % self.region_id_)
            res = {}
            res['domain'] = {'departement_id': [('region_id', '=', self.region_id.id)]}
            logging.info('LISTE DES DEPARTEMENTS DE LA REGION CHOISIE')
            logging.info(res)
            return res

    # charger les communes en fonction du departement_id sélectionné
    @api.onchange('departement_id')
    def onchange_departement_id(self):
        if self.departement_id:
            res = {}
            res['domain'] = {'commune_id': [('departement_id', '=', self.departement_id.id)]}
            logging.info('LISTE DES COMMUNES DU DEPARTEMENT CHOISI')
            logging.info(res)
            return res

    # charger les villages en fonction du commune_id sélectionné
    @api.onchange('commune_id')
    def onchange_commune_id(self):
        if self.commune_id:
            res = {}
            res['domain'] = {'village_id': [('commune_id', '=', self.commune_id.id)]}
            logging.info('LISTE DES VILLAGES OU QUARTIERS DE LA COMMUNE CHOISIE')
            logging.info(res)
            return res

    @api.onchange('reception_courrier_id')
    def onchange_reception_courrier_id(self):
        print("assigne a : %s" % self.reception_courrier_id.assigne_a.id)
        print("user logged : %s" % self.env.user.id)
        self.assigne_a = self.reception_courrier_id.assigne_a
        if self.reception_courrier_id:
            if self.reception_courrier_id.assigne_a.id != self.env.user.id:
                raise UserError(_("Vous n'êtes pas autorisé à exécuter cette tâche!"))

    # @api.onchange('mobile', 'tel')
    # def onchange_mobile(self):
    #     if self.mobile:
    #         if re.match("^[0-9]\d{10}$", self.mobile) == None:
    #             raise ValidationError("Entrez un numéro de téléphone mobile: %s" % self.mobile)
    #     if self.tel:
    #         if re.match("^[0-9]\d{10}$", self.tel) == None:
    #             raise ValidationError("Entrez un numéro de téléphone fixe: %s" % self.tel)

    @api.onchange('email')
    def onchange_email(self):
        if self.email:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", self.email) == None:
                raise ValidationError("Entez une adresse email valide: %s" % self.email)

          
    def action_draft(self):
        self.state = 'draft'

          
    def action_enr_info(self):
        self.state = 'enr_info'
        self.agent_sae_id = self.env.user.id
        self.assigne_a = self.env.user.id
        # envoyer une notif au demandeur pour lui signaler l'étape de sa demande
        # Find the e-mail template
        template = self.env.ref('sig_tresor.verif_conformite_dossier_au_demandeur_notif')
        # Vous pouvez également trouver le modèle de courrier électronique comme ceci:
        # template = self.env['ir.model.data'].get_object('sig_tresor', 'recep_enr_courrier_dem_agrement_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("reponse envoi mail %s" % response)
            self.write({'state': 'enr_info', 'agent_sae_id': self.env.user.id, 'assigne_a': self.env.user.id })  # on modifie l'état du processus'
        # modid = self.env['ir.model.data'].get_object_reference('sig_tresor', 'sig_tresor_dirigeant_form_view')
        # result = {
        #     'name': "Créer Dirigeant",
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'view_id': modid[1],
        #     'res_model': 'sig.tresor.dirigeant',
        #     'type': 'ir.actions.act_window',
        #     'domain': '[]',
        #     'res_id': self.id,
        #     # 'context': {'active_id': self.id},
        #     'target': 'new',
        # }
        # return result

          
    def action_dossier_conforme_non(self):
        self.state = 'dossier_conforme'
        self.agent_sae_id = self.env.user.id
        self.assigne_a = self.env.user.id
        self.res_verif_conformite_dossier = 'non'
        self.is_show_traitement_dossier_non_conforme = True
        self.is_show_traitement_dossier_conforme = False

          
    def action_dossier_conforme_oui(self):
        self.state = 'dossier_conforme'
        self.agent_sae_id = self.env.user.id
        self.assigne_a = self.env.user.id
        self.res_verif_conformite_dossier = 'oui'
        self.is_show_traitement_dossier_conforme = True
        self.is_show_traitement_dossier_non_conforme = False

          
    def action_redac_trans_courrier_au_chief_sae(self):
        self.state = 'redac_trans_courrier_au_chief_sae'
        self.agent_sae_id = self.env.user.id
        self.get_chef_sae()
        # envoi mail notif
        group_id = self.env.ref('sig_tresor.autorisation_exercer_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_etude_forme_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

          
    def action_trans_courrier_au_sda(self):
        self.state = 'trans_courrier_au_sda'
        self.chef_sae_id = self.env.user.id
        group_id = self.env.ref('sig_tresor.sous_direction_agrement_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_etude_forme_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

          
    def action_trans_courrier_au_directeur(self):
        self.state = 'trans_courrier_au_directeur'
        self.sda_id = self.env.user.id
        group_id = self.env.ref('sig_tresor.direction_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_etude_forme_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

          
    def action_imput_courrier_au_secretariat(self):
        self.state = 'imput_courrier_au_secretariat'
        self.directrice_id = self.env.user.id
        self.get_numero_identification_courrier()
        # envoi mail au service secretariat
        group_id = self.env.ref('sig_tresor.secretariat_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_etude_forme_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

          
    def action_num_trans_au_service_courrier(self):
        self.state = 'num_trans_au_service_courrier'
        self.secretariat_id = self.env.user.id
        # envoi mail au service secretariat
        group_id = self.env.ref('sig_tresor.courrier_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_etude_forme_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

          
    def action_trans_courrier_au_demandeur(self):
        self.state = 'trans_courrier_au_demandeur'
        self.courrier_id = self.env.user.id
        # si dossier non conforme, le demandeur va repondre avec un courrier, par conséquent
        # le processus ira à létape jusqu'à l'imputation du chef sae à un agent
        # pour revenir à l'étape de la vérif. de la conform à nouveau
        if self.res_verif_conformite_dossier == 'non':
            self.reception_courrier_id.state = 'draft'
            self.reception_courrier_id.etape = 'etude_forme'
            browsed_reception_courrier = self.env['sig.tresor.reception.courrier'].browse(
                self.reception_courrier_id)  # récupère l'objet reception courrier en fonction de l'id
            print('reception courrier %s ' % browsed_reception_courrier)
            if browsed_reception_courrier:  # if reception courrier trouvé, on fait la mise à jour de state et étape
                updated_reception_courrier = self.env['sig.tresor.reception.courrier'].write(
                    {'state': 'draft', 'etape': 'etude_forme'})
            if updated_reception_courrier:
                self.state = 'enr_info'
                date = str(self.date_notif_note_observation_au_demandeur)  # convertir la date en string
                self.date_reponse_note_observation_du_demandeur = (
                        datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            # uploader la note d'observation dans alfresco
        else:
            print("id %s", self.id)
            print("id 2 %s", self.ids[0])
            self.reception_courrier_id.verif_conformite_dossier_id = self.id
            # enregistrer pour l'étape de l'étude de fond
            self.reception_courrier_id.etude_fond_dossier_id.create(
                {'reception_courrier_id': self.reception_courrier_id.id, 'description': self.reception_courrier_id.description,
                 'assigne_a': self.agent_sae_id.id})

            # uploader le récépissé dans alfresco

          
    def action_retour(self):
        if self.env.user.has_group('sig_tresor.autorisation_exercer_group'):
            # if self.env.user.id == self.get_chef_sae():
            self.state = 'dossier_conforme'
            self.assigne_a = self.agent_sae_id
        if self.env.user.has_group('sig_tresor.sous_direction_agrement_group'):
            self.state = 'redac_trans_courrier_au_chief_sae'
        if self.env.user.has_group('sig_tresor.direction_group'):
            self.state = 'trans_courrier_au_sda'

    #       
    # def action_cancelled(self):
    #     self.state = 'cancelled'

    def show_sig_tresor_dirigeant_form_view(self):
        print("test show modal form dirigeant ok")
        return {
            'name': ('CréerDirigeant'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sig.tresor.dirigeant',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }