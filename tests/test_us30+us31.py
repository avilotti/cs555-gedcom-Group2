#Unit Tests: US30 + US31

import unittest
from typing import Dict, List
from unittest.mock import patch
import os, sys
from datetime import datetime, date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import project3 as ged_analysis
from project3 import us30_list_living_married, us31_list_living_single, Individual, Family, GedLine

TODAY =  datetime.strftime(date.today(), "%d %b %Y")
YESTERDAY =  datetime.strftime(date.today() - timedelta(days=1), "%d %b %Y")
TOMORROW =  datetime.strftime(date.today() + timedelta(days=1), "%d %b %Y")

def _util_setup_indi_output():
    individuals: Dict[str, Individual] = {}
    # No family
    individuals["I1_A"] = Individual(id="I1_A", alive=True, death="NA")
    individuals["I2_A"] = Individual(id="I2_A", alive=False, death="NA")
    individuals["I3_A"] = Individual(id="I3_A", alive=False, death=TOMORROW)
    individuals["I4_D"] = Individual(id="I4_D", alive=False, death=TODAY)
    individuals["I5_D"] = Individual(id="I5_D", alive=False, death=YESTERDAY)

    # 1 Family
    individuals["I1_A_M_ND"] = Individual(id="I1_A_M_ND", alive=True, death="NA")
    individuals["I2_A_S_CD"] = Individual(id="I2_A_S_CD", alive=True, death="NA")
    individuals["I3_A_M_FD"] = Individual(id="I3_A_M_FD", alive=True, death="NA")
    individuals["I4_A_S_PD"] = Individual(id="I4_A_S_PD", alive=True, death="NA")
    individuals["I5_D_M_ND"] = Individual(id="I5_D_M_ND", alive=False, death=YESTERDAY)
    individuals["I6_D_S_PD"] = Individual(id="I6_D_S_PD", alive=False, death=YESTERDAY)

    # 2 Families
    individuals["I1_A_S_PD_PD"] = Individual(id="I1_A_S_PD_PD", alive=True, death="NA")
    individuals["I2_A_M_ND_PD"] = Individual(id="I2_A_M_ND_PD", alive=True, death="NA")
    individuals["I3_A_M_ND_ND"] = Individual(id="I3_A_M_ND_ND", alive=True, death="NA")
    individuals["I4_A_M_ND_ND"] = Individual(id="I4_A_M_ND_ND", alive=True, death="NA")
    individuals["I5_A_S_PD_PD"] = Individual(id="I5_A_S_PD_PD", alive=True, death="NA")
    
    return individuals

def _util_setup_fam_output():
    families: Dict[str, Family] = {}

    families["F1_M"] = Family(id="F1_M", husband_id="I1_A_M_ND", divorced="NA")
    families["F2_D"] = Family(id="F2_D", husband_id="I2_A_S_CD", divorced=TODAY)
    families["F3_M"] = Family(id="F3_M", husband_id="I3_A_M_FD", divorced=TOMORROW)
    families["F4_D"] = Family(id="F4_D", husband_id="I4_A_S_PD", divorced=YESTERDAY)
    families["F5_M"] = Family(id="F5_M", husband_id="I5_D_M_ND", divorced="NA")
    families["F6_D"] = Family(id="F6_D", husband_id="I6_D_S_PD", divorced=YESTERDAY)

    families["F1_I1_D"] = Family(id="F1_I1_D", husband_id="I1_A_S_PD_PD", divorced=YESTERDAY)
    families["F2_I1_D"] = Family(id="F2_I1_D", husband_id="I1_A_S_PD_PD", divorced=YESTERDAY)

    families["F1_I2_M"] = Family(id="F1_I2_M", husband_id="I2_A_M_ND_PD", divorced="NA")
    families["F2_I2_D"] = Family(id="F2_I2_D", husband_id="I2_A_M_ND_PD", divorced=YESTERDAY)
    
    families["F1_I3_M"] = Family(id="F1_I3_M", husband_id="I3_A_M_ND_ND", divorced="NA")
    families["F2_I3_M"] = Family(id="F2_I3_M", husband_id="I3_A_M_ND_ND", divorced="NA")

    families["F1_I4_M"] = Family(id="F1_I4_M", husband_id="I4_A_M_ND_ND", divorced="NA")
    families["F2_I4_M"] = Family(id="F2_I4_M",    wife_id="I4_A_M_ND_ND", divorced="NA")

    families["F1_I5_D"] = Family(id="F1_I5_D", husband_id="I5_A_S_PD_PD", divorced=YESTERDAY)
    families["F2_I5_D"] = Family(id="F2_I5_D",    wife_id="I5_A_S_PD_PD", divorced=YESTERDAY)

    return families

