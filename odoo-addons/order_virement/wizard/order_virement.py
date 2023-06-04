# -*- coding: utf-8 -*-
# -$- Dahech Haithem

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import xlwt
import base64
import os
import urllib3
import datetime
from dateutil.parser import parse
import unicodedata

import csv
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat, float_repr


class TbOrder(models.Model):
    _name = 'tb.order'

    montant = fields.Monetary(string="Montant")
    rib = fields.Char(string="Rib Benifice")
    nom = fields.Char(string="Nom et prenom")
    num_fact = fields.Char(string="slip num")
    date_from = fields.Date(string="date_from")
    date_to = fields.Date(string="date_to")
    company = fields.Many2one('res.company', string="Societe")
    currency_id = fields.Integer(string='currency')


class VoOrderVirement(models.TransientModel):
    _name = 'order.virement'
    _description = 'Order de virement Bancaire'

    company = fields.Many2one('res.company', string="Socièté",default=lambda self: self.env.company)
    x_num_emmeteur = fields.Many2one('res.partner.bank', string="Compte Émetteur")
    date_deb = fields.Date(string="Date de début")
    date_fin = fields.Date(string="Date fin")
    lot = fields.Char(string="Numéro Lot", help="4 chiffre", size=4)
    motif = fields.Char(string="Motif de virement", help="motif de l'operation", size=75)
    montant = fields.Monetary(string="Montant")
    rib = fields.Char(string="Rib Benifice")
    nom = fields.Char(string="Nom et prenom")
    num_fact = fields.Char(string="slip num")
    currency_id = fields.Integer(string='currency')
    x_date_virement = fields.Date(string="Date Virement")


    @api.onchange('company')
    def onchange_company_id(self):
        x_num_emmeteur = self.x_num_emmeteur
        domain = [('partner_id', '=', self.company.partner_id.id)]
        result = {
            'domain': {
                'x_num_emmeteur': domain,
            },

        }
        return result

    # date_cur = fields.Date(default="")

    def genarate_excel_report(self):
        self.env.cr.execute(""" update hr_payslip  SET bank_id =(select acc_number FROM res_partner_bank  WHERE hr_payslip.employee_id=res_partner_bank.employee_id and res_partner_bank.active_account=True) ;""")
        self.env.cr.execute("""delete from tb_order;""")
        self.env.cr.commit()
        rec =  self.env.cr.execute(""" 
               INSERT INTO tb_order (montant,  nom, num_fact, date_from, date_to,rib, company)
           SELECT  DISTINCT l.total as montant ,e.name,slip.number,slip.date_from ,slip.date_to ,slip.bank_id,e.company_id
                    FROM 
                    hr_payslip slip,hr_payslip_line l,hr_employee e

                    WHERE 
                    l.slip_id = slip.id 
                    AND l.code = 'NET_A_PAY'
                    AND slip.state = 'done'
                    AND e.id = l.employee_id 
                    AND e.id = slip.employee_id 
                    ;
               """)
        custom_value = {}
        Global = self.company.report_header
        motif = self.motif
        lot = self.lot
        employee_obj = self.env['tb.order']
        det = self.env['res.company']
        if self.date_deb and self.date_fin and self.company:
            employee_sea = employee_obj.search([('date_from', '>=', self.date_deb), ('date_to', '<=', self.date_fin),
                                            ('company', '=', self.company.id)])
        else:
            employee_sea = employee_obj.search([])
        det_sea = det.search([('name', '=', self.company.name)])
        workbook = xlwt.Workbook()
        # Style for Excel
        style3 = xlwt.easyxf('font: name Arial, bold True, height 200 ;', num_format_str='#,##0.00')
        style1 = xlwt.easyxf('font: name Times New Roman bold on; pattern: pattern solid, fore_colour black;align:'
                             ' horiz center;', num_format_str='#,##0.00')
        style2 = xlwt.easyxf('font:height 400,bold True; pattern: pattern solid, fore_colour black;',
                             num_format_str='#,##0.00')
        style0 = xlwt.easyxf('font:bold False;', num_format_str='#,##0.00')
        style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
        style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
        style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
        style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')

        # Excel Heading Manipulation
        sheet = workbook.add_sheet("vir")
        sheet.write(0, 1, Global, style0)
        sheet.write(8, 0, 'Montant', style0)
        sheet.write(8, 1, 'RIB benificiaire', style0)
        sheet.write(8, 2, 'Nom et Prenom', style0)
        sheet.write(8, 3, 'Numero Facture', style0)
        sheet.write(8, 4, 'Motif operation', style0)

        for det in det_sea:
            sheet.write(4, 1, det.name, style0)

        row = 9
        nb = 0
        for rec in employee_sea:
            sheet.write(row, 0, str(format(rec.montant, '.3f')).replace('.',''), style0)
            sheet.write(row, 1, rec.rib, style0)
            sheet.write(row, 2, rec.nom, style0)
            sheet.write(row, 3, rec.num_fact, style0)
            sheet.write(row, 4, self.company.name, style0)

            nb += rec.montant
            row += 1
        sheet.write(0, 0, ' Global', style0)
        sheet.write(1, 0, ' RIB donneur l order', style0)
        sheet.write(2, 0, ' Total de virement', style0)
        sheet.write(2, 1, nb, style0)
        sheet.write(3, 0, ' Nombre de ligne', style0)
        sheet.write(3, 1, (row - 9), style0)
        sheet.write(4, 0, 'Raison Social', style0)
        sheet.write(5, 0, 'Reference d envoi', style0)
        sheet.write(6, 0, 'Date echaeance', style0)
        sheet.write(7, 0, 'Detail', style0)

        workbook.save('/tmp/order_virement.xls')
        result_file = open('/tmp/order_virement.xls', 'rb').read()
        attach_id = self.env['wizard.excel.report'].create({
            'name': 'Order Virement.xls',
            'report': base64.encodestring(result_file)
        })
        return {
            'name': ('Notification'),
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.excel.report',
            'res_id': attach_id.id,
            'data': None,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def genarate_txt(self):
        self.env.cr.execute("""delete from tb_order;""")
        self.env.cr.execute(""" update hr_payslip  SET bank_id =(select acc_number FROM res_partner_bank  WHERE hr_payslip.employee_id=res_partner_bank.employee_id and res_partner_bank.active_account=True) ;""")
        self.env.cr.commit()
        self.env.cr.execute(""" 
               INSERT INTO tb_order (montant,  nom, num_fact, date_from, date_to,rib, company)
           SELECT  DISTINCT l.total as montant ,e.name,slip.number,slip.date_from ,slip.date_to ,slip.bank_id,e.company_id
                    FROM 
                    hr_payslip slip,hr_payslip_line l,hr_employee e

                    WHERE 
                    l.slip_id = slip.id 
                    AND l.code = 'NET_A_PAY'
                    AND slip.state = 'done'
                    AND e.id = l.employee_id 
                    AND e.id = slip.employee_id 
                    ;
               """)
       
        self.env.cr.execute('SELECT SUM(montant) FROM tb_order ')
        tot = self.env.cr.fetchone()[0] * 1000

        xl = ("%015d" % (int(tot)))
        self.env.cr.execute('SELECT COUNT(montant) FROM tb_order ')
        tot1 = self.env.cr.fetchone()[0]
        xl1 = ("%07d" % (int(tot1)))

        a = 'VIRB'
        b = datetime.strftime(datetime.now(), '%m-%Y')
        c = '.txt'
        b2 = datetime.strftime(datetime.now(), '%d%m%Y')

        fich = a + str(b) + c
        # raise UserError(b2)

        repertoire = '/tmp/ordre/virment/'
        docy = self.env['tb.order'].search([])
        try:
            os.makedirs(repertoire)
        except OSError:
            if not os.path.isdir(repertoire):
                Raise
        fichier = fich
        rp1 = repertoire + fichier

        # docy = self.env['tb.declaration'].search([])
        # ligne = str(b) + str(c) + str(e) + str(f)
        al_n = '110100000'
        al_n1 = '1178800'
        al_n2 = '2178800'
        nbl = 0
        rib = '03705026011500556077'
        cdest = '03'
        cdest1 = '050'
        mot = self.motif if self.motif else ''
        with open(rp1, "w") as f:
            ligne_ex = al_n + str(b2) + str(self.lot) + al_n1 + str(xl) + str(xl1) + "\n"

            f.write(ligne_ex)
            for xs in docy:
                mnt = ("%015d" % (int(xs.montant * 1000)))
                nbl = nbl + 1
                xnbl = ("%015d" % (int(nbl)))
                b_rib = xs.rib
                nom = xs.nom
                r = (len(nom))

                sp = '"'
                sp1 = '%'
                sp2 = str(50 - r)
                sp3 = 's'
                e = " "
                space_i = sp1 + e + sp2 + sp3

                xf = str(space_i)

                xz = (xf % (str('000')))

                r2 = (len(mot))
                sx = '"'
                sx1 = '%'
                sx2 = str(75 - r2)
                sx3 = 's'
                e1 = " "
                space_i1 = sx1 + e1 + sx2 + sx3

                xf1 = str(space_i1)

                vc = (xf1 % (str('0000000000000000')))
                zz = '               '

                ligne_ex1 = al_n + str(b2) + str(self.lot) + al_n2 + str(mnt) + str(xnbl) + rib + cdest + cdest1 + str(
                    b_rib) + str(nom) + xz + str(mot) + vc + zz + "\n"
                f.write(ligne_ex1)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        attachment_obj = self.env['ir.attachment']

        result_file = base64.b64encode(open(rp1, 'rb').read())

        attach_id = self.env['wizard.txt.report'].create({
            'name': fich,
            'report': base64.encodestring(result_file)

        })
        attachment_id = attachment_obj.create(
            {'name': fich, 'res_id': self.id, 'res_model': self._name, 'store_fname': result_file,
             'datas': result_file})
        # prepare download url
        # if attachment_id:
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        # download

        return {'name': ('Notification'), 'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.txt.report',
                'res_id': attach_id.id,
                'data': None,
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                'target': 'new'
                }

    def print_report(self):
        print("Dahech Haithem")
        data = {
            'ids': self.ids,
            'form': {
                'nom_prenom': self.nom,
                'company': self.company.id,
                'num_fact': self.num_fact,
                'montant': self.montant,
                'date_deb': self.date_deb,
                'date_fin': self.date_fin,
                'x_date_virement': self.x_date_virement,
                'rib': self.rib,
                'x_num_emmeteur': self.x_num_emmeteur.acc_number,
            },
        }
        return self.env.ref('order_virement.action_report_report_ordre_virement').report_action(self, data)


class WizardEtxlReport(models.TransientModel):
    _name = "wizard.txt.report"

    report = fields.Binary('Prepared file')
    name = fields.Char('File Name')


class WizardExcelReport(models.TransientModel):
    _name = "wizard.excel.report"

    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)


