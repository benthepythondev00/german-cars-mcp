# Launch kit — german-realestate-mcp (free MCP wedge)

**Goal:** get the free MCP server in front of developers / agent-builders.
**Kill-or-continue gate:** do people install and call it? Each call is logged to stderr (and to
`REALESTATE_USAGE_LOG` if set) — that's your metric.

## 0. Prereqs (done)
- [x] Repo public, zero-config (no API key needed — big adoption advantage)
- [x] GitHub topics: mcp, mcp-server, model-context-protocol, real-estate, immobilien, property, germany
- [x] Tool verified live across Berlin / Munich / Cologne / Hamburg

## Reusable blurb
> **German Real Estate MCP** — give your AI agent structured German property listings from
> immowelt.de. One tool, `search_properties`, filters by city / rent-or-buy / type / price / size /
> rooms and returns clean JSON. **No API key, no proxy — it just works.** Listing data only.

## 1. Directories (free distribution)
- **Glama** — https://glama.ai/mcp/servers — auto-indexes public GitHub MCP repos (`glama.json` added).
- **mcp.so** — https://mcp.so/submit — name + blurb + repo URL.
- **PulseMCP** — https://www.pulsemcp.com/submit — same blurb + repo.
- **Smithery** — https://smithery.ai/new — connect the repo; `smithery.yaml` included (zero-config).
- **awesome-mcp-servers** — PR to https://github.com/punkpeye/awesome-mcp-servers :
  `- [german-realestate-mcp](https://github.com/benthepythondev00/german-realestate-mcp) 🐍 - Structured German property listings from immowelt.de (rent/buy by city, price, size, rooms). No API key.`

## 2. Reddit — r/mcp (also r/ClaudeAI, r/realestate-tech, r/de)
**Title:** Free MCP server for German real-estate data (immowelt) — no API key

Wrapped immowelt.de behind a single MCP tool, `search_properties(city, transaction_type, property_type,
min_price, max_price, min_size, min_rooms)`. Returns structured JSON — price, size, rooms, location,
url. **No key, no proxy — works the moment you add it.** Listing data only (no personal data).
Repo: <link>. What other German/EU data would you want as MCP tools?

## 3. X / Twitter
> Free MCP server: German real-estate listings (immowelt) for your AI agents 🏠🇩🇪
> One tool → structured JSON: price, m², rooms, location, link. Rent or buy, any city.
> No API key, no proxy — just add it and ask. Repo 👇 <link>

## 4. Later
- More sources (kleinanzeigen, price comparison) + detail pages + price history → the paid API.
- Official MCP registry (needs a PyPI publish).
- Hosted demo + Show HN once there's traction.
