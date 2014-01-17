#This file is part sale_margin module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta

__all__ = ['Sale', 'SaleLine']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'
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

    def get_margin(self, name):
        '''
        Return the margin of each sales
        '''
        Currency = Pool().get('currency.currency')
        if (self.state in self._states_cached
                and self.margin_cache is not None):
            return self.margin_cache
        margin = sum((l.margin for l in self.lines if l.type == 'line'),
                Decimal(0))
        return Currency.round(self.currency, margin)

    @classmethod
    def store_cache(cls, sales):
        for sale in sales:
            cls.write([sale], {
                    'untaxed_amount_cache': sale.untaxed_amount,
                    'tax_amount_cache': sale.tax_amount,
                    'total_amount_cache': sale.total_amount,
                    'margin_cache': sale.margin,
                    })


class SaleLine:
    __name__ = 'sale.line'

    cost_price = fields.Numeric('Cost Price', digits=(16, 4),
        states={
            'invisible': Eval('type') != 'line',
            }, depends=['type'])
    margin = fields.Function(fields.Numeric('Margin',
            digits=(16, Eval('_parent_sale', {}).get('currency_digits', 2)),
            states={
                'invisible': ~Eval('type').in_(['line', 'subtotal']),
                'readonly': ~Eval('_parent_sale'),
                }, on_change_with=['type', 'quantity', 'cost_price', 'amount', 
                'unit_price', 'unit', '_parent_sale.currency'],
            depends=['type', 'amount']), 'get_margin')

    @staticmethod
    def default_cost_price():
        return Decimal('0.0')

    def on_change_product(self):
        if not self.product:
            return {}
        res = super(SaleLine, self).on_change_product()
        res['cost_price'] = self.product.cost_price
        return res

    def on_change_with_margin(self):
        cost = Decimal(str(self.quantity or '0.0')) * \
                    (self.cost_price or Decimal('0.0'))
        if self.amount:
            return Decimal(self.amount-cost)
        return Decimal('0.0')

    def get_margin(self, name):
        '''
        Return the margin of each sale lines
        '''
        Currency = Pool().get('currency.currency')
        if self.type == 'line':
            cost = Decimal(str(self.quantity)) * (self.cost_price or Decimal('0.0'))
            return Currency.round(self.sale.currency, self.amount - cost)
        else:
            return Decimal('0.0')
