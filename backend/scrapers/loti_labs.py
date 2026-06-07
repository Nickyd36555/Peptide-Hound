from .base import WooCommerceLoginScraper


class LotiLabsScraper(WooCommerceLoginScraper):
    """Loti Labs — site was returning 503 when checked publicly; may require login.

    Set these environment variables before starting the server:

        export LOTI_LABS_EMAIL="you@example.com"
        export LOTI_LABS_PASSWORD="yourpassword"
    """

    CREDENTIALS_ENV = {"email": "LOTI_LABS_EMAIL", "password": "LOTI_LABS_PASSWORD"}
    LOGIN_URL = "https://lotilabs.com/my-account/"
    BASE_URL = "https://lotilabs.com"
    SHOP_PAGES = [
        "https://lotilabs.com/shop/",
        "https://lotilabs.com/shop/page/2/",
        "https://lotilabs.com/product-category/peptides/",
    ]

    @property
    def vendor_name(self) -> str:
        return "Loti Labs"
