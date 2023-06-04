# -*- coding:utf-8 -*-
#from PIL.PdfParser import check_format_condition


from odoo import fields, models, api, exceptions
from odoo.exceptions import UserError
from odoo.tools.translate import _


class SigTresorSaisineBceao(models.Model):
    _name = 'sig.tresor.saisine.bceao'
    _inherit = ['mail.thread']  # , 'ir.needaction_mixin'
    _description = 'saisine de la bceao workflow de demande d\'agrément'
    _order = 'create_date desc'

    # def __init__(self):
    #     self.assigne_a = self.reception_courrier_id.etude_fond_dossier_id.assigne_a
    #     print("assigne a : %s", self.assigne_a)

    # recuperer l'id du group autorisation_exercer_group

    def get_group_id_autorisation_exercer(self):
        return self.env.ref('sig_tresor.autorisation_exercer_group').id

    # recuperer le chef service d'autorisation d'exercer

    def get_chef_sae(self):
        group_id = self.get_group_id_autorisation_exercer()
        print('group_id >>> %s ', group_id)
        query = 'SELECT g.uid, p.name FROM res_groups_users_rel AS g INNER JOIN res_users u ON g.uid=u.id INNER JOIN res_partner AS p ON u.partner_id=p.id INNER JOIN hr_employee AS e ON e.user_id=u.id  WHERE g.gid = %s AND  e.id IN (SELECT manager_id FROM hr_department)'
        self.env.cr.execute(query, (group_id,))
        user_id = self.env.cr.fetchone()
        print('user_id >>> %s ', user_id)
        return user_id

    
    def get_numero_identification_courrier(self):
        seq_id = 'sig.tresor.saisine.bceao'
        code = self.env['ir.sequence'].next_by_code(seq_id)
        print('code >> %s ' % code)
        if self.res_saisine_bceao == 'oui':
            self.numero_arrete_portant_agrement = code
        else:
            self.numero_courrier_notif_rejet = code
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
                                                ("verif_conformite_dossier_id", "!=",
                                                 False)])  # odoo NULL= False , , ondelete='cascade'
    assigne_a = fields.Many2one("res.users", string="Imputer à",
                                domain=lambda self: [
                                    ("groups_id", "=", self.env.ref("sig_tresor.autorisation_exercer_group").id)],
                                states={'avis_bceao': [
                                    ('required', True)]})
    directrice_id = fields.Many2one("res.users")
    courrier_id = fields.Many2one("res.users")
    secretariat_id = fields.Many2one("res.users")
    sda_id = fields.Many2one("res.users")
    chef_sae_id = fields.Many2one("res.users")
    agent_sae_id = fields.Many2one("res.users")

    # field to follow progress of workflow agreement etude de fond dossier,  will be updated automatically
    state = fields.Selection([('draft', 'Avis de la BCEAO'),
                              ('avis_bceao', 'Agent du Service SAE'),
                              ('redac_trans_courrier_au_chief_sae',
                               'Chef du Service SAE'),
                              ('trans_courrier_au_sda', 'SDA'),
                              ('trans_courrier_au_directeur',
                               'Directrice'),
                              ('imput_courrier_au_secretariat',
                               'Sécretariat'),
                              ('num_trans_au_service_courrier',
                               'Courrier'),
                              ('recep_notif_au_sda',
                               'Notifier SDA'),
                              ('notif_arrete_au_demandeur',
                               'Notifier SFD (SDA)'),
                              ('recep_trans_courrier_notif_au_demandeur',
                               'Terminé')],
                             string="État", default='draft')

    type_courrier_id = fields.Many2one('sig.tresor.type.courrier', 'Type Courrier',
                                       states={'num_trans_au_service_courrier': [('required', True)]})

    # fields of step saisine de la bceao
    res_saisine_bceao = fields.Selection([
        ('oui', 'Oui'),
        ('non', 'Non')],
        string="Avis conforme favorable ?", default='non')
    date_reception_courrier_bceao = fields.Date(
        "Date de réception",
        default=fields.Date.today)
    date_retour_bceao = fields.Date("Retour  BCEAO",
                                    default=fields.Date.today)
    courrier_bceao = fields.Binary("Courrier BCEAO")

    # fields of step redaction et transmission d’un projet arrêté et une note de présentation  au chef sae par l'agent sae si avis favorable conforme
    projet_arrete = fields.Binary("Projet d'arrêté")
    date_trans_projet_arrete = fields.Date("Date transmission", default=fields.Date.today)
    date_accuse_reception_projet_arrete = fields.Date("Date d'accusé de réception",
                                                      default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet arrêté au sda par le chef sae si avis favorable conforme
    date_trans_projet_arrete_par_chef_sae = fields.Date("Date de transmission",
                                                        default=fields.Date.today)
    date_accuse_reception_projet_arrete_par_chef_sae = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet arrêté au directeur par sda si avis favorable conforme
    date_trans_projet_arrete_par_sda = fields.Date("Date de transmission",
                                                   default=fields.Date.today)
    date_accuse_reception_projet_arrete_par_sda = fields.Date("Date d'accusé de réception",
                                                              default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet de courrier de notif de rejet au secretariat par directrice si avis favorable conforme
    date_trans_projet_arrete_par_directrice = fields.Date(
        "Date de transmission",
        default=fields.Date.today)
    date_accuse_reception_projet_arrete_par_directrice = fields.Date(
        "Date d'accusé de réception",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step numérotation et transmission de l'arrêté portant agrément au courrier par le secretariat si avis favorable conforme
    date_reception_arrete_portant_agrement = fields.Date("Date de réception",
                                                         default=fields.Date.today)
    numero_arrete_portant_agrement = fields.Char("N° d'identification")

    # fields of step transmission de l'arrêté portant agrément au sda par le courrier si avis favorable conforme
    date_reception_arrete_portant_agrement_par_courrier = fields.Date("Date de réception",
                                                                      default=fields.Date.today)

    # fields of step transmission de l'arrêté portant agrément au promoteur par le sda si avis favorable conforme
    date_notif_arrete_au_promoteur = fields.Date("Date de notif.",
                                                 default=fields.Date.today)#date début des activités
    arrete_portant_agrement = fields.Binary("Arrêté portant agrément")
    dossier_complet_num_agrement = fields.Binary("Joindre le dossier complet")
    date_sign_arrete_au_promoteur = fields.Date("Date de sign. arrêté",
                                                default=fields.Date.today)#date arrêté

    # fields of step transmission projet de courrier de notif. de rejet au chef sae si avis favorable conforme non
    projet_courrier_notif_rejet = fields.Binary("Joindre projet notif. de rejet")
    date_trans_projet_courrier_notif_rejet = fields.Date(
        "Date transmission projet notif. de rejet", default=fields.Date.today)
    date_accuse_projet_courrier_notif_rejet_par_agent_sae = fields.Date(
        "Date d'accusé de réception projet notif. de rejet", default=fields.Date.today)

    # fields of step transmission projet de courrier de notif de rejet au sda par le chef sae si avis favorable conforme non
    date_trans_projet_courrier_notif_rejet_par_chef_sae = fields.Date(
        "Date de transmission projet notif. de rejet",
        default=fields.Date.today)
    date_accuse_projet_courrier_notif_rejet_par_chef_sae = fields.Date(
        "Date d'accusé de réception projet notif. de rejet",
        default=fields.Date.today)

    # fields of step transmission projet de courrier de notif de rejet au directeur par sda si avis favorable conforme non
    date_trans_projet_courrier_notif_rejet_par_sda = fields.Date(
        "Date de transmission du projet notif. de rejet",
        default=fields.Date.today)
    date_accuse_projet_courrier_notif_rejet_par_sda = fields.Date(
        "Date d'accusé de réception projet notif. de rejet",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission projet de courrier de notif de rejet au secretariat par directrice si avis favorable conforme non
    date_trans_projet_courrier_notif_rejet_par_directrice = fields.Date(
        "Date de transmission du projet notif. de rejet",
        default=fields.Date.today)
    date_accuse_projet_courrier_notif_rejet_par_directrice= fields.Date(
        "Date d'accusé de réception projet notif. de rejet",
        default=fields.Date.today)  # mettre un bouton reçu à l'étape suivante pour mettre ce champ à jour, pareil pour touts les autres champs du genre

    # fields of step transmission du courrier de notif au service courrier par le secretariat
    # si avis favorable conforme non
    date_reception_courrier_notif_rejet = fields.Date(
        "Date réception du courrier de notif. de rejet", default=fields.Date.today)
    numero_courrier_notif_rejet = fields.Char(
        "N° d'identification courrier de notif. de rejet", default=fields.Date.today)

    # fields of step transmission note d'observation au demandeur par le service courrier
    # si avis favorable conforme non
    date_notif_courrier_notif_rejet_au_demandeur = fields.Date(
        "Date de notif.", default=fields.Date.today)
    courrier_notif_rejet = fields.Binary("Joindre le courrier de notif. de rejet")

    # others fields
    is_show_traitement_saisine_bceao_ok = fields.Boolean(string="Avis conforme favorable", default=False)
    is_show_traitement_saisine_bceao_nok = fields.Boolean(string="Avis conforme défavorable", default=False)

    email_next_validate = fields.Char("Email prochaine validation")
    name_next_validate = fields.Char("Nom prochaine validation")

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

         
    def action_avis_bceao_oui(self):
        self.state = 'avis_bceao'
        self.agent_sae_id = self.env.user.id
        self.assigne_a = self.env.user.id
        self.res_saisine_bceao = 'oui'
        self.is_show_traitement_saisine_bceao_ok = True
        self.is_show_traitement_saisine_bceao_nok = False
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.saisine_bceao_au_demandeur_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("reponse envoi mail %s" % response)
            self.write({'state': 'avis_bceao'})  # on modifie l'état du processus'

         
    def action_avis_bceao_non(self):
        self.state = 'avis_bceao'
        self.agent_sae_id = self.env.user.id
        self.assigne_a = self.env.user.id
        self.res_saisine_bceao = 'non'
        self.is_show_traitement_saisine_bceao_nok = True
        self.is_show_traitement_saisine_bceao_ok = False
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.saisine_bceao_au_demandeur_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("reponse envoi mail %s" % response)
            self.write({'state': 'avis_bceao'})  # on modifie l'état du processus'

         
    def action_redac_trans_courrier_au_chief_sae(self):
        self.state = 'redac_trans_courrier_au_chief_sae'
        self.agent_sae_id = self.env.user.id
        # envoi mail notif
        group_id = self.env.ref('sig_tresor.autorisation_exercer_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_saisine_dossier_notif')
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
        template = self.env.ref('sig_tresor.next_validator_saisine_dossier_notif')
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
        template = self.env.ref('sig_tresor.next_validator_saisine_dossier_notif')
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
        template = self.env.ref('sig_tresor.next_validator_saisine_dossier_notif')
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
        template = self.env.ref('sig_tresor.next_validator_saisine_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

         
    def action_recep_trans_courrier_notif_au_demandeur(self):
        self.state = 'recep_trans_courrier_notif_au_demandeur'
        self.courrier_id = self.env.user.id
        # si avis conforme favorable non, le service courrier transmet le courrier de notif de rejet définitif au demandeur
        if self.res_saisine_bceao == 'non':
            print("id %s", self.id)
            print("id 2 %s", self.ids[0])
            self.reception_courrier_id.saisine_bceao_id = self.id
            # uploader la note de rejet définitif dans alfresco
            # Récupérer le modèle de courrier électronique
            template = self.env.ref('sig_tresor.rejet_agrement_au_demandeur_notif')
            # Envoyer le modèle de courrier électronique
            response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
            if response:
                print("reponse envoi mail %s" % response)

         
    def action_recep_notif_au_sda(self):
        self.state = 'recep_notif_au_sda'
        self.courrier_id = self.env.user.id
        group_id = self.env.ref('sig_tresor.sous_direction_agrement_group').id
        self.get_email_next_validator(group_id)
        # Récupérer le modèle de courrier électronique
        template = self.env.ref('sig_tresor.next_validator_saisine_dossier_notif')
        # Envoyer le modèle de courrier électronique
        response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        if response:
            print("Notification envoyeé avec succès!!!")

         
    def action_notif_arrete_au_demandeur(self):
        self.state = 'notif_arrete_au_demandeur'
        self.sda_id = self.env.user.id
        # si avis conforme favorable, le sda transmet l'arrêté portant agrément au demandeur
        if self.res_saisine_bceao == 'oui':
            print("id %s", self.id)
            print("id 2 %s", self.ids[0])
            self.reception_courrier_id.saisine_bceao_id = self.id
            # uploader l'arrêté portant agrément dans alfresco
            # show message notif
            # return {
            #     'info': {
            #         'title': 'Demande d\'agrément',
            #         'message': 'Agrément accordé avec succès', },
            # }
            # Récupérer le modèle de courrier électronique
            template = self.env.ref('sig_tresor.accord_agrement_au_demandeur_notif')
            # Envoyer le modèle de courrier électronique
            response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
            if response:
                print("reponse envoi mail %s" % response)
                self.write({'state': 'notif_arrete_au_demandeur'})  # on modifie l'état du processus'
        else:
            # uploader la note de rejet définitif dans alfresco
            # Récupérer le modèle de courrier électronique
            template = self.env.ref('sig_tresor.rejet_agrement_au_demandeur_notif')
            # Envoyer le modèle de courrier électronique
            response = self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
            if response:
                print("reponse envoi mail %s" % response)

         
    def action_retour(self):
        if self.env.user.has_group('sig_tresor.autorisation_exercer_group'):
            # if self.env.user.id == self.get_chef_sae():
            self.state = 'avis_bceao'
        if self.env.user.has_group('sig_tresor.sous_direction_agrement_group'):
            self.state = 'redac_trans_courrier_au_chief_sae'
        if self.env.user.has_group('sig_tresor.direction_group'):
            self.state = 'trans_courrier_au_sda'

    #      
    # def action_cancelled(self):
    #     self.state = 'cancelled'
