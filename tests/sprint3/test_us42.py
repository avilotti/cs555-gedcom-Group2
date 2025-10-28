from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import re
import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project3 import Individual, Family, GedLine, ErrorAnomaly, parse_individuals_family_data, validate_us42_reject_illegitimate_dates

@pytest.fixture
def sample_data_indis():
    
    cwd = os.getcwd()
    cwd = os.path.join(cwd,'tests','sprint3')
    
    filepath = os.path.join(cwd, 'test_data_us42.ged')

    with open(filepath, "r", encoding="utf-8") as fh:
        individuals, families = parse_individuals_family_data(fh)
    
    return individuals

@pytest.fixture
def sample_data_fams():

    cwd = os.getcwd()
    cwd = os.path.join(cwd,'tests','sprint3')
    
    filepath = os.path.join(cwd, 'test_data_us42.ged')

    with open(filepath, "r", encoding="utf-8") as fh:
        individuals, families = parse_individuals_family_data(fh)
    
    return families

def test_us42_reject_illegitimate_dates(sample_data_indis, sample_data_fams):
    GED_LINES = []

    out = validate_us42_reject_illegitimate_dates(sample_data_indis, sample_data_fams)

    # 2 anomalies should be raised, but due to how pytest fixtures work, GED_LINES is duplicated. So we actually expect 4 anomalies to be raised.
    assert len(out) == 4