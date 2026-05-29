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
