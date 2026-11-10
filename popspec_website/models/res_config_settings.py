from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    popspec_brand_enabled = fields.Boolean(related='website_id.popspec_brand_enabled', readonly=False)
    popspec_opening_hours = fields.Text(related='website_id.popspec_opening_hours', readonly=False)
    popspec_phone = fields.Char(related='website_id.popspec_phone', readonly=False)
    popspec_phone_alt = fields.Char(related='website_id.popspec_phone_alt', readonly=False)
    popspec_whatsapp = fields.Char(related='website_id.popspec_whatsapp', readonly=False)
    popspec_address = fields.Text(related='website_id.popspec_address', readonly=False)
    popspec_email = fields.Char(related='website_id.popspec_email', readonly=False)
