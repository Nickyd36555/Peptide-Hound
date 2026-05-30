from .base import WooCommerceScraper


class PeptideProScraper(WooCommerceScraper):
    BASE_URL = "https://peptidepro.com"
    SHOP_PAGES = [
        "https://peptidepro.com/shop/",
        "https://peptidepro.com/product-category/peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Peptide Pro"
