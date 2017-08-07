{
    'name': "Mpay",
    'version': '10.0',
    'summary': """Mobile payment gateway""",
    'description': """Mobile sms based payment app""",
    'author': 'Yezy Ilomo',
    'company': 'Singo Africa Ltd',
    'website': "singoafrica.com",
    'category': 'eCommerce',
    'depends': ['base', 'payment', 'website_sale', 'account'],
    'data': [
      'views/view.xml',
      'views/templates.xml',
    ],
    'installable': True,
    'application': True,
}
