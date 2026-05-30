from .base import WooCommerceScraper


class SwissChemsScraper(WooCommerceScraper):
    BASE_URL = "https://swisschems.is"
    SHOP_PAGES = [
        "https://swisschems.is/product-category/peptides/",
        "https://swisschems.is/product-category/peptides/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Swiss Chems"
