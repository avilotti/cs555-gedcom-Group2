import os, sys
import project3 as p
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def _load():
    """Parse the acceptance GEDCOM in the repo root."""
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data_us32_33.ged"))
    with open(path, "r", encoding="utf-8") as fh:
        return p.parse_individuals_family_data(fh)

def test_us33():
    individuals, families = _load()
    errs = [e for e in p.validate_us33_list_orphans(individuals, families)]
    assert len(errs) == 1

def test_us32():
    individuals, families = _load()
    errs = [e for e in p.validate_us22_check_duplicates(individuals, families)]
    assert any(e.indi_or_fam_id == "US22.I012" for e in errs)
    assert len(errs) == 2
