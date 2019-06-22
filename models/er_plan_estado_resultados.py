# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions


class ERplan(models.Model):
    _name = 'er.plan.estado.resultados'

    name = fields.Selection([
        ('ENERO', 'ENERO'),
        ('FEBRERO', 'FEBRERO'),
        ('MARZO', 'MARZO'),
        ('ABRIL', 'ABRIL'),
        ('MAYO', 'MAYO'),
        ('JUNIO', 'JUNIO'),
        ('JULIO', 'JULIO'),
        ('AGOSTO', 'AGOSTO'),
        ('SEPTIEMBRE', 'SEPTIEMBRE'),
        ('OCTUBRE', 'OCTUBRE'),
        ('NOVIEMBRE', 'NOVIEMBRE'),
        ('DICIEMBRE', 'DICIEMBRE')], string="Month", required=True)
    year = fields.Char(string='Year', required=True)
    brand_id = fields.Many2one('product.brand', string='Brand', required=True)
    value = fields.Float(string='Value', required=True)
    plan = fields.Selection([
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
        ('INTERESES PAGADOS', 'INTERESES PAGADOS')], string='Plan', required=True, default='VENTAS')
