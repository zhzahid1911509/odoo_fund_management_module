{
    'name': 'Fund Management Module',
    'version': '1.1',
    'summary': 'Track bank funds, account transfers, allocations, and project requisitions.',
    'author': 'Trainee Software Developer Candidate',
    'category': 'Accounting',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'views/fund_management_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}