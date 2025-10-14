#Unit Tests: US14

import unittest
from typing import Dict, List
from unittest.mock import patch
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import project3 as ged_analysis
from project3 import validate_us14_less_than_five_births, Individual, Family, GedLine

def _util_setup_indi_output():
    individuals: Dict[str, Individual] = {}
    individuals["F1I1"] = Individual(id="F1I1", birthday="1 JAN 2000")
    individuals["F1I2"] = Individual(id="F1I2", birthday="1 JAN 2000")
    individuals["F1I3"] = Individual(id="F1I3", birthday="1 JAN 2000")
    individuals["F1I4"] = Individual(id="F1I4", birthday="1 JAN 2000")
    individuals["F1I5"] = Individual(id="F1I5", birthday="1 JAN 2000")
    
    individuals["F2I1"] = Individual(id="F2I1", birthday="1 JAN 2000")
    individuals["F2I2"] = Individual(id="F2I2", birthday="")
    individuals["F2I3"] = Individual(id="F2I3", birthday="")
    individuals["F2I4"] = Individual(id="F2I4", birthday="")
    individuals["F2I5"] = Individual(id="F2I5", birthday="")

    individuals["F3I1"] = Individual(id="F3I1", birthday="1 JAN 2000")
    individuals["F3I2"] = Individual(id="F3I2", birthday="1 JAN 2000")
    individuals["F3I3"] = Individual(id="F3I3", birthday="1 JAN 2000")
    individuals["F3I4"] = Individual(id="F3I4", birthday="1 JAN 2000")
    return individuals

def _util_setup_fam_output():
    families: Dict[str, Family] = {}
    families["F1"] = Family(id="F1", children=["F1I1", "F1I2", "F1I3", "F1I4", "F1I5"])
    families["F2"] = Family(id="F2", children=["F2I1", "F2I2", "F2I3", "F2I4", "F2I5"])
    families["F3"] = Family(id="F3", children=["F3I1", "F3I2", "F3I3", "F3I4"])
    return families

def _util_setup_ged_output():
    """Not necessary for GED_LINES to have correct values; overriding to avoid empty list errors when retrieving line number"""
    ged_lines: List[GedLine] = []
    ged_lines.append(GedLine(line_num=1, level=0, tag="NOTE", value="US14 Test Data"))
    ged_lines.append(GedLine(line_num=2, level=0, tag="TRLR", value=""))
    return ged_lines

class Test_US40_FindGedLines(unittest.TestCase):
    def setUp(self):
        self.individuals = _util_setup_indi_output()
        self.families = _util_setup_fam_output()
        self.patcher = patch("project3.GED_LINES", _util_setup_ged_output())
        self.mocked_ged_lines = self.patcher.start()
        
    def tearDown(self):
        self.patcher.stop()

    def test_births_gte5_alldates_anomaly(self):
        anomalies = validate_us14_less_than_five_births(self.individuals, self.families)
        self.assertTrue(any(a.indi_or_fam_id == "F1" for a in anomalies))

    def test_births_gte5_missingdates_noanomaly(self):
        anomalies = validate_us14_less_than_five_births(self.individuals, self.families)
        self.assertFalse(any(a.indi_or_fam_id == "F2" for a in anomalies))
    
    def test_births_lt5_alldates_noanomaly(self):
        anomalies = validate_us14_less_than_five_births(self.individuals, self.families)
        self.assertFalse(any(a.indi_or_fam_id == "F3" for a in anomalies))
