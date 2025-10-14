#Unit Tests: US40

import unittest
from typing import List
from unittest.mock import patch
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import project3 as ged_analysis
from project3 import GedLine

def _util_setup_ged_output():
    """"Returns a list of GedLine objects that match the expected output from parsing test_data_us40.ged"""
    ged_lines: List[GedLine] = []
    ged_lines.append(GedLine(line_num=1, level=0, tag="NOTE", value="SSW555 US40 Test Data"))
    ged_lines.append(GedLine(line_num=2, level=0, tag="INDI", value="@US40.I01@"))
    ged_lines.append(GedLine(line_num=3, level=1, tag="NAME", value="US40 Test01"))
    ged_lines.append(GedLine(line_num=4, level=1, tag="BIRT", value=""))
    ged_lines.append(GedLine(line_num=5, level=2, tag="DATE", value="1 JAN 2000"))
    ged_lines.append(GedLine(line_num=6, level=1, tag="DEAT", value=""))
    ged_lines.append(GedLine(line_num=7, level=2, tag="DATE", value="29 DEC 2100"))
    ged_lines.append(GedLine(line_num=8, level=0, tag="INDI", value="@US40.I02@"))
    ged_lines.append(GedLine(line_num=9, level=1, tag="NAME", value="US40 Test02"))
    ged_lines.append(GedLine(line_num=10, level=1, tag="BIRT", value=""))
    ged_lines.append(GedLine(line_num=11, level=2, tag="DATE", value="2 JAN 2000"))
    ged_lines.append(GedLine(line_num=12, level=1, tag="DEAT", value=""))
    ged_lines.append(GedLine(line_num=13, level=2, tag="DATE", value="30 DEC 2100"))
    ged_lines.append(GedLine(line_num=14, level=0, tag="INDI", value="@US40.I03@"))
    ged_lines.append(GedLine(line_num=15, level=1, tag="NAME", value="US40 Test03"))
    ged_lines.append(GedLine(line_num=16, level=1, tag="BIRT", value=""))
    ged_lines.append(GedLine(line_num=17, level=2, tag="DATE", value="3 JAN 2000"))
    ged_lines.append(GedLine(line_num=18, level=1, tag="DEAT", value=""))
    ged_lines.append(GedLine(line_num=19, level=2, tag="DATE", value="31 DEC 2100"))
    ged_lines.append(GedLine(line_num=20, level=0, tag="FAM", value="@US40.F01@"))
    ged_lines.append(GedLine(line_num=21, level=1, tag="CHIL", value="@US40.I01@"))
    ged_lines.append(GedLine(line_num=22, level=1, tag="HUSB", value="@US40.I02@"))
    ged_lines.append(GedLine(line_num=23, level=1, tag="WIFE", value="@US40.I03@"))
    ged_lines.append(GedLine(line_num=24, level=1, tag="MARR", value=""))
    ged_lines.append(GedLine(line_num=25, level=2, tag="DATE", value="1 JAN 1999"))
    ged_lines.append(GedLine(line_num=26, level=1, tag="DIV", value=""))
    ged_lines.append(GedLine(line_num=27, level=2, tag="DATE", value="1 JAN 2001"))
    ged_lines.append(GedLine(line_num=28, level=0, tag="TRLR", value=""))
    return ged_lines

class Test_US40_InitGedLines(unittest.TestCase):
    def setUp(self):
        self.test_ged_lines = _util_setup_ged_output()

    def test_parsed_lines_init_list(self):
        self.maxDiff = None        
        file_path = "tests/test_data_us40.ged"
        with open(file_path, "r", encoding="utf-8") as fh:
            individuals, families = ged_analysis.parse_individuals_family_data(fh)
        self.assertListEqual(ged_analysis.GED_LINES, self.test_ged_lines)
        self.assertEqual(individuals["US40.I01"].ged_line_start, 2)
        self.assertEqual(individuals["US40.I01"].ged_line_end, 7)
        self.assertEqual(individuals["US40.I02"].ged_line_start, 8)
        self.assertEqual(individuals["US40.I02"].ged_line_end, 13)
        self.assertEqual(individuals["US40.I03"].ged_line_start, 14)
        self.assertEqual(individuals["US40.I03"].ged_line_end, 19)
        self.assertEqual(families["US40.F01"].ged_line_start, 20)
        self.assertEqual(families["US40.F01"].ged_line_end, 27)

class Test_US40_FindGedLines(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("project3.GED_LINES", _util_setup_ged_output())
        self.mocked_ged_lines = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_find_ged_line_nullstartend(self):
        line_num = ged_analysis.find_ged_line("INDI", "US40.I01", None, None, None)
        self.assertEqual(line_num, 2)

    def test_find_ged_line_nulltagandvalue(self):
        line_num = ged_analysis.find_ged_line(None, None, None, 0, 0)
        self.assertEqual(line_num, None)
        
    def test_find_ged_line_indi_id_fullfile(self):
        line_num = ged_analysis.find_ged_line("INDI", "US40.I01", None, 0, 28)
        self.assertEqual(line_num, 2)

    def test_find_ged_line_indi_id(self):
        line_num = ged_analysis.find_ged_line("INDI", "US40.I01", None, 2, 7)
        self.assertEqual(line_num, 2)

    def test_find_ged_line_indi_name(self):
        line_num = ged_analysis.find_ged_line("NAME", "US40 Test02", None, 8, 13)
        self.assertEqual(line_num, 9)

    def test_find_ged_line_indi_name_incorrectlinerange(self):
        line_num = ged_analysis.find_ged_line("NAME", "US40 Test02", None, 2, 7)
        self.assertEqual(line_num, None)

    def test_find_ged_line_indi_birth_date(self):
        line_num = ged_analysis.find_ged_line("DATE", "3 JAN 2000", "BIRT", 14, 19)
        self.assertEqual(line_num, 17)
        
    def test_find_ged_line_indi_birth_date_incorrecttag(self):
        line_num = ged_analysis.find_ged_line("BIRT", "3 JAN 2000", None, 14, 19)
        self.assertEqual(line_num, None)

    def test_find_ged_line_fam_id(self):
        line_num = ged_analysis.find_ged_line("FAM", "US40.F01", None, 20, 28)
        self.assertEqual(line_num, 20)

    def test_find_ged_line_fam_chil(self):
        line_num = ged_analysis.find_ged_line("CHIL", "US40.I01", None, 20, 28)
        self.assertEqual(line_num, 21)

    def test_find_ged_line_fam_marr_date(self):
        line_num = ged_analysis.find_ged_line("DATE", "1 JAN 1999", "MARR", 20, 28)
        self.assertEqual(line_num, 25)

    def test_find_ged_line_not_found(self):
        line_num = ged_analysis.find_ged_line("INDI", "DOES_NOT_EXIST", None, 0, 28)
        self.assertEqual(line_num, None)

