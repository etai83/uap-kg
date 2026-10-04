from fastapi.testclient import TestClient

from uap_kg.web.app import app
from uap_kg.web.context import extract_sentences, find_claim_context


def test_extract_sentences_basic():
    spans = [
        {"t_start": 0.0, "t_end": 2.0, "text": "First sentence here.", "speaker_label": "SPK1"},
        {"t_start": 2.0, "t_end": 4.0, "text": "Second sentence is longer!", "speaker_label": "SPK2"},
        {"t_start": 4.0, "t_end": 6.0, "text": "Is this third?", "speaker_label": "SPK1"},
    ]
    sentences = extract_sentences(spans)
    assert len(sentences) == 3
    assert sentences[0]["text"] == "First sentence here."
    assert sentences[1]["text"] == "Second sentence is longer!"
    assert sentences[2]["text"] == "Is this third?"
    assert sentences[0]["speaker"] == "SPK1"
    assert sentences[1]["speaker"] == "SPK2"


def test_extract_sentences_split_across_spans():
    spans = [
        {"t_start": 0.0, "t_end": 2.0, "text": "I was walking down", "speaker_label": "SPK1"},
        {"t_start": 2.0, "t_end": 4.0, "text": "the street yesterday. Then I saw", "speaker_label": "SPK1"},
        {"t_start": 4.0, "t_end": 6.0, "text": "a strange craft.", "speaker_label": "SPK1"},
    ]
    sentences = extract_sentences(spans)
    assert len(sentences) == 2
    assert sentences[0]["text"] == "I was walking down the street yesterday."
    assert sentences[1]["text"] == "Then I saw a strange craft."


def test_find_claim_context():
    sentences = [
        {"text": "Before anything happened.", "t_start": 10.0, "t_end": 14.0, "speaker": "SPK1"},
        {"text": "The craft was triangular in shape.", "t_start": 14.0, "t_end": 18.0, "speaker": "SPK1"},
        {"text": "After it flew away.", "t_start": 18.0, "t_end": 22.0, "speaker": "SPK1"},
    ]
    ctx = find_claim_context(sentences, t_start=15.0, quote="The craft was triangular")
    assert ctx["sentence"] == "The craft was triangular in shape."
    assert ctx["prev"] == "Before anything happened."
    assert ctx["after"] == "After it flew away."


def test_find_claim_context_boundary_conditions():
    # First sentence has no prev
    sentences = [
        {"text": "Only one statement here.", "t_start": 0.0, "t_end": 5.0, "speaker": "SPK1"},
        {"text": "Next statement follows.", "t_start": 5.0, "t_end": 10.0, "speaker": "SPK1"},
    ]
    ctx = find_claim_context(sentences, t_start=1.0, quote="Only one statement")
    assert ctx["prev"] == ""
    assert ctx["sentence"] == "Only one statement here."
    assert ctx["after"] == "Next statement follows."

    # Empty sentences fallback
    ctx_empty = find_claim_context([], t_start=0.0, quote="Fallback quote")
    assert ctx_empty["prev"] == ""
    assert ctx_empty["sentence"] == "Fallback quote"
    assert ctx_empty["after"] == ""


def test_api_video_claim_context():
    client = TestClient(app)
    resp = client.get("/api/videos/K4gYHs84BIc/claim-context?t_start=188.36&quote=Dylan Borland")
    assert resp.status_code == 200
    data = resp.json()
    assert "prev" in data
    assert "sentence" in data
    assert "after" in data
    assert "Dylan Borland" in data["sentence"]


def test_api_claim_context():
    client = TestClient(app)
    resp = client.get("/api/claims/CLM-01/context")
    assert resp.status_code == 200
    data = resp.json()
    assert "prev" in data
    assert "sentence" in data
    assert "after" in data
    assert "Dylan Borland" in data["sentence"]
