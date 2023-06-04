from odoo import models, fields, api
import calendar
from datetime import date, datetime, timedelta

class Tbjournal(models.Model):
    _name = "tb.journal"

    slip = fields.Char(string='slip')
    employee = fields.Char(string="employee")
    base = fields.Float(string='base')
    brut = fields.Float(string='brut')
    prime_tr = fields.Float(string='prime de transport')
    prime_pr = fields.Float(string='prime de presence')
    indm_v = fields.Float(string='indimite variable')
    prime_ex = fields.Float(string='prime exceptionnel')
    lait = fields.Float(string='lait')
    psr = fields.Float(string='PSR')
    enc = fields.Float(string='prime ENC')
    pnr = fields.Float(string='prime PNR')
    pr_resp = fields.Float(string='prime pr_resp')
    remboursement_acc = fields.Float(string='remboursement_acc')
    cnss = fields.Float(string='cnss')
    c_imp = fields.Float(string='salaire imposable')
    irpp = fields.Float(string='irpp')
    css = fields.Float(string='css')
    salnet = fields.Float(string='salnet')
    pret = fields.Float(string='pret')
    avances = fields.Float(string='avances')
    month = fields.Char(string='mois')
    annee = fields.Char(string='annee')
    company_id = fields.Integer(string='company')
    net = fields.Float(string='salaire net')


class PayrollRecapReportWizard(models.TransientModel):
    _name = 'payroll.recap.report.wizard'

    def _get_selection(self):
        year_list = []
        for r in range(2021, (datetime.now().year)+2):
            year_list.append((r, r))
        return year_list

    month = fields.Selection(selection=[('1', 'janvier'), ('2', 'février'), ('3', 'Mars'), ('4', 'Avril'), ('5', 'Mai'),
                                        ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Aout'), ('9', 'Septembre'),
                                        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Decembre')],
                             string='Mois en cours')

    year = fields.Selection(selection=_get_selection, string="Année")
    company_id = fields.Many2one(comodel_name='res.company', string='Société', required="True")

    date_start = fields.Date(string='Date début')
    date_end = fields.Date(string='Date fin')
    criteria = fields.Selection(selection=[('mois', 'Par mois'), ('periode', 'Par période')], required="True",
                                default='mois', string="Choix")
    struct_id = fields.Many2one(comodel_name='hr.payroll.structure', string='Structure')

    # @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'form': {
                'month': self.month,
                'annee': self.year,
                'date_deb': self.date_start,
                'date_fin': self.date_end,
                'criteria': self.criteria,
                'struct_id': self.struct_id.id,
                'company_id': self.company_id.id,
            },
        }
        return self.env.ref('journal_paie.recap_report').report_action(self, data=data)


