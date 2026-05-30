from .base import WooCommerceScraper


class BehemothLabzScraper(WooCommerceScraper):
    BASE_URL = "https://behemothlabz.com"
    SHOP_PAGES = [
        "https://behemothlabz.com/product-category/peptides/",
        "https://behemothlabz.com/product-category/peptides/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Behemoth Labz"
