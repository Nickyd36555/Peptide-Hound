from .base import WooCommerceScraper


class CorePeptidesScraper(WooCommerceScraper):
    BASE_URL = "https://corepeptides.com"
    SHOP_PAGES = [
        "https://corepeptides.com/shop/",
        "https://corepeptides.com/shop/page/2/",
        "https://corepeptides.com/product-category/peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Core Peptides"
