import re
import json
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Page, Browser
from app.schemas.analysis import (
    SiteAnalysis, ExistingTag, FormInfo, CTAInfo,
    EcommerceInfo, PageInfo,
)

PAGE_TIMEOUT = 30_000  # 30s
MAX_PAGES = 5


async def crawl_site(url: str) -> SiteAnalysis:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            return await _crawl(browser, url)
        finally:
            await browser.close()


async def _crawl(browser: Browser, url: str) -> SiteAnalysis:
    page = await browser.new_page()
    await page.goto(url, wait_until="networkidle", timeout=PAGE_TIMEOUT)
    await page.wait_for_timeout(1000)

    # Extract from top page
    meta = await _extract_meta(page)
    existing_tags = await _extract_existing_tags(page)
    forms = await _extract_forms(page)
    ctas = await _extract_ctas(page)
    ecommerce = await _detect_ecommerce(page)
    technology = await _detect_technology(page)

    pages_analyzed = [PageInfo(url=url, title=meta["title"], type="top")]

    # Discover and crawl internal links
    internal_links = await _find_internal_links(page, url)
    for link_url in internal_links[:MAX_PAGES - 1]:
        try:
            await page.goto(link_url, wait_until="networkidle", timeout=PAGE_TIMEOUT)
            await page.wait_for_timeout(500)
            title = await page.title()
            page_type = _guess_page_type(link_url, title)
            pages_analyzed.append(PageInfo(url=link_url, title=title, type=page_type))

            # Accumulate data from sub-pages
            forms.extend(await _extract_forms(page))
            ctas.extend(await _extract_ctas(page))

            sub_ecom = await _detect_ecommerce(page)
            if sub_ecom and not ecommerce:
                ecommerce = sub_ecom
            elif sub_ecom and ecommerce:
                ecommerce.has_product_page = ecommerce.has_product_page or sub_ecom.has_product_page
                ecommerce.has_cart = ecommerce.has_cart or sub_ecom.has_cart
                ecommerce.has_checkout = ecommerce.has_checkout or sub_ecom.has_checkout
        except Exception:
            continue

    await page.close()

    site_type = _determine_site_type(existing_tags, ecommerce, forms, ctas, technology, meta)

    return SiteAnalysis(
        url=url,
        title=meta["title"],
        description=meta["description"],
        site_type=site_type,
        existing_tags=existing_tags,
        forms=forms,
        cta_elements=ctas,
        ecommerce=ecommerce,
        technology=technology,
        pages_analyzed=pages_analyzed,
    )


async def _extract_meta(page: Page) -> dict:
    title = await page.title()
    description = await page.evaluate("""
        () => {
            const meta = document.querySelector('meta[name="description"]');
            return meta ? meta.content : '';
        }
    """)
    return {"title": title, "description": description}


async def _extract_existing_tags(page: Page) -> List[ExistingTag]:
    return await page.evaluate("""
        () => {
            const tags = [];
            const scripts = document.querySelectorAll('script[src], script');
            for (const s of scripts) {
                const src = s.src || '';
                const text = s.textContent || '';

                // GA4 / gtag.js
                const gaMatch = src.match(/gtag\\/js\\?id=(G-[A-Z0-9]+)/);
                if (gaMatch) {
                    tags.push({ name: 'Google Analytics 4', type: 'ga4', identifier: gaMatch[1] });
                }
                const gtagConfig = text.match(/gtag\\(['"]config['"],\\s*['"](G-[A-Z0-9]+)['"]/);
                if (gtagConfig) {
                    tags.push({ name: 'Google Analytics 4', type: 'ga4', identifier: gtagConfig[1] });
                }

                // GTM
                const gtmMatch = text.match(/GTM-[A-Z0-9]+/) || src.match(/GTM-[A-Z0-9]+/);
                if (gtmMatch) {
                    tags.push({ name: 'Google Tag Manager', type: 'gtm', identifier: gtmMatch[0] });
                }

                // Meta Pixel
                const fbMatch = text.match(/fbq\\(['"]init['"],\\s*['"]([0-9]+)['"]/);
                if (fbMatch) {
                    tags.push({ name: 'Meta Pixel', type: 'meta_pixel', identifier: fbMatch[1] });
                }

                // Google Ads
                const gadsMatch = text.match(/gtag\\(['"]config['"],\\s*['"](AW-[A-Z0-9]+)['"]/);
                if (gadsMatch) {
                    tags.push({ name: 'Google Ads', type: 'google_ads', identifier: gadsMatch[1] });
                }
            }
            // Deduplicate
            const seen = new Set();
            return tags.filter(t => {
                const key = t.type + ':' + t.identifier;
                if (seen.has(key)) return false;
                seen.add(key);
                return true;
            });
        }
    """)


