from .base import WooCommerceScraper


class EvolvedPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://www.evolvedpeptides.com"
    SHOP_PAGES = [
        "https://www.evolvedpeptides.com/shop/",
        "https://www.evolvedpeptides.com/shop/page/2/",
        "https://www.evolvedpeptides.com/product-category/peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Evolved Peptides"
