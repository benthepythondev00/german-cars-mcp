# Launch kit — german-cars-mcp (free MCP wedge)

**Goal:** get the free MCP server in front of developers / agent-builders.
**Kill-or-continue gate:** do people install and call it? (Each call is logged to stderr, and to
`CARDATA_USAGE_LOG` if set — that's your usage metric.)

## 0. Prereqs (do once)
- [x] Repo public
- [x] GitHub topics: mcp, mcp-server, model-context-protocol, apify, web-scraping, cars, germany, mobile-de
- [ ] Deploy the actor: `cd Documents/api_selling/mobile-de-scraper && apify push`
- [ ] Set `CARDATA_ACTOR_ID=benthepythondev/mobile-de-scraper` (+ `APIFY_TOKEN`) for live data

## Reusable blurb
> **German Used Cars MCP** — give your AI agent structured used-car listings from mobile.de
> (Germany's #1 car marketplace). One tool, `search_used_cars`, filters by
> make / model / price / year / mileage / fuel / transmission / location and returns clean JSON.
> mobile.de has no public API and blocks scrapers; this is powered by a hardened
> Camoufox + residential-proxy backend. Works in demo mode out of the box.

## 1. Directories (free distribution)
- **Glama** — https://glama.ai/mcp/servers — auto-indexes public GitHub MCP repos. Public repo +
  topics + README + `glama.json` (added) is enough; it picks it up.
- **mcp.so** — https://mcp.so/submit — submit name + blurb + repo URL.
- **PulseMCP** — https://www.pulsemcp.com/submit — same blurb + repo.
- **Smithery** — https://smithery.ai/new — connect the GitHub repo; `smithery.yaml` is included.
- **awesome-mcp-servers** — PR to https://github.com/punkpeye/awesome-mcp-servers . Suggested line:
  `- [german-cars-mcp](https://github.com/benthepythondev00/german-cars-mcp) 🐍 ☁️ - Structured German used-car listings from mobile.de (search by make/model/price/year/mileage/fuel).`

## 2. Reddit — r/mcp (also r/ClaudeAI, r/LocalLLaMA)
**Title:** I built a free MCP server for German used-car data (mobile.de)

mobile.de has no public API and blocks scrapers with Akamai, so I wrapped a hardened scraper
(Camoufox + DE residential proxy) behind a single MCP tool:
`search_used_cars(make, model, price_min, price_max, year_min, mileage_max, fuel, transmission, zip_code, radius_km)`.
Returns structured JSON — price, mileage, year, power, location, url. Works in **demo mode** with
no setup; live data via your own Apify actor. Repo: <link>.
What other German/EU data would you want as MCP tools?

## 3. X / Twitter
> Shipped a free MCP server: German used-car listings (mobile.de) for your AI agents 🚗🇩🇪
> One tool → structured JSON: make, model, price, mileage, year, fuel, location.
> mobile.de has no API and blocks scrapers — this gets past that.
> Demo mode works instantly. Repo 👇 <link>

## 4. Later
- Official MCP registry (modelcontextprotocol/registry) — needs a PyPI publish first.
- Hosted/zero-friction version (no Apify token for the user) — small VPS; unlocks the widest reach.
- Show HN once there's a hosted demo.
