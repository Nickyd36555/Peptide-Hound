from .base import WooCommerceScraper


class MaximPeptideScraper(WooCommerceScraper):
    BASE_URL = "https://www.maximpeptide.com"
    SHOP_PAGES = [
        "https://www.maximpeptide.com/product-category/peptides/",
        "https://www.maximpeptide.com/product-category/peptides/page/2/",
        "https://www.maximpeptide.com/shop/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Maxim Peptide"
