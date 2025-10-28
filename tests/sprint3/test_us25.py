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

from project3 import Individual, Family, GedLine, ErrorAnomaly, validate_us25_unique_first_names_in_families

@pytest.fixture
def sample_data_fam_1():

    families: Dict[str, Family] = {}

    fam_data = Family(
        id = "F1",
        married = "1 JAN 2024",
        wife_id = "I1",
        wife_name = "Indivdual1",
        husband_id = "I2",
        husband_name = "Individual2",
        children = ["C1","C2"]
        )

    families["F1"] = fam_data
    return families


@pytest.fixture
def sample_data_indis_1():
    '''
    positive case - two children in the same family with same name and birthday
    '''

    # sample individuals
    individuals: Dict[str, Individual] = {}

    indi_data_1 = Individual(
        id = "C1",
        name = "Child1",
        birthday = "1 JAN 2024"
    )

    indi_data_2 = Individual(
        id = "C2",
        name = "Child1",
        birthday = "1 JAN 2024"
    )

    individuals["C1"] = indi_data_1
    individuals["C2"] = indi_data_2

    return individuals

@pytest.fixture
def sample_data_indis_2():
    '''
    negative case - two children in the same family with different name but same birthday
    '''

    # sample individuals
    individuals: Dict[str, Individual] = {}

    indi_data_1 = Individual(
        id = "C1",
        name = "Child1",
        birthday = "1 JAN 2024"
    )

    indi_data_2 = Individual(
        id = "C2",
        name = "Child2",
        birthday = "1 JAN 2024"
    )

    individuals["C1"] = indi_data_1
    individuals["C2"] = indi_data_2

    return individuals

@pytest.fixture
def sample_data_indis_3():
    '''
    negative case - two children in the same family with same name but different birthday
    '''

    # sample individuals
    individuals: Dict[str, Individual] = {}

    indi_data_1 = Individual(
        id = "C1",
        name = "Child1",
        birthday = "1 JAN 2024"
    )

    indi_data_2 = Individual(
        id = "C2",
        name = "Child1",
        birthday = "2 JAN 2024"
    )

    individuals["C1"] = indi_data_1
    individuals["C2"] = indi_data_2

    return individuals

def test_us25_unique_first_names_in_families_postive(sample_data_indis_1, sample_data_fam_1):
    """
    positive case - two children with same name and same birthdate
    """
    out = validate_us25_unique_first_names_in_families(sample_data_indis_1, sample_data_fam_1)
    assert len(out) == 1 # assert one anomaly is raised per the fixture

def test_us25_unique_first_names_in_families_negative_names(sample_data_indis_2, sample_data_fam_1):
    """
    positive case - two children with different names but same birthdate
    """
    out = validate_us25_unique_first_names_in_families(sample_data_indis_2, sample_data_fam_1)
    assert out == [] # assert no anomalies are raised

def test_us25_unique_first_names_in_families_negative_bds(sample_data_indis_3, sample_data_fam_1):
    """
    positive case - two children with same names and but different birthdates
    """
    out = validate_us25_unique_first_names_in_families(sample_data_indis_3, sample_data_fam_1)
    assert out == [] # assert no anomalies are raised