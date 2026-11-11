"""Apply our XPaths using the actual Odoo 19 inheritance engine, without a DB."""
import copy
import html
from pathlib import Path

from lxml import etree


def validate_native_templates(source, module):
    engine = (source / 'odoo/tools/template_inheritance.py').read_text()
    for line in ('from odoo.tools.translate import LazyTranslate',
                 'from odoo.exceptions import ValidationError',
                 'from .misc import SKIPPED_ELEMENT_TYPES, html_escape'):
        engine = engine.replace(line, '')
    namespace = {
        'LazyTranslate': lambda *_: lambda message, *args: message % args if args else message,
        'ValidationError': ValueError,
        'SKIPPED_ELEMENT_TYPES': (etree._Comment, etree._ProcessingInstruction),
        'html_escape': html.escape,
    }
    exec(compile(engine, 'odoo19_template_inheritance', 'exec'), namespace)
    apply = namespace['apply_inheritance_specs']
    etree.FunctionNamespace(None)['hasclass'] = lambda ctx, *names: all(
        name in (ctx.context_node.get('class') or '').split() for name in names)

    def load(path):
        return etree.parse(str(source / path))

    def template(doc, key):
        return doc.xpath('//template[@id=$key]', key=key)[0]

    def modify(arch, spec):
        instructions = etree.Element('data')
        instructions.extend(copy.deepcopy(list(spec)))
        return apply(arch, instructions)

    web = load('addons/web/views/webclient_templates.xml')
    portal = load('addons/portal/views/portal_templates.xml')
    website = load('addons/website/views/website_templates.xml')
    sale = load('addons/website_sale/views/templates.xml')
    custom = etree.parse(str(module / 'views/layout.xml'))
    base = etree.Element('data')
    base.extend(copy.deepcopy(list(template(web, 'web.layout'))))
    for document, name in [(web, 'web.frontend_layout'), (portal, 'frontend_layout'),
                           (website, 'layout'), (sale, 'website_sale_layout')]:
        base = modify(base, template(document, name))
    headers = website.xpath('//template[@inherit_id="website.layout" and starts-with(@id,"template_header_")]')
    count = 0
    for header in headers:
        if header.get('id') in ('template_header_navlink_no_background',
                               'template_header_additional_color_primary',
                               'template_header_additional_color_secondary'):
            continue
        arch = modify(copy.deepcopy(base), header)
        for extension in sale.xpath('//template[@inherit_id=$ref]', ref='website.' + header.get('id')):
            arch = modify(arch, extension)
        if header.get('id') == 'template_header_default':
            arch = modify(arch, template(custom, 'popspec_header'))
        arch = modify(arch, template(custom, 'layout_brand'))
        assert len(arch.xpath('//header[@id="top"]')) == 1
        assert arch.xpath('//header//t[@t-call="website_sale.header_cart_link"]')
        assert arch.xpath('//header//t[@t-call="website.template_header_mobile"]')
        count += 1
    print(f'PASS: Odoo inheritance engine, {count} native header layouts; native mobile and cart retained.')
    refresh = module.parent / 'popspec_website_catalogue/views/website.xml'
    if refresh.exists():
        changes = etree.parse(str(refresh))
        native_data = load('addons/website/data/website_data.xml')
        pages = etree.parse(str(module / 'data/pages.xml'))
        targets = {
            'remove_banner_label': pages.xpath('//record[@id="page_home"]/field[@name="arch"]')[0],
            'mobile_phones': template(website, 'template_header_mobile'),
            'contact_page': template(native_data, 'website.contactus'),
            'contact_thanks': native_data.xpath('//record[@id="website.contactus_thanks"]/field[@name="arch"]')[0],
        }
        for key, target in targets.items():
            spec = changes.xpath('//record[@id=$key]/field[@name="arch"]', key=key)[0]
            arch = modify(copy.deepcopy(target), spec)
            if key == 'contact_page':
                assert arch.xpath('//form[@id="contactus_form"][@action="/website/form/"]')
        print('PASS: contact, acknowledgement, banner and mobile extensions apply to Odoo 19 views.')
