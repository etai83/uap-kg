import json
import sys
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from uap_kg.web.case_graph import (
    clean_name_score,
    graph_payload,
    mark_same,
    revert_log,
    restore_log,
)
from scripts.db_sanity_check import run_checks


def test_clean_name_score():
    # Canonical capitalized names score higher than sentence fragments
    assert clean_name_score("John Lear")[0] == 0
    assert clean_name_score("man named John Lear")[0] < 0

    assert clean_name_score("George Knapp")[0] == 0
    assert clean_name_score("george knapp won't")[0] < 0
    assert clean_name_score("George Knapp's voice")[0] < 0

    assert clean_name_score("Lou Elizondo")[0] == 0
    assert clean_name_score("Lou Elizondo interview")[0] < 0


def test_mark_same_type_mismatch_rejected(tmp_path):
    # Setup temporary alias path
    alias_path = tmp_path / "node_same.json"

    # Try to merge an object with a named_person
    # borland:ENT-305 is 'Lou Elizondo interview' (object)
    # borland:ENT-253 is 'lou elizondo' (named_person)
    payload = graph_payload(alias_path=alias_path)
    nodes = {n["id"]: n for n in payload["nodes"]}

    person_id = "name:named_person:lou elizondo" if "name:named_person:lou elizondo" in nodes else "borland:ENT-253"
    obj_id = "borland:ENT-305"

    if person_id in nodes and obj_id in nodes:
        with pytest.raises(ValueError, match="Both nodes must share the same entity type"):
            mark_same(person_id, obj_id, alias_path=alias_path)


def test_mark_same_distinct_people_rejected(tmp_path):
    alias_path = tmp_path / "node_same.json"
    payload = graph_payload(alias_path=alias_path)
    nodes = {n["id"]: n for n in payload["nodes"]}

    # Matthew Sullivan vs Matthew Brown
    sullivan_id = next((n["id"] for n in nodes.values() if n.get("full") == "Matthew Sullivan"), None)
    brown_id = next((n["id"] for n in nodes.values() if n.get("full") == "Matthew Brown"), None)

    assert sullivan_id is not None
    assert brown_id is not None

    with pytest.raises(ValueError, match="distinct individuals"):
        mark_same(sullivan_id, brown_id, alias_path=alias_path)


def test_mark_same_actually_changes_node_and_links(tmp_path):
    alias_path = tmp_path / "node_same.json"

    # Pick two mergeable entities of the same type
    payload = graph_payload(alias_path=alias_path)
    entities = [n for n in payload["nodes"] if n.get("kind") == "entity" and n.get("entityType") == "named_person"]
    assert len(entities) >= 2

    # Find two nodes that are not conflicting in surname
    node_a = entities[0]
    node_b = entities[1]
    a_members = set(node_a.get("members", [node_a["id"]]))
    b_members = set(node_b.get("members", [node_b["id"]]))

    res = mark_same(node_a["id"], node_b["id"], alias_path=alias_path)
    new_nodes = {n["id"]: n for n in res["nodes"]}

    # Replaced node should no longer be present
    assert node_b["id"] not in new_nodes
    # Merged node should exist with new ID starting with same:
    merged = next((n for n in res["nodes"] if n["id"].startswith("same:") and a_members.intersection(n.get("members", []))), None)
    assert merged is not None
    assert a_members.issubset(set(merged["members"]))
    assert b_members.issubset(set(merged["members"]))
    assert len(merged["members"]) >= 2
    # Also aliases should include replaced node label or alternative names
    assert merged["full"] == node_a["full"] or merged["full"] == node_b["full"] or len(merged.get("also", [])) > 0


def test_db_sanity_check_passes():
    count, issues = run_checks()
    assert count == 0, f"Database sanity check failed with {count} issues: {issues}"
