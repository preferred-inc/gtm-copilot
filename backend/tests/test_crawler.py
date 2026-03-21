from app.services.crawler import _guess_page_type, _determine_site_type
from app.schemas.analysis import ExistingTag, EcommerceInfo, FormInfo, CTAInfo


class TestGuessPageType:
    def test_product_page(self):
        assert _guess_page_type("https://example.com/product/123", "Cool Product") == "product"

    def test_cart_page(self):
        assert _guess_page_type("https://example.com/cart", "Your Cart") == "cart"

    def test_checkout_page(self):
        assert _guess_page_type("https://example.com/checkout", "Checkout") == "checkout"

    def test_blog_page(self):
        assert _guess_page_type("https://example.com/blog/post-1", "My Blog Post") == "article"

    def test_pricing_page(self):
        assert _guess_page_type("https://example.com/pricing", "Pricing Plans") == "pricing"

    def test_contact_page(self):
        assert _guess_page_type("https://example.com/contact", "Contact Us") == "contact"

    def test_login_page(self):
        assert _guess_page_type("https://example.com/login", "Login") == "login"

    def test_signup_page(self):
        assert _guess_page_type("https://example.com/signup", "Sign Up") == "signup"

    def test_unknown_page(self):
        assert _guess_page_type("https://example.com/xyz", "XYZ Page") == "other"


class TestDetermineSiteType:
    def _meta(self, title="", desc=""):
        return {"title": title, "description": desc}

    def test_ec_with_platform(self):
        ecom = EcommerceInfo(platform="shopify")
        result = _determine_site_type([], ecom, [], [], [], self._meta())
        assert result == "ec"

    def test_ec_with_product_page(self):
        ecom = EcommerceInfo(has_product_page=True)
        result = _determine_site_type([], ecom, [], [], [], self._meta())
        assert result == "ec"

    def test_saas_detection(self):
        ctas = [
            CTAInfo(text="Start Free Trial", tag="button"),
            CTAInfo(text="Sign Up", tag="a"),
            CTAInfo(text="Get Started", tag="button"),
        ]
        result = _determine_site_type([], None, [], ctas, [], self._meta("SaaS App", "pricing plans"))
        assert result == "saas"

    def test_lp_with_forms_and_ctas(self):
        forms = [FormInfo(action="/submit")]
        ctas = [CTAInfo(text=f"CTA {i}", tag="button") for i in range(4)]
        result = _determine_site_type([], None, forms, ctas, [], self._meta())
        assert result == "lp"

    def test_media_detection(self):
        result = _determine_site_type([], None, [], [], [], self._meta("Tech Blog", "Latest news and articles"))
        assert result == "media"

    def test_corporate_fallback(self):
        result = _determine_site_type([], None, [], [], [], self._meta("Company", "Our company"))
        assert result == "corporate"
