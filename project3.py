"""
Course: 2025F SSW 555–WN Agile Methods for Software Development
Professor: Dr. Richard Ens
Group 2 GEDCOM Program
GitHub: cs555-gedcom-Group2
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import re
import sys
import os

@dataclass
class Individual:
    id: str
    name: str = ""
    sex: str = ""
    birthday: str = ""
    age: object = "NA"         
    alive: bool = True
    death: str = "NA"
    child: List[str] = field(default_factory=list)   
    spouse: List[str] = field(default_factory=list)  
    ged_line_start: int = None
    ged_line_end: int = None

@dataclass
class Family:
    id: str
    married: str = "NA"
    divorced: str = "NA"
    husband_id: str = ""
    husband_name: str = ""
    wife_id: str = ""
    wife_name: str = ""
    children: List[str] = field(default_factory=list)
    ged_line_start: int = None
    ged_line_end: int = None

@dataclass
class ErrorAnomaly:
    error_or_anomaly: str
    indi_or_fam: str
    user_story_id: str
    gedcom_line: str
    indi_or_fam_id: str
    message: str

@dataclass
class GedLine:
    line_num: int
    level: int
    tag: str
    value: str
GED_LINES: List[GedLine] = []

VALID_TAGS = {
    "HEAD","TRLR","NOTE","INDI","FAM","NAME","SEX","BIRT","DEAT","DATE",
    "FAMC","FAMS","HUSB","WIFE","CHIL","MARR","DIV"
}

ERRORS_ANOMALIES: List[ErrorAnomaly] = []

def _parse_date(s: str) -> Optional[date]:
    """Parse GEDCOM-like date 'D MON YYYY' -> date or None."""
    try:
        return datetime.strptime(s.strip(), "%d %b %Y").date()
    except Exception:
        return None

def _compute_age(birth: Optional[date], end: Optional[date] = None):
    if not birth:
        return "NA" #AF NOTE: Causes exceptions in int comparisons if returning string or None
    end = end or date.today()
    years = end.year - birth.year
    if (end.month, end.day) < (birth.month, birth.day):
        years -= 1
    return years

def _id_sort_key(x: str) -> int:
    m = re.findall(r"\d+", x or "")
    return int(''.join(m)) if m else 0

def parse_individuals_family_data(ged_file) -> Tuple[Dict[str, Individual], Dict[str, Family]]:
    individuals: Dict[str, Individual] = {}
    families: Dict[str, Family] = {}

    current_person: Optional[Individual] = None
    current_family: Optional[Family] = None
    pending_date_for: Optional[str] = None  

    for line_num, raw in enumerate(ged_file, start=1):
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        parts = line.strip().split()
        try:
            level = int(parts[0])
        except Exception:
            continue

        tag: Optional[str] = None
        args = ""
        if len(parts) >= 2:
            if len(parts) >= 3 and parts[2] in {"INDI", "FAM"}:
                tag = parts[2]
                args = parts[1]               
            else:
                tag = parts[1]
                args = " ".join(parts[2:]) if len(parts) > 2 else ""

        GED_LINES.append(GedLine(line_num=line_num, level=level, tag=tag, value=args))

        if tag not in VALID_TAGS:
            pending_date_for = None
            continue

        if level == 0:
            if current_person: current_person.ged_line_end=line_num-1
            if current_family: current_family.ged_line_end=line_num-1
            pending_date_for = None
            current_person = None
            current_family = None
            if tag == "INDI":
                pid = args.strip("@")                             
                current_person = individuals.get(pid) or Individual(id=pid, ged_line_start=line_num)
                individuals[pid] = current_person
            elif tag == "FAM":
                fid = args.strip("@")                              
                current_family = families.get(fid) or Family(id=fid, ged_line_start=line_num)
                families[fid] = current_family
            continue

        if current_person:
            if tag == "NAME" and level == 1:
                current_person.name = args.strip()
            elif tag == "SEX" and level == 1:
                current_person.sex = args.strip()
            elif tag in {"BIRT", "DEAT"} and level == 1:
                pending_date_for = tag
            elif tag == "DATE" and level == 2 and pending_date_for:
                date_text = args.strip()               
                if pending_date_for == "BIRT":
                    current_person.birthday = date_text
                elif pending_date_for == "DEAT":
                    current_person.death = date_text
                    current_person.alive = False
                    if ( current_person.birthday and _compute_age(_parse_date(current_person.birthday) , _parse_date(date_text) ) < 0 ):
                        error = ErrorAnomaly(
                        error_or_anomaly='ERROR',
                        indi_or_fam = 'INDIVIDUAL',
                        user_story_id = 'US03',
                        gedcom_line = 'TBD',
                        indi_or_fam_id = current_person.id,
                        message= f'{current_person.name}\'s birthday {_parse_date(current_person.birthday)} occurs after death date {date_text}'
                        )
                        ERRORS_ANOMALIES.append(error)
                pending_date_for = None
            elif tag == "FAMC" and level == 1:
                fam_id = args.strip("@")
                if fam_id:
                    current_person.child.append(fam_id)
            elif tag == "FAMS" and level == 1:
                fam_id = args.strip("@")
                if fam_id:
                    current_person.spouse.append(fam_id)
            else:
                pending_date_for = None
            continue

        if current_family:
            if tag in {"MARR", "DIV"} and level == 1:
                pending_date_for = tag
            elif tag == "DATE" and level == 2 and pending_date_for:
                date_text = args.strip()
                if pending_date_for == "MARR":
                    current_family.married = date_text
                    husband = individuals.get(current_family.husband_id)
                    wife = individuals.get(current_family.wife_id)
                    if( husband and husband.birthday and _compute_age( _parse_date(husband.birthday), _parse_date(date_text) ) < 0 ):
                        error = ErrorAnomaly(
                        error_or_anomaly='ERROR',
                        indi_or_fam = 'FAMILY',
                        user_story_id = 'US02',
                        gedcom_line = 'TBD',
                        indi_or_fam_id = current_family.id,
                        message= f'Husband {husband.name}\'s birth date {_parse_date(husband.birthday)} occurs after marriage date {_parse_date(date_text)}'
                        )
                        ERRORS_ANOMALIES.append(error)
                    if(wife and wife.birthday and _compute_age( _parse_date(wife.birthday), _parse_date(date_text) ) < 0 ):
                        error = ErrorAnomaly(
                        error_or_anomaly='ERROR',
                        indi_or_fam = 'FAMILY',
                        user_story_id = 'US02',
                        gedcom_line = 'TBD',
                        indi_or_fam_id = current_family.id,
                        message= f'Wife {wife.name}\'s birth date {_parse_date(wife.birthday)} occurs after marriage date {_parse_date(date_text)}'
                        )
                        ERRORS_ANOMALIES.append(error)
                elif pending_date_for == "DIV":
                    current_family.divorced = date_text
                pending_date_for = None
            elif tag == "HUSB" and level == 1:
                current_family.husband_id = args.strip("@")
            elif tag == "WIFE" and level == 1:
                current_family.wife_id = args.strip("@")
            elif tag == "CHIL" and level == 1:
                cid = args.strip("@")
                if cid:
                    current_family.children.append(cid)
            else:
                pending_date_for = None
            continue

    for person in individuals.values():
        b = _parse_date(person.birthday)
        d = _parse_date(person.death) if not person.alive else None
        person.age = _compute_age(b, d)

    for fam in families.values():
        fam.husband_name = individuals.get(fam.husband_id, Individual(fam.husband_id)).name
        fam.wife_name    = individuals.get(fam.wife_id,    Individual(fam.wife_id)).name

    return individuals, families

def individual_prettytable(individuals: Dict[str, Individual]):
    from prettytable import PrettyTable
    t = PrettyTable()
    t.field_names = ['ID','Name','Gender','Birthday','Age','Alive','Death','Child','Spouse']
    for iid in sorted(individuals.keys(), key=_id_sort_key):
        p = individuals[iid]
        t.add_row([
            p.id, p.name, p.sex, p.birthday, p.age, p.alive,
            p.death, p.child, p.spouse
        ])
    return t

def family_prettytable(families: Dict[str, Family]):
    from prettytable import PrettyTable
    t = PrettyTable()
    t.field_names = ['ID','Married','Divorced','Husband ID','Husband Name','Wife ID','Wife Name','Children']
    for fid in sorted(families.keys(), key=_id_sort_key):
        f = families[fid]
        t.add_row([
            f.id, f.married, f.divorced,
            f.husband_id, f.husband_name, f.wife_id, f.wife_name, f.children
        ])
    return t

def error_anomaly_prettytable(error_anomalies: List[ErrorAnomaly]):
    from prettytable import PrettyTable
    t = PrettyTable()
    t.field_names = ['Type','Tag','User Story','File Line','ID','Message']
    for e in error_anomalies:
        t.add_row([
            e.error_or_anomaly, e.indi_or_fam, e.user_story_id,
            e.gedcom_line, e.indi_or_fam_id, e.message
        ])
    return t

def prompt_user_for_input():
    """
    This function will query the user for a GEDCOM file input before returning.
    This function will query again until the user exits by entering q or provides the correct input.
    :return: A validated GEDCOM file
    """
    user_input = 0
    while True:
        try:
            user_input = input("\nEnter the GEDCOM file path or enter q to exit the program: ")
            if user_input is 'q':
                print("\n*****User exited the program******")
                sys.exit()
            user_input = str(user_input)
            if len(user_input) == 0:
                print("\n*****Please check your input and try again.")
                continue
            if not os.path.exists(user_input):
                print("\n*****Could not find file. Please check your input and try again.")
                continue
        except ValueError:
            #Providing generic feedback for the error
            print("\n*****An incorrect input was identified. Please check your input and try again.")
            continue
        else:
            break

    return user_input

    # ---------- AV Sprint 1 (US04, US05, US06) ----------

from datetime import datetime, date  

def _to_date(s: str) -> date | None:
    """Parse 'DD MON YYYY' or return None for 'NA'/blank."""
    if not s or s == "NA":
        return None
    try:
        return datetime.strptime(s.strip(), "%d %b %Y").date()
    except Exception:
        return None

def validate_dates_before_current_date(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]: #us01
    out: List[ErrorAnomaly] = []
    current_date = date.today()
    for person in individuals.values():
        b = _parse_date(person.birthday)
        d = _parse_date(person.death) if not person.alive else None
        if b and _compute_age(b, current_date) < 0:
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='INDIVIDUAL',
                user_story_id='US01',
                gedcom_line='TBD',
                indi_or_fam_id=person.id,
                message=f'Birthday {b} occurs in the future'
            )
            out.append(error)
        if d and not person.alive and _compute_age(d, current_date) < 0:
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='INDIVIDUAL',
                user_story_id='US01',
                gedcom_line='TBD',
                indi_or_fam_id=person.id,
                message=f'Death {d} occurs in the future'
            )
            out.append(error)

    for fam in families.values():
        m = _parse_date(fam.married)
        d = _parse_date(fam.divorced)
        if not m is None and _compute_age(m, current_date) < 0:
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='FAMILY',
                user_story_id='US01',
                gedcom_line='TBD',
                indi_or_fam_id=fam.id,
                message=f'Marriage date {m} occurs in the future'
            )
            out.append(error)
        if not d is None and _compute_age(d, current_date) < 0:
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='FAMILY',
                user_story_id='US01',
                gedcom_line='TBD',
                indi_or_fam_id=fam.id,
                message=f'Divorce date {d} occurs in the future'
            )
            out.append(error)
    return out

def validate_less_than_150_years_old(individuals: Dict[str, Individual]) -> List[ErrorAnomaly]: #us07
    out: List[ErrorAnomaly] = []
    for person in individuals.values():
        b = _parse_date(person.birthday)
        d = _parse_date(person.death) if not person.alive else None
        if person.age != "NA" and person.age >= 150:
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='INDIVIDUAL',
                user_story_id='US07',
                gedcom_line='TBD',
                indi_or_fam_id=person.id,
                message=f'More than 150 years old - Birth {b}'
            )
            if not person.alive:
                error.message=f'More than 150 years old at death - Birth {b} : Death {d}'
            out.append(error)
    return out

def validate_us04(families: Dict[str, Family]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    for f in families.values():
        m = _parse_date(f.married)
        d = _parse_date(f.divorced)
        if m and d and m > d:
            out.append(ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='FAMILY',
                user_story_id='US04',
                gedcom_line='TBD',
                indi_or_fam_id=f.id,
                message=f'Marriage date {m} occurs after divorce date {d}'
            ))
    return out

def validate_us05(individuals: Dict[str, Individual],
                  families: Dict[str, Family]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    for f in families.values():
        m = _parse_date(f.married)
        if not m: 
            continue
        h = individuals.get(f.husband_id)
        if h:
            hd = _parse_date(h.death) if not h.alive else None
            if hd and m > hd:
                out.append(ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam='FAMILY',
                    user_story_id='US05',
                    gedcom_line='TBD',
                    indi_or_fam_id=f.id,
                    message=f'Marriage date {m} occurs after death of husband {h.id} ({h.name}) on {hd}'
                ))
        w = individuals.get(f.wife_id)
        if w:
            wd = _parse_date(w.death) if not w.alive else None
            if wd and m > wd:
                out.append(ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam='FAMILY',
                    user_story_id='US05',
                    gedcom_line='TBD',
                    indi_or_fam_id=f.id,
                    message=f'Marriage date {m} occurs after death of wife {w.id} ({w.name}) on {wd}'
                ))
    return out

def validate_us06(individuals: Dict[str, Individual],
                  families: Dict[str, Family]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    for f in families.values():
        dv = _parse_date(f.divorced)
        if not dv:
            continue
        h = individuals.get(f.husband_id)
        if h:
            hd = _parse_date(h.death) if not h.alive else None
            if hd and dv > hd:
                out.append(ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam='FAMILY',
                    user_story_id='US06',
                    gedcom_line='TBD',
                    indi_or_fam_id=f.id,
                    message=f'Divorce date {dv} occurs after death of husband {h.id} ({h.name}) on {hd}'
                ))
        w = individuals.get(f.wife_id)
        if w:
            wd = _parse_date(w.death) if not w.alive else None
            if wd and dv > wd:
                out.append(ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam='FAMILY',
                    user_story_id='US06',
                    gedcom_line='TBD',
                    indi_or_fam_id=f.id,
                    message=f'Divorce date {dv} occurs after death of wife {w.id} ({w.name}) on {wd}'
                ))
    return out

def validate_birth_before_parent_marriage(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:  #US08
    out: List[ErrorAnomaly] = []
    for indi in individuals.values():
        try:
            indi_dob = _parse_date(indi.birthday)
            if not indi_dob: continue
            fams = [f for f in families.values() if any(c == indi.id for c in f.children)]
            for fam in fams: #Allow child to be member of multiple families - a separate validation should handle this
                try:
                    fam_marr = _parse_date(fam.married)
                    if not fam_marr: continue
                    if indi_dob < fam_marr:
                        line_num = find_ged_line("DATE", fam.married, "MARR", fam.ged_line_start, fam.ged_line_end)
                        out.append(
                            ErrorAnomaly(
                                error_or_anomaly = "ANOMALY",
                                indi_or_fam = "FAMILY",
                                user_story_id = "US08",
                                gedcom_line = line_num,
                                indi_or_fam_id = fam.id,
                                message = f"Child {indi.id} born {indi_dob} before marriage on {fam_marr}"
                            )
                        )
                except: continue
        except: continue
    return out

def validate_birth_before_parent_death(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]: #US08
    out: List[ErrorAnomaly] = []
    for indi in individuals.values():
        try:
            indi_dob = _parse_date(indi.birthday)
            if not indi_dob: continue
            fams = [f for f in families.values() if any(c == indi.id for c in f.children)]
            for fam in fams: #Allow child to be member of multiple families - a separate validation should handle this
                try:
                    if (not fam.wife_id or fam.wife_id == "NA") and (not fam.husband_id or fam.husband_id == "NA"): continue
                    for (parent_type, parent_id) in [("mother", fam.wife_id), ("father", fam.husband_id)]:
                        try:
                            if parent_id and parent_id != "NA":
                                parents = [p for p in individuals.values() if p.id == parent_id]
                                for parent in parents: #Allow multiple mothers/fathers - a separate validation should handle this
                                    try:
                                        parent_dod = _parse_date(parent.death)
                                        if parent.alive or not parent_dod: continue
                                        if indi_dob > parent_dod:
                                            line_num = find_ged_line("DATE", indi.birthday, "BIRT", indi.ged_line_start, indi.ged_line_end)
                                            out.append(
                                                ErrorAnomaly(
                                                    error_or_anomaly = "ERROR",
                                                    indi_or_fam = "FAMILY",
                                                    user_story_id = "US09",
                                                    gedcom_line = line_num,
                                                    indi_or_fam_id = fam.id,
                                                    message = f"Child {indi.id} born {indi_dob} after {parent_type}'s death on {parent_dod}"
                                                )
                                            )
                                    except: continue
                        except: continue
                except: continue
        except: continue
    return out

def validate_marriage_after_14(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]: #US10
    out: List[ErrorAnomaly] = []
    for fam in families.values():
        if fam.married != 'NA': # if no marriage date do nothing
            fam_married_dt = _parse_date(fam.married) # store marriage date for familiy
            
            # locate and store husband and wife if they exist
            indis = [] 
            if not fam.husband_id: 
                pass
            else:
                indis.append(fam.husband_id)

            if not fam.wife_id:
                pass
            else:
                indis.append(fam.wife_id)

            # locate and store birthdates for husband and wife if they exist,
            # calculate age at marriage in years
            dobs = []

            for indi in individuals.values():
                if indi.id in indis:
                    
                    try:
                        dob = _parse_date(indi.birthday)
                        delta = relativedelta(fam_married_dt, dob) # calculate age at marriage
                        age_at_marriage = delta.years # floor years
                        dobs.append([indi.id, dob, age_at_marriage])

                    except Exception:
                        continue
            
            # check all spouses for age >= 14 at marraige
            for dob in dobs:
                if dob[2] < 14:
                    line_num = find_ged_line("DATE", fam.married, "MARR", fam.ged_line_start, fam.ged_line_end)
                    out.append(
                            ErrorAnomaly(
                                error_or_anomaly = "ANOMALY",
                                indi_or_fam = "FAMILY",
                                user_story_id = "US10",
                                gedcom_line = line_num,
                                indi_or_fam_id = fam.id,
                                message = f"Spouse {dob[0]} born on {dob[1]} had age {dob[2]} < 14 at marriage date {fam_married_dt}"
                            )
                    )
    return out


def find_ged_line(tag: str, value: str, prev_tag: str, start:int, end:int) -> int:
    if not tag and not value: return None
    if start > end: return None
    ged_lines = [g for g in GED_LINES if start <= g.line_num <= end and g.tag == tag and g.value == value and (not prev_tag or (0 < g.line_num < len(GED_LINES) and prev_tag == GED_LINES[g.line_num-1].tag))]
    if ged_lines:
        return ged_lines[0].line_num #Returns first found instance
    else:
        return None

def main():
    path = "data/TestData.ged"
    #path = prompt_user_for_input()
    if len(sys.argv) > 1:
        path = sys.argv[1]

    try:
        with open(path, "r", encoding="utf-8") as fh:
            individuals, families = parse_individuals_family_data(fh)
    except Exception as e:
        print("Cannot open GEDCOM file:", path)
        print(e)
        sys.exit(1)

    ERRORS_ANOMALIES.extend(validate_dates_before_current_date(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us04(families))
    ERRORS_ANOMALIES.extend(validate_us05(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us06(individuals, families))
    ERRORS_ANOMALIES.extend(validate_less_than_150_years_old(individuals))
    ERRORS_ANOMALIES.extend(validate_birth_before_parent_marriage(individuals, families))
    ERRORS_ANOMALIES.extend(validate_birth_before_parent_death(individuals, families))
    ERRORS_ANOMALIES.extend(validate_marriage_after_14(individuals, families))

    i_table = individual_prettytable(individuals)
    f_table = family_prettytable(families)
    e_table = error_anomaly_prettytable(ERRORS_ANOMALIES)

    print("\nIndividuals")
    print(i_table)
    print("\nFamilies")
    print(f_table)
    print("\nErrors & Anomalies")
    print(e_table)

    with open("run_output.txt", "w", encoding="utf-8") as out:
        out.write("Individuals\n")
        out.write(str(i_table))
        out.write("\n\nFamilies\n")
        out.write(str(f_table))
        out.write("\n\nErrors & Anomalies\n")
        out.write(str(e_table))
        out.write("\n")

if __name__ == "__main__":
    main()

