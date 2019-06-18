# -*- coding: utf-8 -*-
{
    'name': "er_report",
    'summary': """
        Statement Income Report""",
    'description': """
        Statement Income Report
    """,
    'author': "gflores",
    'website': "https://www.gruporequiez.com",
    'category': 'Account',
    'version': '0.2.0',
    'depends': [
        'account',
        'sale_brand'],
    'data': [
        # views
        'wizard/er_report_wizard.xml',
        'views/er_plan_estado_resultado_view.xml',
        # reports
        'reports/er_report_template.xml',
        # data
        'data/report_data.xml',
    ],
    'demo': [
    ],
}
