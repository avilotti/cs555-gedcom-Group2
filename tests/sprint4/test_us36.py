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

from project3 import Individual, Family, GedLine, ErrorAnomaly, us36_list_recent_deaths


@pytest.fixture
def sample_data_indi_1():
    '''
    positive case - person died in the last 30 days
    '''

    # sample individuals
    individuals: Dict[str, Individual] = {}

    indi_data_1 = Individual(
        id = "US36.I1",
        name = "US36.I1",
        death = "7 NOV 2025"
    )
    
    individuals["US36.I1"] = indi_data_1

    return individuals

def test_us36_list_recent_births(sample_data_indi_1):
    """
    positive case - death in the last 30 days
    """
    out = us36_list_recent_deaths(sample_data_indi_1)
    assert len(out) == 1 # assert one anomaly is raised per the fixture