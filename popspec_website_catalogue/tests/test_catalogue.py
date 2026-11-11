from lxml import html
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestPopSpecCatalogue(HttpCase):
    def test_native_catalogue_records(self):
        for i in range(1, 7):
            product = self.env.ref(f'popspec_website_catalogue.demo_frame_{i}')
            self.assertTrue(product.is_published)
            self.assertNotIn('demo', product.name.lower())
            self.assertNotIn('demo', str(product.website_description).lower())
            self.assertEqual(product.tracking, 'serial')
            self.assertTrue(product.image_1920)
            self.assertEqual(len(product.attribute_line_ids), 6)
            self.assertTrue(product.seller_ids)
            self.assertEqual(product.qty_available, 0)
            self.assertFalse(product.allow_out_of_stock_order)
            lot = self.env.ref(f'popspec_website_catalogue.demo_serial_{i}')
            self.assertEqual(lot.product_id, product.product_variant_id)

    def test_contact_and_clean_banner(self):
        home = html.fromstring(self.url_open('/').content)
        self.assertFalse(home.xpath('//span[@class="photo-label"]'))
        for number in ['+1 868 620-8711', '+1 868 760-0838']:
            self.assertTrue(home.xpath(f'//li[@class="ps-mobile-contact"]//a[@href="tel:{number}"]'))
        for path in ['/contactus', '/contactus-thank-you']:
            response = self.url_open(path)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('Fake Buena Vista', response.text)
            self.assertNotIn('555-555-5556', response.text)
            self.assertNotIn('info@yourcompany.example.com', response.text)
        contact = html.fromstring(self.url_open('/contactus').content)
        self.assertTrue(contact.xpath('//form[@id="contactus_form"][@action="/website/form/"][@data-model_name="mail.mail"]'))
        self.assertTrue(contact.xpath('//input[@name="email_to"]'))
        self.assertIn('popspecltd@gmail.com', contact.text_content())

    def test_mobile_contact_and_catalogue(self):
        self.browser_size = '390x844'
        self.browser_js('/contactus', """
            (async () => {
                const check=(v,m)=>{if(!v)throw new Error(m)};
                check(document.documentElement.scrollWidth<=innerWidth+1, 'Contact page overflow');
                const toggle=document.querySelector('[data-bs-target="#top_menu_collapse_mobile"]');
                check(toggle, 'Mobile menu toggle');toggle.click();
                await new Promise(r=>setTimeout(r,500));
                const phones=document.querySelectorAll('#top_menu_collapse_mobile .ps-mobile-contact a[href^="tel:"]');
                check(phones.length===2, 'Two mobile phones');
                check(phones[0].getBoundingClientRect().width>0, 'Phone visible');
                console.log('test successful');
            })().catch(e=>console.error(e));
        """, ready="document.querySelector('.ps-contact-page')", timeout=90)
        product = self.env.ref('popspec_website_catalogue.demo_frame_1')
        response = self.url_open(product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Classic Black', response.text)
        self.assertNotIn('Demonstration product', response.text)
