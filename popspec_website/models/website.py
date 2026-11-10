from odoo import fields, models
from odoo.fields import Domain


class Website(models.Model):
    _inherit = 'website'

    popspec_brand_enabled = fields.Boolean('Use Pop Spec branding', default=False)
    popspec_opening_hours = fields.Text('Opening hours', translate=True)
    popspec_phone = fields.Char('Telephone', default='+1 868 620-8711')
    popspec_whatsapp = fields.Char('WhatsApp number', default=False, help='International digits only.')
    popspec_address = fields.Text('Business address', default=False)
    popspec_phone_alt = fields.Char('Second telephone', default='+1 868 760-0838')
    popspec_email = fields.Char('Business email', default='popspecltd@gmail.com')

    def _popspec_whatsapp_url(self):
        self.ensure_one()
        digits = ''.join(c for c in (self.popspec_whatsapp or '') if c.isascii() and c.isdigit())
        return 'https://wa.me/' + digits if 7 <= len(digits) <= 15 else False

    def _popspec_maps_url(self):
        from urllib.parse import urlencode
        self.ensure_one()
        if not self.popspec_address:
            return False
        return 'https://www.google.com/maps/search/?' + urlencode({'api': '1', 'query': self.popspec_address})


    def _popspec_categories(self):
        """The same website/publication boundary as Odoo's normal category list."""
        self.ensure_one()
        Category = self.env['product.public.category'].with_context(website_id=self.id)
        if not self.popspec_brand_enabled or not self.has_ecommerce_access():
            return Category.browse()
        return Category.search(Domain.AND([
            self.website_domain(),
            [('popspec_homepage_featured', '=', True), ('has_published_products', '=', True)],
        ]), order='sequence, name, id', limit=12)

    def _popspec_featured_products(self):
        self.ensure_one()
        Product = self.env['product.template'].with_context(website_id=self.id)
        if not self.popspec_brand_enabled or not self.has_ecommerce_access():
            return Product.browse()
        # Explicit published/active predicates also apply when an editor previews the page.
        # No sudo: normal product/company/website access rules remain authoritative.
        domain = Domain.AND([
            self.sale_product_domain(),
            [('active', '=', True), ('is_published', '=', True),
             ('popspec_homepage_featured', '=', True)],
        ])
        featured = Product.search(domain, order='website_sequence, id', limit=8)
        return featured or Product.search(Domain.AND([self.sale_product_domain(), [('active', '=', True), ('is_published', '=', True)]]), order='website_sequence, id', limit=8)

