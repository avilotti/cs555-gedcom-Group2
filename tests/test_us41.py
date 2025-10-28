#Unit Tests: US41

import unittest
from ddt import ddt, data
from datetime import date

import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import project3 as ged_analysis
from project3 import _parse_date

@ddt
class Test_US41_IncludePartialDates(unittest.TestCase):

    def test_date_pattern_dmy_accept(self):
        self.assertTrue(_parse_date("31 JAN 2000") == date(2000, 1, 31))
    
    def test_date_pattern_my_accept(self):
        self.assertTrue(_parse_date("JAN 2000") == date(2000, 1, 1))

    def test_date_pattern_y_accept(self):
        self.assertTrue(_parse_date("2000") == date(2000, 1, 1))
        
    def test_date_pattern_dm_reject(self):
        self.assertTrue(_parse_date("1 JAN") is None)
        
    def test_date_pattern_m_reject(self):
        self.assertTrue(_parse_date("JAN") is None)
        
    def test_date_pattern_d_reject(self):
        self.assertTrue(_parse_date("1") is None)

    def test_date_pattern_dmy_invalid_reject(self):
        self.assertTrue(_parse_date("31 FEB 2000") is None)
    
    invalid_date_strs = ["NOT_A_DATE", "99 NAM 9999", "NAD NAM NAYY", "NAM 2000"]
    @data(*invalid_date_strs)
    def test_date_pattern_str_reject(self, invalid_date_str):
        self.assertTrue(_parse_date(invalid_date_str) is None)
        
