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

from project3 import (
    Individual,
    Family,
    GedLine,
    parse_individuals_family_data,
    validate_us11_no_bigamy,
    validate_us17_marriage_to_descendants,
    validate_us19_first_cousins_marry
)

@pytest.fixture
def test_data_us11_families():

    families: Dict[str, Family] = {} # mock families data, to be populated

    # first familiy is missing marriage date
    fam_data = Family(
        id = "F_test_1",
        married = "NA",
        husband_id = "I_test_1M",
        husband_name = "I_test_1M",
        wife_id = "I_test_1F",
        wife_name = "I_test_1F",
        )
    
    families["F_test_1"] = fam_data

    # second family has the same husband
    fam_data = Family(
        id = "F_test_2",
        married = "1 JUN 2008",
        husband_id = "I_test_1M",
        husband_name = "I_test_1M",
        wife_id = "I_test_2F",
        wife_name = "I_test_2F",
        )
    
    families["F_test_2"] = fam_data

    return families

@pytest.fixture
def test_data_us11_individuals():

    individuals: Dict[str, Individual] = {} # mock individuals data, can be empty as it is not used by the user story
    return individuals


@pytest.fixture
def test_data_us17_families():

    families: Dict[str, Family] = {} # mock families data, to be populated

    # first familiy has three children
    fam_data = Family(
        id = "F_test_1",
        married = "1 JUN 2008",
        husband_id = "I_test_1M",
        husband_name = "I_test_1M",
        wife_id = "I_test_1F",
        wife_name = "I_test_1F",
        children = ["I_test_1C", "I_test_2C", "I_test_3C"],
        ged_line_start = 0,
        ged_line_end = 6
        )
    
    families["F_test_1"] = fam_data

    # second family has last child "I_test_3C" married to parent "I_test_1M"
    fam_data = Family(
        id = "F_test_2",
        married = "1 JUN 2008",
        husband_id = "I_test_1M",
        husband_name = "I_test_1M",
        wife_id = "I_test_3C",
        wife_name = "I_test_3C",
        ged_line_start = 0,
        ged_line_end = 6
        )
    
    families["F_test_2"] = fam_data

    return families

@pytest.fixture
def test_data_us19_families():

    families: Dict[str, Family] = {} # mock families data, to be populated

    # first familiy has children/siblings "I_test_1C", "I_test_2C"
    fam_data = Family(
        id = "F_test_1",
        married = "1 JUN 2008",
        husband_id = "I_test_1M",
        husband_name = "I_test_1M",
        wife_id = "I_test_1F",
        wife_name = "I_test_1F",
        children = ["I_test_1C", "I_test_2C"],
        ged_line_start = 0,
        ged_line_end = 6
        )
    families["F_test_1"] = fam_data

    # family of "I_test_1C"
    fam_data = Family(
        id = "F_test_2",
        married = "1 JUN 2008",
        husband_id = "I_test_1C",
        husband_name = "I_test_1C",
        wife_id = "I_test_2F",
        wife_name = "I_test_2F",
        children = ["I_test_3C"], # "I_test_3C" is cousins to both "I_test_4C" and "I_test_5C"
        ged_line_start = 0,
        ged_line_end = 6
        )
    families["F_test_2"] = fam_data

    # family of "I_test_2C"
    fam_data = Family(
        id = "F_test_3",
        married = "1 JUN 2008",
        husband_id = "I_test_2C",
        husband_name = "I_test_2C",
        wife_id = "I_test_3F",
        wife_name = "I_test_3F",
        children = ["I_test_4C","I_test_5C"], # "I_test_3C" is cousins to both "I_test_4C" and "I_test_5C"
        ged_line_start = 0,
        ged_line_end = 6
        )
    families["F_test_3"] = fam_data

    # marriage to cousin #1
    fam_data = Family(
        id = "F_test_4",
        married = "1 JUN 2008",
        husband_id = "I_test_3C",
        husband_name = "I_test_3C",
        wife_id = "I_test_4C",
        wife_name = "I_test_4C",
        ged_line_start = 0,
        ged_line_end = 6
        )
    families["F_test_4"] = fam_data

    # marriage to cousin #2
    fam_data = Family(
        id = "F_test_5",
        married = "1 JUN 2008",
        husband_id = "I_test_3C",
        husband_name = "I_test_3C",
        wife_id = "I_test_5C",
        wife_name = "I_test_5C",
        ged_line_start = 0,
        ged_line_end = 6
        )
    families["F_test_5"] = fam_data

    return families


def test_us11(test_data_us11_individuals, test_data_us11_families):
    '''
    Test that the US11 anomaly is not raised when marriage date is missing, as the condition for bigamy cannot be checked (marriage should not occur during marriage to another spouse)
    '''
    out = validate_us11_no_bigamy(individuals = test_data_us11_individuals, families = test_data_us11_families)
    assert len(out) == 0

def test_us17(test_data_us17_families):
    '''
    Test that the US17 anomaly is raised when the last child listed in the family is the violation (married to a parent)
    (depends on parse_individuals_family_data returned families)
    '''
    out = validate_us17_marriage_to_descendants(test_data_us17_families)
    assert len(out) == 1 # assert that the one anomaly from the pytest fixture is raised, "I_test_1M" married to "I_test_3C"

def test_us19(test_data_us19_families):
    '''
    Test that US19 anomaly is raised for multiple cousin-marriage violations
    4 violations are raised due to combinations (2 violations x 2 combinations (violations go both ways))
    '''
    out = validate_us19_first_cousins_marry(test_data_us19_families)
    assert len(out) == 4 # all pairwise combinations: "I_test_4C" to "I_test_3C", "I_test_3C" to "I_test_4C", \
                         # "I_test_5C" to "I_test_3C", "I_test_3C" to "I_test_5C"
