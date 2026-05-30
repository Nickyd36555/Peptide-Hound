from .base import WooCommerceScraper


class BlueSkyPeptideScraper(WooCommerceScraper):
    BASE_URL = "https://www.blueskypeptide.com"
    SHOP_PAGES = [
        "https://www.blueskypeptide.com/shop/",
        "https://www.blueskypeptide.com/shop/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Blue Sky Peptide"
