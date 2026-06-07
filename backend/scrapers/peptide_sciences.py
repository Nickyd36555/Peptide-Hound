from .base import WooCommerceScraper


class PeptideSciencesScraper(WooCommerceScraper):
    BASE_URL = "https://www.peptidesciences.com"
    SHOP_PAGES = [
        "https://www.peptidesciences.com/peptides/",
        "https://www.peptidesciences.com/peptides/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Peptide Sciences"
