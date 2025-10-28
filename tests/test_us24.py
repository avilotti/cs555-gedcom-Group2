#Unit Tests: US24

import unittest
from typing import Dict, List
from unittest.mock import patch
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import project3 as ged_analysis
from project3 import validate_us24_unique_families_by_spouses, Family, GedLine

def _util_setup_fam_output():
    families: Dict[str, Family] = {}
    families["F1"] = Family(id="F1", husband_id="H1", wife_id="W1", married="1 JAN 2000")
    families["F2"] = Family(id="F2", husband_id="H1", wife_id="W1", married="1 JAN 2000")
    families["F3"] = Family(id="F3", husband_id="H1", wife_id="W1", married="1 JAN 2000")
    families["F4"] = Family(id="F4", husband_id="H2", wife_id="W2", married="1 JAN 2000")
    families["F5"] = Family(id="F5", husband_id="H2", wife_id="W2", married="2 JAN 2000")
    families["F6"] = Family(id="F6", husband_id="H3", wife_id="W3", married="1 JAN 2000")
    families["F7"] = Family(id="F7", husband_id="H3", wife_id="W3", married="1 JAN 2000")
    families["F8"] = Family(id="F8", husband_id="H3", wife_id="W3", married="2 JAN 2000")
    families["F9"] = Family(id="F9", husband_id="", wife_id="", married="")
    families["F10"] = Family(id="F10", husband_id="", wife_id="", married="")
    return families

def _util_setup_ged_output():
    """Not necessary for GED_LINES to have correct values; overriding to avoid empty list errors when retrieving line number"""
    ged_lines: List[GedLine] = []
    ged_lines.append(GedLine(line_num=1, level=0, tag="NOTE", value="US24 Test Data"))
    ged_lines.append(GedLine(line_num=2, level=0, tag="TRLR", value=""))
    return ged_lines

class Test_US24_ValidateUniqueFamilies(unittest.TestCase):
    def setUp(self):
        self.families = _util_setup_fam_output()
        self.patcher = patch("project3.GED_LINES", _util_setup_ged_output())
        self.mocked_ged_lines = self.patcher.start()
        
    def tearDown(self):
        self.patcher.stop()

    def test_duplicate_attrs_gte2_fams_error(self):
        errors = validate_us24_unique_families_by_spouses(self.families)
        self.assertTrue(any(e.indi_or_fam_id == "F1" for e in errors))
        self.assertTrue(any(e.indi_or_fam_id == "F2" for e in errors))
        self.assertTrue(any(e.indi_or_fam_id == "F3" for e in errors))

    def test_duplicate_spouse_diff_marr_noerror(self):
        errors = validate_us24_unique_families_by_spouses(self.families)
        self.assertFalse(any(e.indi_or_fam_id == "F4" for e in errors))
        self.assertFalse(any(e.indi_or_fam_id == "F5" for e in errors))
        
    def test_duplicate_spouse_3_fams_diff_marr_error(self):
        errors = validate_us24_unique_families_by_spouses(self.families)
        self.assertTrue(any(e.indi_or_fam_id == "F6" for e in errors))
        self.assertTrue(any(e.indi_or_fam_id == "F7" for e in errors))
        self.assertFalse(any(e.indi_or_fam_id == "F9" for e in errors))
        
    def test_missing_allattrs_noerror(self):
        errors = validate_us24_unique_families_by_spouses(self.families)
        self.assertFalse(any(e.indi_or_fam_id == "F9" for e in errors))
        self.assertFalse(any(e.indi_or_fam_id == "F10" for e in errors))
