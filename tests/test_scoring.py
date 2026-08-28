"""Unit tests for the rubric. Fixtures are SYNTHETIC and never become evidence."""
import json, os, pathlib, sys

os.environ["QUALIFY_TODAY"] = "2026-08-28"
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from qualify import score_shop, today            # noqa: E402
from capture import normalise_review, assert_clean  # noqa: E402
from taxonomy import match_signals               # noqa: E402

FIX = pathlib.Path(__file__).parent / "fixtures"
load = lambda n: json.loads((FIX / n).read_text())
META = lambda s, r: {"shop": s, "shop_url": "https://example.invalid", "category": "lamp", "ratio_per_year": r}


def test_hot_lead_qualifies():
    l = score_shop(META("SyntheticHot", 3880), load("SYNTHETIC_hot.json"), today())
    assert l["tier"] == "hot", l
    assert {"transit_time", "customs", "damage"} <= set(l["signals"])
    assert l["evidence"] and all(e["signals"] for e in l["evidence"])


def test_clean_shop_is_rejected_with_a_reason():
    l = score_shop(META("SyntheticPass", 900), load("SYNTHETIC_pass.json"), today())
    assert l["tier"] == "pass", l
    assert l["reasons"], "a rejection must explain itself"


def test_rubric_discriminates():
    hot = score_shop(META("SyntheticHot", 3880), load("SYNTHETIC_hot.json"), today())
    bad = score_shop(META("SyntheticPass", 900), load("SYNTHETIC_pass.json"), today())
    assert hot["score"] - bad["score"] >= 30


def test_positive_reviews_raise_no_signal():
    assert match_signals("Beautiful lamp, arrived quickly, great seller") == set()


def test_reviewer_identity_never_reaches_disk():
    r = normalise_review({"authorName": "Jane D", "buyerProfileUrl": "http://x",
                          "avatar": "http://a.png", "stars": 1, "reviewDate": "2026-07-14",
                          "reviewText": "Took 3 weeks", "listingUrl": "http://l"})
    assert set(r) == {"rating", "date", "text", "url"}
    assert_clean({"reviews": [r]})


def test_no_synthetic_data_in_committed_snapshot():
    for p in (ROOT / "fallback" / "snapshot").glob("*.json"):
        assert "SYNTHETIC" not in p.read_text(), f"{p} contains synthetic data"
