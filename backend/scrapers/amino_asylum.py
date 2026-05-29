from typing import List
from .base import BaseScraper, ProductData

# Shopify JSON API — no HTML parsing needed
PRODUCTS_API = "https://aminoasylum.shop/products.json?limit=250"
BASE_URL = "https://aminoasylum.shop"


class AminoAsylumScraper(BaseScraper):
    @property
    def vendor_name(self) -> str:
        return "Amino Asylum"

    async def scrape(self) -> List[ProductData]:
        data = await self.fetch_json(PRODUCTS_API)
        if data is None:
            return []

        products: List[ProductData] = []
        for product in data.get("products", []):
            title = product.get("title", "").strip()
            handle = product.get("handle", "")
            product_url = f"{BASE_URL}/products/{handle}"

            for variant in product.get("variants", []):
                variant_title = (variant.get("title") or "").strip()
                price_str = variant.get("price", "0") or "0"
                try:
                    price = float(price_str)
                except ValueError:
                    continue

                name = f"{title} {variant_title}" if variant_title.lower() not in ("", "default title") else title
                weight_mg = self.parse_weight_mg(name)
                if weight_mg:
                    p = self.build_product(name, price, product_url, weight_mg)
                    if p:
                        products.append(p)

        return products
