from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import re
import httpx
from bs4 import BeautifulSoup

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


@dataclass
class ProductData:
    name: str
    price: float
    url: str
    vendor: str
    weight_mg: float
    price_per_mg: float


class BaseScraper(ABC):
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    @property
    @abstractmethod
    def vendor_name(self) -> str: ...

    @abstractmethod
    async def scrape(self) -> List[ProductData]: ...

    async def fetch_html(self, url: str) -> Optional[BeautifulSoup]:
        """GET a URL and return parsed HTML, or None on any error."""
        try:
            resp = await self.client.get(
                url, headers=REQUEST_HEADERS, timeout=30.0, follow_redirects=True
            )
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except Exception:
            return None

    async def fetch_json(self, url: str) -> Optional[dict]:
        """GET a URL and return parsed JSON, or None on any error."""
        try:
            resp = await self.client.get(
                url, headers=REQUEST_HEADERS, timeout=30.0, follow_redirects=True
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    @staticmethod
    def parse_price(text: str) -> Optional[float]:
        """Extract a USD price from strings like '$49.99' or '49.99'."""
        clean = text.replace(",", "")
        m = re.search(r"\$?\s*([\d]+\.?\d*)", clean)
        return float(m.group(1)) if m else None

    @staticmethod
    def parse_weight_mg(text: str) -> Optional[float]:
        """Extract weight in mg, converting mcg if needed."""
        mcg = re.search(r"(\d+(?:\.\d+)?)\s*mcg\b", text, re.IGNORECASE)
        if mcg:
            return float(mcg.group(1)) / 1000.0
        mg = re.search(r"(\d+(?:\.\d+)?)\s*mg\b", text, re.IGNORECASE)
        return float(mg.group(1)) if mg else None

    def build_product(
        self, name: str, price: float, url: str, weight_mg: float
    ) -> Optional[ProductData]:
        if not (weight_mg and weight_mg > 0 and price and price > 0):
            return None
        return ProductData(
            name=name.strip(),
            price=round(price, 2),
            url=url,
            vendor=self.vendor_name,
            weight_mg=weight_mg,
            price_per_mg=round(price / weight_mg, 4),
        )


class LoginScraper(BaseScraper):
    """Base for sites that require a session login before scraping.

    Credentials are read from environment variables — NEVER hardcoded.
    Set CREDENTIALS_ENV on each subclass:

        CREDENTIALS_ENV = {"email": "MYSITE_EMAIL", "password": "MYSITE_PASSWORD"}

    Then export those vars before starting the server:

        export MYSITE_EMAIL="you@example.com"
        export MYSITE_PASSWORD="yourpassword"
        uvicorn backend.main:app

    If the env vars are absent the scraper silently returns [].
    """

    CREDENTIALS_ENV: dict[str, str] = {}

    def _creds(self) -> Optional[tuple[str, str]]:
        """Return (email, password) from env vars, or None if not set."""
        import os
        email = os.getenv(self.CREDENTIALS_ENV.get("email", ""), "")
        password = os.getenv(self.CREDENTIALS_ENV.get("password", ""), "")
        return (email, password) if email and password else None

    async def login(self, email: str, password: str) -> bool:
        """Perform the site login. Return True on success."""
        raise NotImplementedError

    async def scrape(self) -> List[ProductData]:
        creds = self._creds()
        if not creds:
            return []
        ok = await self.login(*creds)
        if not ok:
            return []
        return await self.scrape_authenticated()

    async def scrape_authenticated(self) -> List[ProductData]:
        """Scrape after a successful login. Subclasses implement this."""
        raise NotImplementedError


class WooCommerceLoginScraper(LoginScraper):
    """LoginScraper for standard WooCommerce sites.

    Login flow:
      1. GET /my-account/ — extract woocommerce-login-nonce hidden field
      2. POST /my-account/ with email + password + nonce
      3. Verify redirect landed on the account dashboard (not back on login)
      4. Scrape SHOP_PAGES with the authenticated session cookie
    """

    LOGIN_URL: str = ""   # e.g. "https://example.com/my-account/"
    SHOP_PAGES: List[str] = []
    BASE_URL: str = ""

    async def login(self, email: str, password: str) -> bool:
        # Step 1: fetch login page and extract nonce
        soup = await self.fetch_html(self.LOGIN_URL)
        if not soup:
            return False

        nonce_input = soup.find("input", {"name": "woocommerce-login-nonce"})
        nonce = nonce_input["value"] if nonce_input else ""

        referer_input = soup.find("input", {"name": "_wp_http_referer"})
        referer = referer_input["value"] if referer_input else "/my-account/"

        # Step 2: POST credentials
        try:
            resp = await self.client.post(
                self.LOGIN_URL,
                data={
                    "username": email,
                    "password": password,
                    "login": "Sign in",
                    "woocommerce-login-nonce": nonce,
                    "_wp_http_referer": referer,
                },
                headers={**REQUEST_HEADERS, "Referer": self.LOGIN_URL},
                timeout=30.0,
                follow_redirects=True,
            )
        except Exception:
            return False

        # Step 3: success = we're no longer on the login page
        # WooCommerce redirects to /my-account/ dashboard on success;
        # on failure it re-renders the login form with an error notice.
        return "woocommerce-error" not in resp.text and "woocommerce-login-nonce" not in resp.text

    async def scrape_authenticated(self) -> List[ProductData]:
        """Same WooCommerce product grid parsing as WooCommerceScraper."""
        products: List[ProductData] = []
        for page_url in self.SHOP_PAGES:
            soup = await self.fetch_html(page_url)
            if soup is None:
                continue
            items = soup.select(
                "ul.products li.product, .products .type-product, "
                ".woocommerce-loop-product, .product-item"
            )
            if not items:
                break
            for item in items:
                try:
                    name_el = item.select_one(
                        ".woocommerce-loop-product__title, "
                        "h2.woocommerce-loop-product__title, h2, h3"
                    )
                    price_els = item.select(
                        ".woocommerce-Price-amount bdi, .woocommerce-Price-amount"
                    )
                    link_el = item.select_one("a[href]")
                    if not name_el or not price_els:
                        continue
                    name = name_el.get_text(strip=True)
                    price = self.parse_price(price_els[-1].get_text(strip=True))
                    href = link_el.get("href", self.BASE_URL) if link_el else self.BASE_URL
                    weight_mg = self.parse_weight_mg(name)
                    if price and weight_mg:
                        p = self.build_product(name, price, href, weight_mg)
                        if p:
                            products.append(p)
                except Exception:
                    continue
        return products


class WooCommerceScraper(BaseScraper):
    """Shared scrape() logic for WooCommerce product grids.

    Subclasses set SHOP_PAGES (list of paginated URLs to try) and
    BASE_URL (fallback for products with no href).
    """

    SHOP_PAGES: List[str] = []
    BASE_URL: str = ""

    async def scrape(self) -> List[ProductData]:
        products: List[ProductData] = []
        for page_url in self.SHOP_PAGES:
            soup = await self.fetch_html(page_url)
            if soup is None:
                continue
            items = soup.select(
                "ul.products li.product, .products .type-product, "
                ".woocommerce-loop-product, .product-item"
            )
            if not items:
                break
            for item in items:
                try:
                    name_el = item.select_one(
                        ".woocommerce-loop-product__title, "
                        "h2.woocommerce-loop-product__title, h2, h3"
                    )
                    # Pick the last price element — on sale items it's the sale price
                    price_els = item.select(
                        ".woocommerce-Price-amount bdi, .woocommerce-Price-amount"
                    )
                    link_el = item.select_one("a[href]")
                    if not name_el or not price_els:
                        continue
                    name = name_el.get_text(strip=True)
                    price = self.parse_price(price_els[-1].get_text(strip=True))
                    href = link_el.get("href", self.BASE_URL) if link_el else self.BASE_URL
                    weight_mg = self.parse_weight_mg(name)
                    if price and weight_mg:
                        p = self.build_product(name, price, href, weight_mg)
                        if p:
                            products.append(p)
                except Exception:
                    continue
        return products
