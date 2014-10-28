#This file is part sale_margin module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.config import CONFIG
DIGITS = int(CONFIG.get('unit_price_digits', 4))

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
    cost_price = fields.Numeric('Cost Price', digits=(16, DIGITS),
        states={
            'invisible': Eval('type') != 'line',
            }, depends=['type'])
    margin = fields.Function(fields.Numeric('Margin',
            digits=(16, Eval('_parent_sale', {}).get('currency_digits', 2)),
            states={
                'invisible': ~Eval('type').in_(['line', 'subtotal']),
                'readonly': ~Eval('_parent_sale'),
                },
            depends=['type', 'amount']), 'get_margin')

    @staticmethod
    def default_cost_price():
        return Decimal('0.0')

    @fields.depends('product', 'unit', 'quantity', 'description',
        '_parent_sale.party', '_parent_sale.currency',
        '_parent_sale.sale_date')
    def on_change_product(self):
        res = super(SaleLine, self).on_change_product()
        if self.product:
            res['cost_price'] = self.product.cost_price
        return res

    @fields.depends('type', 'quantity', 'cost_price', 'amount', 'unit_price',
        'unit', '_parent_sale.currency')
    def on_change_with_margin(self):
        cost = Decimal(str(self.quantity or '0.0')) * \
                    (self.cost_price or Decimal('0.0'))
        if self.amount:
            return Decimal(self.amount - cost)
        return Decimal('0.0')

    def get_margin(self, name):
        '''
        Return the margin of each sale lines
        '''
        Currency = Pool().get('currency.currency')
        currency = self.sale.currency
        if self.type == 'line':
            cost = Decimal(str(self.quantity)) * (self.cost_price or
                Decimal('0.0'))
            return Currency.round(currency, self.amount - cost)

        elif self.type == 'subtotal':
            cost = Decimal('0.0')
            for line2 in self.sale.lines:
                if line2.type == 'line':
                    cost2 = Decimal(str(line2.quantity)) * (line2.cost_price or
                        Decimal('0.0'))
                    cost += Currency.round(currency, line2.amount - cost2)
                elif line2.type == 'subtotal':
                    if self == line2:
                        return cost
                    cost = Decimal('0.0')
        else:
            return Decimal('0.0')