class report_credit_template(models.AbstractModel):
    _name = 'report.journal_paie.payroll_recap_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        struct_id = int(data['form']['struct_id'])
        month = data['form']['month']
        annee = data['form']['annee']
        if month and annee :
            import datetime
            first_date = datetime.date(int(annee), int(month), 1)
            last_date = datetime.date(int(annee), int(month), calendar.monthrange(int(annee), int(month))[1])

        company_id = data['form']['company_id']
        date_deb = fields.Date.from_string(data['form']['date_deb'])
        date_fin = fields.Date.from_string(data['form']['date_fin'])
        criteria = data['form']['criteria']
        data = []
        res = []
        text_search = ''
        payslip_line_obj = self.env['hr.payslip.line']
        l = 0

        if criteria == 'mois':

            # payslip_ids = self.env['hr.payslip'].search([('state', '=', 'done'),
            #                                              ('company_id', '=', company_id),
            #
            #                                              ('date_from', '=', first_date),
            #                                              ('date_to', '=', last_date)])
            self._cr.execute("SELECT upper(hr.name) as name, hp.employee_id, hr.job_id, "
                             "hr.matricule_cnss, hr.children, hr.identification_id "
                             "FROM hr_payslip hp "
                             "INNER JOIN hr_contract hc ON hc.id = hp.contract_id "
                             "INNER JOIN hr_employee hr ON hr.id = hp.employee_id "
                             "WHERE hp.state = 'done' AND hp.company_id = %s "
                             "AND hp.date_to between %s AND %s AND hc.struct_id = %s"
                             "GROUP BY hp.employee_id, hr.id "
                             "ORDER BY hr.matricule_cnss "
                             , (company_id, first_date, last_date, struct_id))
            payslip_ids = self.env.cr.dictfetchall()

            for slip in payslip_ids:
                basic = 0.0
                gross = 0.0
                CREDIT = 0.0
                AV = 0.0
                CNSS = 0.0
                IRPP = 0.0
                C_IMP = 0.0
                CNSSP = 0.0
                NET_A_PAY = 0.0
                NET = 0.0
                CSS = 0.0
                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'BASIC' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_basic = self._cr.dictfetchall()
                for basic in all_basic:
                    basic = basic['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'GROSS' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_gross = self._cr.dictfetchall()
                for gross in all_gross:
                    gross = gross['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'C_IMP' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_C_IMP = self._cr.dictfetchall()
                for imp in all_C_IMP:
                    C_IMP = imp['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'IRPP' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_IRPP = self._cr.dictfetchall()
                for irpp in all_IRPP:
                    IRPP = irpp['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'CNSS' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_CNSS = self._cr.dictfetchall()
                for cnss in all_CNSS:
                    CNSS = cnss['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'NET' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_NET = self._cr.dictfetchall()
                for net in all_NET:
                    NET = net['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'CNSSP' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_CNSSP = self._cr.dictfetchall()
                for cnssp in all_CNSSP:
                    CNSSP = cnssp['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'CSS' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_CSS = self._cr.dictfetchall()
                for css in all_CSS:
                    CSS = css['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'AV' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_AV = self._cr.dictfetchall()
                for av in all_AV:
                    AV = av['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'CREDIT' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_CREDIT = self._cr.dictfetchall()
                for cr in all_CREDIT:
                    CREDIT = cr['total']

                self._cr.execute("SELECT line.total AS total "
                                 "FROM hr_payslip_line line "
                                 "INNER JOIN hr_payslip hp ON line.slip_id = hp.id "
                                 "WHERE hp.state = 'done'  "
                                 "AND line.code = 'NET_A_PAY' "
                                 "AND hp.employee_id = %s "
                                 "AND hp.date_to BETWEEN %s AND %s "
                                 "GROUP BY hp.date_to, line.total "
                                 "ORDER BY hp.date_to ",
                                 (slip['employee_id'], first_date, last_date))
                all_NET_A_PAY = self._cr.dictfetchall()
                for pay in all_NET_A_PAY:
                    NET_A_PAY = pay['total']

                l += 1
                data.append({
                    'ligne': l,
                    'matricule': slip['identification_id'] or 00000000,
                    'matricule_cnss': slip['matricule_cnss'] or 00000000,
                    'nom_prenom': slip['name'],
                    'base': basic,
                    'brut': gross,
                    'cnss': CNSS,
                    'salaire_impo': C_IMP,
                    'irpp': IRPP,
                    'net_salary': NET,
                    'cnss_p': CNSSP,
                    'css': CSS,
                    'amount_avance': AV,
                    'amount_loan': CREDIT,
                    'net_salary_to_pay': NET_A_PAY,
                })
                text_search = "Pour le mois du " + ' ' + calendar.month_name[
                    int(month)].capitalize() + ' ' + "et l'année " + ' ' + annee

        elif criteria == 'periode':
            gross_total = 0
            payslip_ids = self.env['hr.payslip'].search([('state', '=', 'done'),
                                                         ('company_id', '=', company_id),
                                                         ('struct_id', '=', int(struct_id))])
            for pays in payslip_ids:
                if date_deb <= pays.date_from <= date_fin:
                    l += 1

                    data.append({
                        'ligne': l,
                        'matricule': pays.employee_id.identification_id or 00000000,
                        'matricule_cnss': pays.employee_id.matricule_cnss or 00000000,
                        'nom_prenom': pays.employee_id.name,
                        'base': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                         ('code', '=', 'BASIC'),
                                                         ('slip_id', '=', pays.id)]).total,

                        'brut': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                         ('code', '=', 'GROSS'),
                                                         ('slip_id', '=', pays.id)]).total,

                        'cnss': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                         ('code', '=', 'CNSS'),
                                                         ('slip_id', '=', pays.id)]).total,

                        'salaire_impo': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                                 ('code', '=', 'C_IMP'),
                                                                 ('slip_id', '=', pays.id)]).total,

                        'irpp': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                         ('code', '=', 'IRPP'),
                                                         ('slip_id', '=', pays.id)]).total,

                        'net_salary': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                               ('code', '=', 'NET'),
                                                               ('slip_id', '=', pays.id)]).total,

                        'cnss_p': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                           ('code', '=', 'CNSSP'),
                                                           ('slip_id', '=', pays.id)]).total,

                        'css': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                        ('code', '=', 'CSS'),
                                                        ('slip_id', '=', pays.id)]).total,

                        'amount_avance': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                                  ('code', '=', 'AV'),
                                                                  ('slip_id', '=', pays.id)]).total,

                        'amount_loan': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                                ('code', '=', 'CREDIT'),
                                                                ('slip_id', '=', pays.id)]).total,

                        'net_salary_to_pay': payslip_line_obj.search([('employee_id', '=', pays.employee_id.id),
                                                                      ('code', '=', 'NET_A_PAY'),
                                                                      ('slip_id', '=', pays.id)]).total,
                    })

                    text_search = "Pour la période du " + ' ' + str(date_deb) + ' ' + "au" + ' ' + str(date_fin)
        res.append({
            'title': text_search,
        })

        vals = {
            'doc_ids': docids,
            'doc_model': "self._name",
            # 'docs': docs,
            'res': res,
            'data': data,
        }
        return vals



