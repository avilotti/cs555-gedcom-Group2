from io import StringIO
import project3 as p

def _reset_globals():
    p.GED_LINES.clear()
    p.ERRORS_ANOMALIES.clear()

def test_us23_duplicate_name_and_birthday_detected():
    """
    Two different individuals with the same NAME + BIRTHDAY should raise a single US23 anomaly.
    """
    _reset_globals()
    ged = StringIO(
        "0 NOTE test\n"
        "0 @D1@ INDI\n1 NAME John Smith\n1 BIRT\n2 DATE 1 JAN 2000\n"
        "0 @D2@ INDI\n1 NAME John Smith\n1 BIRT\n2 DATE 1 JAN 2000\n"
        "0 @OK@ INDI\n1 NAME John Smith\n1 BIRT\n2 DATE 2 JAN 2000\n"
        "0 TRLR\n"
    )
    individuals, _ = p.parse_individuals_family_data(ged)
    out = p.validate_us23_unique_name_and_birthday(individuals)

    hits = [e for e in out if e.user_story_id == "US23"]
    assert len(hits) == 1, "Exactly one US23 anomaly expected for the duplicate pair"
    msg = hits[0].message
    assert "Duplicate Name+Birthday" in msg
    assert "D1" in hits[0].indi_or_fam_id and "D2" in hits[0].indi_or_fam_id

def test_us23_no_duplicates_when_dates_differ():
    """
    Same name but different birthday is OK (no US23 anomalies).
    """
    _reset_globals()
    ged = StringIO(
        "0 NOTE test\n"
        "0 @A@ INDI\n1 NAME Alice Doe\n1 BIRT\n2 DATE 1 JAN 2000\n"
        "0 @B@ INDI\n1 NAME Alice Doe\n1 BIRT\n2 DATE 2 JAN 2000\n"
        "0 TRLR\n"
    )
    individuals, _ = p.parse_individuals_family_data(ged)
    out = p.validate_us23_unique_name_and_birthday(individuals)
    assert not [e for e in out if e.user_story_id == "US23"]
