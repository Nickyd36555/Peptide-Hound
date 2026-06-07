from .base import WooCommerceLoginScraper


class NuLifePeptidesScraper(WooCommerceLoginScraper):
    """NuLife Peptides requires an account to browse their full catalog.

    Set these environment variables before starting the server:

        export NULIFE_EMAIL="you@example.com"
        export NULIFE_PASSWORD="yourpassword"
    """

    CREDENTIALS_ENV = {"email": "NULIFE_EMAIL", "password": "NULIFE_PASSWORD"}
    LOGIN_URL = "https://nulifepeptides.com/my-account/"
    BASE_URL = "https://nulifepeptides.com"
    SHOP_PAGES = [
        "https://nulifepeptides.com/shop/",
        "https://nulifepeptides.com/shop/page/2/",
        "https://nulifepeptides.com/product-category/peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "NuLife Peptides"
