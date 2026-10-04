"""Tests for the Item & Graph Review section and closest items API."""

from fastapi.testclient import TestClient

from uap_kg.web.app import app
from uap_kg.web.case_graph import closest_items, graph_payload


def test_review_page_renders():
    client = TestClient(app)
    response = client.get("/review")
    assert response.status_code == 200
    html = response.text
    assert "Review &amp; Resolve" in html or "Review & Resolve" in html
    assert "rv-item-search" in html
    assert "review-cy" in html
    assert "review-sidebar" in html
    assert "tab-graph-btn" in html
    assert "tab-claims-btn" in html
    assert "review-graph.js" in html


def test_review_page_with_query_params():
    client = TestClient(app)
    res1 = client.get("/review?node=borland:PER-BORLAND&tab=graph")
    assert res1.status_code == 200
    assert "borland:PER-BORLAND" in res1.text

    res2 = client.get("/review?tab=claims&video=K4gYHs84BIc")
    assert res2.status_code == 200
    assert "claims" in res2.text


def test_closest_items_basic():
    # Dylan Borland
    results = closest_items("borland:PER-BORLAND", type_filter="all", limit=10)
    assert len(results) > 0
    assert len(results) <= 10
    # verify structure
    for r in results:
        assert "node" in r
        assert "score" in r
        assert "reason" in r
        assert r["score"] > 0
    # verify score is sorted descending
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_closest_items_type_filter():
    # Organization filter
    org_results = closest_items("borland:PER-BORLAND", type_filter="organization", limit=10)
    assert len(org_results) > 0
    for r in org_results:
        node = r["node"]
        assert node.get("entityType") == "organization"

    # Location filter
    loc_results = closest_items("borland:PER-BORLAND", type_filter="location", limit=10)
    assert len(loc_results) > 0
    for r in loc_results:
        node = r["node"]
        assert node.get("entityType") == "location"


def test_closest_items_unknown_node():
    results = closest_items("invalid:node:id", type_filter="all", limit=10)
    assert results == []


def test_api_review_closest_endpoint():
    client = TestClient(app)
    response = client.get("/api/review/closest?node_id=borland:PER-BORLAND&type_filter=organization&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    for item in data:
        assert item["node"]["entityType"] == "organization"
        assert item["score"] > 0
        assert "reason" in item


def test_closest_items_always_suggests_ten():
    # Node with 0 direct co-mentions should still return 10 suggestions
    payload = graph_payload()
    for sample in payload["nodes"][:15]:
        results = closest_items(sample["id"], type_filter="all", limit=10)
        assert len(results) == 10, f"Expected 10 suggestions for {sample['id']}, got {len(results)}"
        for r in results:
            assert r["score"] > 0
            assert r["reason"]

