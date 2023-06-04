import logging

from odoo import models, fields, api
from datetime import date, datetime
_logger = logging.getLogger(__name__)


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


class wizard_declaration_hr(models.TransientModel):
    _name = 'wizard.declaration.cnss.det'

    def _get_selection(self):
        year_list = []
        for r in range(2021, (datetime.now().year)+2):
            year_list.append((r, r))
        return year_list

    date_start = fields.Date(string='Date début')
    date_end = fields.Date(string='Date fin')
    company_id = fields.Many2one(comodel_name='res.company', string='Société', required="True", default=lambda self: self.env.company)
    month = fields.Selection(selection=[('1', 'janvier'), ('2', 'février'), ('3', 'Mars'), ('4', 'Avril'), ('5', 'Mai'),
                                        ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Aout'), ('9', 'Septembre'),
                                        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Decembre')],
                             string='Mois en cours')
    year = fields.Selection(selection=_get_selection, string="Année")
    x_trimester = fields.Selection(selection=[('1', '1ère trimestre'), ('2', '2ème trimestre'),
                                              ('3', '3ème trimestre'), ('4', '4ème trimestre')], string='Trimestre')

    def print_report(self):
        data = {
            'ids': self.ids,
            'form': {
                'company_id': self.company_id.id,
                'year': self.year,
                'month': self.month,
                'x_trimester': self.x_trimester,
            },
        }
        return self.env.ref('spc_declaration_cnss_detaillee.action_report_payslip_avantag').report_action(self, data)


class Report_Declaration_hr(models.AbstractModel):
    _name = 'report.spc_declaration_cnss_detaillee.avantag_report_cnss'

    def _get_report_values(self, docids, data=None):
        tn_struct_id = self.env.ref('spc_hr_payroll.hr_payroll_salary_structure_base').id
        docs = []
        res = []
        nbr = 0
        company_id = data['form']['company_id']
        company = self.env['res.company'].browse(company_id)
        year = int(data['form']['year'])
        x_trimester = data['form']['x_trimester']
        company_cnss_id = company.matricule_cnss
        company_name = company.name
        company_street = company.street
        company_street2 = company.street2
        company_city = company.city
        company_zip = company.zip
        company_country_id = company.country_id.name
        company_code_exploitation = company.code_exploitation
        company_br = company.bureau_regional
        company_vat = company.vat

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
                         "ORDER BY hr.matricule_cnss "
                         , (tn_struct_id, company_id, from_date, to_date))


        p = 1
        ligne = 1
        total = 0
        total_trimestre_x = 0
        pages = []
        total_list = []
        total_m1 =total_m2=total_m3= 0
        payslips = self.env.cr.dictfetchall()
        print(len(payslips))
       
        x = len(payslips) / 12
        num_page=round(x)
        nb_pages = round(x) + 1
        
        if len(payslips)<13:
            pages.append(p) 
        for l, slip in enumerate(payslips):
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
                total = gross1+gross2+gross3




            docs.append({
                'matricule': slip['matricule_cnss'],
                'nom_prenom': slip['name'],
                'x_trimester': x_trimester,
                'cin': slip['identification_id'],
                'job': self.env['hr.job'].browse(slip['job_id']).name,
                'children': slip['children'],
                'm1': gross1,
                'm2': gross2,
                'm3': gross3,
                'ligne': ligne,
                'page': p,
                'total': total,
            })

            ligne += 1
            
            if len(payslips)>=13:    
                if ligne == 13 :
                    pages.append(p)
                    ligne = 1
                    p += 1
                if ligne != 13 and len(pages) ==num_page:
                    pages.append(p)
                  
            print(total)
            total_trimestre_x += total
            total_m1+=gross1
            total_m2+=gross2
            total_m3+=gross3
            
        for p in pages:
            res.append({
                'company_code_exploitation': company_code_exploitation,
                'company_br': company_br,
                'company_cnss_id': company_cnss_id,
                'company_name': company_name,
                'company_street': company_street,
                'company_street2': company_street2,
                'company_city': company_city,
                'company_zip': company_zip,
                'company_country_id': company_country_id,
                'company_vat': company_vat,
                'year': year,
                'total_page': nb_pages,
                'page': p,
                'x_trimester': x_trimester,


            })

        total_list.append({
            'total_trimestre_x': total_trimestre_x,
            'total_m1':total_m1,
             'total_m2':total_m2,
           'total_m3':total_m3,
          
        })
        return {
            'doc_ids': docids,
            'doc_model': "self._name",
            'docs': docs,
            'res': res,
            'total_list': total_list
        }



