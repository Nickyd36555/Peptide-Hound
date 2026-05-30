from typing import List
from .base import BaseScraper, ProductData

# Iron Daddy uses a Shopify-style JSON endpoint
PRODUCTS_API = "https://www.irondaddy.to/products.json?limit=250"
BASE_URL = "https://www.irondaddy.to"

# Fallback WooCommerce pages if JSON endpoint unavailable
WC_PAGES = [
    "https://www.irondaddy.to/product-category/peptides/",
    "https://www.irondaddy.to/shop/",
]


class IronDaddyScraper(BaseScraper):
    @property
    def vendor_name(self) -> str:
        return "Iron Daddy"

    async def scrape(self) -> List[ProductData]:
        # Try Shopify JSON first
        data = await self.fetch_json(PRODUCTS_API)
        if data and "products" in data:
            return self._parse_shopify(data)
        # Fallback to HTML
        return await self._parse_woocommerce()

    def _parse_shopify(self, data: dict) -> List[ProductData]:
        products: List[ProductData] = []
        for product in data.get("products", []):
            title = product.get("title", "").strip()
            handle = product.get("handle", "")
            url = f"{BASE_URL}/products/{handle}"
            for variant in product.get("variants", []):
                variant_title = (variant.get("title") or "").strip()
                try:
                    price = float(variant.get("price", "0") or 0)
                except (ValueError, TypeError):
                    continue
                name = f"{title} {variant_title}" if variant_title.lower() not in ("", "default title") else title
                weight_mg = self.parse_weight_mg(name)
                if weight_mg:
                    p = self.build_product(name, price, url, weight_mg)
                    if p:
                        products.append(p)
        return products

    async def _parse_woocommerce(self) -> List[ProductData]:
        products: List[ProductData] = []
        for page_url in WC_PAGES:
            soup = await self.fetch_html(page_url)
            if soup is None:
                continue
            items = soup.select("ul.products li.product, .products .type-product")
            if not items:
                break
            for item in items:
                try:
                    name_el = item.select_one(".woocommerce-loop-product__title, h2, h3")
                    price_els = item.select(".woocommerce-Price-amount bdi, .woocommerce-Price-amount")
                    link_el = item.select_one("a[href]")
                    if not name_el or not price_els:
                        continue
                    name = name_el.get_text(strip=True)
                    price = self.parse_price(price_els[-1].get_text(strip=True))
                    href = link_el.get("href", BASE_URL) if link_el else BASE_URL
                    weight_mg = self.parse_weight_mg(name)
                    if price and weight_mg:
                        p = self.build_product(name, price, href, weight_mg)
                        if p:
                            products.append(p)
                except Exception:
                    continue
        return products
