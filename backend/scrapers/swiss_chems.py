from typing import List
from .base import BaseScraper, ProductData

SHOP_PAGES = [
    "https://swisschems.is/product-category/peptides/",
    "https://swisschems.is/product-category/peptides/page/2/",
]


class SwissChemsScraper(BaseScraper):
    @property
    def vendor_name(self) -> str:
        return "Swiss Chems"

    async def scrape(self) -> List[ProductData]:
        products: List[ProductData] = []
        for page_url in SHOP_PAGES:
            soup = await self.fetch_html(page_url)
            if soup is None:
                continue
            items = soup.select("ul.products li.product, .products .type-product")
            if not items:
                break
            for item in items:
                try:
                    name_el = item.select_one(
                        ".woocommerce-loop-product__title, h2, h3"
                    )
                    price_els = item.select(".woocommerce-Price-amount bdi, .woocommerce-Price-amount")
                    link_el = item.select_one("a[href]")
                    if not name_el or not price_els:
                        continue
                    name = name_el.get_text(strip=True)
                    price = self.parse_price(price_els[-1].get_text(strip=True))
                    url = link_el.get("href", "https://swisschems.is") if link_el else "https://swisschems.is"
                    weight_mg = self.parse_weight_mg(name)
                    if price and weight_mg:
                        p = self.build_product(name, price, url, weight_mg)
                        if p:
                            products.append(p)
                except Exception:
                    continue
        return products
