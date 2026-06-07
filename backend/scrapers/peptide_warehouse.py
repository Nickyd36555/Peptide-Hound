from .base import WooCommerceScraper


class PeptideWarehouseScraper(WooCommerceScraper):
    BASE_URL = "https://www.peptidewarehouse.com"
    SHOP_PAGES = [
        "https://www.peptidewarehouse.com/shop/",
        "https://www.peptidewarehouse.com/shop/page/2/",
        "https://www.peptidewarehouse.com/product-category/peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Peptide Warehouse"
