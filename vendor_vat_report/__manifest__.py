{
    'name': "Vendor Vat Report ",
    'author': 'Doaa Negm',
    'category': 'ALL',
    'summary': """
    Report vat to vendor bill
     """,
    'license': 'AGPL-3',
    'description': """
""",
    'version': '1.0',
    'depends': ['base','account','sale'],
    'data': [
        'security/ir.model.access.csv',
        'report/pos_order_report.xml',
        'views/vendor_vat_wizard_view.xml',
        'views/account_move_inherit_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