class Report_Declaration_hr(models.AbstractModel):
    _name = 'report.order_virement.report_ordre_virement'

    def _get_report_values(self, docids, data=None):
        nom_prenom = data['form']['nom_prenom']
        num_fact = data['form']['num_fact']
        date_deb = data['form']['date_deb']
        date_fin = data['form']['date_fin']
        montant = data['form']['montant']
        company = data['form']['company']
        rib = data['form']['rib']
        x_num_emmeteur = data['form']['x_num_emmeteur']
        x_date_virement = data['form']['x_date_virement']
        self.env.cr.execute("""delete from tb_order;""")
        self.env.cr.execute(""" update hr_payslip  SET bank_id =(select acc_number FROM res_partner_bank  WHERE hr_payslip.employee_id=res_partner_bank.employee_id and res_partner_bank.active_account=True) ;""")
        self.env.cr.commit()
        rec =  self.env.cr.execute(""" 
           INSERT INTO tb_order (montant,  nom, num_fact, date_from, date_to,rib, company)
           SELECT  DISTINCT l.total as montant ,e.name,slip.number,slip.date_from ,slip.date_to ,slip.bank_id,e.company_id
                    FROM 
                    hr_payslip slip,hr_payslip_line l,hr_employee e

                    WHERE 
                    l.slip_id = slip.id 
                    AND l.code = 'NET_A_PAY'
                    AND slip.state = 'done'
                    AND e.id = l.employee_id 
                    AND e.id = slip.employee_id 
                    ;
               """)
        docs = []

        employee_obj = self.env['tb.order'].search([])
        det = self.env['res.company']
        if date_deb and date_fin and company:
            employee_sea = employee_obj.search([('date_from', '>=', date_deb), ('date_to', '<=', date_fin),
                                                ('company', '=', company)])
        else:
            employee_sea = employee_obj.search([])    
        det_sea = det.search([('name', '=', self.env.company.name)])
        for rec in employee_sea:
            docs.append({
                'nom_prenom': rec.nom,
                'company': rec.company.name,
                'street': rec.company.street,
                'rib': rec.rib,
                'montant': rec.montant,
                'x_num_emmeteur': x_num_emmeteur,
                'x_date_virement': x_date_virement,
            })

        return {
            'doc_ids': docids,
            'doc_model': "self._name",
            'docs': docs,

        }
