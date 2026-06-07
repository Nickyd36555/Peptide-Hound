from .base import WooCommerceScraper


class AxiomPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://axiompeptides.com"
    SHOP_PAGES = [
        "https://axiompeptides.com/product-category/peptides/",
        "https://axiompeptides.com/shop/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Axiom Peptides"
