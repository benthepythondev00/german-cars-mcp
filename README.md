# German Real Estate — MCP server

A free [MCP](https://modelcontextprotocol.io) server that gives your AI agent **structured German
property listings from immowelt.de**. One tool, clean JSON, **no API key and no proxy — it just
works.**

## Tool

### `search_properties`
| Param | Type | Example |
|---|---|---|
| `city` | string | `"berlin"`, `"munich"`, `"hamburg"`, `"cologne"` |
| `transaction_type` | string | `"rent"` or `"buy"` |
| `property_type` | string | `"apartment"`, `"house"`, `"plot"`, `"commercial"` |
| `min_price` / `max_price` | int (EUR) | `800` / `2000` |
| `min_size` | int (m²) | `60` |
| `min_rooms` | number | `3` |
| `limit` | int | `10` (free tier capped) |

Returns `{ "listings": [ { price_eur, price_label, size_sqm, rooms, floor, address, district, city, plz, url, image_url } ], "note": "..." }`.

## Quick start (no key needed)

```bash
git clone <this repo> && cd german-realestate-mcp
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Add to your MCP client (e.g. Claude Desktop `claude_desktop_config.json`) — **no env vars required**:

```json
{
  "mcpServers": {
    "german-real-estate": {
      "command": "/absolute/path/german-realestate-mcp/venv/bin/python",
      "args": ["/absolute/path/german-realestate-mcp/src/server.py"]
    }
  }
}
```

Then ask your agent: *"Find 3-room apartments to rent in Munich under €2,000."*

## How it works
Scrapes immowelt.de directly with `httpx` + BeautifulSoup. **Listing data only** — realtor/agent
personal data is intentionally dropped. If a query returns nothing, the tool returns a small sample
so it never comes back empty.

## Free tier & beyond
The free tier caps results (`REALESTATE_FREE_LIMIT`, default 10). A paid API is the next step:
more cities and sources (kleinanzeigen, price comparison), detail-page enrichment, price history,
and higher limits. The free MCP server is the front door.

## Develop
```bash
pip install -r requirements-dev.txt
pytest
```

## Legal
Returns listing data only (price/size/rooms/location) — no personal data. Use in line with
immowelt's terms and applicable law.
