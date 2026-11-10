# Pop Spec Ltd — Odoo 19 Community website

**19.0.1.0.0 · Developed by Spxcorp Limited**

A turquoise, black and white eyewear storefront with real photography and the supplied Pop Spec logo. Native Odoo products, website categories, variants, pricing, stock rules, search, cart, checkout and customer accounts remain authoritative. No replacement commerce controllers or external catalogue.

## Install on CloudPepper

1. Connect `https://github.com/sheveioncallender-boop/popspec-website-.git`, branch `main`, to the intended Odoo 19 Community instance.
2. Rebuild/redeploy so the addon is on the server. The repository root belongs on the addons path.
3. Enable developer mode → Apps → Update Apps List.
4. Install **Pop Spec — Website & Shop** (`popspec_website`). It installs the native `website_sale_stock` dependency.
5. Review Website → Configuration → Settings → **Pop Spec Ltd**. Configure company details separately for invoices and Odoo's contact form.
6. For subsequent releases, redeploy then **Upgrade** this module.

The initial setup targets `website.default_website`. Install on the intended Pop Spec database, not a database whose default website belongs to another client. Other websites retain their own branding. Content and category records use `noupdate=1`; upgrades preserve merchant edits. The setup hook is idempotent and uninstall restores unchanged prior homepage/name/logo/menu settings.

## Pages

| Page | Route |
|---|---|
| Home, rotating photography, live categories/products | `/` via `/popspec-home` |
| Our Services | `/optical-services` |
| Lens Guide | `/lens-guide` |
| About Us | `/about-us` |
| Visit & Contact | `/visit-us` |
| Odoo catalogue and product pages | `/shop` |
| Odoo cart / checkout | `/shop/cart`, `/shop/checkout` |
| Odoo account / orders | `/my`, `/my/orders` |
| Odoo general enquiry form | `/contactus` |

## Publish your products

Create products in Odoo and set their images, variants, descriptions, sales prices, taxes and ecommerce categories. Publish each product on the website. Published products immediately appear in the native shop; the homepage displays up to eight eligible products automatically. Use **Feature on Pop Spec homepage** in the Sales tab to curate that selection; when any featured eligible products exist they take priority over the automatic selection. Unpublishing or archiving removes a product from that selection.

Four editable native ecommerce categories are supplied: Optical Frames, Sunglasses, Lenses and Accessories. Categories appear on the homepage only when they contain published products and **Show on Pop Spec homepage** is enabled. Upload category images in Odoo. No invented products, stock, prices, clinical records or orders are installed.

Prices use Odoo's visitor pricelist, currency, fiscal position and tax calculation. Nothing is hard-coded to TTD or a tax rate. Configure the company currency and sales settings for the business. Out-of-stock and payment behaviour are native Odoo settings.

## Contact and imagery

The supplied logo contains `popspecltd@gmail.com`, `6208711` and `7600838`; telephone links use Trinidad & Tobago's +1 868 prefix. The original logo JPEG is preserved, with its main mark framed through CSS in the header and footer. Real Unsplash photographs are bundled locally; see `ASSET_CREDITS.json` for sources and licence links. Photographs are editorial, not claims about staff, customers, stocked brands or products. Product cards use actual merchant-uploaded images.

The store address, hours and WhatsApp number are deliberately unset pending confirmation. Configure them in Website settings. Booking links currently lead to an enquiry or telephone call; there is no instant appointment confirmation. No WhatsApp/SMS campaign, payment provider or social media account is fabricated or activated. Configure native Odoo social links once verified.

Before accepting orders: configure real products, stock policy, prices, taxes, delivery/pickup, payment provider, outgoing email, contact recipient, terms/privacy and return/warranty policies. Native checkout is included but payment credentials must be configured on the target instance.

## Optical operations — subsequent phase

The website is independent of the future optical module. **No optical operations module is included in this first website release.** The complete client requirements and native Odoo extension approach are recorded in [docs/OPTICAL_REQUIREMENTS.md](docs/OPTICAL_REQUIREMENTS.md). Each requirement needs implementation, integration configuration and acceptance testing before operational go-live.

## Validation

Local checks validate against Odoo 19 source revision `e5164977aa55016422e83da70c08f61d32cac0de`: XML schemas, QWeb expressions, Python and JavaScript syntax, SCSS compilation, bundled image/font references and inheritance across 11 native Odoo header layouts.

```sh
python -m pip install lxml Pillow libsass tinycss2
python scripts/validate_module.py --odoo-source /path/to/odoo19
```

GitHub Actions performs an isolated Odoo/PostgreSQL install and tests page rendering, catalogue publication/website isolation, native cart/checkout, asset compilation, and mobile banner behaviour. Check the Actions result for runtime verification. Production payment, emails and target CloudPepper installation are not validated merely by these tests.

The code is LGPL-3; separate photo/font licences are retained with their credits.
