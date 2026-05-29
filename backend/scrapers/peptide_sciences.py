from typing import List
from .base import BaseScraper, ProductData

SHOP_PAGES = [
    "https://www.peptidesciences.com/peptides/",
    "https://www.peptidesciences.com/peptides/page/2/",
]


class PeptideSciencesScraper(BaseScraper):
    @property
    def vendor_name(self) -> str:
        return "Peptide Sciences"

    async def scrape(self) -> List[ProductData]:
        products: List[ProductData] = []
        for page_url in SHOP_PAGES:
            soup = await self.fetch_html(page_url)
            if soup is None:
                continue
            # Standard WooCommerce product grid
            items = soup.select("ul.products li.product, .products .type-product")
            if not items:
                break
            for item in items:
                try:
                    name_el = item.select_one(
                        ".woocommerce-loop-product__title, h2.woocommerce-loop-product__title, h3"
                    )
                    # Use the lowest listed price (range shows sale price last)
                    price_els = item.select(".woocommerce-Price-amount bdi, .woocommerce-Price-amount")
                    link_el = item.select_one("a.woocommerce-LoopProduct-link, a[href]")
                    if not name_el or not price_els:
                        continue
                    name = name_el.get_text(strip=True)
                    price_text = price_els[-1].get_text(strip=True)
                    price = self.parse_price(price_text)
                    url = link_el.get("href", "https://www.peptidesciences.com") if link_el else "https://www.peptidesciences.com"
                    weight_mg = self.parse_weight_mg(name)
                    if price and weight_mg:
                        p = self.build_product(name, price, url, weight_mg)
                        if p:
                            products.append(p)
                except Exception:
                    continue
        return products
