from .base import WooCommerceScraper


class EternalPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://eternalpeptides.com"
    SHOP_PAGES = [
        "https://eternalpeptides.com/shop/",
        "https://eternalpeptides.com/shop/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Eternal Peptides"
