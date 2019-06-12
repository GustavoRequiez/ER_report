# -*- coding: utf-8 -*-

from datetime import datetime
import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class ErReportWizard(models.TransientModel):
    _name = 'er.report.wizard'

    date_start = fields.Date(
        string="Start Date", required=True, default='2019-04-01')  # default=fields.Date.today
    date_end = fields.Date(
        string="End Date", required=True, default='2019-04-30')

    statement_income_data = fields.One2many(
        'statement.income.detail',
        'er_report_id',
        'Details')

    @api.multi
    def get_report(self):
        day = datetime.strptime(self.date_end, '%Y-%m-%d').strftime('%d')
        month = datetime.strptime(self.date_start, '%Y-%m-%d').strftime('%m')
        mes = datetime.strptime(self.date_end, '%Y-%m-%d').strftime('%m')
        year_full = datetime.strptime(
            self.date_start, '%Y-%m-%d').strftime('%Y')
        year = datetime.strptime(self.date_start, '%Y-%m-%d').strftime('%y')

        account_move_line_obj = self.env['account.move.line']
        er_plan_obj = self.env['er.plan.estado.resultados']

        date_start = self.date_start
        date_stop = self.date_end

        statement_income_data = self.env['statement.income.detail']

        date_start_fisrt_day = year_full + '/01/01'

        if month == '01':
            str_month = 'ENERO'
        elif month == '02':
            str_month = 'FEBRERO'
        elif month == '03':
            str_month = 'MARZO'
        elif month == '04':
            str_month = 'ABRIL'
        elif month == '05':
            str_month = 'MAYO'
        elif month == '06':
            str_month = 'JUNIO'
        elif month == '07':
            str_month = 'JULIO'
        elif month == '08':
            str_month = 'AGOSTO'
        elif month == '09':
            str_month = 'SEPTIEMBRE'
        elif month == '10':
            str_month = 'OCTUBRE'
        elif month == '11':
            str_month = 'NOVIEMBRE'
        elif month == '12':
            str_month = 'DICIEMBRE'

        def get_value_credit(ids, date_start, date_end):
            account_ids = account_move_line_obj.search([
                ('date', '>=', date_start),
                ('date', '<=', date_end),
                ('account_id', 'in', ids)])
            credit = sum(account_ids.mapped('credit'))
            return credit

        def get_value_debit(ids, date_start, date_end):
            account_ids = account_move_line_obj.search([
                ('date', '>=', date_start),
                ('date', '<=', date_end),
                ('account_id', 'in', ids)])
            debit = sum(account_ids.mapped('debit'))
            return debit

        def get_value_plan(str_month, year, plan):
            er_plan_id = er_plan_obj.search(
                [('name', '=', str_month), ('year', '=', year), ('plan', '=', plan)])
            total_plan = sum(er_plan_id.mapped('value'))
            return total_plan

        def get_value_plan_acumulado(lista, year, plan):
            total_plan = 0
            for mes in lista:
                er_plan_id = er_plan_obj.search(
                    [('name', '=', mes), ('year', '=', year), ('plan', '=', plan)])
                total_plan += sum(er_plan_id.mapped('value'))
            return total_plan

        accounts = ([6932, 6933, 6934, 6935, 6936, 6937, 6938, 6939])
        ventas_credit = get_value_credit(accounts, date_start, date_stop)

        ventas_debit = get_value_debit(accounts, date_start, date_stop)
        ventas = ventas_credit - ventas_debit

        accounts = ([6942, 6943, 6944, 6945, 6946, 6947, 6948, 6949,
                     6950, 6951, 6952, 6953, 6954, 6955, 6956, 6957, 6958])
        rebajas_credit = get_value_credit(accounts, date_start, date_stop)
        rebajas_debit = get_value_debit(accounts, date_start, date_stop)
        rebajas = rebajas_debit - rebajas_credit
        ventas_netas = ventas - rebajas
        plan = get_value_plan(str_month, year_full, 'VENTAS')
        plan_rebajas = get_value_plan(
            str_month, year_full, 'REBAJAS Y DEVOLUCIONES')
        plan_saldo = plan - plan_rebajas
        ventas_desviacion = ventas - plan
        rebajas_desviacion = rebajas - plan_rebajas
        ventas_netas_desviacion = ventas_netas - plan_saldo
        accounts = ([6932, 6933, 6934, 6935, 6936, 6937, 6938, 6939])
        ventas_acumulado_credit = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        ventas_acumulado_debit = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        ventas_acumulado = round(
            (ventas_acumulado_credit - ventas_acumulado_debit), 0)
        accounts = ([6941, 6951, 6952, 6946, 6953, 6954,
                     6955, 6956, 6957, 6958, 6959])
        rebajas_credit_acumulado = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        rebajas_debit_acumulado = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        rebajas_acumulado = round(
            rebajas_debit_acumulado - rebajas_credit_acumulado, 0)
        desviacion_rebajas = ventas_acumulado - rebajas_acumulado
        ventas_acumulado_porcentaje = round(
            (ventas_acumulado * 100) / desviacion_rebajas, 1)
        rebajas_acumulado_procentaje = round(
            (rebajas_acumulado * 100) / desviacion_rebajas, 1)
        months_list = ['ENERO',  'FEBRERO', 'MARZO', 'ABRIL',  'MAYO',  'JUNIO',
                       'JULIO',  'AGOSTO',  'SEPTIEMBRE',  'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
        lista = []
        mes = int(str(month))
        m = 0
        while m < mes:
            lista.append(months_list[m])
            m = m + 1
        plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'VENTAS')
        plan_acumulado_rebajas = get_value_plan_acumulado(
            lista, year_full, 'REBAJAS Y DEVOLUCIONES')
        plan_acumulado_saldo = plan_acumulado - plan_acumulado_rebajas

        plan_acumulado_porcentaje = round(
            (plan_acumulado * 100) / plan_acumulado_saldo, 1)
        plan_acumulado_rebajas_porcentaje = round(
            (plan_acumulado_rebajas * 100) / plan_acumulado_saldo, 1)
        ventas_acumulado_desviacion = ventas_acumulado - plan_acumulado
        rebajas_acumulado_desviacion = rebajas_acumulado - plan_acumulado_rebajas
        ventas_netas_acumulado_desviacion = desviacion_rebajas - plan_acumulado_saldo
        ventas_acumulado_desviacion_porcentaje = round(
            (ventas_acumulado_desviacion * 100) / plan_acumulado, 1)
        rebajas_acumulado_desviacion_porcentaje = round(
            (rebajas_acumulado_desviacion * 100) / plan_acumulado_rebajas, 1)
        desviacion_rebajas_desviacion_procentaje = round(
            (ventas_netas_acumulado_desviacion * 100) / plan_acumulado_saldo, 1)
        last_year = int(year_full.strip())
        last_year = (last_year - 1)
        date_start_last_year = (str(last_year) + '/01/01')
        date_end_last_year = (str(last_year) + '/' +
                              str(month) + '/' + str(day))
        accounts = ([6932, 6933, 6934, 6935, 6936, 6937, 6938, 6939])
        ventas_acumulado_credit_last_year = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        ventas_acumulado_debit_last_year = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        ventas_acumulado_last_year = round(
            (ventas_acumulado_credit_last_year - ventas_acumulado_debit_last_year), 0)
        accounts = ([6942, 6943, 6944, 6945, 6946, 6947, 6948, 6949,
                     6950, 6951, 6952, 6953, 6954, 6955, 6956, 6957, 6958])
        rebajas_credit_acumulado_last_year = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        rebajas_debit_acumulado_last_year = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        rebajas_acumulado_last_year = round(
            rebajas_debit_acumulado_last_year - rebajas_credit_acumulado_last_year, 0)
        rebajas_acumulado_last_year_saldo = ventas_acumulado_last_year - \
            rebajas_acumulado_last_year
        ventas_acumulado_last_year_porcentaje = round(
            (ventas_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo, 1)
        rebajas_acumulado_last_year_porcentaje = round(
            (rebajas_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo, 1)

        accounts = ([6961, 6962, 6963, 6964, 6965, 6966, 6967, 6968,
                     6969, 6970, 6972, 6973, 6974, 6975, 6976, 6977, 6978, 6979, 6980])
        costo_venta_debit = get_value_debit(accounts, date_start, date_stop)
        costo_venta_credit = get_value_credit(accounts, date_start, date_stop)
        costo_venta_real = costo_venta_debit - costo_venta_credit

        utilidad_bruta_real = ventas_netas - costo_venta_real
        utilidad_porcentaje = round(
            (utilidad_bruta_real * 100) / ventas_netas, 1)
        costo_venta_plan = get_value_plan(
            str_month, year_full, 'COSTO DE VENTA')
        utilidad_bruta_plan = plan_saldo - costo_venta_plan
        utilidad_bruta_plan_procentaje = round(
            (utilidad_bruta_plan * 100) / plan_saldo, 0)
        costo_venta_desviacion = costo_venta_plan - costo_venta_real
        utilidad_bruta_desviacion = utilidad_bruta_real - utilidad_bruta_plan

        accounts = ([6961, 6962, 6963, 6964, 6965, 6966, 6967, 6968,
                     6969, 6970, 6972, 6973, 6974, 6975, 6976, 6977, 6978, 6979, 6980])
        costo_venta_debit_plan_acumulado = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        costo_venta_credit_plan_acumulado = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        costo_venta_acumulado = costo_venta_debit_plan_acumulado - \
            costo_venta_credit_plan_acumulado

        utilidad_bruta_acumulado_saldo = desviacion_rebajas - costo_venta_acumulado

        costo_venta_acumulado_porcentaje = (
            costo_venta_acumulado * 100) / desviacion_rebajas

        utilidad_bruta_acumulado_saldo_porcentaje = round(
            (utilidad_bruta_acumulado_saldo * 100) / desviacion_rebajas, 1)
        costo_venta_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'COSTO DE VENTA')
        utilidad_bruta_plan_saldo = plan_acumulado_saldo - costo_venta_plan_acumulado
        costo_venta_plan_acumulado_porcentaje = round(
            (costo_venta_plan_acumulado * 100) / plan_acumulado_saldo, 1)
        utilidad_bruta_plan_saldo_porcentaje = round(
            (utilidad_bruta_plan_saldo * 100) / plan_acumulado_saldo, 1)
        costo_venta_plan_desviacion = costo_venta_plan_acumulado - costo_venta_acumulado
        utilidad_bruta_plan_desviacion = utilidad_bruta_acumulado_saldo - \
            utilidad_bruta_plan_saldo
        costo_venta_plan_desviacion_porcentaje = round(
            (costo_venta_plan_desviacion * 100) / costo_venta_plan_acumulado, 1)
        utilidad_bruta_plan_desviacion_porcentaje = round(
            (utilidad_bruta_plan_desviacion * 100) / utilidad_bruta_plan_saldo, 1)
        accounts = ([6961, 6962, 6963, 6964, 6965, 6966, 6967, 6968,
                     6969, 6970, 6972, 6973, 6974, 6975, 6976, 6977, 6978, 6979, 6980])
        costo_venta_debit_acumulado_last_year = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        costo_venta_credit_acumulado_last_year = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        costo_venta_last_year = round(
            costo_venta_debit_acumulado_last_year - costo_venta_credit_acumulado_last_year, 0)
        costo_venta_last_year_saldo = rebajas_acumulado_last_year_saldo - costo_venta_last_year
        costo_venta_last_year_porcentaje = round(
            (costo_venta_last_year * 100) / rebajas_acumulado_last_year_saldo, 1)
        costo_venta_last_year_saldo_porcentaje = round(
            (costo_venta_last_year_saldo * 100) / rebajas_acumulado_last_year_saldo, 1)

        accounts = ([7132, 7133, 7134, 7135, 7136, 7137, 7138])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        depreciacion_amortizacion = total_debits - total_credits
        accounts = ([6981, 6982, 6983, 6984, 6985, 6986, 6987, 6988, 6989, 6990, 6991, 6992, 6993,
                     6994, 6995, 6996, 6997, 6998, 6999, 7000, 7001, 7002, 7003, 7004, 7005,
                     7006, 7007, 7008, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017,
                     7018, 7019, 7020, 7021, 7022, 7023, 7024, 7025, 7026, 7027, 7028, 7029,
                     7030, 7031, 7032, 7033, 7034, 7035, 7036, 7037, 7038, 7039, 6428, 7040,
                     7041, 7042, 7043, 7044, 7045, 7046, 7047, 7048, 7049, 7050, 7051, 7052,
                     7053, 7054, 7055])
        gastos_operacion_debit = get_value_debit(
            accounts, date_start, date_stop)
        gastos_operacion_credit = get_value_credit(
            accounts, date_start, date_stop)
        gastos_operacion = gastos_operacion_debit - gastos_operacion_credit
        gastos_operacion += depreciacion_amortizacion

        utilidad_operacion = utilidad_bruta_real - gastos_operacion
        gastos_operacion_plan = get_value_plan(
            str_month, year_full, 'GASTOS DE OPERACION')
        utilidad_operacion_plan = utilidad_bruta_plan - gastos_operacion_plan
        gastos_operacion_desviacion = gastos_operacion_plan - gastos_operacion
        utilidad_operacion_desviacion = utilidad_operacion - utilidad_operacion_plan

        accounts = ([7132, 7133, 7134, 7135, 7136, 7137, 7138])
        total_debits = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credits = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        depreciacion_amortizacion_acumulado = total_debits - total_credits
        depreciacion_amortizacion_acumulado_porcentaje = (
            depreciacion_amortizacion_acumulado * 100) / desviacion_rebajas
        accounts = ([6982, 6983, 6984, 6985, 6986, 6987, 6988, 6989, 6990, 6991, 6992, 6993,
                     6994, 6995, 6996, 6997, 6998, 6999, 7000, 7001, 7002, 7003, 7004, 7005,
                     7006, 7007, 7008, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017,
                     7018, 7019, 7020, 7021, 7022, 7023, 7024, 7025, 7026, 7027, 7028, 7029,
                     7030, 7031, 7032, 7033, 7034, 7035, 7036, 7037, 7038, 7039, 6428, 7040,
                     7041, 7042, 7043, 7044, 7045, 7046, 7047, 7048, 7049, 7050, 7051, 7052,
                     7053, 7054, 7055])
        gastos_operacion_debit = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        gastos_operacion_credit = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        gastos_operacion_acumulado = gastos_operacion_debit - gastos_operacion_credit

        gastos_operacion_acumulado += depreciacion_amortizacion_acumulado

        utilidad_operacion_acumulado = utilidad_bruta_acumulado_saldo - \
            gastos_operacion_acumulado
        gastos_operacion_acumulado_porcentaje = (
            gastos_operacion_acumulado * 100) / desviacion_rebajas
        utilidad_operacion_acumulado_porcentaje = utilidad_bruta_acumulado_saldo_porcentaje - \
            gastos_operacion_acumulado_porcentaje
        depreciacion_amortizacion_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'DEPRECIACIONES Y AMORTIZACIONES')
        depreciacion_amortizacion_plan_acumulado_porcentaje = (
            depreciacion_amortizacion_plan_acumulado * 100) / plan_acumulado_saldo
        gastos_operacion_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'GASTOS DE OPERACION')
        gastos_operacion_plan_acumulado += depreciacion_amortizacion_plan_acumulado
        utilidad_operacion_plan_acumulado = utilidad_bruta_plan_saldo - \
            gastos_operacion_plan_acumulado
        gastos_operacion_plan_acumulado_porcentaje = (
            gastos_operacion_plan_acumulado * 100) / plan_acumulado_saldo
        utilidad_operacion_plan_acumulado_porcentaje = utilidad_bruta_plan_saldo_porcentaje - \
            gastos_operacion_plan_acumulado_porcentaje
        gastos_operacion_plan_acumulado_desviacion = gastos_operacion_acumulado - \
            gastos_operacion_plan_acumulado
        utilidad_operacion_plan_acumulado_desviacion = utilidad_bruta_plan_desviacion - \
            gastos_operacion_plan_acumulado_desviacion
        gastos_operacion_plan_acumulado_desviacion_porcentaje = (
            gastos_operacion_plan_acumulado_desviacion * 100) / gastos_operacion_plan_acumulado
        utilidad_operacion_plan_acumulado_desviacion_porcentaje = (
            utilidad_operacion_plan_acumulado_desviacion * 100) / utilidad_operacion_plan_acumulado

        accounts = ([7132, 7133, 7134, 7135, 7136, 7137, 7138])
        total_debits = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credits = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        depreciacion_amortizacion_last_year = total_debits - total_credits

        accounts = ([6982, 6983, 6984, 6985, 6986, 6987, 6988, 6989, 6990, 6991, 6992, 6993,
                     6994, 6995, 6996, 6997, 6998, 6999, 7000, 7001, 7002, 7003, 7004, 7005,
                     7006, 7007, 7008, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017,
                     7018, 7019, 7020, 7021, 7022, 7023, 7024, 7025, 7026, 7027, 7028, 7029,
                     7030, 7031, 7032, 7033, 7034, 7035, 7036, 7037, 7038, 7039, 6428, 7040,
                     7041, 7042, 7043, 7044, 7045, 7046, 7047, 7048, 7049, 7050, 7051, 7052,
                     7053, 7054, 7055])
        gastos_operacion_debit = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        gastos_operacion_credit = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        gastos_operacion_acumulado_last_year = gastos_operacion_debit - gastos_operacion_credit

        gastos_operacion_acumulado_last_year += depreciacion_amortizacion_last_year

        utilidad_operacion_acumulado_last_year = costo_venta_last_year_saldo - \
            gastos_operacion_acumulado_last_year
        gastos_operacion_acumulado_last_year_porcentaje = (
            gastos_operacion_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        utilidad_operacion_acumulado_last_year_porcentaje = costo_venta_last_year_saldo_porcentaje - \
            gastos_operacion_acumulado_last_year_porcentaje
        accounts = ([7139])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        perdida_cambiaria = total_credits - total_debits

        accounts = ([7140, 7141])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        intereses_pagados = total_credits - total_debits

        accounts = ([7143])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        ingresos_interes = total_credits - total_debits
        accounts = ([7142])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        utilidad_cambiaria = total_credits - total_debits
        perdida_cambiaria_plan = get_value_plan(
            str_month, year_full, 'PERDIDA CAMBIARIA')

        intereses_pagados_plan = get_value_plan(
            str_month, year_full, 'INTERESES PAGADOS')

        intereses_pagados_desviacion = intereses_pagados - intereses_pagados_plan

        ingresos_interes_plan = get_value_plan(
            str_month, year_full, 'INGRESOS POR INTERES')
        utilidad_cambiaria_plan = get_value_plan(
            str_month, year_full, 'UTILIDAD CAMBIARIA')
        perdida_cambiaria_desviacion = perdida_cambiaria_plan - perdida_cambiaria
        ingresos_interes_desviacion = ingresos_interes - ingresos_interes_plan
        utilidad_cambiaria_desviacion = utilidad_cambiaria - utilidad_cambiaria_plan
        perdida_cambiaria_saldo = perdida_cambiaria + \
            ingresos_interes + utilidad_cambiaria + intereses_pagados
        ingresos_interes_saldo = perdida_cambiaria_plan + \
            ingresos_interes_plan + utilidad_cambiaria_plan + intereses_pagados_plan
        utilidad_cambiaria_saldo = perdida_cambiaria_saldo - ingresos_interes_saldo
        accounts = ([7139])
        total_debits = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credits = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        perdida_cambiaria_acumulado = total_credits - total_debits

        accounts = ([7140, 7141])
        total_debits = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credits = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        intereses_pagados_acumulado = total_credits - total_debits

        intereses_pagados_acumulado_porcentaje = (
            intereses_pagados_acumulado * 100) / desviacion_rebajas

        intereses_pagados_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'INTERESES PAGADOS')
        intereses_pagados_plan_acumulado_porcentaje = (
            intereses_pagados_plan_acumulado * 100) / plan_acumulado_saldo

        intereses_pagados_plan_desviacion = intereses_pagados_acumulado - \
            intereses_pagados_plan_acumulado
        intereses_pagados_plan_desviacion_porcentaje = (
            intereses_pagados_plan_desviacion * 100) / ventas_netas_acumulado_desviacion

        accounts = ([7140, 7141])
        total_debits = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credits = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        intereses_pagados_acumulado_last_year = total_credits - total_debits
        intereses_pagados_acumulado_last_year_porcentaje = (
            intereses_pagados_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo

        accounts = ([7143])
        total_debits = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credits = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        ingresos_interes_acumulado = total_credits - total_debits
        accounts = ([7142])
        total_debits = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credits = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        utilidad_cambiaria_acumulado = total_credits - total_debits
        perdida_cambiaria_acumulado_saldo = perdida_cambiaria_acumulado + \
            ingresos_interes_acumulado + utilidad_cambiaria_acumulado + \
            intereses_pagados_acumulado
        perdida_cambiaria_acumulado_porcentaje = (
            perdida_cambiaria_acumulado * 100) / desviacion_rebajas
        ingresos_interes_acumulado_porcentaje = (
            ingresos_interes_acumulado * 100) / desviacion_rebajas
        utilidad_cambiaria_acumulado_porcentaje = (
            utilidad_cambiaria_acumulado * 100) / desviacion_rebajas
        perdida_cambiaria_acumulado_saldo_porcentaje = (
            perdida_cambiaria_acumulado_saldo * 100) / desviacion_rebajas
        perdida_cambiaria_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'PERDIDA CAMBIARIA')
        ingresos_interes_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'INGRESOS POR INTERES')
        utilidad_cambiaria_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'UTILIDAD CAMBIARIA')
        utilidad_cambiaria_plan_acumulado_saldo = perdida_cambiaria_plan_acumulado + \
            ingresos_interes_plan_acumulado + utilidad_cambiaria_plan_acumulado + \
            intereses_pagados_plan_acumulado
        perdida_cambiaria_plan_acumulado_porcentaje = (
            perdida_cambiaria_plan_acumulado * 100) / plan_acumulado_saldo
        ingresos_interes_plan_acumulado_porcentaje = (
            ingresos_interes_plan_acumulado * 100) / plan_acumulado_saldo
        utilidad_cambiaria_plan_acumulado_porcentaje = (
            utilidad_cambiaria_plan_acumulado * 100) / plan_acumulado_saldo
        utilidad_cambiaria_plan_acumulado_saldo_porcentaje = (
            utilidad_cambiaria_plan_acumulado_saldo * 100) / plan_acumulado_saldo
        perdida_cambiaria_plan_acumulado_desviacion = perdida_cambiaria_acumulado - \
            perdida_cambiaria_plan_acumulado
        ingresos_interes_plan_acumulado_desviacion = ingresos_interes_acumulado - \
            ingresos_interes_plan_acumulado
        utilidad_cambiaria_plan_acumulado_desviacion = utilidad_cambiaria_acumulado - \
            utilidad_cambiaria_plan_acumulado
        utilidad_cambiaria_plan_acumulado_saldo_desviacion = perdida_cambiaria_acumulado_saldo - \
            utilidad_cambiaria_plan_acumulado_saldo
        perdida_cambiaria_plan_acumulado_desviacion_porcentaje = (
            perdida_cambiaria_plan_acumulado_desviacion * 100) / perdida_cambiaria_plan_acumulado
        ingresos_interes_plan_acumulado_desviacion_desviacion = (
            ingresos_interes_plan_acumulado_desviacion * 100) / ingresos_interes_plan_acumulado
        utilidad_cambiaria_plan_acumulado_desviacion_porcentaje = (
            utilidad_cambiaria_plan_acumulado_desviacion * 100) / utilidad_cambiaria_plan_acumulado
        utilidad_cambiaria_plan_acumulado_saldo_desviacion_porcentaje = (
            utilidad_cambiaria_plan_acumulado_saldo_desviacion * 100) / utilidad_cambiaria_plan_acumulado_saldo
        accounts = ([7139])
        total_debits = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credits = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        perdida_cambiaria_acumulado_last_year = total_credits - total_debits
        accounts = ([7143])
        total_debits = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credits = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        ingresos_interes_acumulado_last_year = total_credits - total_debits
        accounts = ([7142])
        total_debits = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credits = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        utilidad_cambiaria_acumulado_last_year = total_credits - total_debits
        perdida_cambiaria_acumulado_last_year_saldo = perdida_cambiaria_acumulado_last_year + \
            ingresos_interes_acumulado_last_year + utilidad_cambiaria_acumulado_last_year
        perdida_cambiaria_acumulado_last_year_porcentaje = (
            perdida_cambiaria_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        ingresos_interes_acumulado_last_year_porcentaje = (
            ingresos_interes_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        utilidad_cambiaria_acumulado_last_year_porcentaje = (
            utilidad_cambiaria_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        perdida_cambiaria_acumulado_last_year_saldo_porcentaje = (
            perdida_cambiaria_acumulado_last_year_saldo * 100) / rebajas_acumulado_last_year_saldo
        accounts = ([7144])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        otros_gastos = total_debits - total_credits
        accounts = ([6960])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        otros_ingresos = total_credits - total_debits
        otros_gastos_plan = get_value_plan(
            str_month, year_full, 'OTROS GASTOS')
        otros_ingresos_plan = get_value_plan(
            str_month, year_full, 'OTROS INGRESOS')
        otros_gastos_desviacion = otros_gastos_plan - otros_gastos
        otros_ingresos_desviacion = otros_ingresos - otros_ingresos_plan
        utilidad_antes_impuestos = utilidad_operacion + \
            perdida_cambiaria_saldo + (otros_ingresos - otros_gastos)
        utilidad_antes_impuestos_plan = utilidad_operacion_plan + \
            ingresos_interes_saldo + (otros_ingresos_plan - otros_gastos_plan)
        utilidad_antes_impuestos_desviacion = utilidad_operacion_desviacion + \
            utilidad_cambiaria_saldo + \
            (otros_ingresos_desviacion - otros_gastos_desviacion)
        accounts = ([7144])
        total_debit = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credit = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        otros_gastos_acumulado = total_debit - total_credit
        accounts = ([6960])
        total_debit = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credit = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        otros_ingresos_acumulado = total_credit - total_debit
        utilidad_antes_impuestos_acumulado = utilidad_operacion_acumulado + \
            perdida_cambiaria_acumulado_saldo + \
            (otros_ingresos_acumulado - otros_gastos_acumulado)
        otros_gastos_acumulado_porcentaje = (
            otros_gastos_acumulado * 100) / desviacion_rebajas
        otros_ingresos_acumulado_porcentaje = (
            otros_ingresos_acumulado * 100) / desviacion_rebajas
        utilidad_antes_impuestos_acumulado_porcentaje = (
            utilidad_antes_impuestos_acumulado * 100) / desviacion_rebajas
        otros_gastos_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'OTROS GASTOS')
        otros_ingresos_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'OTROS INGRESOS')
        utilidad_antes_impuestos_plan_acumulado = utilidad_operacion_plan_acumulado + \
            utilidad_cambiaria_plan_acumulado_saldo + \
            (otros_ingresos_plan_acumulado - otros_gastos_plan_acumulado)
        otros_gastos_plan_acumulado_porcentaje = (
            otros_gastos_plan_acumulado * 100) / plan_acumulado_saldo
        otros_ingresos_plan_acumulado_porcentaje = (
            otros_ingresos_plan_acumulado * 100) / plan_acumulado_saldo
        utilidad_antes_impuestos_plan_acumulado_porcentaje = (
            utilidad_antes_impuestos_plan_acumulado * 100) / plan_acumulado_saldo
        otros_gastos_plan_acumulado_desviacion = otros_gastos_plan_acumulado - \
            otros_gastos_acumulado
        otros_ingresos_plan_acumulado_desviacion = otros_ingresos_acumulado - \
            otros_ingresos_plan_acumulado
        utilidad_antes_impuestos_plan_acumulado_desviacion = utilidad_antes_impuestos_acumulado - \
            utilidad_antes_impuestos_plan_acumulado
        if otros_gastos_plan_acumulado <= 0:
            otros_gastos_plan_acumulado_desviacion_porcentaje = 0
        else:
            otros_gastos_plan_acumulado_desviacion_porcentaje = (
                otros_gastos_plan_acumulado_desviacion * 100) / otros_gastos_plan_acumulado
        otros_ingresos_plan_acumulado_desviacion_porcentaje = (
            otros_ingresos_plan_acumulado_desviacion * 100) / otros_ingresos_plan_acumulado
        utilidad_antes_impuestos_plan_acumulado_desviacion_porcentaje = (
            utilidad_antes_impuestos_plan_acumulado_desviacion * 100) / utilidad_antes_impuestos_plan_acumulado
        accounts = ([7144])
        total_debit = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credit = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        otros_gastos_acumulado_last_year = total_debit - total_credit
        accounts = ([6960])
        total_debit = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credit = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        otros_ingresos_acumulado_last_year = total_credit - total_debit
        utilidad_antes_impuestos_plan_acumulado_last_year = utilidad_operacion_acumulado_last_year + perdida_cambiaria_acumulado_last_year_saldo + (otros_ingresos_acumulado_last_year
                                                                                                                                                    - otros_gastos_acumulado_last_year)
        otros_gastos_acumulado_last_year_porcentaje = (
            otros_gastos_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        otros_ingresos_acumulado_last_year_porcentaje = (
            otros_ingresos_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        utilidad_antes_impuestos_plan_acumulado_last_year_porcentaje = (
            utilidad_antes_impuestos_plan_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        accounts = ([7131])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        isr = total_debits - total_credits
        accounts = ([6924])
        total_debits = get_value_debit(
            accounts, date_start, date_stop)
        total_credits = get_value_credit(
            accounts, date_start, date_stop)
        ptu = total_credits - total_debits
        isr_plan = get_value_plan(
            str_month, year_full, 'ISR')
        ptu_plan = get_value_plan(
            str_month, year_full, 'PTU')
        isr_desviacion = isr_plan - isr
        ptu_desviacion = ptu_plan - ptu
        isr_ptu = isr + ptu
        isr_plan_ptu_plan = isr_plan + ptu_plan
        isr_desviacion_ptu_desviacion = isr_desviacion + ptu_desviacion
        accounts = ([7131])
        total_debits = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credits = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        isr_acumulado = total_debits - total_credits
        accounts = ([6924])
        total_debits = get_value_debit(
            accounts, date_start_fisrt_day, date_stop)
        total_credits = get_value_credit(
            accounts, date_start_fisrt_day, date_stop)
        ptu_acumulado = total_credits - total_debits
        isr_ptu_acumulado = isr_acumulado + ptu_acumulado
        isr_acumulado_porcentaje = (isr_acumulado * 100) / desviacion_rebajas
        ptu_acumulado_porcentaje = (ptu_acumulado * 100) / desviacion_rebajas
        isr_ptu_acumulado_porcentaje = (
            isr_ptu_acumulado * 100) / desviacion_rebajas
        isr_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'ISR')
        ptu_plan_acumulado = get_value_plan_acumulado(
            lista, year_full, 'PTU')
        isr_plan_ptu_plan_acumulado = isr_plan_acumulado + ptu_plan_acumulado
        isr_plan_acumulado_porcentaje = (
            isr_plan_acumulado * 100) / plan_acumulado_saldo
        ptu_plan_acumulado_porcentaje = (
            ptu_plan_acumulado * 100) / plan_acumulado_saldo
        isr_plan_ptu_plan_acumulado_porcentaje = (
            isr_plan_ptu_plan_acumulado * 100) / plan_acumulado_saldo
        isr_plan_desviacion = isr_plan_acumulado - isr_acumulado
        ptu_plan_desviacion = ptu_plan_acumulado - ptu_acumulado
        isr_plan_ptu_plan_desviacion = isr_plan_ptu_plan_acumulado - isr_ptu_acumulado
        isr_plan_desviacion_porcentaje = (
            isr_plan_desviacion * 100) / isr_plan_acumulado
        ptu_plan_desviacion_porcentaje = (
            ptu_plan_desviacion * 100) / ptu_plan_acumulado
        isr_plan_ptu_plan_desviacion_porcentaje = (
            isr_plan_ptu_plan_desviacion * 100) / isr_plan_ptu_plan_acumulado
        accounts = ([7131])
        total_debits = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credits = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        isr_acumulado_last_year = total_debits - total_credits
        accounts = ([6924])
        total_debits = get_value_debit(
            accounts, date_start_last_year, date_end_last_year)
        total_credits = get_value_credit(
            accounts, date_start_last_year, date_end_last_year)
        ptu_acumulado_last_year = total_credits - total_debits
        isr_ptu_acumulado_last_year = isr_acumulado_last_year + ptu_acumulado_last_year
        isr_acumulado_last_year_porcentaje = (
            isr_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        ptu_acumulado_last_year_porcentaje = (
            ptu_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        isr_ptu_acumulado_last_year_porcentaje = (
            isr_ptu_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo
        utilidad_neta = utilidad_antes_impuestos - isr_ptu
        utilidad_neta_plan = utilidad_antes_impuestos_plan - isr_plan_ptu_plan
        if utilidad_antes_impuestos_desviacion <= 0:
            utilidad_neta_desviacion = utilidad_antes_impuestos_desviacion + \
                isr_desviacion_ptu_desviacion
        else:
            utilidad_neta_desviacion = utilidad_antes_impuestos_desviacion - \
                isr_desviacion_ptu_desviacion
        utilidad_neta_acumulado = utilidad_antes_impuestos_acumulado - isr_ptu_acumulado
        utilidad_neta_acumulado_porcentaje = (
            utilidad_neta_acumulado * 100) / desviacion_rebajas
        utilidad_neta_plan_acumulado = utilidad_antes_impuestos_plan_acumulado - \
            isr_plan_ptu_plan_acumulado
        utilidad_neta_plan_acumulado_porcentaje = (
            utilidad_neta_plan_acumulado * 100) / plan_acumulado_saldo
        if utilidad_antes_impuestos_plan_acumulado_desviacion <= 0:
            utilidad_neta_desviacion_acumulado = utilidad_antes_impuestos_plan_acumulado_desviacion + \
                isr_plan_ptu_plan_desviacion
        else:
            utilidad_neta_desviacion_acumulado = utilidad_antes_impuestos_plan_acumulado_desviacion - \
                isr_plan_ptu_plan_desviacion
        utilidad_neta_desviacion_acumulado_porcentaje = (
            utilidad_neta_desviacion_acumulado * 100) / utilidad_neta_plan_acumulado
        utilidad_neta_last_year = utilidad_antes_impuestos_plan_acumulado_last_year - \
            isr_ptu_acumulado_last_year
        utilidad_neta_last_year_porcentaje = (
            utilidad_neta_last_year * 100) / rebajas_acumulado_last_year_saldo

        ebitda_periodo = depreciacion_amortizacion + utilidad_antes_impuestos
        ebitda_periodo_porcentaje = (ebitda_periodo * 100) / ventas_netas

        ebitda_periodo_acumulado = depreciacion_amortizacion_acumulado + \
            utilidad_antes_impuestos_acumulado

        ebitda_periodo_acumulado_porcentaje = (
            ebitda_periodo_acumulado * 100) / desviacion_rebajas

        depreciacion_amortizacion_plan_acumulado_porcentaje = (
            depreciacion_amortizacion_plan_acumulado * 100) / plan_acumulado_saldo
        ebitda_periodo_plan_acumulado = depreciacion_amortizacion_plan_acumulado + \
            utilidad_antes_impuestos_plan_acumulado
        ebitda_periodo_plan_acumulado_porcentaje = (
            ebitda_periodo_plan_acumulado * 100) / plan_acumulado_saldo

        depreciacion_amortizacion_last_year_porcentaje = (
            depreciacion_amortizacion_last_year * 100) / rebajas_acumulado_last_year_saldo
        ebitda_periodo_acumulado_last_year = depreciacion_amortizacion_last_year + \
            utilidad_antes_impuestos_plan_acumulado_last_year
        ebitda_periodo_acumulado_last_year_porcentaje = (
            ebitda_periodo_acumulado_last_year * 100) / rebajas_acumulado_last_year_saldo

        print('Ventas;',
              ventas, ';',
              plan, ';',
              ventas_desviacion, ';',
              ventas_acumulado, ';',
              ventas_acumulado_porcentaje, ';',
              plan_acumulado, ';',
              plan_acumulado_porcentaje, ';',
              ventas_acumulado_desviacion, ';',
              ventas_acumulado_desviacion_porcentaje, ';',
              ventas_acumulado_last_year, ';',
              ventas_acumulado_last_year_porcentaje
              )
        print('Rebajas;',
              rebajas, ';',
              plan_rebajas, ';',
              rebajas_desviacion, ';',
              rebajas_acumulado, ';',
              rebajas_acumulado_procentaje, ';',
              plan_acumulado_rebajas, ';',
              plan_acumulado_rebajas_porcentaje, ';',
              rebajas_acumulado_desviacion, ';',
              rebajas_acumulado_desviacion_porcentaje, ';',
              rebajas_acumulado_last_year, ';',
              rebajas_acumulado_last_year_porcentaje
              )
        print('Ventas Netas;',
              ventas_netas, ';',
              plan_saldo, ';',
              ventas_netas_desviacion, ';',
              desviacion_rebajas, ';',
              '100% ;',
              plan_acumulado_saldo, ';',
              '100% ;',
              ventas_netas_acumulado_desviacion, ';',
              desviacion_rebajas_desviacion_procentaje, ';',
              rebajas_acumulado_last_year_saldo, ';',
              '100% ;'
              )
        print('')
        print('Costo de venta;',
              costo_venta_real, ';',
              costo_venta_plan, ';',
              costo_venta_desviacion, ';',
              costo_venta_acumulado, ';',
              costo_venta_acumulado_porcentaje, ';',
              costo_venta_plan_acumulado, ';',
              costo_venta_plan_acumulado_porcentaje, ';',
              costo_venta_plan_desviacion, ';',
              costo_venta_plan_desviacion_porcentaje, ';',
              costo_venta_last_year, ';',
              costo_venta_last_year_porcentaje
              )
        print('Utilidad bruta;',
              utilidad_bruta_real, ';',
              utilidad_bruta_plan, ';',
              utilidad_bruta_desviacion, ';',
              utilidad_bruta_acumulado_saldo, ';',
              utilidad_bruta_acumulado_saldo_porcentaje, ';',
              utilidad_bruta_plan_saldo, ';',
              utilidad_bruta_plan_saldo_porcentaje, ';',
              utilidad_bruta_plan_desviacion, ';',
              utilidad_bruta_plan_desviacion_porcentaje, ';',
              costo_venta_last_year_saldo, ';',
              costo_venta_last_year_saldo_porcentaje
              )
        print(';',
              utilidad_porcentaje, ';',
              utilidad_bruta_plan_procentaje
              )
        print('')
        print('Gastos de operacion', ';',
              gastos_operacion, ';',
              gastos_operacion_plan, ';',
              gastos_operacion_desviacion, ';',
              gastos_operacion_acumulado, ';',
              gastos_operacion_acumulado_porcentaje, ';',
              gastos_operacion_plan_acumulado, ';',
              gastos_operacion_plan_acumulado_porcentaje, ';',
              gastos_operacion_plan_acumulado_desviacion, ';',
              gastos_operacion_plan_acumulado_desviacion_porcentaje, ';',
              gastos_operacion_acumulado_last_year, ';',
              gastos_operacion_acumulado_last_year_porcentaje
              )
        print('Utilidad de operacion', ';',
              utilidad_operacion, ';',
              utilidad_operacion_plan, ';',
              utilidad_operacion_desviacion, ';',
              utilidad_operacion_acumulado, ';',
              utilidad_operacion_acumulado_porcentaje, ';',
              utilidad_operacion_plan_acumulado, ';',
              utilidad_operacion_plan_acumulado_porcentaje, ';',
              utilidad_operacion_plan_acumulado_desviacion, ';',
              utilidad_operacion_plan_acumulado_desviacion_porcentaje, ';',
              utilidad_operacion_acumulado_last_year, ';',
              utilidad_operacion_acumulado_last_year_porcentaje
              )
        print('')
        print('Intereses Ganados', ';',
              ingresos_interes, ';',
              ingresos_interes_plan, ';',
              ingresos_interes_desviacion, ';',
              ingresos_interes_acumulado, ';',
              ingresos_interes_acumulado_porcentaje, ';',
              ingresos_interes_plan_acumulado, ';',
              ingresos_interes_plan_acumulado_porcentaje, ';',
              ingresos_interes_plan_acumulado_desviacion, ';',
              ingresos_interes_plan_acumulado_desviacion_desviacion, ';',
              ingresos_interes_acumulado_last_year, ';',
              ingresos_interes_acumulado_last_year_porcentaje
              )
        print('Intereses Pagados;',
              intereses_pagados, ';',
              intereses_pagados_plan, ';',
              intereses_pagados_desviacion, ';',
              intereses_pagados_acumulado, ';',
              intereses_pagados_acumulado_porcentaje, ';',
              intereses_pagados_plan_acumulado, ';',
              intereses_pagados_plan_acumulado_porcentaje, ';',
              intereses_pagados_plan_desviacion, ';',
              intereses_pagados_plan_desviacion_porcentaje, ';',
              intereses_pagados_acumulado_last_year, ';',
              intereses_pagados_acumulado_last_year_porcentaje
              )
        print('Perdida cambiaria', ';',
              perdida_cambiaria, ';',
              perdida_cambiaria_plan, ';',
              perdida_cambiaria_desviacion, ';',
              perdida_cambiaria_acumulado, ';',
              perdida_cambiaria_acumulado_porcentaje, ';',
              perdida_cambiaria_plan_acumulado, ';',
              perdida_cambiaria_plan_acumulado_porcentaje, ';',
              perdida_cambiaria_plan_acumulado_desviacion, ';',
              perdida_cambiaria_plan_acumulado_desviacion_porcentaje, ';',
              perdida_cambiaria_acumulado_last_year, ';',
              perdida_cambiaria_acumulado_last_year_porcentaje
              )
        print('Utilidad cambiaria', ';',
              utilidad_cambiaria, ';',
              utilidad_cambiaria_plan, ';',
              utilidad_cambiaria_desviacion, ';',
              utilidad_cambiaria_acumulado, ';',
              utilidad_cambiaria_acumulado_porcentaje, ';',
              utilidad_cambiaria_plan_acumulado, ';',
              utilidad_cambiaria_plan_acumulado_porcentaje, ';',
              utilidad_cambiaria_plan_acumulado_desviacion, ';',
              utilidad_cambiaria_plan_acumulado_desviacion_porcentaje, ';',
              utilidad_cambiaria_acumulado_last_year, ';',
              utilidad_cambiaria_acumulado_last_year_porcentaje
              )
        print(';',
              perdida_cambiaria_saldo, ';',
              ingresos_interes_saldo, ';',
              utilidad_cambiaria_saldo, ';',
              perdida_cambiaria_acumulado_saldo, ';',
              perdida_cambiaria_acumulado_saldo_porcentaje, ';',
              utilidad_cambiaria_plan_acumulado_saldo, ';',
              utilidad_cambiaria_plan_acumulado_saldo_porcentaje, ';',
              utilidad_cambiaria_plan_acumulado_saldo_desviacion, ';',
              utilidad_cambiaria_plan_acumulado_saldo_desviacion_porcentaje, ';',
              perdida_cambiaria_acumulado_last_year_saldo, ';',
              perdida_cambiaria_acumulado_last_year_saldo_porcentaje
              )
        print('')
        print('Otros Gastos;',
              otros_gastos, ';',
              otros_gastos_plan, ';',
              otros_gastos_desviacion, ';',
              otros_gastos_acumulado, ';',
              otros_gastos_acumulado_porcentaje, ';',
              otros_gastos_plan_acumulado, ';',
              otros_gastos_plan_acumulado_porcentaje, ';',
              otros_gastos_plan_acumulado_desviacion, ';',
              otros_gastos_plan_acumulado_desviacion_porcentaje, ';',
              otros_gastos_acumulado_last_year, ';',
              otros_gastos_acumulado_last_year_porcentaje
              )
        print('Otros Ingresos;',
              otros_ingresos, ';',
              otros_ingresos_plan, ';',
              otros_ingresos_desviacion, ';',
              otros_ingresos_acumulado, ';',
              otros_ingresos_acumulado_porcentaje, ';',
              otros_ingresos_plan_acumulado, ';',
              otros_ingresos_plan_acumulado_porcentaje, ';',
              otros_ingresos_plan_acumulado_desviacion, ';',
              otros_ingresos_plan_acumulado_desviacion_porcentaje, ';',
              otros_ingresos_acumulado_last_year, ';',
              otros_ingresos_acumulado_last_year_porcentaje
              )
        print('UAI;',
              utilidad_antes_impuestos, ';',
              utilidad_antes_impuestos_plan, ';',
              utilidad_antes_impuestos_desviacion, ';',
              utilidad_antes_impuestos_acumulado, ';',
              utilidad_antes_impuestos_acumulado_porcentaje, ';',
              utilidad_antes_impuestos_plan_acumulado, ';',
              utilidad_antes_impuestos_plan_acumulado_porcentaje, ';',
              utilidad_antes_impuestos_plan_acumulado_desviacion, ';',
              utilidad_antes_impuestos_plan_acumulado_desviacion_porcentaje, ';',
              utilidad_antes_impuestos_plan_acumulado_last_year, ';',
              utilidad_antes_impuestos_plan_acumulado_last_year_porcentaje
              )
        print('')
        print('ISR;',
              isr, ';',
              isr_plan, ';',
              isr_desviacion, ';',
              isr_acumulado, ';',
              isr_acumulado_porcentaje, ';',
              isr_plan_acumulado, ';',
              isr_plan_acumulado_porcentaje, ';',
              isr_plan_desviacion, ';',
              isr_plan_desviacion_porcentaje, ';',
              isr_acumulado_last_year, ';',
              isr_acumulado_last_year_porcentaje
              )
        print('PTU;',
              ptu, ';',
              ptu_plan, ';',
              ptu_desviacion, ';',
              ptu_acumulado, ';',
              ptu_acumulado_porcentaje, ';',
              ptu_plan_acumulado, ';',
              ptu_plan_acumulado_porcentaje, ';',
              ptu_plan_desviacion, ';',
              ptu_plan_desviacion_porcentaje, ';',
              ptu_acumulado_last_year, ';',
              ptu_acumulado_last_year_porcentaje
              )
        print(';',
              isr_ptu, ';',
              isr_plan_ptu_plan, ';',
              isr_desviacion_ptu_desviacion, ';',
              isr_ptu_acumulado, ';',
              isr_ptu_acumulado_porcentaje, ';',
              isr_plan_ptu_plan_acumulado, ';',
              isr_plan_ptu_plan_acumulado_porcentaje, ';',
              isr_plan_ptu_plan_desviacion, ';',
              isr_plan_ptu_plan_desviacion_porcentaje, ';',
              isr_ptu_acumulado_last_year, ';',
              isr_ptu_acumulado_last_year_porcentaje
              )
        print('')
        print('Utilidad Neta;',
              utilidad_neta, ';',
              utilidad_neta_plan, ';',
              utilidad_neta_desviacion, ';',
              utilidad_neta_acumulado, ';',
              utilidad_neta_acumulado_porcentaje, ';',
              utilidad_neta_plan_acumulado, ';',
              utilidad_neta_plan_acumulado_porcentaje, ';',
              utilidad_neta_desviacion_acumulado, ';',
              utilidad_neta_desviacion_acumulado_porcentaje, ';',
              utilidad_neta_last_year, ';',
              utilidad_neta_last_year_porcentaje
              )
        print('')
        print('UAI;',
              utilidad_antes_impuestos, ';;;',
              utilidad_antes_impuestos_acumulado, ';',
              utilidad_antes_impuestos_acumulado_porcentaje, ';',
              utilidad_antes_impuestos_plan_acumulado, ';',
              utilidad_antes_impuestos_plan_acumulado_porcentaje, ';;;',
              utilidad_antes_impuestos_plan_acumulado_last_year, ';',
              utilidad_antes_impuestos_plan_acumulado_last_year_porcentaje
              )
        print('Drepeciacion y Mortizacion;',
              depreciacion_amortizacion, ';;;',
              depreciacion_amortizacion_acumulado, ';',
              depreciacion_amortizacion_acumulado_porcentaje, ';',
              depreciacion_amortizacion_plan_acumulado, ';',
              depreciacion_amortizacion_plan_acumulado_porcentaje, ';;;',
              depreciacion_amortizacion_last_year, ';',
              depreciacion_amortizacion_last_year_porcentaje
              )
        print('')
        print('Ebitda Del Periodo;',
              ebitda_periodo, ';;;',
              ebitda_periodo_acumulado, ';',
              ebitda_periodo_acumulado_porcentaje, ';',
              ebitda_periodo_plan_acumulado, ';',
              ebitda_periodo_plan_acumulado_porcentaje, ';;;',
              ebitda_periodo_acumulado_last_year, ';',
              ebitda_periodo_acumulado_last_year_porcentaje
              )
        print(';', ebitda_periodo_porcentaje)

        statement_income_data.create({
            'er_report_id': self.id,
            'ventas': round(ventas, 0),
            'plan': round(plan, 0),
            'ventas_desviacion': round(ventas_desviacion, 0),
            'ventas_acumulado': round(ventas_acumulado, 0),
            'ventas_acumulado_porcentaje': round(ventas_acumulado_porcentaje, 1),
            'plan_acumulado': round(plan_acumulado, 0),
            'plan_acumulado_porcentaje': round(plan_acumulado_porcentaje, 1),
            'ventas_acumulado_desviacion': round(ventas_acumulado_desviacion, 0),
            'ventas_acumulado_desviacion_porcentaje': round(ventas_acumulado_desviacion_porcentaje, 1),
            'ventas_acumulado_last_year': round(ventas_acumulado_last_year, 0),
            'ventas_acumulado_last_year_porcentaje': round(ventas_acumulado_last_year_porcentaje, 1),

            'rebajas': round(rebajas, 0),
            'plan_rebajas': round(plan_rebajas, 0),
            'rebajas_desviacion': round(rebajas_desviacion, 0),
            'rebajas_acumulado': round(rebajas_acumulado, 0),
            'rebajas_acumulado_procentaje': round(rebajas_acumulado_procentaje, 0),
            'plan_acumulado_rebajas': round(plan_acumulado_rebajas, 0),
            'plan_acumulado_rebajas_porcentaje': round(plan_acumulado_rebajas_porcentaje, 1),
            'rebajas_acumulado_desviacion': round(rebajas_acumulado_desviacion, 0),
            'rebajas_acumulado_desviacion_porcentaje': round(rebajas_acumulado_desviacion_porcentaje, 1),
            'rebajas_acumulado_last_year': round(rebajas_acumulado_last_year, 0),
            'rebajas_acumulado_last_year_porcentaje': round(rebajas_acumulado_last_year_porcentaje, 1),

            'ventas_netas': round(ventas_netas, 0),
            'plan_saldo': round(plan_saldo, 0),
            'ventas_netas_desviacion': round(ventas_netas_desviacion, 0),
            'desviacion_rebajas': round(desviacion_rebajas, 0),
            'plan_acumulado_saldo': round(plan_acumulado_saldo, 0),
            'ventas_netas_acumulado_desviacion': round(ventas_netas_acumulado_desviacion, 0),
            'desviacion_rebajas_desviacion_procentaje': round(desviacion_rebajas_desviacion_procentaje, 0),
            'rebajas_acumulado_last_year_saldo': round(rebajas_acumulado_last_year_saldo, 0),

            'costo_venta_real': round(costo_venta_real, 0),
            'costo_venta_plan': round(costo_venta_plan, 0),
            'costo_venta_desviacion': round(costo_venta_desviacion, 0),
            'costo_venta_acumulado': round(costo_venta_acumulado, 0),
            'costo_venta_acumulado_porcentaje': round(costo_venta_acumulado_porcentaje, 1),
            'costo_venta_plan_acumulado': round(costo_venta_plan_acumulado, 0),
            'costo_venta_plan_acumulado_porcentaje': round(costo_venta_plan_acumulado_porcentaje, 1),
            'costo_venta_plan_desviacion': round(costo_venta_plan_desviacion, 0),
            'costo_venta_plan_desviacion_porcentaje': round(costo_venta_plan_desviacion_porcentaje, 1),
            'costo_venta_last_year': round(costo_venta_last_year, 0),
            'costo_venta_last_year_porcentaje': round(costo_venta_last_year_porcentaje, 1),

            'utilidad_bruta_real': round(utilidad_bruta_real, 0),
            'utilidad_bruta_plan': round(utilidad_bruta_plan, 0),
            'utilidad_bruta_desviacion': round(utilidad_bruta_desviacion, 0),
            'utilidad_bruta_acumulado_saldo': round(utilidad_bruta_acumulado_saldo, 0),
            'utilidad_bruta_acumulado_saldo_porcentaje': round(utilidad_bruta_acumulado_saldo_porcentaje, 1),
            'utilidad_bruta_plan_saldo': round(utilidad_bruta_plan_saldo, 0),
            'utilidad_bruta_plan_saldo_porcentaje': round(utilidad_bruta_plan_saldo_porcentaje, 1),
            'utilidad_bruta_plan_desviacion': round(utilidad_bruta_plan_desviacion, 0),
            'utilidad_bruta_plan_desviacion_porcentaje': round(utilidad_bruta_plan_desviacion_porcentaje, 1),
            'costo_venta_last_year_saldo': round(costo_venta_last_year_saldo, 0),
            'costo_venta_last_year_saldo_porcentaje': round(costo_venta_last_year_saldo_porcentaje, 1),

            'utilidad_porcentaje': round(utilidad_porcentaje, 1),
            'utilidad_bruta_plan_procentaje': round(utilidad_bruta_plan_procentaje, 0),

            'gastos_operacion': round(gastos_operacion, 0),
            'gastos_operacion_plan': round(gastos_operacion_plan, 0),
            'gastos_operacion_desviacion': round(gastos_operacion_desviacion, 0),
            'gastos_operacion_acumulado': round(gastos_operacion_acumulado, 0),
            'gastos_operacion_acumulado_porcentaje': round(gastos_operacion_acumulado_porcentaje, 1),
            'gastos_operacion_plan_acumulado': round(gastos_operacion_plan_acumulado, 0),
            'gastos_operacion_plan_acumulado_porcentaje': round(gastos_operacion_plan_acumulado_porcentaje, 1),
            'gastos_operacion_plan_acumulado_desviacion': round(gastos_operacion_plan_acumulado_desviacion, 0),
            'gastos_operacion_plan_acumulado_desviacion_porcentaje': round(gastos_operacion_plan_acumulado_desviacion_porcentaje, 1),
            'gastos_operacion_acumulado_last_year': round(gastos_operacion_acumulado_last_year, 0),
            'gastos_operacion_acumulado_last_year_porcentaje': round(gastos_operacion_acumulado_last_year_porcentaje, 1),

            'utilidad_operacion': round(utilidad_operacion, 0),
            'utilidad_operacion_plan': round(utilidad_operacion_plan, 0),
            'utilidad_operacion_desviacion': round(utilidad_operacion_desviacion, 0),
            'utilidad_operacion_acumulado': round(utilidad_operacion_acumulado, 0),
            'utilidad_operacion_acumulado_porcentaje': round(utilidad_operacion_acumulado_porcentaje, 1),
            'utilidad_operacion_plan_acumulado': round(utilidad_operacion_plan_acumulado, 0),
            'utilidad_operacion_plan_acumulado_porcentaje': round(utilidad_operacion_plan_acumulado_porcentaje, 1),
            'utilidad_operacion_plan_acumulado_desviacion': round(utilidad_operacion_plan_acumulado_desviacion, 0),
            'utilidad_operacion_plan_acumulado_desviacion_porcentaje': round(utilidad_operacion_plan_acumulado_desviacion_porcentaje, 1),
            'utilidad_operacion_acumulado_last_year': round(utilidad_operacion_acumulado_last_year, 0),
            'utilidad_operacion_acumulado_last_year_porcentaje': round(utilidad_operacion_acumulado_last_year_porcentaje, 1),

            'perdida_cambiaria': round(perdida_cambiaria, 0),
            'perdida_cambiaria_plan': round(perdida_cambiaria_plan, 0),
            'perdida_cambiaria_desviacion': round(perdida_cambiaria_desviacion, 0),
            'perdida_cambiaria_acumulado': round(perdida_cambiaria_acumulado, 0),
            'perdida_cambiaria_acumulado_porcentaje': round(perdida_cambiaria_acumulado_porcentaje, 1),
            'perdida_cambiaria_plan_acumulado': round(perdida_cambiaria_plan_acumulado, 0),
            'perdida_cambiaria_plan_acumulado_porcentaje': round(perdida_cambiaria_plan_acumulado_porcentaje, 1),
            'perdida_cambiaria_plan_acumulado_desviacion': round(perdida_cambiaria_plan_acumulado_desviacion, 0),
            'perdida_cambiaria_plan_acumulado_desviacion_porcentaje': round(perdida_cambiaria_plan_acumulado_desviacion_porcentaje, 1),
            'perdida_cambiaria_acumulado_last_year': round(perdida_cambiaria_acumulado_last_year, 0),
            'perdida_cambiaria_acumulado_last_year_porcentaje': round(perdida_cambiaria_acumulado_last_year_porcentaje, 1),

            'intereses_pagados': round(intereses_pagados, 0),
            'intereses_pagados_plan': round(intereses_pagados_plan, 0),
            'intereses_pagados_desviacion': round(intereses_pagados_desviacion, 0),
            'intereses_pagados_acumulado': round(intereses_pagados_acumulado, 0),
            'intereses_pagados_acumulado_porcentaje': round(intereses_pagados_acumulado_porcentaje, 1),
            'intereses_pagados_plan_acumulado': round(intereses_pagados_plan_acumulado, 0),
            'intereses_pagados_plan_acumulado_porcentaje': round(intereses_pagados_plan_acumulado_porcentaje, 1),
            'intereses_pagados_plan_desviacion': round(intereses_pagados_plan_desviacion, 0),
            'intereses_pagados_plan_desviacion_porcentaje': round(intereses_pagados_plan_desviacion_porcentaje, 1),
            'intereses_pagados_acumulado_last_year': round(intereses_pagados_acumulado_last_year, 0),
            'intereses_pagados_acumulado_last_year_porcentaje': round(intereses_pagados_acumulado_last_year_porcentaje, 1),

            'ingresos_interes': round(ingresos_interes, 0),
            'ingresos_interes_plan': round(ingresos_interes_plan, 0),
            'ingresos_interes_desviacion': round(ingresos_interes_desviacion, 0),
            'ingresos_interes_acumulado': round(ingresos_interes_acumulado, 0),
            'ingresos_interes_acumulado_porcentaje': round(ingresos_interes_acumulado_porcentaje, 1),
            'ingresos_interes_plan_acumulado': round(ingresos_interes_plan_acumulado, 0),
            'ingresos_interes_plan_acumulado_porcentaje': round(ingresos_interes_plan_acumulado_porcentaje, 1),
            'ingresos_interes_plan_acumulado_desviacion': round(ingresos_interes_plan_acumulado_desviacion, 0),
            'ingresos_interes_plan_acumulado_desviacion_desviacion': round(ingresos_interes_plan_acumulado_desviacion_desviacion, 0),
            'ingresos_interes_acumulado_last_year': round(ingresos_interes_acumulado_last_year, 0),
            'ingresos_interes_acumulado_last_year_porcentaje': round(ingresos_interes_acumulado_last_year_porcentaje, 1),

            'utilidad_cambiaria': round(utilidad_cambiaria, 0),
            'utilidad_cambiaria_plan': round(utilidad_cambiaria_plan, 0),
            'utilidad_cambiaria_desviacion': round(utilidad_cambiaria_desviacion, 0),
            'utilidad_cambiaria_acumulado': round(utilidad_cambiaria_acumulado, 0),
            'utilidad_cambiaria_acumulado_porcentaje': round(utilidad_cambiaria_acumulado_porcentaje, 1),
            'utilidad_cambiaria_plan_acumulado': round(utilidad_cambiaria_plan_acumulado, 0),
            'utilidad_cambiaria_plan_acumulado_porcentaje': round(utilidad_cambiaria_plan_acumulado_porcentaje, 1),
            'utilidad_cambiaria_plan_acumulado_desviacion': round(utilidad_cambiaria_plan_acumulado_desviacion, 0),
            'utilidad_cambiaria_plan_acumulado_desviacion_porcentaje': round(utilidad_cambiaria_plan_acumulado_desviacion_porcentaje, 1),
            'utilidad_cambiaria_acumulado_last_year': round(utilidad_cambiaria_acumulado_last_year, 0),
            'utilidad_cambiaria_acumulado_last_year_porcentaje': round(utilidad_cambiaria_acumulado_last_year_porcentaje, 1),

            'perdida_cambiaria_saldo': round(perdida_cambiaria_saldo, 0),
            'ingresos_interes_saldo': round(ingresos_interes_saldo, 0),
            'utilidad_cambiaria_saldo': round(utilidad_cambiaria_saldo, 0),
            'perdida_cambiaria_acumulado_saldo': round(perdida_cambiaria_acumulado_saldo, 0),
            'perdida_cambiaria_acumulado_saldo_porcentaje': round(perdida_cambiaria_acumulado_saldo_porcentaje, 1),
            'utilidad_cambiaria_plan_acumulado_saldo': round(utilidad_cambiaria_plan_acumulado_saldo, 0),
            'utilidad_cambiaria_plan_acumulado_saldo_porcentaje': round(utilidad_cambiaria_plan_acumulado_saldo_porcentaje, 1),
            'utilidad_cambiaria_plan_acumulado_saldo_desviacion': round(utilidad_cambiaria_plan_acumulado_saldo_desviacion, 0),
            'utilidad_cambiaria_plan_acumulado_saldo_desviacion_porcentaje': round(utilidad_cambiaria_plan_acumulado_saldo_desviacion_porcentaje, 1),
            'perdida_cambiaria_acumulado_last_year_saldo': round(perdida_cambiaria_acumulado_last_year_saldo, 0),
            'perdida_cambiaria_acumulado_last_year_saldo_porcentaje': round(perdida_cambiaria_acumulado_last_year_saldo_porcentaje, 1),

            'otros_gastos': round(otros_gastos, 0),
            'otros_gastos_plan': round(otros_gastos_plan, 0),
            'otros_gastos_desviacion': round(otros_gastos_desviacion, 0),
            'otros_gastos_acumulado': round(otros_gastos_acumulado, 0),
            'otros_gastos_acumulado_porcentaje': round(otros_gastos_acumulado_porcentaje, 1),
            'otros_gastos_plan_acumulado': round(otros_gastos_plan_acumulado, 0),
            'otros_gastos_plan_acumulado_porcentaje': round(otros_gastos_plan_acumulado_porcentaje, 1),
            'otros_gastos_plan_acumulado_desviacion': round(otros_gastos_plan_acumulado_desviacion, 0),
            'otros_gastos_plan_acumulado_desviacion_porcentaje': round(otros_gastos_plan_acumulado_desviacion_porcentaje, 1),
            'otros_gastos_acumulado_last_year': round(otros_gastos_acumulado_last_year, 0),
            'otros_gastos_acumulado_last_year_porcentaje': round(otros_gastos_acumulado_last_year_porcentaje, 1),

            'otros_ingresos': round(otros_ingresos, 0),
            'otros_ingresos_plan': round(otros_ingresos_plan, 0),
            'otros_ingresos_desviacion': round(otros_ingresos_desviacion, 0),
            'otros_ingresos_acumulado': round(otros_ingresos_acumulado, 0),
            'otros_ingresos_acumulado_porcentaje': round(otros_ingresos_acumulado_porcentaje, 1),
            'otros_ingresos_plan_acumulado': round(otros_ingresos_plan_acumulado, 0),
            'otros_ingresos_plan_acumulado_porcentaje': round(otros_ingresos_plan_acumulado_porcentaje, 1),
            'otros_ingresos_plan_acumulado_desviacion': round(otros_ingresos_plan_acumulado_desviacion, 0),
            'otros_ingresos_plan_acumulado_desviacion_porcentaje': round(otros_ingresos_plan_acumulado_desviacion_porcentaje, 1),
            'otros_ingresos_acumulado_last_year': round(otros_ingresos_acumulado_last_year, 0),
            'otros_ingresos_acumulado_last_year_porcentaje': round(otros_ingresos_acumulado_last_year_porcentaje, 1),

            'utilidad_antes_impuestos': round(utilidad_antes_impuestos, 0),
            'utilidad_antes_impuestos_plan': round(utilidad_antes_impuestos_plan, 0),
            'utilidad_antes_impuestos_desviacion': round(utilidad_antes_impuestos_desviacion, 0),
            'utilidad_antes_impuestos_acumulado': round(utilidad_antes_impuestos_acumulado, 0),
            'utilidad_antes_impuestos_acumulado_porcentaje': round(utilidad_antes_impuestos_acumulado_porcentaje, 1),
            'utilidad_antes_impuestos_plan_acumulado': round(utilidad_antes_impuestos_plan_acumulado, 0),
            'utilidad_antes_impuestos_plan_acumulado_porcentaje': round(utilidad_antes_impuestos_plan_acumulado_porcentaje, 1),
            'utilidad_antes_impuestos_plan_acumulado_desviacion': round(utilidad_antes_impuestos_plan_acumulado_desviacion, 0),
            'utilidad_antes_impuestos_plan_acumulado_desviacion_porcentaje': round(utilidad_antes_impuestos_plan_acumulado_desviacion_porcentaje, 1),
            'utilidad_antes_impuestos_plan_acumulado_last_year': round(utilidad_antes_impuestos_plan_acumulado_last_year, 0),
            'utilidad_antes_impuestos_plan_acumulado_last_year_porcentaje': round(utilidad_antes_impuestos_plan_acumulado_last_year_porcentaje, 1),

            'isr': round(isr, 0),
            'isr_plan': round(isr_plan, 0),
            'isr_desviacion': round(isr_desviacion, 0),
            'isr_acumulado': round(isr_acumulado, 0),
            'isr_acumulado_porcentaje': round(isr_acumulado_porcentaje, 1),
            'isr_plan_acumulado': round(isr_plan_acumulado, 0),
            'isr_plan_acumulado_porcentaje': round(isr_plan_acumulado_porcentaje, 1),
            'isr_plan_desviacion': round(isr_plan_desviacion, 0),
            'isr_plan_desviacion_porcentaje': round(isr_plan_desviacion_porcentaje, 1),
            'isr_acumulado_last_year': round(isr_acumulado_last_year, 0),
            'isr_acumulado_last_year_porcentaje': round(isr_acumulado_last_year_porcentaje, 1),

            'ptu': round(ptu, 0),
            'ptu_plan': round(ptu_plan, 0),
            'ptu_desviacion': round(ptu_desviacion, 0),
            'ptu_acumulado': round(ptu_acumulado, 0),
            'ptu_acumulado_porcentaje': round(ptu_acumulado_porcentaje, 1),
            'ptu_plan_acumulado': round(ptu_plan_acumulado, 0),
            'ptu_plan_acumulado_porcentaje': round(ptu_plan_acumulado_porcentaje, 1),
            'ptu_plan_desviacion': round(ptu_plan_desviacion, 0),
            'ptu_plan_desviacion_porcentaje': round(ptu_plan_desviacion_porcentaje, 1),
            'ptu_acumulado_last_year': round(ptu_acumulado_last_year, 0),
            'ptu_acumulado_last_year_porcentaje': round(ptu_acumulado_last_year_porcentaje, 1),

            'isr_ptu': round(isr_ptu, 0),
            'isr_plan_ptu_plan': round(isr_plan_ptu_plan, 0),
            'isr_desviacion_ptu_desviacion': round(isr_desviacion_ptu_desviacion, 0),
            'isr_ptu_acumulado': round(isr_ptu_acumulado, 0),
            'isr_ptu_acumulado_porcentaje': round(isr_ptu_acumulado_porcentaje, 1),
            'isr_plan_ptu_plan_acumulado': round(isr_plan_ptu_plan_acumulado, 0),
            'isr_plan_ptu_plan_acumulado_porcentaje': round(isr_plan_ptu_plan_acumulado_porcentaje, 1),
            'isr_plan_ptu_plan_desviacion': round(isr_plan_ptu_plan_desviacion, 0),
            'isr_plan_ptu_plan_desviacion_porcentaje': round(isr_plan_ptu_plan_desviacion_porcentaje, 1),
            'isr_ptu_acumulado_last_year': round(isr_ptu_acumulado_last_year, 0),
            'isr_ptu_acumulado_last_year_porcentaje': round(isr_ptu_acumulado_last_year_porcentaje, 1),

            'utilidad_neta': round(utilidad_neta, 0),
            'utilidad_neta_plan': round(utilidad_neta_plan, 0),
            'utilidad_neta_desviacion': round(utilidad_neta_desviacion, 0),
            'utilidad_neta_acumulado': round(utilidad_neta_acumulado, 0),
            'utilidad_neta_acumulado_porcentaje': round(utilidad_neta_acumulado_porcentaje, 1),
            'utilidad_neta_plan_acumulado': round(utilidad_neta_plan_acumulado, 0),
            'utilidad_neta_plan_acumulado_porcentaje': round(utilidad_neta_plan_acumulado_porcentaje, 1),
            'utilidad_neta_desviacion_acumulado': round(utilidad_neta_desviacion_acumulado, 0),
            'utilidad_neta_desviacion_acumulado_porcentaje': round(utilidad_neta_desviacion_acumulado_porcentaje, 1),
            'utilidad_neta_last_year': round(utilidad_neta_last_year, 0),
            'utilidad_neta_last_year_porcentaje': round(utilidad_neta_last_year_porcentaje, 1),

            'depreciacion_amortizacion': round(depreciacion_amortizacion, 0),
            'depreciacion_amortizacion_acumulado': round(depreciacion_amortizacion_acumulado, 0),
            'depreciacion_amortizacion_acumulado_porcentaje': round(depreciacion_amortizacion_acumulado_porcentaje, 1),
            'depreciacion_amortizacion_plan_acumulado': round(depreciacion_amortizacion_plan_acumulado, 0),
            'depreciacion_amortizacion_plan_acumulado_porcentaje': round(depreciacion_amortizacion_plan_acumulado_porcentaje, 1),
            'depreciacion_amortizacion_last_year': round(depreciacion_amortizacion_last_year, 0),
            'depreciacion_amortizacion_last_year_porcentaje': round(depreciacion_amortizacion_last_year_porcentaje, 1),

            'ebitda_periodo': round(ebitda_periodo, 0),
            'ebitda_periodo_acumulado': round(ebitda_periodo_acumulado, 0),
            'ebitda_periodo_acumulado_porcentaje': round(ebitda_periodo_acumulado_porcentaje, 1),
            'ebitda_periodo_plan_acumulado': round(ebitda_periodo_plan_acumulado, 0),
            'ebitda_periodo_plan_acumulado_porcentaje': round(ebitda_periodo_plan_acumulado_porcentaje, 1),
            'ebitda_periodo_acumulado_last_year': round(ebitda_periodo_acumulado_last_year, 0),
            'ebitda_periodo_acumulado_last_year_porcentaje': round(ebitda_periodo_acumulado_last_year_porcentaje, 1),

            'ebitda_periodo_porcentaje': round(ebitda_periodo_porcentaje, 1)
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'er.report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def get_pdf_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
            },
        }
        return self.env.ref('ER_report.action_statement_report_pdf').report_action(self, data=data)


class StatementIncomeDetail(models.TransientModel):
    _name = "statement.income.detail"

    er_report_id = fields.Many2one('er.report.wizard', 'Statement')
    ventas = fields.Float(string='Ventas', readonly=True)
    plan = fields.Float(string='Plan', readonly=True)
    ventas_desviacion = fields.Float(
        string='Ventas Desviacion', readonly=True)
    ventas_acumulado = fields.Float(string='Ventas Acumulado', readonly=True)
    ventas_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    plan_acumulado = fields.Float(string='Plan Acumulado', readonly=True)
    plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    ventas_acumulado_desviacion = fields.Float(
        string='Acumulado Desviacion', readonly=True)
    ventas_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    ventas_acumulado_last_year = fields.Float(
        string='Ventas Año Anterior', readonly=True)
    ventas_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    rebajas = fields.Float(string='rebajas', readonly=True)

    plan_rebajas = fields.Float(string='Rebajas Plan', readonly=True)
    rebajas_desviacion = fields.Float(
        string='Debajas Desviacion', readonly=True)
    rebajas_acumulado = fields.Float(string='Rebajas Acumulado', readonly=True)
    rebajas_acumulado_procentaje = fields.Float(
        string='Procentaje', readonly=True)
    plan_acumulado_rebajas = fields.Float(
        string='Rebajas Plan Acumulado', readonly=True)
    plan_acumulado_rebajas_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    rebajas_acumulado_desviacion = fields.Float(
        string='Rebajas Acumulado Desviacion', readonly=True)
    rebajas_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    rebajas_acumulado_last_year = fields.Float(
        string='Rebajas Acumulado Año Anterior', readonly=True)
    rebajas_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    ventas_netas = fields.Float(string='Ventas Netas', readonly=True)
    plan_saldo = fields.Float(string='Ventas Netas Saldo', readonly=True)
    ventas_netas_desviacion = fields.Float(
        string='Ventas Netas Desviacion', readonly=True)
    desviacion_rebajas = fields.Float(
        string='Desviacion Rebajas', readonly=True)
    plan_acumulado_saldo = fields.Float(
        string='Plan Acumulado Saldo', readonly=True)
    ventas_netas_acumulado_desviacion = fields.Float(
        string='Ventas Netas Acumulado Desviacion', readonly=True)
    desviacion_rebajas_desviacion_procentaje = fields.Float(
        string='Procentaje', readonly=True)
    rebajas_acumulado_last_year_saldo = fields.Float(
        string='Rebajas Acumulado Año Anterior', readonly=True)

    costo_venta_real = fields.Float(string='Costo Venta', readonly=True)
    costo_venta_plan = fields.Float(string='Costo_venta_plan', readonly=True)
    costo_venta_desviacion = fields.Float(
        string='costo_venta_desviacion', readonly=True)
    costo_venta_acumulado = fields.Float(
        string='costo_venta_acumulado', readonly=True)
    costo_venta_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    costo_venta_plan_acumulado = fields.Float(
        string='costo_venta_plan_acumulado', readonly=True)
    costo_venta_plan_acumulado_porcentaje = fields.Float(
        string='porcentaje', readonly=True)
    costo_venta_plan_desviacion = fields.Float(
        string='costo_venta_plan_desviacion', readonly=True)
    costo_venta_plan_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    costo_venta_last_year = fields.Float(
        string='costo_venta_last_year', readonly=True)
    costo_venta_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    utilidad_bruta_real = fields.Float(
        string='utilidad_bruta_real', readonly=True)
    utilidad_bruta_plan = fields.Float(
        string='utilidad_bruta_plan', readonly=True)
    utilidad_bruta_desviacion = fields.Float(
        string='utilidad_bruta_desviacion', readonly=True)
    utilidad_bruta_acumulado_saldo = fields.Float(
        string='utilidad_bruta_acumulado_saldo', readonly=True)
    utilidad_bruta_acumulado_saldo_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_bruta_plan_saldo = fields.Float(
        string='utilidad_bruta_plan_saldo', readonly=True)
    utilidad_bruta_plan_saldo_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_bruta_plan_desviacion = fields.Float(
        string='utilidad_bruta_plan_desviacion', readonly=True)
    utilidad_bruta_plan_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    costo_venta_last_year_saldo = fields.Float(
        string='costo_venta_last_year_saldo', readonly=True)
    costo_venta_last_year_saldo_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    utilidad_porcentaje = fields.Float(string='Porcentaje', readonly=True)
    utilidad_bruta_plan_procentaje = fields.Float(
        string='utilidad_bruta_plan_procentaje', readonly=True)

    gastos_operacion = fields.Float(string='gastos_operacion', readonly=True)
    gastos_operacion_plan = fields.Float(
        string='gastos_operacion_plan', readonly=True)
    gastos_operacion_desviacion = fields.Float(
        string='gastos_operacion_desviacion', readonly=True)
    gastos_operacion_acumulado = fields.Float(
        string='gastos_operacion_acumulado', readonly=True)
    gastos_operacion_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    gastos_operacion_plan_acumulado = fields.Float(
        string='gastos_operacion_plan_acumulado', readonly=True)
    gastos_operacion_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    gastos_operacion_plan_acumulado_desviacion = fields.Float(
        string='gastos_operacion_plan_acumulado_desviacion', readonly=True)
    gastos_operacion_plan_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    gastos_operacion_acumulado_last_year = fields.Float(
        string='gastos_operacion_acumulado_last_year', readonly=True)
    gastos_operacion_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    utilidad_operacion = fields.Float(
        string='utilidad_operacion', readonly=True)
    utilidad_operacion_plan = fields.Float(
        string='utilidad_operacion_plan', readonly=True)
    utilidad_operacion_desviacion = fields.Float(
        string='utilidad_operacion_desviacion', readonly=True)
    utilidad_operacion_acumulado = fields.Float(
        string='utilidad_operacion_acumulado', readonly=True)
    utilidad_operacion_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_operacion_plan_acumulado = fields.Float(
        string='utilidad_operacion_plan_acumulado', readonly=True)
    utilidad_operacion_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_operacion_plan_acumulado_desviacion = fields.Float(
        string='utilidad_operacion_plan_acumulado_desviacion', readonly=True)
    utilidad_operacion_plan_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_operacion_acumulado_last_year = fields.Float(
        string='utilidad_operacion_acumulado_last_year', readonly=True)
    utilidad_operacion_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    perdida_cambiaria = fields.Float(string='perdida_cambiaria', readonly=True)
    perdida_cambiaria_plan = fields.Float(
        string='perdida_cambiaria_plan', readonly=True)
    perdida_cambiaria_desviacion = fields.Float(
        string='perdida_cambiaria_desviacion', readonly=True)
    perdida_cambiaria_acumulado = fields.Float(
        string='perdida_cambiaria_acumulado', readonly=True)
    perdida_cambiaria_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    perdida_cambiaria_plan_acumulado = fields.Float(
        string='perdida_cambiaria_plan_acumulado', readonly=True)
    perdida_cambiaria_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    perdida_cambiaria_plan_acumulado_desviacion = fields.Float(
        string='perdida_cambiaria_plan_acumulado_desviacion', readonly=True)
    perdida_cambiaria_plan_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    perdida_cambiaria_acumulado_last_year = fields.Float(
        string='perdida_cambiaria_acumulado_last_year', readonly=True)
    perdida_cambiaria_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    intereses_pagados = fields.Float(string='intereses_pagados', readonly=True)
    intereses_pagados_plan = fields.Float(
        string='intereses_pagados_plan', readonly=True)
    intereses_pagados_desviacion = fields.Float(
        string='intereses_pagados_desviacion', readonly=True)
    intereses_pagados_acumulado = fields.Float(
        string='intereses_pagados_acumulado', readonly=True)
    intereses_pagados_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    intereses_pagados_plan_acumulado = fields.Float(
        string='intereses_pagados_plan_acumulado', readonly=True)
    intereses_pagados_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    intereses_pagados_plan_desviacion = fields.Float(
        string='intereses_pagados_plan_desviacion', readonly=True)
    intereses_pagados_plan_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    intereses_pagados_acumulado_last_year = fields.Float(
        string='intereses_pagados_acumulado_last_year', readonly=True)
    intereses_pagados_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    ingresos_interes = fields.Float(string='ingresos_interes', readonly=True)
    ingresos_interes_plan = fields.Float(
        string='ingresos_interes_plan', readonly=True)
    ingresos_interes_desviacion = fields.Float(
        string='ingresos_interes_desviacion', readonly=True)
    ingresos_interes_acumulado = fields.Float(
        string='ingresos_interes_acumulado', readonly=True)
    ingresos_interes_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    ingresos_interes_plan_acumulado = fields.Float(
        string='ingresos_interes_plan_acumulado', readonly=True)
    ingresos_interes_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    ingresos_interes_plan_acumulado_desviacion = fields.Float(
        string='ingresos_interes_plan_acumulado_desviacion', readonly=True)
    ingresos_interes_plan_acumulado_desviacion_desviacion = fields.Float(
        string='ingresos_interes_plan_acumulado_desviacion_desviacion', readonly=True)
    ingresos_interes_acumulado_last_year = fields.Float(
        string='ingresos_interes_acumulado_last_year', readonly=True)
    ingresos_interes_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    utilidad_cambiaria = fields.Float(
        string='utilidad_cambiaria', readonly=True)
    utilidad_cambiaria_plan = fields.Float(
        string='utilidad_cambiaria_plan', readonly=True)
    utilidad_cambiaria_desviacion = fields.Float(
        string='utilidad_cambiaria_desviacion', readonly=True)
    utilidad_cambiaria_acumulado = fields.Float(
        string='utilidad_cambiaria_acumulado', readonly=True)
    utilidad_cambiaria_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_cambiaria_plan_acumulado = fields.Float(
        string='utilidad_cambiaria_plan_acumulado', readonly=True)
    utilidad_cambiaria_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_cambiaria_plan_acumulado_desviacion = fields.Float(
        string='utilidad_cambiaria_plan_acumulado_desviacion', readonly=True)
    utilidad_cambiaria_plan_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_cambiaria_acumulado_last_year = fields.Float(
        string='utilidad_cambiaria_acumulado_last_year', readonly=True)
    utilidad_cambiaria_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    perdida_cambiaria_saldo = fields.Float(
        string='perdida_cambiaria_saldo', readonly=True)
    ingresos_interes_saldo = fields.Float(
        string='ingresos_interes_saldo', readonly=True)
    utilidad_cambiaria_saldo = fields.Float(
        string='utilidad_cambiaria_saldo', readonly=True)
    perdida_cambiaria_acumulado_saldo = fields.Float(
        string='perdida_cambiaria_acumulado_saldo', readonly=True)
    perdida_cambiaria_acumulado_saldo_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_cambiaria_plan_acumulado_saldo = fields.Float(
        string='utilidad_cambiaria_plan_acumulado_saldo', readonly=True)
    utilidad_cambiaria_plan_acumulado_saldo_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_cambiaria_plan_acumulado_saldo_desviacion = fields.Float(
        string='utilidad_cambiaria_plan_acumulado_saldo_desviacion', readonly=True)
    utilidad_cambiaria_plan_acumulado_saldo_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    perdida_cambiaria_acumulado_last_year_saldo = fields.Float(
        string='perdida_cambiaria_acumulado_last_year_saldo', readonly=True)
    perdida_cambiaria_acumulado_last_year_saldo_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    otros_gastos = fields.Float(string='otros_gastos', readonly=True)
    otros_gastos_plan = fields.Float(string='otros_gastos_plan', readonly=True)
    otros_gastos_desviacion = fields.Float(
        string='otros_gastos_desviacion', readonly=True)
    otros_gastos_acumulado = fields.Float(
        string='otros_gastos_acumulado', readonly=True)
    otros_gastos_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    otros_gastos_plan_acumulado = fields.Float(
        string='otros_gastos_plan_acumulado', readonly=True)
    otros_gastos_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    otros_gastos_plan_acumulado_desviacion = fields.Float(
        string='otros_gastos_plan_acumulado_desviacion', readonly=True)
    otros_gastos_plan_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    otros_gastos_acumulado_last_year = fields.Float(
        string='otros_gastos_acumulado_last_year', readonly=True)
    otros_gastos_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    otros_ingresos = fields.Float(string='otros_ingresos', readonly=True)
    otros_ingresos_plan = fields.Float(
        string='otros_ingresos_plan', readonly=True)
    otros_ingresos_desviacion = fields.Float(
        string='otros_ingresos_desviacion', readonly=True)
    otros_ingresos_acumulado = fields.Float(
        string='otros_ingresos_acumulado', readonly=True)
    otros_ingresos_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    otros_ingresos_plan_acumulado = fields.Float(
        string='otros_ingresos_plan_acumulado', readonly=True)
    otros_ingresos_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    otros_ingresos_plan_acumulado_desviacion = fields.Float(
        string='otros_ingresos_plan_acumulado_desviacion', readonly=True)
    otros_ingresos_plan_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    otros_ingresos_acumulado_last_year = fields.Float(
        string='otros_ingresos_acumulado_last_year', readonly=True)
    otros_ingresos_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    utilidad_antes_impuestos = fields.Float(
        string='utilidad_antes_impuestos', readonly=True)
    utilidad_antes_impuestos_plan = fields.Float(
        string='utilidad_antes_impuestos_plan', readonly=True)
    utilidad_antes_impuestos_desviacion = fields.Float(
        string='utilidad_antes_impuestos_desviacion', readonly=True)
    utilidad_antes_impuestos_acumulado = fields.Float(
        string='utilidad_antes_impuestos_acumulado', readonly=True)
    utilidad_antes_impuestos_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_antes_impuestos_plan_acumulado = fields.Float(
        string='utilidad_antes_impuestos_plan_acumulado', readonly=True)
    utilidad_antes_impuestos_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_antes_impuestos_plan_acumulado_desviacion = fields.Float(
        string='utilidad_antes_impuestos_plan_acumulado_desviacion', readonly=True)
    utilidad_antes_impuestos_plan_acumulado_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_antes_impuestos_plan_acumulado_last_year = fields.Float(
        string='utilidad_antes_impuestos_plan_acumulado_last_year', readonly=True)
    utilidad_antes_impuestos_plan_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    isr = fields.Float(string='isr', readonly=True)
    isr_plan = fields.Float(string='isr_plan', readonly=True)
    isr_desviacion = fields.Float(string='isr_desviacion', readonly=True)
    isr_acumulado = fields.Float(string='isr_acumulado', readonly=True)
    isr_acumulado_porcentaje = fields.Float(string='Porcentaje', readonly=True)
    isr_plan_acumulado = fields.Float(
        string='isr_plan_acumulado', readonly=True)
    isr_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    isr_plan_desviacion = fields.Float(
        string='isr_plan_desviacion', readonly=True)
    isr_plan_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    isr_acumulado_last_year = fields.Float(
        string='isr_acumulado_last_year', readonly=True)
    isr_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    ptu = fields.Float(string='ptu', readonly=True)
    ptu_plan = fields.Float(string='ptu_plan', readonly=True)
    ptu_desviacion = fields.Float(string='ptu_desviacion', readonly=True)
    ptu_acumulado = fields.Float(string='ptu_acumulado', readonly=True)
    ptu_acumulado_porcentaje = fields.Float(string='Porcentaje', readonly=True)
    ptu_plan_acumulado = fields.Float(
        string='ptu_plan_acumulado', readonly=True)
    ptu_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    ptu_plan_desviacion = fields.Float(
        string='ptu_plan_desviacion', readonly=True)
    ptu_plan_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    ptu_acumulado_last_year = fields.Float(
        string='ptu_acumulado_last_year', readonly=True)
    ptu_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    isr_ptu = fields.Float(string='isr_ptu', readonly=True)
    isr_plan_ptu_plan = fields.Float(string='isr_plan_ptu_plan', readonly=True)
    isr_desviacion_ptu_desviacion = fields.Float(
        string='isr_desviacion_ptu_desviacion', readonly=True)
    isr_ptu_acumulado = fields.Float(string='isr_ptu_acumulado', readonly=True)
    isr_ptu_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    isr_plan_ptu_plan_acumulado = fields.Float(
        string='isr_plan_ptu_plan_acumulado', readonly=True)
    isr_plan_ptu_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    isr_plan_ptu_plan_desviacion = fields.Float(
        string='isr_plan_ptu_plan_desviacion', readonly=True)
    isr_plan_ptu_plan_desviacion_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    isr_ptu_acumulado_last_year = fields.Float(
        string='isr_ptu_acumulado_last_year', readonly=True)
    isr_ptu_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    utilidad_neta = fields.Float(string='utilidad_neta', readonly=True)
    utilidad_neta_plan = fields.Float(
        string='utilidad_neta_plan', readonly=True)
    utilidad_neta_desviacion = fields.Float(
        string='utilidad_neta_desviacion', readonly=True)
    utilidad_neta_acumulado = fields.Float(
        string='utilidad_neta_acumulado', readonly=True)
    utilidad_neta_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_neta_plan_acumulado = fields.Float(
        string='utilidad_neta_plan_acumulado', readonly=True)
    utilidad_neta_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_neta_desviacion_acumulado = fields.Float(
        string='utilidad_neta_desviacion_acumulado', readonly=True)
    utilidad_neta_desviacion_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    utilidad_neta_last_year = fields.Float(
        string='utilidad_neta_last_year', readonly=True)
    utilidad_neta_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    depreciacion_amortizacion = fields.Float(
        string='depreciacion_amortizacion', readonly=True)
    depreciacion_amortizacion_acumulado = fields.Float(
        string='depreciacion_amortizacion_acumulado', readonly=True)
    depreciacion_amortizacion_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    depreciacion_amortizacion_plan_acumulado = fields.Float(
        string='depreciacion_amortizacion_plan_acumulado', readonly=True)
    depreciacion_amortizacion_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    depreciacion_amortizacion_last_year = fields.Float(
        string='depreciacion_amortizacion_last_year', readonly=True)
    depreciacion_amortizacion_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    ebitda_periodo = fields.Float(string='ebitda_periodo', readonly=True)
    ebitda_periodo_acumulado = fields.Float(
        string='ebitda_periodo_acumulado', readonly=True)
    ebitda_periodo_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    ebitda_periodo_plan_acumulado = fields.Float(
        string='ebitda_periodo_plan_acumulado', readonly=True)
    ebitda_periodo_plan_acumulado_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)
    ebitda_periodo_acumulado_last_year = fields.Float(
        string='ebitda_periodo_acumulado_last_year', readonly=True)
    ebitda_periodo_acumulado_last_year_porcentaje = fields.Float(
        string='Porcentaje', readonly=True)

    ebitda_periodo_porcentaje = fields.Float(
        string='porcentaje', readonly=True)
