import pytest
from app.reconciliation.scoring import MatchScorer

def test_reference_normalization():
    scorer = MatchScorer()
    assert scorer.normalize_reference("REF-INV-1011-KRY") == "refinv1011kry"

def test_reference_conflict_detection():
    scorer = MatchScorer()
    has_conflict, reason = scorer.compare_reference_identity("REF-INV-1011-KRY", "REF-INV-1136-KRY")
    assert has_conflict is True
    assert "INV-1136" in reason

def test_reference_no_conflict():
    scorer = MatchScorer()
    has_conflict, _ = scorer.compare_reference_identity("REF-INV-1011-KRY", "REF-INV-1011-KRY")
    assert has_conflict is False

def test_amount_score_exact():
    scorer = MatchScorer()
    assert scorer.score_amount(100.0, 100.0) == 1.0

def test_amount_score_tolerance():
    scorer = MatchScorer()
    assert scorer.score_amount(100.0, 99.5) == 0.95
