# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class PremuimRules(models.TransientModel):
    _name = 'hr.premuim.rules.wizard'

    struct_id = fields.Many2one(comodel_name='hr.payroll.structure', string='Structure salariale')

    def add_prime_into_struct(self):
        values = {}
        struct_salary_id = self.struct_id.id

        # get the name and the code of the prime
        prime_name = self.env['hr.premium'].browse(self._context.get('premium_id')).name
        prime_code = self._context.get('code')

        prime_imposable = self._context.get('imposable')
        prime_cotisable = self._context.get('cotisable')
        absence = self._context.get('absence')
        category_id = 0
        sequence = 0

        if prime_imposable:
            category_search_id = self.env['hr.salary.rule.category'].search([('code', '=', 'PRIME_IMPO')]).id
            category_id = self.env['hr.salary.rule.category'].browse(category_search_id).id
            sequence = 50

        # les primes cotisables et imposables
        if prime_cotisable and prime_imposable:
            category_search_id = self.env['hr.salary.rule.category'].search([('code', '=', 'PRIME_COT_IMPO')]).id
            category_id = self.env['hr.salary.rule.category'].browse(category_search_id).id
            sequence = 40

        # les primes ni cotisables ni imposables
        if not prime_cotisable and not prime_imposable:
            category_search_id = self.env['hr.salary.rule.category'].search([('code', '=', 'PRIME_ORD')]).id
            category_id = self.env['hr.salary.rule.category'].browse(category_search_id).id
            sequence = 12500

        # prepare values data for prime
        condition_result = 'result=inputs.' + prime_code + ' and inputs.' + prime_code + '.amount or False'
        calcul_result = "if worked_days.WORK100 and not (worked_days.LEAVE120 and worked_days.LEAVE90) :\n" \
    "   result = inputs."+ prime_code +".amount \n"\
"if worked_days.WORK100 and worked_days.LEAVE120 and  worked_days.LEAVE90:\n"\
    "   result = (inputs."+ prime_code+" .amount / payslip.number_of_days_per_month) * (worked_days.WORK100.number_of_days + worked_days.LEAVE120.number_of_days)\n"\
"if worked_days.WORK100 and worked_days.LEAVE120 and not (worked_days.LEAVE90):\n"\
    "   result = inputs."+ prime_code +".amount\n"\
