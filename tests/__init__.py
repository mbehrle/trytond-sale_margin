#This file is part sale_margin module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

try:
    from trytond.modules.sale_margin.tests.test_sale_margin import suite
except ImportError:
    from .test_sale_margin import suite

__all__ = ['suite']
