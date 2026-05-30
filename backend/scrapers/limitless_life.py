from .base import WooCommerceScraper


class LimitlessLifeScraper(WooCommerceScraper):
    BASE_URL = "https://limitlesslifenootropics.com"
    SHOP_PAGES = [
        "https://limitlesslifenootropics.com/product-category/peptides/",
        "https://limitlesslifenootropics.com/product-category/peptides/page/2/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Limitless Life"
