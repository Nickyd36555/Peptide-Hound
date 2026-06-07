from .base import WooCommerceScraper


class PolarispeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://polarispeptides.com"
    SHOP_PAGES = [
        "https://polarispeptides.com/shop/",
        "https://polarispeptides.com/shop/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Polaris Peptides"
