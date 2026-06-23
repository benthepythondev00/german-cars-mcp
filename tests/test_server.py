from src import realestate, server


def test_demo_fallback_when_no_live_results(monkeypatch):
    monkeypatch.setattr(realestate, "search", lambda **k: [])
    r = server._search_properties(city="berlin", limit=3)
    assert r["demo"] is True
    assert len(r["listings"]) == 3
    assert r["listings"][0]["url"].startswith("http")


def test_live_path_caps_and_passes_filters(monkeypatch):
    captured = {}

    def fake_search(**kwargs):
        captured.update(kwargs)
        return [{"price_eur": 1000, "city": "Munich", "url": "u"}] * kwargs["limit"]

    monkeypatch.setattr(realestate, "search", fake_search)
    monkeypatch.setattr(server, "FREE_LIMIT", 5)
    r = server._search_properties(city="munich", max_price=2000, limit=100)
    assert captured["city"] == "munich"
    assert captured["max_price"] == 2000
    assert len(r["listings"]) <= 5
    assert "count" in r


def test_build_search_url_maps_types():
    u = realestate.build_search_url("Berlin", "buy", "house", max_price=500000, min_rooms=3)
    assert "/berlin/haeuser/kaufen" in u
    assert "pmax=500000" in u
    assert "zimin=3" in u


def test_parse_extracts_listing_and_drops_pii():
    html = (
        '<div class="css-79elbk"><a href="/expose/abc123"><h2>Nice flat</h2></a>'
        ' 1.200 € Kaltmiete 60 m² 2 Zimmer Beispielstr. 1, Mitte, Berlin (10115)</div>'
    )
    items = realestate.extract_listings_from_html(html)
    assert len(items) == 1
    it = items[0]
    assert it["expose_id"] == "abc123"
    assert it["price_eur"] == 1200.0
    assert it["size_sqm"] == 60.0
    assert it["rooms"] == 2.0
    assert it["city"] == "Berlin"
    assert it["plz"] == "10115"
    assert "agent_name" not in it  # personal data dropped
