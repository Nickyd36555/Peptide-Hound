from .base import WooCommerceLoginScraper


class LibertyPeptidesScraper(WooCommerceLoginScraper):
    """Liberty Peptides requires login to access their catalog.

    Set these environment variables before starting the server:

        export LIBERTY_EMAIL="you@example.com"
        export LIBERTY_PASSWORD="yourpassword"
    """

    CREDENTIALS_ENV = {"email": "LIBERTY_EMAIL", "password": "LIBERTY_PASSWORD"}
    LOGIN_URL = "https://libertypeptides.com/my-account/"
    BASE_URL = "https://libertypeptides.com"
    SHOP_PAGES = [
        "https://libertypeptides.com/shop/",
        "https://libertypeptides.com/shop/page/2/",
        "https://libertypeptides.com/product-category/peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Liberty Peptides"
