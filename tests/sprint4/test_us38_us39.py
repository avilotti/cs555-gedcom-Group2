import pytest
from datetime import date, timedelta
from project3 import validate_us38_upcoming_birthdays, validate_us39_upcoming_anniversaries, Individual, Family

def test_us38_upcoming_birthdays():
    today = date.today()
    soon = (today + timedelta(days=10)).strftime("%d %b %Y")
    later = (today + timedelta(days=40)).strftime("%d %b %Y")

    individuals = {
        "I1": Individual(id="I1", name="John /Doe/", sex="M", birthday=soon, alive=True),
        "I2": Individual(id="I2", name="Jane /Doe/", sex="F", birthday=later, alive=True),
    }

    results = validate_us38_upcoming_birthdays(individuals)
    assert any("John" in e.message for e in results)
    assert not any("Jane" in e.message for e in results)

def test_us39_upcoming_anniversaries():
    today = date.today()
    soon = (today + timedelta(days=15)).strftime("%d %b %Y")
    later = (today + timedelta(days=45)).strftime("%d %b %Y")

    individuals = {
        "I1": Individual(id="I1", name="John /Doe/", alive=True),
        "I2": Individual(id="I2", name="Jane /Doe/", alive=True),
    }
    families = {
        "F1": Family(id="F1", married=soon, husband_id="I1", wife_id="I2"),
        "F2": Family(id="F2", married=later, husband_id="I1", wife_id="I2"),
    }

    results = validate_us39_upcoming_anniversaries(families, individuals)
    assert any("John" in e.message for e in results)
    assert not any("F2" in e.message for e in results)
