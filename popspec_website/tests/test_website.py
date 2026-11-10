from lxml import html
from odoo.tests import HttpCase, tagged
from odoo.addons.website_sale.tests.common import MockRequest
from ..hooks import post_init_hook

@tagged('post_install', '-at_install')
class TestPopSpecWebsite(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.website.write({'domain': False, 'ecommerce_access': 'everyone'})
        cls.category = cls.env.ref('popspec_website.category_1')
        cls.product = cls.env['product.template'].create({
            'name': 'TEST ONLY Optical Frame', 'list_price': 250,
            'website_id': cls.website.id, 'is_published': True,
            'public_categ_ids': [(6, 0, cls.category.ids)],
        })

    def test_publishing_and_isolation(self):
        public = self.website.with_user(self.website.user_id).with_context(website_id=self.website.id)
        with MockRequest(public.env, website=public):
            self.assertIn(self.product.id, public._popspec_featured_products().ids)
            self.assertIn(self.category.id, public._popspec_categories().ids)
            self.product.is_published = False
            self.assertNotIn(self.product.id, public._popspec_featured_products().ids)
            self.assertNotIn(self.category.id, public._popspec_categories().ids)
            self.product.is_published = True
            self.product.active = False
            self.assertNotIn(self.product.id, public._popspec_featured_products().ids)
        self.product.active = True
        other = self.env['website'].create({'name': 'Other website', 'company_id': self.website.company_id.id, 'popspec_brand_enabled': True})
        public_other = other.with_user(other.user_id).with_context(website_id=other.id)
        with MockRequest(public_other.env, website=public_other):
            self.assertNotIn(self.product.id, public_other._popspec_featured_products().ids)
            self.assertNotIn(self.category.id, public_other._popspec_categories().ids)
        self.website.ecommerce_access = 'logged_in'
        with MockRequest(public.env, website=public):
            self.assertFalse(public._popspec_featured_products())
            self.assertFalse(public._popspec_categories())

    def test_setup_is_idempotent(self):
        self.website.popspec_phone = '+1 868 555 0199'
        count = self.env['website.menu'].search_count([('website_id', '=', self.website.id)])
        post_init_hook(self.env)
        self.assertEqual(self.website.popspec_phone, '+1 868 555 0199')
        self.assertEqual(self.website.homepage_url, '/popspec-home')
        self.assertEqual(count, self.env['website.menu'].search_count([('website_id', '=', self.website.id)]))

    def test_native_pages_and_assets(self):
        for path in ['/', '/optical-services', '/lens-guide', '/about-us', '/visit-us', '/shop', self.product.website_url]:
            with self.subTest(path=path):
                response = self.url_open(path, timeout=90)
                self.assertEqual(response.status_code, 200, response.text[:1500])
                page = html.fromstring(response.content)
                self.assertEqual(len(page.xpath('//header[@id="top"]')), 1)
                self.assertTrue(page.xpath('//header//a[@href="/shop/cart"]'))
        page = html.fromstring(self.url_open('/').content)
        self.assertEqual(len(page.xpath('//div[contains(concat(" ",@class," ")," banner-slide ")]')), 3)
        self.assertEqual(len(page.xpath('//h1')), 1)
        for href in page.xpath('//link[@rel="stylesheet"]/@href'):
            if '/web/assets/' in href:
                response = self.url_open(href, timeout=120)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn('style compilation failed', response.text.lower())
        contact = html.fromstring(self.url_open('/visit-us').content)
        self.assertTrue(contact.xpath('//a[@href="mailto:popspecltd@gmail.com"]'))
        self.assertTrue(contact.xpath('//a[@href="tel:+1 868 620-8711"]'))
        self.assertTrue(contact.xpath('//a[@href="tel:+1 868 760-0838"]'))
        self.assertFalse(contact.xpath('//a[starts-with(@href,"https://wa.me/")]'))

    def test_native_cart(self):
        self.url_open('/')
        result = self.make_jsonrpc_request('/shop/cart/add', {'product_template_id': self.product.id, 'product_id': self.product.product_variant_id.id, 'quantity': 1}, timeout=60)
        self.assertEqual(result['quantity'], 1)
        cart = self.url_open('/shop/cart', timeout=60)
        self.assertEqual(cart.status_code, 200)
        self.assertIn(self.product.name, html.fromstring(cart.content).text_content())
        self.assertEqual(self.url_open('/shop/checkout', timeout=60).status_code, 200)

    def test_mobile_and_slider(self):
        self.browser_size = '390x844'
        self.browser_js('/', """
            (async () => {
                const check = (value, message) => { if (!value) throw new Error(message); };
                const banner = document.querySelector('.banner-slider');
                const photo = banner.querySelector('.banner-slide.active img');
                await photo.decode();
                check(photo.getBoundingClientRect().height >= 300, 'Mobile photo visible');
                check(document.documentElement.scrollWidth <= innerWidth + 1, 'No horizontal overflow');
                const first = banner.querySelector('.banner-slide.active');
                banner.querySelector('.slide-next').click();
                await new Promise(resolve => setTimeout(resolve, 500));
                check(!first.classList.contains('active'), 'Next banner works');
                check(first.inert, 'Hidden banner not keyboard focusable');
                console.log('test successful');
            })().catch(error => console.error(error));
        """, ready="document.querySelector('.banner-slider .slide-next')", timeout=90)
