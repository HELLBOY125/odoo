# -*- coding:utf-8 -*-
import datetime

from odoo import fields, models, api , _
from odoo.exceptions import UserError


class SigTresorEtudeFondDossier(models.Model):
    _name = 'sig.tresor.etude.fond.dossier'
    _inherit = ['mail.thread']  # , 'ir.needaction_mixin'
    _description = 'étude de fond du dossier workflow de demande d\'agrément'
    _order = 'create_date desc'

    # def __init__(self):
    #     self.assigne_a = self.reception_courrier_id

    # recuperer l'id du group autorisation_exercer_group
          
    def get_group_id_autorisation_exercer(self):
        return self.env.ref('sig_tresor.autorisation_exercer_group').id

    # recuperer len() chef ModuleNotFoundError service d'autorisation d'exercer
          
    def get_chef_sae(self):
        group_id = self.get_group_id_autorisation_exercer()
        print('group_id >>> %s ', group_id)
        query = 'SELECT g.uid, p.name FROM res_groups_users_rel AS g INNER JOIN res_users u ON g.uid=u.id INNER JOIN res_partner AS p ON u.partner_id=p.id INNER JOIN hr_employee AS e ON e.user_id=u.id  WHERE g.gid = %s AND  e.id IN (SELECT manager_id FROM hr_department)'
        self.env.cr.execute(query, (group_id,))
        user_id = self.env.cr.fetchone()
        print('user_id >>> %s ', user_id)
        return user_id

    def get_numero_identification_courrier(self):
        seq_id = 'sig.tresor.etude.fond.dossier'
        # génerer numéro note de transmission et de synthèse
        code = self.env['ir.sequence'].next_by_code(seq_id)
        self.numero_note_trans_synt_avis = code
        # génerer numéro note de transmission 1
        code = self.env['ir.sequence'].next_by_code(seq_id)
        self.note_trans_bceao_1 = code
        # génerer numéro note de transmission 2
        code = self.env['ir.sequence'].next_by_code(seq_id)
        self.note_trans_bceao_2 = code

          
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
                                                 ("verif_conformite_dossier_id", "!=",
                                                 False)])  # odoo NULL= False , , ondelete='cascade'
    assigne_a = fields.Many2one("res.users", string="Imputer à",
                                domain=lambda self: [
                                    ("groups_id", "=", self.env.ref("sig_tresor.autorisation_exercer_group").id)],
                                states={'etude_fond': [
                                    ('required', True)]})

    courrier_id = fields.Many2one("res.users")
    secretariat_id = fields.Many2one("res.users")
    directrice_id = fields.Many2one("res.users")
    sda_id = fields.Many2one("res.users")
    chef_sae_id = fields.Many2one("res.users")
    agent_sae_id = fields.Many2one("res.users")

    # field to follow progress of workflow agreement etude de fond dossier,  will be updated automatically
    state = fields.Selection([('draft', 'Etude de fond'),
                              ('etude_fond', 'Agent du Service SAE'),
                              ('redac_trans_courrier_au_chief_sae',
                               'Chef du Service SAE'),
                              ('trans_courrier_au_sda', 'SDA'),
                              ('trans_courrier_au_directeur',
                               'Directrice'),
                              ('imput_courrier_au_secretariat',
                               'Sécretariat'),
                              ('num_trans_au_service_courrier',
                               'Courrier'),
                              ('trans_courrier_a_bceao_ou_demandeur',
                               'Terminé')],
                             string="État", default='draft')

    # fields of step approval checking conformity folder agreement request
    res_etude_fond_dossier = fields.Selection([
        ('oui', 'Oui'),
        ('non', 'Non')],
        string="Résultats Satisfaisants ?", default='non')

    type_courrier_id = fields.Many2one('sig.tresor.type.courrier', 'Type Courrier',
                                       states={'num_trans_au_service_courrier': [('required', True)]})

    # fields of step redaction et transmission note de transmission, synthèse et de l'avis au chef sae par l'agent sae si resultats satisfaisants
    note_trans_synt_avis = fields.Binary("Note de présentation")
    note_trans_bceao_1 = fields.Binary("Note transmission 1")
    note_trans_bceao_2 = fields.Binary("Note transmission 2")

    date_trans_note_trans_synt_avis = fields.Date("Date transmission",
                                                  default=fields.Date.today)
    date_accuse_reception_note_trans_synt_avis_agent_sae = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission note de trans., de synthèse et d'avis au sda par le chef sae si resultats satisfaisants
    date_trans_note_trans_synt_avis_par_chef_sae = fields.Date(
        "Date de transmission",
        default=fields.Date.today)
    date_accuse_reception_note_trans_synt_avis_par_chef_sae = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission note de trans., de synthèse et d'avis au directeur par sda si resultats satisfaisants
    date_trans_note_trans_synt_avis_par_sda = fields.Date("Date de transmission",
                                                          default=fields.Date.today)
    date_accuse_reception_note_trans_synt_avis_par_sda = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet récépissé au sécretariat par directrice si dossier conforme
    date_trans_note_trans_synt_avis_par_directrice = fields.Date("Date de transmission",
                                                             default=fields.Date.today)
    date_accuse_reception_note_trans_synt_avis_par_directrice = fields.Date("Date d'accusé de réception",
                                                                        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step numérotation et transmission note trans au courrier par le secretariat si resultats satisfaisants
    date_reception_note_trans_bceao = fields.Date("Date de transmission", default=fields.Date.today)
    numero_note_trans_synt_avis = fields.Char("N° note présentation")
    numero_note_trans_bceao_1 = fields.Char("N° note transmission 1")
    numero_note_trans_bceao_2 = fields.Char("N° note transmission 2")

    # fields of step transmission du récépissé au courrier par le courrier si resultats satisfaisants
    date_reception_dossier_bceao = fields.Date("Date de réception", default=fields.Date.today)
    date_trans_dossier_bceao = fields.Date("Date de transmission", default=fields.Date.today)

    # fields of step transmission projet de courrier de notif. de non conformité au chef sae si resultats satisfaisants non
    projet_courrier_notif_non_conformite = fields.Binary("Joindre projet de courrier de notification non-conformité")
    date_trans_projet_courrier_notif_non_conformite = fields.Date(
        "Date transmission projet de courrier de notification non-conformité", default=fields.Date.today)
    date_accuse_projet_courrier_notif_non_conformite_par_agent_sae = fields.Date(
        "Date d'accusé de réception projet de courrier de notification non-conformité", default=fields.Date.today)

    # fields of step transmission projet récépissé au sda par le chef sae si resultats satisfaisants non
    date_trans_projet_courrier_notif_non_conformite_par_chef_sae = fields.Date(
        "Date de transmission projet de courrier de notification non-conformité",
        default=fields.Date.today)
    date_accuse_projet_courrier_notif_non_conformite_par_chef_sae = fields.Date(
        "Date d'accusé de réception projet de courrier de notification non-conformité",
        default=fields.Date.today)

    # fields of step transmission projet récépissé au directeur par sda si resultats satisfaisants non
    date_trans_projet_courrier_notif_non_conformite_par_sda = fields.Date(
        "Date de transmission du projet de courrier de notification non-conformité",
        default=fields.Date.today)
    date_accuse_projet_courrier_notif_non_conformite_par_sda = fields.Date(
        "Date d'accusé de réception projet de courrier de notification non-conformité",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission note d'observation au service courrier par le secretariat
    # si resultats satisfaisants non
    date_reception_note_observation = fields.Date(
        "Date réception note d'observation", default=fields.Date.today)
    numero_note_observation = fields.Char(
        "Numéro d'identification note d'observation", default=fields.Date.today)

    # fields of step transmission note d'observation au demandeur par le service courrier
    # si resultats satisfaisants non
    date_notif_note_observation_au_demandeur = fields.Date(
        "Date de notification note d'observation", default=fields.Date.today)
    date_reponse_note_observation_du_demandeur = fields.Date(
        "Date de réponse de la note d'observation")  # , default=(datetime.datetime.now().date() + datetime.timedelta(days=30))
    note_observation = fields.Binary("Joindre la note d'observation")

    # others fields
    is_show_no_rccm = fields.Boolean(string="Masquer RCCM")
    is_show_traitement_etude_fond = fields.Boolean(string="Resultats satisfaisants ou non", default=False)
    is_show_traitement_etude_fond_ok = fields.Boolean(string="Resultats satisfaisants", default=False)
    is_show_traitement_etude_fond_nok = fields.Boolean(string="Resultats non satisfaisants", default=False)
    email_next_validate = fields.Char("Email prochaine validation")
    name_next_validate = fields.Char("Nom prochaine validation")

    # hide or show number rccm by legal_form_id
    @api.onchange('legal_form_id')
    def onchange_legal_form_id(self):
        if self.legal_form_id.is_required_no_rccm:
            self.is_show_no_rccm = True
        else:
            self.is_show_no_rccm = False

    @api.onchange('reception_courrier_id')
    def onchange_reception_courrier_id(self):
        print("assigne a : %s" % self.reception_courrier_id.assigne_a.id)
        print("user logged : %s" % self.env.user.id)
        self.assigne_a = self.reception_courrier_id.assigne_a
        if self.reception_courrier_id:
            if self.reception_courrier_id.assigne_a.id != self.env.user.id:
                raise UserError(_("Vous n'êtes pas autorisé à exécuter cette tâche!"))

          
    def action_draft(self):
        self.state = 'draft'

          
    def action_etude_fond_oui(self):
        self.state = 'etude_fond'
        self.agent_sae_id = self.env.user.id
        self.assigne_a = self.env.user.id
        self.res_etude_fond_dossier = 'oui'
        self.is_show_traitement_etude_fond_ok = True
        self.is_show_traitement_etude_fond_nok = False
        self.is_show_traitement_etude_fond = True
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.etude_de_fond_dossier_au_demandeur_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("reponse envoi mail %s" % response)
            self.write({'state': 'etude_fond', 'agent_sae_id': self.env.user.id, 'assigne_a': self.env.user.id,
                        'res_etude_fond_dossier': 'oui'}) # on modifie l'état du processus'

          
    def action_etude_fond_non(self):
        self.state = 'etude_fond'
        self.agent_sae_id = self.env.user.id
        self.assigne_a = self.env.user.id
        self.res_etude_fond_dossier = 'non'
        self.is_show_traitement_etude_fond_nok = True
        self.is_show_traitement_etude_fond_ok = False
        self.is_show_traitement_etude_fond = True
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.etude_de_fond_dossier_au_demandeur_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("reponse envoi mail %s" % response)
            self.write({'state': 'etude_fond', 'agent_sae_id': self.env.user.id, 'assigne_a': self.env.user.id, 'res_etude_fond_dossier': 'non'})  # on modifie l'état du processus'

          
    def action_redac_trans_courrier_au_chief_sae(self):
        self.state = 'redac_trans_courrier_au_chief_sae'
        self.agent_sae_id = self.env.user.id
        # envoi mail notif
        group_id = self.env.ref('sig_tresor.autorisation_exercer_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_etude_fond_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            self.assigne_a = self.get_chef_sae()
            self.chef_sae_id = self.assigne_a
            print("Notification envoyeé avec succès!!!")

          
    def action_trans_courrier_au_sda(self):
        self.state = 'trans_courrier_au_sda'
        self.chef_sae_id = self.env.user.id
        group_id = self.env.ref('sig_tresor.sous_direction_agrement_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_etude_fond_dossier_notif')
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
        template = self.env.ref('sig_tresor.next_validator_etude_fond_dossier_notif')
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
        template = self.env.ref('sig_tresor.next_validator_etude_fond_dossier_notif')
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
        template = self.env.ref('sig_tresor.next_validator_etude_fond_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

          
    def action_trans_courrier_a_bceao_ou_demandeur(self):
        self.state = 'trans_courrier_a_bceao_ou_demandeur'
        self.courrier_id = self.env.user.id
        # si résultats non staisfaisants, le demandeur va repondre avec un courrier, par conséquent
        # le processus ira à létape jusqu'à l'transmission du chef sae à un agent
        #  pour revenir à l'étape de l'étude de fond du dossier à nouveau
        if self.res_etude_fond_dossier == 'non':
            self.reception_courrier_id.state = 'draft'
            # self.state = 'draft'
            self.date_reponse_note_observation_du_demandeur = (
                    datetime.datetime.strptime(str(self.date_notif_note_observation_au_demandeur),
                                               '%Y-%m-%d') + datetime.timedelta(days=30)).strftime('%Y-%m-%d')

            self.reception_courrier_id.etude_fond_dossier_id = self.id
            # dans les 2 cas, y'aura un courrier entrant'
            self.reception_courrier_id.etape = 'etude_fond'
            browsed_reception_courrier = self.env['sig.tresor.reception.courrier'].browse(
                self.reception_courrier_id)  # récupère l'objet reception courrier en fonction de l'id
            print('reception courrier %s ' % browsed_reception_courrier)
            if browsed_reception_courrier:  # if reception courrier trouvé, on fait la mise à jour de state et étape
                updated_reception_courrier = self.env['sig.tresor.reception.courrier'].write(
                    {'state': 'draft', 'etape': 'etude_fond'})
        else:
            print("id %s", self.id)
            print("id 2 %s", self.ids[0])
            self.reception_courrier_id.etude_fond_dossier_id = self.id
            self.reception_courrier_id.state = 'draft'
            # self.state = 'draft'
        # dans les 2 cas, y'aura un courrier entrant'
        self.reception_courrier_id.etape = 'etude_fond'
        browsed_reception_courrier = self.env['sig.tresor.reception.courrier'].browse(
            self.reception_courrier_id)  # récupère l'objet reception courrier en fonction de l'id
        print('reception courrier %s ' % browsed_reception_courrier)
        if browsed_reception_courrier:  # if reception courrier trouvé, on fait la mise à jour de state et étape
            updated_reception_courrier = self.env['sig.tresor.reception.courrier'].write(
                {'state': 'draft', 'etape': 'etude_fond'})

        # enregistrer pour l'étape de la saisine de la BCEAO
        self.reception_courrier_id.saisine_bceao_id.create(
            {'reception_courrier_id': self.reception_courrier_id.id,
             'description': self.reception_courrier_id.description,
             'assigne_a': self.agent_sae_id.id})

        # uploader la note de transmission 1 & 2 et présentation et synthèse également dans alfresco

          
    def action_retour(self):
        if self.env.user.has_group('sig_tresor.autorisation_exercer_group'):
            # if self.env.user.id == self.get_chef_sae():
            self.state = 'etude_fond'
        if self.env.user.has_group('sig_tresor.sous_direction_agrement_group'):
            self.state = 'redac_trans_courrier_au_chief_sae'
        if self.env.user.has_group('sig_tresor.direction_group'):
            self.state = 'trans_courrier_au_sda'

    #       
    # def action_cancelled(self):
    #     self.state = 'cancelled'
