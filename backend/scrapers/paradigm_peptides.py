from .base import WooCommerceScraper


class ParadigmPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://paradigmpeptides.com"
    SHOP_PAGES = [
        "https://paradigmpeptides.com/product-category/peptides/",
        "https://paradigmpeptides.com/product-category/peptides/page/2/",
        "https://paradigmpeptides.com/shop/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Paradigm Peptides"
