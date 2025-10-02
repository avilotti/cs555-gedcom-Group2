import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project3 import (
    parse_individuals_family_data,
    validate_us13_siblings_spacing,
    validate_us18_siblings_not_marry,
)

def _load():
    """Parse the acceptance GEDCOM in the repo root."""
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "TestData.ged"))
    with open(path, "r", encoding="utf-8") as fh:
        return parse_individuals_family_data(fh)

def test_us13_has_one_violation_and_twins_pass():
    individuals, families = _load()
    errs = [e for e in validate_us13_siblings_spacing(individuals, families)]

    assert any(e.indi_or_fam_id == "F900" for e in errs)
    assert all(e.indi_or_fam_id != "F901FAM" for e in errs)
    assert len([e for e in errs if e.user_story_id == "US13"]) == 1

def test_us18_blocks_siblings_but_allows_clean_marriage():
    individuals, families = _load()
    errs = [e for e in validate_us18_siblings_not_marry(individuals, families)]

    assert any(e.indi_or_fam_id == "F930" for e in errs)
    assert all(e.indi_or_fam_id != "F931" for e in errs)
    assert len([e for e in errs if e.user_story_id == "US18"]) == 1
