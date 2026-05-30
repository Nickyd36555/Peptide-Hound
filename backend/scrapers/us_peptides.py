from .base import WooCommerceScraper


class USPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://uspeptides.com"
    SHOP_PAGES = [
        "https://uspeptides.com/product-category/peptides/",
        "https://uspeptides.com/shop/",
    ]

    @property
    def vendor_name(self) -> str:
        return "US Peptides"
