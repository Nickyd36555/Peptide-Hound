from .base import WooCommerceScraper


class CoastalPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://coastalpeptides.com"
    SHOP_PAGES = [
        "https://coastalpeptides.com/product-category/healing-research-peptides/",
        "https://coastalpeptides.com/product-category/ghrp-research-peptides/",
        "https://coastalpeptides.com/product-category/glp-research-peptides/",
        "https://coastalpeptides.com/product-category/wellness-research-peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Coastal Peptides"
