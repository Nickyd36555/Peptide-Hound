from .base import WooCommerceScraper


class PureRawzScraper(WooCommerceScraper):
    BASE_URL = "https://purerawz.co"
    SHOP_PAGES = [
        "https://purerawz.co/product-category/peptides/",
        "https://purerawz.co/product-category/peptides/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Pure Rawz"
