from .base import WooCommerceScraper


class ParamountPeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://paramountpeptides.com"
    SHOP_PAGES = [
        "https://paramountpeptides.com/all-peptide/",
        "https://paramountpeptides.com/all-peptide/page/2/",
        "https://paramountpeptides.com/shop/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Paramount Peptides"
