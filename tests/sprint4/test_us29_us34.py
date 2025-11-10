import unittest
from typing import Dict, List
from project3_test import Individual, Family, validate_u29_list_deceased, validate_u34_list_large_age_difference_between_married_couples

def get_individual_test_data():
    '''
    1 positive and 2 negative cases
    '''

    individuals: Dict[str, Individual] = {}

    indi_data_1 = Individual(
        id="US29.I1",
        name="US29.I1",
        birthday="1 JAN 1900",
        death="1 JAN 2020"
    )
    indi_data_2 = Individual(
        id="US29.I2",
        name="US29.I2",
        birthday="1 JAN 1921",
        death="1 JAN 2222"
    )
    indi_data_3 = Individual(
        id="US29.I3",
        name="US29.I3",
        birthday="1 JAN 1941",
        death=""
    )

    individuals["US29.I1"] = indi_data_1
    individuals["US29.I2"] = indi_data_2
    individuals["US29.I3"] = indi_data_3
    return individuals

def get_family_test_data():
    '''
    3 cases
    '''

    families: Dict[str, Family] = {}

    fam_data_1 = Family(
        id="US34.F1",
        husband_id="US29.I1",
        wife_id="US29.I2",
        married="2 JAN 1940"
    )
    fam_data_2 = Family(
        id="US34.F2",
        husband_id="US29.I1",
        wife_id="US29.I3",
        married="2 JAN 1960"
    )
    fam_data_3 = Family(
        id="US34.F3",
        husband_id="US29.I3",
        wife_id="US29.I2",
        married="2 JAN 1960"
    )

    families["US34.F1"] = fam_data_1
    families["US34.F2"] = fam_data_2
    families["US34.F3"] = fam_data_3
    return families

class TestClass(unittest.TestCase):
    def test_validate_us29_two_deceased_individuals(self):
        errs = validate_u29_list_deceased(get_individual_test_data())
        self.assertTrue(len(errs) == 2)
    def test_validate_u34_list_large_age_difference_between_married_couples(self):
        errs = validate_u34_list_large_age_difference_between_married_couples(get_individual_test_data(), get_family_test_data())
        self.assertTrue(len(errs) == 3)

if __name__ == '__main__':
    unittest.main()