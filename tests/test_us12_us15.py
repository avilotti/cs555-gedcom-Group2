import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project3 import (
    parse_individuals_family_data,
    validate_us12_parents_not_too_old,
    validate_us15_fewer_than_15_siblings
)

def _load():
    """Parse the acceptance GEDCOM in the repo root."""
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "TestData.ged"))
    with open(path, "r", encoding="utf-8") as fh:
        return parse_individuals_family_data(fh)

def test_us12():
    individuals, families = _load()
    errs = [e for e in validate_us12_parents_not_too_old(individuals, families)]

    assert any(e.indi_or_fam_id == "US15.F01" for e in errs)
    assert len([e.indi_or_fam_id == "US15.F01" for e in errs]) == 2

def test_us15():
    individuals, families = _load()
    errs = [e for e in validate_us15_fewer_than_15_siblings(families)]

    assert any(e.indi_or_fam_id == "US15.F01" for e in errs)
    assert len([e.indi_or_fam_id == "US15.F01" for e in errs]) == 1