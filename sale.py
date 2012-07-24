#This file is part sale_margin module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.

from decimal import Decimal
from trytond.model import ModelView, ModelSQL, fields
from trytond.tools import safe_eval, datetime_strftime
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.pool import Pool

class Sale(ModelSQL, ModelView):
    _name = 'sale.sale'

    margin = fields.Function(fields.Numeric('Margin',
            digits=(16, Eval('currency_digits', 2),),
            depends=['currency_digits'], 
            help='It gives profitability by calculating the difference '
             'between the Unit Price and Cost Price.'), 
            'get_margin')
    margin_cache = fields.Numeric('Margin Cache',
        digits=(16, Eval('currency_digits', 2)),
        readonly=True,
        depends=['currency_digits'])

    def get_margin(self, ids, name):
        '''
        Return the margin of each sales
        '''
        currency_obj = Pool().get('currency.currency')
        margins = {}
        for sale in self.browse(ids):
            if (sale.state in self._states_cached
                    and sale.margin_cache is not None):
                margins[sale.id] = sale.margin_cache
                continue
            for l in sale.lines:
                margin = sum((l.margin for l in sale.lines if l.type == 'line'),
                    Decimal(0))
                margins[sale.id] = currency_obj.round(sale.currency, margin)
        return margins

    def store_cache(self, ids):
        for sale in self.browse(ids):
            self.write(sale.id, {
                    'untaxed_amount_cache': sale.untaxed_amount,
                    'tax_amount_cache': sale.tax_amount,
                    'total_amount_cache': sale.total_amount,
                    'margin_cache': sale.margin,
                    })

Sale()

class SaleLine(ModelSQL, ModelView):
    _name = 'sale.line'

    cost_price = fields.Numeric('Cost Price', digits=(16, 4),
        states={
            'invisible': Eval('type') != 'line',
            'required': Eval('type') == 'line',
            }, depends=['type'])
    margin = fields.Function(fields.Numeric('Margin',
            digits=(16, Eval('_parent_sale', {}).get('currency_digits', 2)),
            states={
                'invisible': ~Eval('type').in_(['line', 'subtotal']),
                'readonly': ~Eval('_parent_sale'),
                }, on_change_with=['type', 'quantity', 'cost_price', 
                'unit_price', 'unit', '_parent_sale.currency'],
            depends=['type']), 'get_margin')

    def on_change_product(self, vals):
        pool = Pool()
        product_obj = pool.get('product.product')

        if not vals.get('product'):
            return {}

        res = super(SaleLine, self).on_change_product(vals)

        product = product_obj.browse(vals['product'])
        res['cost_price'] = product.cost_price
        return res

    def on_change_with_margin(self, vals):
        cost = Decimal(str(vals.get('quantity') or '0.0')) * \
                    (vals.get('cost_price') or Decimal('0.0'))
        amount = Decimal(str(vals.get('quantity') or '0.0')) * \
                    (vals.get('unit_price') or Decimal('0.0'))
        res = Decimal(amount-cost)
        return res

    def get_margin(self, ids, name):
        '''
        Return the margin of each sale lines
        '''
        currency_obj = Pool().get('currency.currency')
        res = {}
        for line in self.browse(ids):
            if line.type == 'line':
                cost = Decimal(str(line.quantity)) * (line.cost_price or Decimal('0.0')) 
                amount = Decimal(str(line.quantity)) * (line.unit_price)
                res[line.id] = currency_obj.round(line.sale.currency, amount - cost)
            else:
                res[line.id] = Decimal('0.0')
        return res

SaleLine()
