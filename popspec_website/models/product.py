from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    popspec_homepage_featured = fields.Boolean('Feature on Pop Spec homepage', copy=False)

class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'
    popspec_homepage_featured = fields.Boolean('Show on Pop Spec homepage', default=True, copy=False)
