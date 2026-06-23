"""Direct immowelt.de scraper for the MCP server.

Pure httpx + BeautifulSoup (no proxy, no Apify) — immowelt serves listings to a
normal residential request, so the server can scrape it directly and stay
zero-friction for users. Listing data only; realtor/agent personal data is dropped.

URL/parse logic adapted from the existing immowelt actor.
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://www.immowelt.de"
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)

_TX = {"rent": "mieten", "mieten": "mieten", "buy": "kaufen", "kaufen": "kaufen", "sale": "kaufen"}
_PT = {
    "apartment": "wohnungen", "apartments": "wohnungen", "wohnungen": "wohnungen", "flat": "wohnungen",
    "house": "haeuser", "houses": "haeuser", "haeuser": "haeuser", "haus": "haeuser",
    "plot": "grundstuecke", "grundstuecke": "grundstuecke", "commercial": "gewerbe", "gewerbe": "gewerbe",
}

# immowelt expects German city slugs; map common English/umlaut forms.
_CITY_ALIASES = {
    "munich": "muenchen", "münchen": "muenchen",
    "cologne": "koeln", "köln": "koeln",
    "nuremberg": "nuernberg", "nürnberg": "nuernberg",
    "hanover": "hannover",
    "düsseldorf": "duesseldorf", "dusseldorf": "duesseldorf",
    "brunswick": "braunschweig",
}


def _city_slug(city: str) -> str:
    c = (city or "").strip().lower()
    return _CITY_ALIASES.get(c, c)

PRICE_PATTERN = re.compile(r"([\d.]+)\s*€")
SIZE_PATTERN = re.compile(r"([\d.,]+)\s*m²")
ROOMS_PATTERN = re.compile(r"([\d.,]+)\s*Zimmer")
FLOOR_PATTERN = re.compile(r"\b(\d{1,2})\.\s*Geschoss\b|\b(EG|Erdgeschoss|DG|Dachgeschoss|UG|KG)\b")
ADDRESS_PATTERN = re.compile(
    r"([A-Za-zÄÖÜäöüß\.\-'][\wäöüÄÖÜß\.\-'\s]*?\d+[a-zA-Z]?),\s*"
    r"([A-Za-zÄÖÜäöüß\.\-'][\wäöüÄÖÜß\.\-']*?),\s*"
    r"([A-Za-zÄÖÜäöüß\.\-'\s]+?)\s*"
    r"\((\d{5})\)"
)


def build_search_url(city, transaction_type="mieten", property_type="wohnungen", page=1,
                     min_price=None, max_price=None, min_size=None, min_rooms=None) -> str:
    tx = _TX.get((transaction_type or "").lower(), "mieten")
    pt = _PT.get((property_type or "").lower(), "wohnungen")
    url = f"{BASE_URL}/liste/{quote(_city_slug(city))}/{pt}/{tx}"
    params: list[str] = []
    if min_price is not None:
        params.append(f"pmin={min_price}")
    if max_price is not None:
        params.append(f"pmax={max_price}")
    if min_size is not None:
        params.append(f"wfmin={min_size}")
    if min_rooms is not None:
        params.append(f"zimin={min_rooms}")
    if page > 1:
        params.append(f"cp={page}")
    if params:
        url += "?" + "&".join(params)
    return url


def extract_listings_from_html(html: str) -> list[dict[str, Any]]:
    """Parse immowelt search HTML into structured listings (no agent/personal data)."""
    soup = BeautifulSoup(html, "lxml")
    listings: list[dict[str, Any]] = []
    seen: set[str] = set()

    cards = soup.select("div.css-79elbk")
    if not cards:
        by_id: dict[str, Any] = {}
        for link in soup.select('a[href*="/expose/"]'):
            href = link.get("href", "")
            m = re.search(r"/expose/([A-Za-z0-9-_]+)", href)
            if m and m.group(1) not in by_id and link.parent is not None:
                by_id[m.group(1)] = link.parent.parent or link.parent
        cards = list(by_id.values())

    for card in cards:
        link = card.select_one('a[href*="/expose/"]')
        if not link:
            continue
        href = link.get("href", "")
        url = href if href.startswith("http") else urljoin(BASE_URL, href)
        m = re.search(r"/expose/([A-Za-z0-9-_]+)", url)
        expose_id = m.group(1) if m else None
        if not expose_id or expose_id in seen:
            continue
        seen.add(expose_id)

        text = card.get_text(" ", strip=True)

        price_eur = None
        price_label = None
        for label in ("Kaltmiete", "Kaufpreis", "Warmmiete", "Gesamtmiete"):
            m = re.search(rf"([\d.]+)\s*€\s*{label}", text)
            if m:
                try:
                    price_eur = float(m.group(1).replace(".", ""))
                    price_label = label
                    break
                except ValueError:
                    pass
        if price_eur is None:
            m = PRICE_PATTERN.search(text)
            if m:
                try:
                    price_eur = float(m.group(1).replace(".", ""))
                except ValueError:
                    pass

        size_sqm = None
        m = SIZE_PATTERN.search(text)
        if m:
            try:
                size_sqm = float(m.group(1).replace(",", "."))
            except ValueError:
                pass

        rooms = None
        m = ROOMS_PATTERN.search(text)
        if m:
            try:
                rooms = float(m.group(1).replace(",", "."))
            except ValueError:
                pass

        street = district = city = plz = None
        am = ADDRESS_PATTERN.search(text)
        if am:
            street = re.sub(r"^\d+\.\s*Geschoss\s+", "", am.group(1).strip())
            street = re.sub(r"^(EG|DG|UG|KG|Erdgeschoss|Dachgeschoss|Geschoss)\s+", "", street)
            district, city, plz = am.group(2).strip(), am.group(3).strip(), am.group(4).strip()

        floor = None
        m = FLOOR_PATTERN.search(text)
        if m:
            floor = m.group(1) or m.group(2)

        title_el = link.select_one("h2, h3, .heading")
        title = title_el.get_text(" ", strip=True) if title_el else ""

        img = card.select_one("img")
        image_url = (img.get("src") or img.get("data-src")) if img else None

        listings.append({
            "expose_id": expose_id, "url": url, "title": title,
            "price_eur": price_eur, "price_label": price_label,
            "size_sqm": size_sqm, "rooms": rooms, "floor": floor,
            "address": street, "district": district, "city": city, "plz": plz,
            "image_url": image_url,
        })
    return listings


def search(city="berlin", transaction_type="mieten", property_type="wohnungen",
           min_price=None, max_price=None, min_size=None, min_rooms=None, limit=10) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    headers = {"User-Agent": _UA, "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True) as client:
        page = 1
        while len(out) < limit and page <= 5:
            url = build_search_url(city, transaction_type, property_type, page,
                                   min_price, max_price, min_size, min_rooms)
            try:
                r = client.get(url)
            except httpx.HTTPError:
                break
            if r.status_code != 200:
                break
            new = [i for i in extract_listings_from_html(r.text) if i["expose_id"] not in seen]
            if not new:
                break
            for i in new:
                seen.add(i["expose_id"])
                out.append(i)
                if len(out) >= limit:
                    break
            page += 1
    return out[:limit]
