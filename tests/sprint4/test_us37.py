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

from project3 import Individual, Family, GedLine, ErrorAnomaly, us37_list_recent_survivors


@pytest.fixture
def sample_data_indi_1():
    '''
    positive case - survivor spouse
    '''

    # sample individuals
    individuals: Dict[str, Individual] = {}

    indi_data_1 = Individual(
        id = "US37.I1",
        name = "US37.I1",
        birthday = "1 JAN 2000",
        death = "7 NOV 2025"
    )

    indi_data_2 = Individual(
        id = "US37.I2",
        name = "US37.I2",
        birthday = "1 JAN 2000",
    )
    
    individuals["US37.I1"] = indi_data_1
    individuals["US37.I2"] = indi_data_2

    return individuals

@pytest.fixture
def sample_data_fam_1():
    '''
    positive case - survivor spouse
    '''

    # sample individuals
    families: Dict[str, Family] = {}

    fam_data_1 = Family(
        id = "US37.F1",
        husband_id = "US37.I1",
        wife_id = "US37.I2",
        married = "1 JAN 2020",
    )
    
    families["US37.F1"] = fam_data_1

    return families

def test_us37_list_recent_survivors(sample_data_indi_1, sample_data_fam_1):
    """
    positive case - birthday in the last 30 days
    """
    out = us37_list_recent_survivors(sample_data_indi_1, sample_data_fam_1)
    assert len(out) == 1 # assert one anomaly is raised per the fixture
