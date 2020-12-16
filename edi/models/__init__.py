# -*- coding: utf-8 -*-

from .models import edi
from odoo.addons.product.models.product_template import ProductTemplate
from odoo.api import Environment


x = edi.get_all_so()

# myClass = ProductTemplate()
# print(ProductTemplate.fields_get())
