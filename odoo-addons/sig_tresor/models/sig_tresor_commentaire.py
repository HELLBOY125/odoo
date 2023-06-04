# -*- coding:utf-8 -*-

from odoo import models, fields


class SigTresorCommentaire(models.Model):
    _name = 'sig.tresor.commentaire'
    _description = 'Commentaire'

    commentaire = fields.Text('Commentaire', required=True)