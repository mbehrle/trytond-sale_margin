#This file is part sale_margin module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
{
    'name': 'Sale Margin',
    'name_ca_ES': 'Marges comanda de venda',
    'name_es_ES': 'Margen pedido de venta',
    'version': '2.4.0',
    'author': 'Zikzakmedia',
    'email': 'zikzak@zikzakmedia.com',
    'website': 'http://www.zikzakmedia.com/',
    'description': '''The sale_margin module adds the 'Margin' on sales, 
which gives the profitability by calculating the difference between the Unit Price and Cost Price.
''',
    'description_ca_ES': '''Aquest mòdul afegeix el 'Marge' en la comanda de venda,
que proporciona la rendibilitat calculant la diferència entre el preu unitari i el preu de cost
''',
    'description_es_ES': '''Este módulo añade el 'Margen' en el pedido de venta,
que proporciona la rentabilidad calculando la diferencia entre el precio unidad y el precio de coste
''',
    'depends': [
        'ir',
        'res',
        'sale',
    ],
    'xml': [
        'sale.xml',
    ],
    'translation': [
        'locale/ca_ES.po',
        'locale/es_ES.po',
    ]
}
