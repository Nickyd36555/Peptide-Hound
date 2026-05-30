from .base import WooCommerceScraper


class NootropicSourceScraper(WooCommerceScraper):
    BASE_URL = "https://nootropicsource.com"
    SHOP_PAGES = [
        "https://nootropicsource.com/product-category/peptides/",
        "https://nootropicsource.com/shop/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Nootropic Source"
