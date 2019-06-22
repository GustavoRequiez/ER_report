# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions


class ERCuentas(models.Model):
    _name = 'er.cuentas.estado.resultados'

    name = fields.Selection([
        ('VENTAS', 'VENTAS'),
        ('REBAJAS Y DEVOLUCIONES', 'REBAJAS Y DEVOLUCIONES'),
        ('COSTO DE VENTA', 'COSTO DE VENTA'),
        ('GASTOS DE OPERACION', 'GASTOS DE OPERACION'),
        ('PERDIDA CAMBIARIA', 'PERDIDA CAMBIARIA'),
        ('INGRESOS POR INTERES', 'INGRESOS POR INTERES'),
        ('UTILIDAD CAMBIARIA', 'UTILIDAD CAMBIARIA'),
        ('OTROS GASTOS', 'OTROS GASTOS'),
        ('OTROS INGRESOS', 'OTROS INGRESOS'),
        ('ISR', 'ISR'),
        ('PTU', 'PTU'),
        ('DEPRECIACIONES Y AMORTIZACIONES', 'DEPRECIACIONES Y AMORTIZACIONES'),
        ('INTERESES PAGADOS', 'INTERESES PAGADOS')], string='Name', required=True, default='VENTAS')
    account_ids = fields.Many2many(
        'account.account', 'name', 'code', 'gid', 'Accounts')
