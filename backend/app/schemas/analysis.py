from pydantic import BaseModel
from typing import List, Optional


class ExistingTag(BaseModel):
    name: str           # e.g. "Google Analytics 4", "Meta Pixel"
    type: str           # e.g. "ga4", "meta_pixel", "gtm"
    identifier: str     # e.g. measurement_id, pixel_id


class FormInfo(BaseModel):
    action: str = ""
    method: str = ""
    id: str = ""
    name: str = ""
    fields: List[str] = []   # field names/types


class CTAInfo(BaseModel):
    text: str
    tag: str              # "a", "button", etc.
    href: str = ""
    classes: str = ""


class EcommerceInfo(BaseModel):
    platform: str = ""         # "shopify", "woocommerce", etc.
    has_product_page: bool = False
    has_cart: bool = False
    has_checkout: bool = False
    currency: str = ""


class PageInfo(BaseModel):
    url: str
    title: str
    type: str = ""    # "top", "product", "cart", "article", etc.


class SiteAnalysis(BaseModel):
    url: str
    title: str
    description: str
    site_type: str                              # "ec", "saas", "media", "lp", "corporate"
    existing_tags: List[ExistingTag] = []
    forms: List[FormInfo] = []
    cta_elements: List[CTAInfo] = []
    ecommerce: Optional[EcommerceInfo] = None
    technology: List[str] = []
    pages_analyzed: List[PageInfo] = []
