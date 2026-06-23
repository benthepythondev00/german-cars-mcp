"""German Real Estate — free MCP server.

One tool, `search_properties`, returns structured German property listings from
immowelt.de. Pure httpx + BeautifulSoup — **no API key, no proxy, works instantly**.
Listing data only (agent/personal data is dropped). Free tier caps results.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

from mcp.server.fastmcp import FastMCP

try:  # works both as `python src/server.py` and `from src import server`
    from src import realestate
except ImportError:
    import realestate

FREE_LIMIT = int(os.environ.get("REALESTATE_FREE_LIMIT", "10"))
UPGRADE_URL = os.environ.get("REALESTATE_UPGRADE_URL", "https://example.com")
USAGE_LOG = os.environ.get("REALESTATE_USAGE_LOG", "")

mcp = FastMCP("German Real Estate")


def _log_usage(event: dict[str, Any]) -> None:
    """Record a tool call — the kill-or-continue metric. stderr always; file if set."""
    record = {"ts": int(time.time()), **event}
    line = json.dumps(record, ensure_ascii=False)
    print(f"[realestate] {line}", file=sys.stderr)
    if USAGE_LOG:
        try:
            with open(USAGE_LOG, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError:
            pass


_DEMO = [
    {"price_eur": 1799.0, "price_label": "Warmmiete", "size_sqm": 80.7, "rooms": 3.0,
     "district": "Kreuzberg", "city": "Berlin", "plz": "10999",
     "url": "https://www.immowelt.de/expose/demo-1"},
    {"price_eur": 849.0, "price_label": "Kaltmiete", "size_sqm": 28.6, "rooms": 1.0,
     "district": "Friedenau", "city": "Berlin", "plz": "12161",
     "url": "https://www.immowelt.de/expose/demo-2"},
    {"price_eur": 2061.0, "price_label": "Kaltmiete", "size_sqm": 90.8, "rooms": 4.0,
     "district": "Spandau", "city": "Berlin", "plz": "13597",
     "url": "https://www.immowelt.de/expose/demo-3"},
]


def _demo(limit: int) -> list[dict[str, Any]]:
    return (_DEMO * (limit // len(_DEMO) + 1))[:limit]


def _search_properties(
    city: str = "berlin",
    transaction_type: str = "rent",
    property_type: str = "apartment",
    min_price: int | None = None,
    max_price: int | None = None,
    min_size: int | None = None,
    min_rooms: float | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    capped = max(1, min(limit or FREE_LIMIT, FREE_LIMIT))
    _log_usage({"tool": "search_properties", "city": city, "tx": transaction_type,
                "type": property_type, "limit": capped})
    try:
        items = realestate.search(
            city=city, transaction_type=transaction_type, property_type=property_type,
            min_price=min_price, max_price=max_price, min_size=min_size,
            min_rooms=min_rooms, limit=capped,
        )
    except Exception:  # noqa: BLE001 — never crash the tool
        items = []

    if not items:
        return {
            "listings": _demo(capped),
            "demo": True,
            "note": "No live results just now — showing a sample. Try a city like 'munich' or 'hamburg'.",
        }
    return {
        "listings": items,
        "count": len(items),
        "note": (
            f"Free tier: up to {FREE_LIMIT} listings from immowelt.de. "
            f"More cities/sources, detail pages & price history → {UPGRADE_URL}"
        ),
    }


@mcp.tool()
def search_properties(
    city: str = "berlin",
    transaction_type: str = "rent",
    property_type: str = "apartment",
    min_price: int | None = None,
    max_price: int | None = None,
    min_size: int | None = None,
    min_rooms: float | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Search German real-estate listings from immowelt.de and return structured results.

    Args:
        city: German city, e.g. "berlin", "munich", "hamburg", "cologne".
        transaction_type: "rent" or "buy".
        property_type: "apartment", "house", "plot" or "commercial".
        min_price: minimum price in EUR.
        max_price: maximum price in EUR.
        min_size: minimum living area in m².
        min_rooms: minimum number of rooms.
        limit: max listings to return (free tier is capped).
    """
    return _search_properties(
        city=city, transaction_type=transaction_type, property_type=property_type,
        min_price=min_price, max_price=max_price, min_size=min_size,
        min_rooms=min_rooms, limit=limit,
    )


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