"if worked_days.WORK100 and worked_days.LEAVE90 and not (worked_days.LEAVE120):\n"\
    "   result = (inputs."+ prime_code+" .amount / payslip.number_of_days_per_month) * worked_days.WORK100.number_of_days\n"\

        # prepare values data for absence
        # traitement de l'absence sur les valeurs des primes
        code = 'AB_PR_' + prime_code
        calcul_result_absence = 'result= (inputs.' + prime_code + '.amount / 26 ) * worked_days.Unpaid.number_of_days'
        condition_result_absence = 'result =  worked_days.Unpaid and worked_days.Unpaid.number_of_days or False'

        if absence:
            # c'est le calcul de l'absence concernant chaque primes
            category_values = {
                'code': code,
                'name': 'Absence prime ' + prime_code,
                'parent_id': 11,
            }

            # TESTER si le code du prime absence existe ou nn dans la gatégorie (hr.salary.rule.gategory)
            exist_code = self.env['hr.salary.rule.category'].search([('code', '=', code)])
            exist_code_id = self.env['hr.salary.rule'].browse(exist_code).id

            if not exist_code:  # code de la catégorie
                absence_categ_rule_id = self.env['hr.salary.rule.category'].create(category_values)
                rule_category_id = absence_categ_rule_id

                #######
                values_ab_pr = {
                    'name': 'Absence prime ' + prime_code,
                    'code': code,
                    'category_id': rule_category_id,  # hr_salary_rule_category AB_PR
                    'condition_select': 'python',
                    'condition_python': condition_result_absence,
                    'amount_select': 'code',
                    'amount_python_compute': calcul_result_absence,
                    'appears_in_payslip': False,
                }

                # TESTER si le code du prime absence existe ou nn dans les règles (hr.salary.rule)
                exist_ab_pr = self.env['hr.salary.rule'].search([('code', '=', code)])

                # traiter l'existance des règles
                if not exist_ab_pr:
                    absence_prime_rule_id = self.env['hr.salary.rule'].create(values_ab_pr)
                    create_ab = self.env.cr.execute(
                        "INSERT INTO hr_structure_salary_rule_rel (struct_id , rule_id) VALUES (%s, %s)",
                        (struct_salary_id, absence_prime_rule_id))

                    # le calcul des primes concernant absence
                    calcul_result_prime_absence = 'result= inputs.' + prime_code + '.amount - categories.AB_PR_' + prime_code
                    values_ab = {
                        'name': prime_name,
                        'code': prime_code,
                        'category_id': category_id,
                        'condition_select': 'python',
                        'condition_python': condition_result,
                        'amount_select': 'code',
                        'amount_python_compute': calcul_result_prime_absence,
                        'sequence': sequence,
                    }

                    # ajouter les règles pour chaque primes dans (hr_salary_rule)
                    # TESTER si la règle existe ou nn
                    exist = self.env['hr.salary.rule'].search([('code', '=', prime_code)])
                    if not exist:
                        prime_rule_id = self.env['hr.salary.rule'].create(values_ab)

                        create = self.env.cr.execute(
                            "INSERT INTO hr_structure_salary_rule_rel (struct_id , rule_id) VALUES (%s, %s)",
                            (struct_salary_id, prime_rule_id))

                        return create
                    else:
                        # le modifier
                        # cr.execute("DELETE FROM hr_salary_rule WHERE code = %s",(prime_code,)) ==> pour le supprimer
                        # mais c'est impossible car les rules sont attachés par des bulletins de paie
                        exist_id = self.env['hr.salary.rule'].browse(exist).id
                        new_prime_rule_id = self.env['hr.salary.rule'].write(exist, values_ab)
                        struct_exit = self.env.cr.execute(
                            "SELECT struct_id , rule_id FROM hr_structure_salary_rule_rel WHERE "
                            "struct_id =%s AND rule_id =%s",
                            (struct_salary_id, exist[0]))
                        struct_exit_lines = self.env.cr.dictfetchall()

                        if not struct_exit_lines:
                            recreate = self.env.cr.execute(
                                "INSERT INTO hr_structure_salary_rule_rel (struct_id , rule_id) VALUES (%s, %s)",
                                (struct_salary_id, exist[0]))
                            return recreate
                        return True
                else:
                    write_absence_prime_rule_id = self.pool.get('hr.salary.rule').write(exist_ab_pr, values_ab_pr)

            else:
                rule_category_id = exist_code_id
                ####

                values_ab_pr = {
                    'name': 'Absence prime ' + prime_code,
                    'code': code,
                    'category_id': rule_category_id,  # hr_salary_rule_category AB_PR
                    'condition_select': 'python',
                    'condition_python': condition_result_absence,
                    'amount_select': 'code',
                    'amount_python_compute': calcul_result_absence,
                }

                exist_ab_pr = self.env['hr.salary.rule'].search([('code', '=', code)])

                if not exist_ab_pr:
                    absence_prime_rule_id = self.env['hr.salary.rule'].create(values_ab_pr)

                    create_ab = self.env.cr.execute(
                        "INSERT INTO hr_structure_salary_rule_rel (struct_id , rule_id) VALUES (%s, %s)",
                        (struct_salary_id, absence_prime_rule_id))

                    return create_ab
                else:
                    write_absence_prime_rule_id = self.env['hr.salary.rule'].write(exist_ab_pr, values_ab_pr)

                # le calcul des primes concernant absence
                calcul_result_prime_absence = 'result= inputs.' + prime_code + '.amount - categories.AB_PR_' + prime_code
                values_ab = {
                    'name': prime_name,
                    'code': prime_code,
                    'category_id': category_id,
                    'condition_select': 'python',
                    'condition_python': condition_result,
                    'amount_select': 'code',
                    'amount_python_compute': calcul_result_prime_absence,
                    'sequence': sequence,
                }

                # create into salary_rule
                # test if exist ou nn
                exist = self.env['hr.salary.rule'].search([('code', '=', prime_code)])

                if not exist:
                    prime_rule_id = self.env['hr.salary.rule'].create(values_ab)

                    create = self.env.cr.execute(
                        "INSERT INTO hr_structure_salary_rule_rel (struct_id , rule_id) VALUES (%s, %s)",
                        (struct_salary_id, prime_rule_id))

                    return create
                else:
                    # le modifier
                    # cr.execute("DELETE FROM hr_salary_rule WHERE code = %s",(prime_code,)) ==> pour le supprimer mais
                    # c'est impossible car les rules sont attachés par des bulletins de paie

                    new_prime_rule_id = self.env['hr.salary.rule'].write(exist, values_ab)

                    struct_exit = self.env.cr.execute(
                        "SELECT struct_id , rule_id FROM hr_structure_salary_rule_rel "
                        "WHERE struct_id =%s AND rule_id =%s",
                        (struct_salary_id, exist[0]))
                    struct_exit_lines = self.env.cr.dictfetchall()

                    if not struct_exit_lines:
                        recreate = self.env.cr.execute(
                            "INSERT INTO hr_structure_salary_rule_rel (struct_id , rule_id) VALUES (%s, %s)",
                            (struct_salary_id, exist[0]))

                        return recreate

        else:  # sans absence

            values = {
                'name': prime_name,
                'code': prime_code,
                'category_id': category_id,
                'condition_select': 'python',
                'condition_python': condition_result,
                'amount_select': 'code',
                'amount_python_compute': calcul_result,
                'sequence': sequence,
            }

            # create into salary_rule
            # test if exist ou nn
            exist = self.env['hr.salary.rule'].search([('code', '=', prime_code)]).id

            if not exist:
                prime_rule_id = self.env['hr.salary.rule'].create(values)

                create = self.env.cr.execute("INSERT INTO hr_structure_salary_rule_rel "
                                             "(struct_id , rule_id) VALUES (%s, %s)", (struct_salary_id, prime_rule_id.id))

                return create
            else:
                self.env['hr.salary.rule'].browse(exist).write(values)

                self.env.cr.execute(
                    "SELECT struct_id , rule_id FROM hr_structure_salary_rule_rel WHERE struct_id =%s AND rule_id =%s",
                    (struct_salary_id, exist))
                struct_exit_lines = self.env.cr.dictfetchall()

                if not struct_exit_lines:
                    recreate = self.env.cr.execute(
                        "INSERT INTO hr_structure_salary_rule_rel (struct_id , rule_id) VALUES (%s, %s)",
                        (struct_salary_id, exist))

                    return recreate
                return True

