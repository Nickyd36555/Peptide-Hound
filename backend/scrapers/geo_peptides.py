from .base import WooCommerceScraper


class GeoPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://www.geopeptides.com"
    SHOP_PAGES = [
        "https://www.geopeptides.com/product-category/peptides/",
        "https://www.geopeptides.com/shop/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Geo Peptides"