def _util_setup_ged_output():
    """Not necessary for GED_LINES to have correct values; overriding to avoid empty list errors when retrieving line number"""
    ged_lines: List[GedLine] = []
    ged_lines.append(GedLine(line_num=1, level=0, tag="NOTE", value="US30/31 Test Data"))
    ged_lines.append(GedLine(line_num=2, level=0, tag="TRLR", value=""))
    return ged_lines

class Test_US30_ListLivingMarried(unittest.TestCase):
    def setUp(self):
        self.individuals = _util_setup_indi_output()
        self.families = _util_setup_fam_output()
        self.patcher = patch("project3.GED_LINES", _util_setup_ged_output())
        self.mocked_ged_lines = self.patcher.start()

        self.living_married = us30_list_living_married(self.individuals, self.families)
        self.living_single = us31_list_living_single(self.individuals, self.families)
        
    def tearDown(self):
        self.patcher.stop()

    def test_alivetrue_nodeathdt_nofam_livingsingle(self):
        self.assertFalse(any(a.indi_or_fam_id == "I1_A" for a in self.living_married))
        self.assertTrue(any(a.indi_or_fam_id == "I1_A" for a in self.living_single))
    def test_alivefalse_nodeathdt_nofam_livingsingle(self):
        self.assertFalse(any(a.indi_or_fam_id == "I2_A" for a in self.living_married))
        self.assertTrue(any(a.indi_or_fam_id == "I2_A" for a in self.living_single))
    def test_alivefalse_futuredeathdt_nofam_livingsingle(self):
        self.assertFalse(any(a.indi_or_fam_id == "I3_A" for a in self.living_married))
        self.assertTrue(any(a.indi_or_fam_id == "I3_A" for a in self.living_single))
    def test_alivefalse_todaydeathdt_nofam_notlisted(self):
        self.assertFalse(any(a.indi_or_fam_id == "I4_D" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I4_D" for a in self.living_single))
    def test_alivefalse_pastdeathdt_nofam_notlisted(self):
        self.assertFalse(any(a.indi_or_fam_id == "I5_D" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I5_D" for a in self.living_single))
        
    def test_living_onefam_nodivdt_livingmarried(self):
        self.assertTrue(any(a.indi_or_fam_id == "I1_A_M_ND" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I1_A_M_ND" for a in self.living_single))
    def test_living_onefam_todaydivdt_livingsingle(self):
        self.assertFalse(any(a.indi_or_fam_id == "I2_A_S_CD" for a in self.living_married))
        self.assertTrue(any(a.indi_or_fam_id == "I2_A_S_CD" for a in self.living_single))
    def test_living_onefam_futuredivdt_livingmarried(self):
        self.assertTrue(any(a.indi_or_fam_id == "I3_A_M_FD" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I3_A_M_FD" for a in self.living_single))
    def test_living_onefam_pastdivdt_livingsingle(self):
        self.assertFalse(any(a.indi_or_fam_id == "I4_A_S_PD" for a in self.living_married))
        self.assertTrue(any(a.indi_or_fam_id == "I4_A_S_PD" for a in self.living_single))

    def test_dead_onefam_nodivdt_notlisted(self):
        self.assertFalse(any(a.indi_or_fam_id == "I5_D_M_ND" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I5_D_M_ND" for a in self.living_single))
    def test_dead_onefam_pastdivdt_notlisted(self):
        self.assertFalse(any(a.indi_or_fam_id == "I5_D_M_ND" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I5_D_M_ND" for a in self.living_single))

    def test_living_twofam_bothdiv_livingsingle(self):
        self.assertFalse(any(a.indi_or_fam_id == "I1_A_S_PD_PD" for a in self.living_married))
        self.assertTrue(any(a.indi_or_fam_id == "I1_A_S_PD_PD" for a in self.living_single))
    def test_living_twofam_onediv_livingmarried(self):
        self.assertTrue(any(a.indi_or_fam_id == "I2_A_M_ND_PD" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I2_A_M_ND_PD" for a in self.living_single))
    def test_living_twofam_nodiv_livingmarried(self):
        self.assertTrue(any(a.indi_or_fam_id == "I3_A_M_ND_ND" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I3_A_M_ND_ND" for a in self.living_single))
    def test_living_twofam_mixspousetype_nodiv_livingmarried(self):
        self.assertTrue(any(a.indi_or_fam_id == "I4_A_M_ND_ND" for a in self.living_married))
        self.assertFalse(any(a.indi_or_fam_id == "I4_A_M_ND_ND" for a in self.living_single))
    def test_living_twofam_mixspousetype_bothdiv_livingsingle(self):
        self.assertFalse(any(a.indi_or_fam_id == "I5_A_S_PD_PD" for a in self.living_married))
        self.assertTrue(any(a.indi_or_fam_id == "I5_A_S_PD_PD" for a in self.living_single))
