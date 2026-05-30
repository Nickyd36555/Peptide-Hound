from .base import WooCommerceScraper


class VerifiedPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://verifiedpeptides.com"
    SHOP_PAGES = [
        "https://verifiedpeptides.com/peptides/",
        "https://verifiedpeptides.com/peptides/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Verified Peptides"
