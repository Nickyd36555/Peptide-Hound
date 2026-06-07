from .base import WooCommerceScraper


class BiotechPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://www.biotechpeptides.com"
    SHOP_PAGES = [
        "https://www.biotechpeptides.com/shop/",
        "https://www.biotechpeptides.com/shop/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Biotech Peptides"
