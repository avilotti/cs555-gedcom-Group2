from io import StringIO
import project3 as p

def _reset_globals():
    p.GED_LINES.clear()
    p.ERRORS_ANOMALIES.clear()

def test_us28_order_children_oldest_to_youngest_and_missing_last():
    """
    US28: ordered_children_ids_by_age returns oldest -> youngest,
    and children without birthdays are placed at the end.
    """
    _reset_globals()
    ged = StringIO(
        "0 NOTE test\n"
        "0 @C1@ INDI\n1 NAME Kid One\n1 BIRT\n2 DATE 1 JAN 2000\n"
        "0 @C2@ INDI\n1 NAME Kid Two\n1 BIRT\n2 DATE 15 APR 2000\n"
        "0 @C3@ INDI\n1 NAME Kid Three\n"                    # no birthday
        "0 @F1@ FAM\n1 CHIL @C1@\n1 CHIL @C2@\n1 CHIL @C3@\n"
        "0 TRLR\n"
    )
    individuals, families = p.parse_individuals_family_data(ged)
    fam = families["F1"]
    ordered = p.ordered_children_ids_by_age(fam, individuals)
    assert ordered == ["C1", "C2", "C3"]
    # display-only: don't mutate stored list
    assert fam.children == ["C1", "C2", "C3"]

def test_us28_ties_preserve_original_child_order():
    """
    When birthdays are the same, the stable sort preserves the original CHIL order.
    """
    _reset_globals()
    ged = StringIO(
        "0 NOTE test\n"
        "0 @T1@ INDI\n1 NAME Twin A\n1 BIRT\n2 DATE 10 OCT 2001\n"
        "0 @T2@ INDI\n1 NAME Twin B\n1 BIRT\n2 DATE 10 OCT 2001\n"
        "0 @F2@ FAM\n1 CHIL @T1@\n1 CHIL @T2@\n"
        "0 TRLR\n"
    )
    individuals, families = p.parse_individuals_family_data(ged)
    fam = families["F2"]
    ordered = p.ordered_children_ids_by_age(fam, individuals)
    assert ordered == ["T1", "T2"]
