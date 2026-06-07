from .base import WooCommerceLoginScraper


class PrimePeptidesScraper(WooCommerceLoginScraper):
    """Prime Peptides requires login to access their catalog.

    Set these environment variables before starting the server:

        export PRIME_PEPTIDES_EMAIL="you@example.com"
        export PRIME_PEPTIDES_PASSWORD="yourpassword"
    """

    CREDENTIALS_ENV = {"email": "PRIME_PEPTIDES_EMAIL", "password": "PRIME_PEPTIDES_PASSWORD"}
    LOGIN_URL = "https://primepeptides.com/my-account/"
    BASE_URL = "https://primepeptides.com"
    SHOP_PAGES = [
        "https://primepeptides.com/shop/",
        "https://primepeptides.com/shop/page/2/",
        "https://primepeptides.com/product-category/peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Prime Peptides"