async def _extract_forms(page: Page) -> List[FormInfo]:
    raw = await page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('form')).slice(0, 10).map(f => ({
                action: f.action || '',
                method: (f.method || 'get').toUpperCase(),
                id: f.id || '',
                name: f.name || '',
                fields: Array.from(f.querySelectorAll('input, select, textarea')).map(el =>
                    el.name || el.type || el.tagName.toLowerCase()
                ).filter(Boolean),
            }));
        }
    """)
    return [FormInfo(**f) for f in raw]


async def _extract_ctas(page: Page) -> List[CTAInfo]:
    raw = await page.evaluate("""
        () => {
            const ctas = [];
            // Buttons
            document.querySelectorAll('button, [role="button"], a.btn, a.button, input[type="submit"]').forEach(el => {
                const text = (el.textContent || el.value || '').trim();
                if (text && text.length < 100) {
                    ctas.push({
                        text: text.substring(0, 80),
                        tag: el.tagName.toLowerCase(),
                        href: el.href || '',
                        classes: el.className ? String(el.className).substring(0, 100) : '',
                    });
                }
            });
            return ctas.slice(0, 20);
        }
    """)
    return [CTAInfo(**c) for c in raw]


async def _detect_ecommerce(page: Page) -> Optional[EcommerceInfo]:
    result = await page.evaluate("""
        () => {
            const html = document.documentElement.innerHTML;
            const info = { platform: '', has_product_page: false, has_cart: false, has_checkout: false, currency: '' };

            // Platform detection
            if (html.includes('Shopify') || html.includes('shopify')) info.platform = 'shopify';
            else if (html.includes('WooCommerce') || html.includes('woocommerce')) info.platform = 'woocommerce';
            else if (html.includes('BigCommerce')) info.platform = 'bigcommerce';
            else if (html.includes('Magento')) info.platform = 'magento';

            // Page type detection
            const url = location.href.toLowerCase();
            const path = location.pathname.toLowerCase();
            if (path.includes('/product') || path.includes('/item') || document.querySelector('[data-product-id], .product-price, .add-to-cart'))
                info.has_product_page = true;
            if (path.includes('/cart') || document.querySelector('.cart, #cart, [data-cart]'))
                info.has_cart = true;
            if (path.includes('/checkout') || document.querySelector('.checkout, #checkout'))
                info.has_checkout = true;

            // Currency
            const currMatch = html.match(/["']currency["']:\\s*["']([A-Z]{3})["']/);
            if (currMatch) info.currency = currMatch[1];

            if (!info.platform && !info.has_product_page && !info.has_cart) return null;
            return info;
        }
    """)
    return EcommerceInfo(**result) if result else None


async def _detect_technology(page: Page) -> List[str]:
    return await page.evaluate("""
        () => {
            const tech = [];
            const html = document.documentElement.innerHTML;

            // Frameworks
            if (document.querySelector('#__next') || html.includes('_next/')) tech.push('Next.js');
            if (document.querySelector('#__nuxt') || html.includes('_nuxt/')) tech.push('Nuxt.js');
            if (window.__GATSBY) tech.push('Gatsby');
            if (window.React || document.querySelector('[data-reactroot]')) tech.push('React');
            if (window.Vue || document.querySelector('[data-v-]')) tech.push('Vue.js');
            if (window.angular || document.querySelector('[ng-app], [data-ng-app]')) tech.push('Angular');

            // Services
            if (html.includes('stripe.com') || window.Stripe) tech.push('Stripe');
            if (html.includes('intercom') || window.Intercom) tech.push('Intercom');
            if (html.includes('hubspot')) tech.push('HubSpot');
            if (html.includes('segment.com') || window.analytics) tech.push('Segment');
            if (html.includes('hotjar') || window.hj) tech.push('Hotjar');
            if (html.includes('clarity.ms')) tech.push('Microsoft Clarity');
            if (html.includes('crisp.chat')) tech.push('Crisp');
            if (html.includes('zendesk')) tech.push('Zendesk');

            // CMS/Platforms
            if (html.includes('Shopify') || html.includes('shopify')) tech.push('Shopify');
            if (html.includes('WordPress') || html.includes('wp-content')) tech.push('WordPress');
            if (html.includes('Wix')) tech.push('Wix');
            if (html.includes('Squarespace')) tech.push('Squarespace');

            return [...new Set(tech)];
        }
    """)


async def _find_internal_links(page: Page, base_url: str) -> List[str]:
    parsed = urlparse(base_url)
    domain = parsed.netloc
    links = await page.evaluate("""
        (domain) => {
            const links = new Set();
            document.querySelectorAll('a[href]').forEach(a => {
                try {
                    const url = new URL(a.href, location.origin);
                    if (url.hostname === domain || url.hostname === location.hostname) {
                        const clean = url.origin + url.pathname;
                        if (clean !== location.origin + location.pathname) {
                            links.add(clean);
                        }
                    }
                } catch {}
            });
            return [...links].slice(0, 20);
        }
    """, domain)

    # Prioritize important pages
    priority_keywords = ["product", "item", "cart", "checkout", "pricing", "signup",
                         "login", "contact", "about", "blog", "shop"]
    scored = []
    for link in links:
        score = sum(1 for kw in priority_keywords if kw in link.lower())
        scored.append((score, link))
    scored.sort(key=lambda x: -x[0])
    return [link for _, link in scored]


def _guess_page_type(url: str, title: str) -> str:
    lower = (url + " " + title).lower()
    if any(k in lower for k in ["product", "item", "shop"]):
        return "product"
    if "cart" in lower:
        return "cart"
    if "checkout" in lower:
        return "checkout"
    if any(k in lower for k in ["blog", "article", "news", "post"]):
        return "article"
    if any(k in lower for k in ["pricing", "price", "plan"]):
        return "pricing"
    if any(k in lower for k in ["contact", "support"]):
        return "contact"
    if any(k in lower for k in ["login", "signin", "sign-in"]):
        return "login"
    if any(k in lower for k in ["signup", "register", "sign-up"]):
        return "signup"
    if any(k in lower for k in ["about"]):
        return "about"
    return "other"


def _determine_site_type(
    existing_tags: List[ExistingTag],
    ecommerce: Optional[EcommerceInfo],
    forms: List[FormInfo],
    ctas: List[CTAInfo],
    technology: List[str],
    meta: dict,
) -> str:
    # EC detection
    if ecommerce and (ecommerce.platform or ecommerce.has_product_page):
        return "ec"

    # SaaS detection
    saas_signals = ["pricing", "signup", "login", "sign up", "free trial", "start free",
                    "get started", "dashboard"]
    text = (meta.get("title", "") + " " + meta.get("description", "")).lower()
    cta_texts = " ".join(c.text.lower() for c in ctas)
    if sum(1 for s in saas_signals if s in text or s in cta_texts) >= 2:
        return "saas"

    # LP detection (single page with forms and CTAs, few nav links)
    if forms and len(ctas) >= 3:
        return "lp"

    # Media detection
    media_signals = ["blog", "article", "news", "magazine", "journal"]
    if any(s in text for s in media_signals):
        return "media"

    return "corporate"
