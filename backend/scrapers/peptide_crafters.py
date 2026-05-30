from .base import WooCommerceScraper


class PeptideCraftersScraper(WooCommerceScraper):
    BASE_URL = "https://peptidecrafters.com"
    SHOP_PAGES = [
        "https://peptidecrafters.com/shop/",
        "https://peptidecrafters.com/shop/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Peptide Crafters"
