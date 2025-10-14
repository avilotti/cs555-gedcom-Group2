import unittest, os
from ..project3 import validate_us20_aunts_and_uncles, parse_individuals_family_data, validate_us16_male_last_names

def parse_test_data(self):
    """Parse the acceptance GEDCOM in the repo root."""
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests\\TestData_us16+us20.ged"))
    with open(path, "r", encoding="utf-8") as fh:
        return parse_individuals_family_data(fh)

class TestClass(unittest.TestCase):
    def test_validate_us16_finds_one_error(self):
        individuals, families = parse_test_data(self)
        errs = [e for e in validate_us16_male_last_names(individuals, families)]
        self.assertTrue(len(errs) == 1)
    def test_validate_us20_finds_two_errors(self):
        individuals, families = parse_test_data(self)
        errs = [e for e in validate_us20_aunts_and_uncles(individuals, families)]
        self.assertTrue(len(errs) == 2)

if __name__ == '__main__':
    unittest.main()
