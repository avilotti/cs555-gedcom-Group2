import unittest, os
from project3_test import validate_us21_correct_gender_for_role, validate_us26_corresponding_entries, parse_individuals_family_data

def parse_test_data(self):
    """Parse the acceptance GEDCOM in the repo root."""
    path = os.path.abspath(os.path.join(os.path.dirname(__file__),"TestData_us21+us26.ged"))
    with open(path, "r", encoding="utf-8") as fh:
        return parse_individuals_family_data(fh)

class TestClass(unittest.TestCase):
    def test_validate_us21_correct_gender_for_role_two_errors(self):
        individuals, families = parse_test_data(self)
        errs = [e for e in validate_us21_correct_gender_for_role(individuals, families)]
        self.assertTrue(len(errs) == 2)
    def test_validate_us26_corresponding_entries(self):
        individuals, families = parse_test_data(self)
        errs = [e for e in validate_us26_corresponding_entries(individuals, families)]
        self.assertTrue(len(errs) == 4)

if __name__ == '__main__':
    unittest.main()