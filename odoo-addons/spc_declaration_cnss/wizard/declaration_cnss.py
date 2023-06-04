# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import os
import os.path
from datetime import date, datetime


class Hr_Payslip(models.Model):
    _inherit = 'hr.payslip'

    def get_trimestre(self, month):
        if int(month) < 4:
            return '1'
        elif int(month) < 7:
            return '2'
        elif int(month) < 10:
            return '3'
        else:
            return '4'


class DeclarationCNSS(models.TransientModel):
    _name = 'declaration.cnss'
    _description = 'Declaration CNSS'

    def _get_selection(self):
        year_list = []
        for r in range(2021, (datetime.now().year)+2):
            year_list.append((r, r))
        return year_list

    file = fields.Binary('File')
    file_name = fields.Char('txt File', size=64)
    company = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)
    trimestre = fields.Selection(selection=[('1', '1ère trimestre'), ('2', '2ème trimestre'),
                                            ('3', '3ème trimestre'), ('4', '4ème trimestre')],
                                 string='Trimestre')
    year = fields.Selection(selection=_get_selection, string="Année")
    excel_file = fields.Binary('Telecharger teledeclaration CNSS', attachment=True)

    def action_save(self):
        for object in self:
            object.attach_id = [(6, 0, object.attach_id.ids)]

    def hachage(self, p, n, pos, ca):
        ln = len(str(n))
        if ln == p:
            return n
        elif ln < p:
            if type(n) == int:
                str_n = str(n)
            else:
                str_n = n

            pp = p - ln
            i = 0
            for i in range(pp):
                if pos == 'D':
                    str_n = str_n + ca
                else:
                    if str_n:
                        str_n = ca + str_n
            return str_n
        else:
            return False

    def genarate_txt(self):
        tn_struct_id = self.env.ref('spc_hr_payroll.hr_payroll_salary_structure_base').id
        x_trimester = self.trimestre
        year = int(self.year)
        try:
            filename = 'DS' + self.hachage(10, self.company.matricule_cnss, 'G', '0') + \
                       self.hachage(4, self.company.code_exploitation, 'G', '0') + '.' + self.trimestre + self.year + ".txt"
        except:
            raise UserError("Verifier la matricule CNSS ou le code d'exploitation")

        if int(x_trimester) == 1:
            from_date = date(year, 1, 1).strftime('%Y-%m-%d')
            to_date = date(year, 3, 31).strftime('%Y-%m-%d')
        if int(x_trimester) == 2:
            nbr = 3
            from_date = date(year, 4, 1).strftime('%Y-%m-%d')
            to_date = date(year, 6, 30).strftime('%Y-%m-%d')
        if int(x_trimester) == 3:
            nbr = 6
            from_date = date(year, 7, 1).strftime('%Y-%m-%d')
            to_date = date(year, 9, 30).strftime('%Y-%m-%d')
        if int(x_trimester) == 4:
            nbr = 9
            from_date = date(year, 10, 1).strftime('%Y-%m-%d')
            to_date = date(year, 12, 31).strftime('%Y-%m-%d')

        self._cr.execute("SELECT upper(hr.name) as name, hp.employee_id, hr.job_id, "
                         "hr.matricule_cnss, hr.children, hr.identification_id "
                         "FROM hr_payslip hp "
                         "INNER JOIN hr_employee hr ON hr.id = hp.employee_id "
                         "WHERE hp.struct_id = %s AND hp.state = 'done' AND hp.company_id = %s "
                         "AND hp.date_to between %s AND %s "
                         "GROUP BY hp.employee_id, hr.id "
                         "ORDER BY hr.matricule_cnss"
                         , (tn_struct_id, self.company.id, from_date, to_date))

        page = ligne = 1
        total = 0

        lines = []
        ln_zero = 0
        lnpage_zero = 0
        lnline_zero = 0
        lnmatricule_assure_zero = 0
        lnempname_zero = 0
        lnidentification_zero = 0
        lnsalaire = 0

        payslips = self.env.cr.dictfetchall()
        for l, slip in enumerate(payslips, start=1):
            # if not slip['identification_id']:
            #     print('--------')
            #     raise except_orm(('Error'), ('Missing Identification No for %s') % (slip['name']))

            self._cr.execute("SELECT EXTRACT(MONTH FROM hp.date_to) - %s as rnum, line.total AS total, "
                             "COUNT(line.id) as nb_line "
                             "FROM hr_payslip_line line "
                             "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                             "WHERE hp.state = 'done' "
                             "AND line.code = 'GROSS' "
                             "AND hp.employee_id = %s "
                             "AND hp.date_to BETWEEN %s AND %s "
                             "GROUP BY hp.date_to, line.total "
                             "ORDER BY hp.date_to ",
                             (nbr, slip['employee_id'], from_date, to_date))
            all_gross = self._cr.dictfetchall()
            gross1 = gross2 = gross3 = 0.0

            for gross in all_gross:
                if int(gross['rnum']) == 1:
                    gross1 = gross['total']
                if int(gross['rnum']) == 2:
                    gross2 = gross['total']
                if int(gross['rnum']) == 3:
                    gross3 = gross['total']
                total = gross1 + gross2 + gross3
            chaine = ''

            # traitement matricule 10 caractère
            matricule_cnss = self.company.matricule_cnss
            if len(matricule_cnss) < 10:
                ln_zero = 10 - len(matricule_cnss)
                while ln_zero > 0:
                    ln_zero = ln_zero - 1
                    matricule_cnss = '0' + matricule_cnss

            chaine += matricule_cnss + self.company.code_exploitation + self.trimestre + self.year
            pg = str(page)

            ###traitement page 3 caractères
            if len(pg) < 3:
                lnpage_zero = 3 - len(pg)
                while lnpage_zero > 0:
                    lnpage_zero = lnpage_zero - 1
                    pg = '0' + pg
            chaine += pg


            ###traitement ligne 2 caractères
            line = str(ligne)
            if len(line) < 2:
                lnline_zero = 2 - len(line)
                while lnline_zero > 0:
                    lnline_zero = lnline_zero - 1
                    line = '0' + line

            chaine += line

            ###traitement matrucule  de l'assure 10 carac
            cnss_id = slip['matricule_cnss'] or 0000000000
            strcnss_id = str(cnss_id)
            if len(str(cnss_id)) < 10:
                lnmatricule_assure_zero = 10 - len(str(cnss_id))
                while lnmatricule_assure_zero > 0:
                    lnmatricule_assure_zero = lnmatricule_assure_zero - 1
                    strcnss_id = '0' + strcnss_id

            chaine += strcnss_id

            ###traitement nom et prénom 60 carac
            name = slip['name']
            if len(name) < 60:
                lnempname_zero = 60 - len(name)
                while lnempname_zero > 0:
                    lnempname_zero = lnempname_zero - 1
                    name = name + ' '

            chaine += name

            ###traitement cin 8 carac
            stridentification_id = slip['identification_id']
            if len(stridentification_id) < 8:
                lnidentification_zero = 8 - len(stridentification_id)
                while lnidentification_zero > 0:
                    lnidentification_zero = lnidentification_zero - 1
                    stridentification_id = '0' + stridentification_id

            chaine += stridentification_id

            sal = format(total, '.3f')
            amount = str(sal)
            amount = amount.replace('.', '')
            if len(str(amount)) < 10:
                lnsalaire = 10 - len(str(amount))
                while lnsalaire > 0:
                    lnsalaire = lnsalaire - 1
                    amount = '0' + amount
            chaine += amount
            
            chaine += ' '+' '+' '+' '+' '+' '+' '+' '+' '+' '
            # chaine += "          "  # zone vierge 10 carac

            lines.append(chaine)

            ligne += 1

            if ligne == 13:
                ligne = 1
                page += 1
                chaine += '\n'

        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "data/"+filename)

        file = open(path, 'w+')
        if file:
            output = ''
            for line in lines:
                output += line + '\n'
            file_data = bytes(output, "utf-8")
            file.close()
            encoded = base64.b64encode(file_data)

            self.file = encoded
            self.file_name = filename
            cnss_wiz = self.env.ref('spc_declaration_cnss.declaration_cnss_form_view', False)
        return {
            'name': _('Déclaration CNSS'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'declaration.cnss',
            'res_id': self.id,
            'view_id': cnss_wiz.id,
            'target': 'new',
        }
