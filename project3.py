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
    allowed_date_patterns = {
        "%d %b %Y", #D MMM YYYY
        "%b %Y",    #MMM YYYY
        "%Y"        #YYYY
    }
    for pattern in allowed_date_patterns:
        try:
            return datetime.strptime(s.strip(), pattern).date()
        except Exception:
            continue
    else:
        return None

def _compute_age(birth: Optional[date], end: Optional[date] = None) -> int:
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
                #US22 - Check duplicate individual IDs
                if(individuals.get(pid)):
                    error = ErrorAnomaly(
                        error_or_anomaly='ERROR',
                        indi_or_fam='INDIVIDUAL',
                        user_story_id='US22',
                        gedcom_line=line_num,
                        indi_or_fam_id=pid,
                        message=f'Individual ID {pid} is a duplicate'
                    )
                    ERRORS_ANOMALIES.append(error)
                current_person = individuals.get(pid) or Individual(id=pid, ged_line_start=line_num)
                individuals[pid] = current_person
            elif tag == "FAM":
                fid = args.strip("@")
                #US22 - Check duplicate family IDs
                if(families.get(fid)):
                    error = ErrorAnomaly(
                        error_or_anomaly='ERROR',
                        indi_or_fam='FAMILY',
                        user_story_id='US22',
                        gedcom_line=line_num,
                        indi_or_fam_id=fid,
                        message=f'Family ID {fid} is a duplicate'
                    )
                    ERRORS_ANOMALIES.append(error)                              
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
                    #US32 List multiple births
                    if(current_person.birthday):
                        error = ErrorAnomaly(
                            error_or_anomaly='ANOMALY',
                            indi_or_fam='INDIVIDUAL',
                            user_story_id='US32',
                            gedcom_line=line_num,
                            indi_or_fam_id=current_person.id,
                            message=f'Individual {pid} has another birth at {current_person.birthday}'
                        )
                        ERRORS_ANOMALIES.append(error)    
                    current_person.birthday = date_text
                elif pending_date_for == "DEAT":
                    current_person.death = date_text
                    current_person.alive = False
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

def ordered_children_ids_by_age(fam: Family, individuals: Dict[str, Individual]) -> List[str]:
    """
    Return the family's children ordered from oldest to youngest.
    Children without a valid birthday go at the end (US28).
    """
    items: List[Tuple[str, Optional[date]]] = []
    for cid in fam.children:
        p = individuals.get(cid)
        dob = _parse_date(p.birthday) if p else None
        items.append((cid, dob))
    items.sort(key=lambda x: (x[1] is None, x[1]))
    return [cid for cid, _ in items]

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

def family_prettytable(families: Dict[str, Family], individuals: Dict[str, Individual]):
    from prettytable import PrettyTable
    t = PrettyTable()
    t.field_names = ['ID','Married','Divorced','Husband ID','Husband Name','Wife ID','Wife Name','Children (oldest→youngest)']
    for fid in sorted(families.keys(), key=_id_sort_key):
        f = families[fid]
        ordered_kids = ordered_children_ids_by_age(f, individuals)  # US28: display-only order
        t.add_row([
            f.id, f.married, f.divorced,
            f.husband_id, f.husband_name, f.wife_id, f.wife_name, ordered_kids
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
            if str(user_input).strip().lower() == 'q':                
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

def validate_dates_before_current_date(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]: #us01
    out: List[ErrorAnomaly] = []
    current_date = date.today()
    for person in individuals.values():
        b = _parse_date(person.birthday)
        d = _parse_date(person.death) if not person.alive else None
        if b and _compute_age(b, current_date) < 0:
            line_num = find_ged_line("DATE", person.birthday, "BIRT", person.ged_line_start, person.ged_line_end) #or person.ged_line_start
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='INDIVIDUAL',
                user_story_id='US01',
                gedcom_line=line_num,
                indi_or_fam_id=person.id,
                message=f'Birthday {b} occurs in the future'
            )
            out.append(error)
        if d and not person.alive and _compute_age(d, current_date) < 0:
            line_num = find_ged_line("DATE", person.death, "DEAT", person.ged_line_start, person.ged_line_end) #or person.ged_line_start
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='INDIVIDUAL',
                user_story_id='US01',
                gedcom_line=line_num,
                indi_or_fam_id=person.id,
                message=f'Death {d} occurs in the future'
            )
            out.append(error)

    for fam in families.values():
        m = _parse_date(fam.married)
        d = _parse_date(fam.divorced)
        if not m is None and _compute_age(m, current_date) < 0:
            line_num = find_ged_line("DATE", fam.married, "MARR", fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='FAMILY',
                user_story_id='US01',
                gedcom_line=line_num,
                indi_or_fam_id=fam.id,
                message=f'Marriage date {m} occurs in the future'
            )
            out.append(error)
        if not d is None and _compute_age(d, current_date) < 0:
            line_num = find_ged_line("DATE", fam.divorced, "DIV", fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='FAMILY',
                user_story_id='US01',
                gedcom_line=line_num,
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
            line_num = find_ged_line("DATE", person.birthday, "BIRT", person.ged_line_start, person.ged_line_end) #or person.ged_line_start
            error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='INDIVIDUAL',
                user_story_id='US07',
                gedcom_line=line_num,
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
            line_num = find_ged_line("DATE", f.married, "MARR", f.ged_line_start, f.ged_line_end) #or f.ged_line_start
            out.append(ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam='FAMILY',
                user_story_id='US04',
                gedcom_line=line_num,
                indi_or_fam_id=f.id,
                message=f'Marriage date {m} occurs after divorce date {d}'
            ))
    return out

def validate_us05(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    for f in families.values():
        m = _parse_date(f.married)
        if not m: 
            continue
        h = individuals.get(f.husband_id)
        if h:
            hd = _parse_date(h.death) if not h.alive else None
            if hd and m > hd:
                line_num = find_ged_line("DATE", f.married, "MARR", f.ged_line_start, f.ged_line_end) #or f.ged_line_start
                out.append(ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam='FAMILY',
                    user_story_id='US05',
                    gedcom_line=line_num,
                    indi_or_fam_id=f.id,
                    message=f'Marriage date {m} occurs after death of husband {h.id} ({h.name}) on {hd}'
                ))
        w = individuals.get(f.wife_id)
        if w:
            wd = _parse_date(w.death) if not w.alive else None
            if wd and m > wd:
                line_num = find_ged_line("DATE", f.married, "MARR", f.ged_line_start, f.ged_line_end) #or f.ged_line_start
                out.append(ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam='FAMILY',
                    user_story_id='US05',
                    gedcom_line=line_num,
                    indi_or_fam_id=f.id,
                    message=f'Marriage date {m} occurs after death of wife {w.id} ({w.name}) on {wd}'
                ))
    return out

def validate_us06(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    for f in families.values():
        dv = _parse_date(f.divorced)
        if not dv:
            continue
        h = individuals.get(f.husband_id)
        if h:
            hd = _parse_date(h.death) if not h.alive else None
            if hd and dv > hd:
                line_num = find_ged_line("DATE", f.divorced, "DIV", f.ged_line_start, f.ged_line_end) #or f.ged_line_start
                out.append(ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam='FAMILY',
                    user_story_id='US06',
                    gedcom_line=line_num,
                    indi_or_fam_id=f.id,
                    message=f'Divorce date {dv} occurs after death of husband {h.id} ({h.name}) on {hd}'
                ))
        w = individuals.get(f.wife_id)
        if w:
            wd = _parse_date(w.death) if not w.alive else None
            if wd and dv > wd:
                line_num = find_ged_line("DATE", f.divorced, "DIV", f.ged_line_start, f.ged_line_end) #or f.ged_line_start
                out.append(ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam='FAMILY',
                    user_story_id='US06',
                    gedcom_line=line_num,
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
                        line_num = find_ged_line("DATE", fam.married, "MARR", fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
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
                                            line_num = find_ged_line("DATE", indi.birthday, "BIRT", indi.ged_line_start, indi.ged_line_end) #or indi.ged_line_start
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

def validate_us10_marriage_after_14(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]: #US10
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
                    line_num = find_ged_line("DATE", fam.married, "MARR", fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
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

def validate_us11_no_bigamy(individuals: Dict[str, Individual], families: Dict[str, Family]):
    out: List[ErrorAnomaly] = []
    married: Dict[str, Family] = {}

    # collect valid marriages
    for fam in families.values():
        if ((fam.married != 'NA') and (fam.married != '') and (fam.husband_id) and (fam.wife_id)):
            married[fam.id] = fam

    # collect spouses
    husbands = [fam.husband_id for fam in married.values()]
    wifes = [fam.wife_id for fam in married.values()]

    # check if each spouse occurs more than once
    for husband in set(husbands):
        count = husbands.count(husband)

        if count > 1:
            temp = [fam for fam in married.values() if fam.husband_id == husband]
            temp = sorted(
                [fam for fam in temp if fam.married not in ('NA','',None)],
            key = lambda f: _parse_date(f.married),
            )
            
            div = _parse_date(temp[0].divorced)
            marr = _parse_date(temp[0].married)
            family1 = temp[0].id
            wife_id = temp[0].wife_id
            wife_death = None

            wife = [indi for indi in individuals.values() if indi.id == wife_id]
            if wife:
                wife_death = _parse_date(wife[0].death)

            # for each later marriage
            for mar in temp[1:]:
                next_marr = _parse_date(mar.married)

                # check if divorce, and prior to next marraige
                if div:
                    if (div < next_marr):

                        # next marriage is the valid marriage
                        div = _parse_date(mar.divorced)
                        marr = _parse_date(mar.married)
                        wife_id = mar.wife_id

                # check if wifes death, and prior to next marraige
                elif wife and wife_death is not None:
                    if (wife_death < next_marr):

                        # next marraige if the valid marriage
                        div = _parse_date(mar.divorced)
                        marr = _parse_date(mar.married)
                        wife_id = mar.wife_id
                        wife = [indi for indi in individuals.values() if indi.id == wife_id]
                        if wife:
                            wife_death = _parse_date(wife[0].death)
                        
                else:
                    ind_husb = individuals.get(husband)
                    line_num = find_ged_line("INDI", husband, None, ind_husb.ged_line_start, ind_husb.ged_line_end) #or ind_husb.ged_line_start
                    out.append(ErrorAnomaly(
                        error_or_anomaly='ANOMALY',
                        indi_or_fam = 'INDIVIDUAL',
                        user_story_id = 'US11',
                        gedcom_line = line_num,
                        indi_or_fam_id = husband,
                        message= f'{husband} engaged in Bigamy in families {family1} and {mar.id}'
                        )
                    )
    # check if each spouse occurs more than once
    for wife in set(wifes):
        count = wifes.count(wife)

        if count > 1:
            temp = [fam for fam in married.values() if fam.wife_id == wife]
            temp = sorted(
                [fam for fam in temp if fam.married not in ('NA','',None)],
            key = lambda f: _parse_date(f.married),
            )
            
            div = _parse_date(temp[0].divorced)
            marr = _parse_date(temp[0].married)
            family1 = temp[0].id
            husband_id = temp[0].husband_id
            husband_death = None

            husband = [indi for indi in individuals.values() if indi.id == husband_id]
            if husband:
                husband_death = _parse_date(husband[0].death)

            # for each later marriage
            for mar in temp[1:]:
                next_marr = _parse_date(mar.married)

                # check if divorce, and prior to next marraige
                if div:
                    if (div < next_marr):

                        # next marriage is the valid marriage
                        div = _parse_date(mar.divorced)
                        marr = _parse_date(mar.married)
                        husband_id = mar.husband_id
                        husband = [indi for indi in individuals.values() if indi.id == husband_id]
                        if husband:
                            husband_death = _parse_date(husband[0].death)
                        continue

                # check if husbands death, and prior to next marraige
                elif husband and husband_death is not None:
                    if (husband_death < next_marr):

                        # next marraige if the valid marriage
                        div = _parse_date(mar.divorced)
                        marr = _parse_date(mar.married)
                        husband_id = mar.husband_id
                        continue
                        
                else:
                    ind_wife = individuals.get(wife)
                    line_num = find_ged_line("INDI", wife, None, ind_wife.ged_line_start, ind_wife.ged_line_end) #or ind_wife.ged_line_start
                    out.append(ErrorAnomaly(
                        error_or_anomaly='ANOMALY',
                        indi_or_fam = 'INDIVIDUAL',
                        user_story_id = 'US11',
                        gedcom_line = line_num,
                        indi_or_fam_id = wife,
                        message= f'{wife} engaged in Bigamy in families {family1} and {mar.id}'
                        )
                    )
    return out

def validate_us02_death_before_marriage(individuals: Dict[str, Individual], families: Dict[str, Family]):
    out: List[ErrorAnomaly] = []
    for family in families.values():
        if(family and family.married != 'NA' and family.husband_id and family.wife_id):
            marriageDate = _parse_date(family.married)
            husband = individuals.get(family.husband_id)
            wife = individuals.get(family.wife_id)
            if(husband):
                husbandBirthday = _parse_date(husband.birthday)
                if(husbandBirthday and _compute_age(husbandBirthday, marriageDate) < 0):
                    line_num = find_ged_line("DATE", family.married, "MARR", family.ged_line_start, family.ged_line_end) #or family.ged_line_start
                    error = ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam = 'FAMILY',
                    user_story_id = 'US02',
                    gedcom_line = line_num,
                    indi_or_fam_id = family.id,
                    message= f'Husband {husband.name}\'s birth date {husbandBirthday} occurs after marriage date {marriageDate}'
                    )
                    out.append(error)
            if(wife):
                wifeBirthday = _parse_date(wife.birthday)
                if(wifeBirthday and _compute_age(wifeBirthday, marriageDate) < 0):
                    line_num = find_ged_line("DATE", family.married, "MARR", family.ged_line_start, family.ged_line_end) #or family.ged_line_start
                    error = ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam = 'FAMILY',
                    user_story_id = 'US02',
                    gedcom_line = line_num,
                    indi_or_fam_id = family.id,
                    message= f'Wife {wife.name}\'s birth date {wifeBirthday} occurs after marriage date {marriageDate}'
                    )
                    out.append(error)
    return out

def validate_us03_death_before_birth(individuals: Dict[str, Individual]):
    out: List[ErrorAnomaly] = []
    for person in individuals.values():
        if(person.birthday and person.death and  person.death != 'NA'):
            birthday = _parse_date(person.birthday)
            death = _parse_date(person.death)
            if(birthday and _compute_age(birthday, death) < 0):
                line_num = find_ged_line("DATE", person.birthday, "BIRT", person.ged_line_start, person.ged_line_end) #or person.ged_line_start
                error = ErrorAnomaly(
                error_or_anomaly='ERROR',
                indi_or_fam = 'INDIVIDUAL',
                user_story_id = 'US03',
                gedcom_line = line_num,
                indi_or_fam_id = person.id,
                message= f'{person.name}\'s birthday {birthday} occurs after death date {death}'
                )
                out.append(error)
    return out

def validate_us12_parents_not_too_old(individuals: Dict[str, Individual], families: Dict[str, Family]):
    out: List[ErrorAnomaly] = []
    for family in families.values():
        if family.husband_id and family.wife_id:
            #Get the youngest child
            latest = _parse_date("1 JAN 1800")
            for child in family.children:
                current = individuals.get(child)
                if current:
                    currentBirthday = _parse_date(current.birthday)
                    if type(latest) == type(currentBirthday) and _compute_age(latest, currentBirthday) > 0:
                        latest = currentBirthday

            husband = individuals.get(family.husband_id)
            if husband:
                husbandBirthday = _parse_date(husband.birthday)
                if husbandBirthday and type(husbandBirthday) == type(latest) and _compute_age(husbandBirthday, latest) >= 80:
                    line_num = find_ged_line("HUSB", family.husband_id, None, family.ged_line_start, family.ged_line_end) #or family.ged_line_start
                    error = ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam = 'FAMILY',
                    user_story_id = 'US12',
                    gedcom_line = line_num,
                    indi_or_fam_id = family.id,
                    message= f'{husband.name} is at least 80 years older then their children'
                    )
                    out.append(error)

            wife = individuals.get(family.wife_id)
            if wife:
                wifeBirthday = _parse_date(wife.birthday)
                if wifeBirthday and type(wifeBirthday) == type(latest) and _compute_age(wifeBirthday, latest) >= 60:
                    line_num = find_ged_line("WIFE", family.wife_id, None, family.ged_line_start, family.ged_line_end) #or family.ged_line_start
                    error = ErrorAnomaly(
                    error_or_anomaly='ERROR',
                    indi_or_fam = 'FAMILY',
                    user_story_id = 'US12',
                    gedcom_line = line_num,
                    indi_or_fam_id = family.id,
                    message= f'{wife.name} is at least 60 years older then their children'
                    )
                    out.append(error)
    return out
                
def validate_us13_siblings_spacing(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    """
    US13: Birth dates of siblings should be more than 8 months apart or less than 2 days apart.
    Violation iff day_diff > 2 AND month_diff < 8.
    """
    out: List[ErrorAnomaly] = []
    for fam in families.values():
        kids = []
        for cid in fam.children:
            p = individuals.get(cid)
            if not p:
                continue
            dob = _parse_date(p.birthday)
            if dob:
                kids.append((p, dob))

        n = len(kids)
        for i in range(n):
            for j in range(i + 1, n):
                (pi, di), (pj, dj) = kids[i], kids[j]
                if di > dj:
                    (pi, di), (pj, dj) = (pj, dj), (pi, di)

                day_diff = (dj - di).days
                rel = relativedelta(dj, di)
                month_diff = rel.years * 12 + rel.months

                if day_diff > 2 and month_diff < 8:
                    line_num = find_ged_line("DATE", pi.birthday, "BIRT", pi.ged_line_start, pi.ged_line_end) #or pi.ged_line_start
                    out.append(ErrorAnomaly(
                        error_or_anomaly="ERROR",
                        indi_or_fam="FAMILY",
                        user_story_id="US13",
                        gedcom_line=line_num,
                        indi_or_fam_id=fam.id,
                        message=(f"Siblings {pi.id} ({pi.name}, {di}) and "
                                 f"{pj.id} ({pj.name}, {dj}) too close in age")
                    ))
    return out

def validate_us17_marriage_to_descendants(families: Dict[str, Family]):
    out: List[ErrorAnomaly] = []

    # for each family
    for fam in families.values():
        
        # if there are children
        if fam.children:

            # for each child
            for child in fam.children:

                # check for their marriages
                marriages = [f for f in families.values() if ((f.husband_id == child) or (f.wife_id == child))]

                # for each childs marriages
                for mar in marriages:

                    # if the wife id is the mom, or the husband id is the dad, raise the anomaly
                    if (mar.wife_id == fam.wife_id) or (mar.husband_id == fam.husband_id):
                        
                        # get the parent for the violation
                        parent = mar.wife_id if mar.wife_id == fam.wife_id else mar.husband_id

                        # get the line number if global variable GED_LINES exists
                        if GED_LINES:
                            line_num = find_ged_line("FAM", mar.id, None, mar.ged_line_start, mar.ged_line_end) #or fam.ged_line_start
                        else:
                            line_num = None

                        out.append(ErrorAnomaly(
                        error_or_anomaly='ANOMALY',
                        indi_or_fam = 'FAMILY',
                        user_story_id = 'US17',
                        gedcom_line = line_num,
                        indi_or_fam_id = mar.id,
                        message= f'descendant {child} married to parent {parent} (US17).'
                        )
                    )
    return out

def validate_us18_siblings_not_marry(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    """
    US18: Siblings should not marry one another.
    If spouses share any parent family (intersection of their FAMC sets), flag an error.
    """
    out: List[ErrorAnomaly] = []
    for fam in families.values():
        h = individuals.get(fam.husband_id) if fam.husband_id else None
        w = individuals.get(fam.wife_id) if fam.wife_id else None
        if not h or not w:
            continue

        h_par = set(h.child or [])
        w_par = set(w.child or [])
        if h_par and w_par and h_par.intersection(w_par):
            line_num = (find_ged_line("DATE", fam.married, "MARR", fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
                        or fam.ged_line_start or "TBD")
            out.append(ErrorAnomaly(
                error_or_anomaly="ERROR",
                indi_or_fam="FAMILY",
                user_story_id="US18",
                gedcom_line=line_num,
                indi_or_fam_id=fam.id,
                message=f"Spouses {h.id} ({h.name}) and {w.id} ({w.name}) are siblings"
            ))
    return out

def validate_us19_first_cousins_marry(families: Dict[str, Family]):
    out: List[ErrorAnomaly] = []

    # for each family
    for fam in families.values():
        
        # gather the spouses
        spouses = [fam.husband_id, fam.wife_id]

        # for each spouse
        for spouse in spouses:
            
            # get all their other marriages
            other_marriages = [d for d in families.values() if ((spouse == d.husband_id) or (spouse == d.wife_id))]

            # get their parents
            spouse_fam = [f for f in families.values() if spouse in f.children]

            if len(spouse_fam) > 0:
                # get the spouses parents
                spouse_parents = [spouse_fam[0].husband_id, spouse_fam[0].wife_id]
            else:
                spouse_parents = []
            
            # for each parent
            for x in spouse_parents:

                # get the parents families, to get their siblings
                fam1 = [g for g in families.values() if x in g.children]
                
                # collect the parents' siblings
                for i in fam1:
                    siblings = i.children
                    siblings = [i for i in siblings if i != x]

                    # for each of the parents' siblings, get their children (cousins)
                    for j in siblings:
                        fam2 = [h for h in families.values() if (h.husband_id == j) or (h.wife_id == j)]

                        for k in fam2:
                            cousins = k.children
                            cousins = [c for c in cousins if c != spouse]

                            # check if the spouse had any marriage to their cousins
                            for mar in other_marriages:

                                if ((mar.wife_id in cousins) or (mar.husband_id in cousins)):

                                    cousin = mar.wife_id if mar.wife_id in cousins else mar.husband_id

                                    # get the line number if global variable GED_LINES exists
                                    if GED_LINES:
                                        line_num = find_ged_line("FAM", mar.id, None, mar.ged_line_start, mar.ged_line_end) #or ind_wife.ged_line_start
                                    else:
                                        line_num = None
                                    
                                    # avoid duplicate errors
                                    matches = [i for i in out if i.message == f'{spouse} married to cousin {cousin} in family {mar.id} (US19).']
                                    if len(matches) == 0:
                                        out.append(ErrorAnomaly(
                                            error_or_anomaly='ANOMALY',
                                            indi_or_fam = 'FAMILY',
                                            user_story_id = 'US19',
                                            gedcom_line = line_num,
                                            indi_or_fam_id = spouse,
                                            message= f'{spouse} married to cousin {cousin} in family {mar.id} (US19).'
                                            )
                    )
                                    
    return out

def validate_us15_fewer_than_15_siblings(families: Dict[str, Family]):
    out: List[ErrorAnomaly] = []
    for family in families.values():
        if len(family.children) >= 15:
            line_num = find_ged_line("FAM", family.id, None, family.ged_line_start, family.ged_line_end) #or family.ged_line_start
            error = ErrorAnomaly(
            error_or_anomaly='ERROR',
            indi_or_fam = 'FAMILY',
            user_story_id = 'US15',
            gedcom_line = line_num,
            indi_or_fam_id = family.id,
            message= f'{family.id} has 15 or more siblings in a family'
            )
            out.append(error)
    return out

def validate_us16_male_last_names(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    """
    US16: Male last names
    All male members of a family should have the same last name, if not then flag an anomaly.
    """
    out: List[ErrorAnomaly] = []
    for fam in families.values():
        h = individuals.get(fam.husband_id) if fam.husband_id else None
        if not h:
            continue
        name_parts = h.name.split()
        if len(name_parts) != 2:
            continue
        last_name = name_parts[-1]
        for child in fam.children:
            ch = individuals.get(child)
            if ch.sex != 'M':
                continue
            name_parts = ch.name.split()
            if len(name_parts) != 2:
                continue
            child_last_name = name_parts[-1]
            if child_last_name != last_name:
                line_num = find_ged_line("CHIL", ch.id, None, fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
                out.append(ErrorAnomaly(
                    error_or_anomaly="ANOMALY",
                    indi_or_fam="FAMILY",
                    user_story_id="US16",
                    gedcom_line=line_num,
                    indi_or_fam_id=fam.id,
                    message=f"Male member {ch.id} ({ch.name}) does not share the same last name {last_name} in the family"
                ))
    return out

def validate_us14_less_than_five_births(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    """
    US14: Multiple births <= 5
    No more than five siblings should be born at the same time
    """
    out: List[ErrorAnomaly] = []
    for fam in families.values():
        child_count = len(fam.children)
        if child_count < 5:
            continue
        birth_dates = []
        for child in fam.children:
            ch = individuals.get(child)
            birth_dates.append(ch.birthday)
        if all(d is None or d == "" for d in birth_dates):
            continue
        if len(set(birth_dates)) == 1:
            line_num = find_ged_line("FAM", fam.id, None, fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
            out.append(ErrorAnomaly(
                error_or_anomaly="ANOMALY",
                indi_or_fam="FAMILY",
                user_story_id="US14",
                gedcom_line=line_num,
                indi_or_fam_id=fam.id,
                message=f"5 or more sibling born on the same date {birth_dates[0]}"
            ))
    return out

def validate_us20_aunts_and_uncles(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    """
    US20: Aunts and uncles
    Aunts and uncles should not marry their nieces or nephews 24
    """
    out: List[ErrorAnomaly] = []
    for fam in families.values():
        h = individuals.get(fam.husband_id) if fam.husband_id else None
        w = individuals.get(fam.wife_id) if fam.wife_id else None
        if not h or not w:
            continue
        if len(h.child) > 0:
            for h_families in h.child:
                h_fam = families.get(h_families)
                h_father = individuals.get(h_fam.husband_id)
                h_mother = individuals.get(h_fam.wife_id)
                if h_father and len(h_father.child) > 0:
                    for h_father_families in h_father.child:
                        h_father_fam = families.get(h_father_families)
                        if h_father_fam.children.__contains__(w.id):
                            line_num = find_ged_line("WIFE", w.id, None, fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
                            out.append(ErrorAnomaly(
                                error_or_anomaly="ANOMALY",
                                indi_or_fam="FAMILY",
                                user_story_id="US20",
                                gedcom_line=line_num,
                                indi_or_fam_id=fam.id,
                                message=f"Spouse {w.name} is an aunt to {h.name}"
                            ))
                if h_mother and len(h_mother.child) > 0:
                    for h_mother_families in h_mother.child:
                        h_mother_fam = families.get(h_mother_families)
                        if h_mother_fam.children.__contains__(w.id):
                            line_num = find_ged_line("WIFE", w.id, None, fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
                            out.append(ErrorAnomaly(
                                error_or_anomaly="ANOMALY",
                                indi_or_fam="FAMILY",
                                user_story_id="US20",
                                gedcom_line=line_num,
                                indi_or_fam_id=fam.id,
                                message=f"Spouse {w.name} is an aunt to {h.name}"
                            ))
        if len(w.child) > 0:
            for w_families in w.child:
                w_fam = families.get(w_families)
                w_father = individuals.get(w_fam.husband_id)
                w_mother = individuals.get(w_fam.wife_id)
                if w_father and len(w_father.child) > 0:
                    for w_father_families in w_father.child:
                        w_father_fam = families.get(w_father_families)
                        if w_father_fam.children.__contains__(h.id):
                            line_num = find_ged_line("HUSB", h.id, None, fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
                            out.append(ErrorAnomaly(
                                error_or_anomaly="ANOMALY",
                                indi_or_fam="FAMILY",
                                user_story_id="US20",
                                gedcom_line=line_num,
                                indi_or_fam_id=fam.id,
                                message=f"Spouse {h.name} is an uncle to {w.name}"
                            ))
                if w_mother and len(w_mother.child) > 0:
                    for w_mother_families in w_mother.child:
                        w_mother_fam = families.get(w_mother_families)
                        if w_mother_fam.children.__contains__(h.id):
                            line_num = find_ged_line("HUSB", h.id, None, fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
                            out.append(ErrorAnomaly(
                                error_or_anomaly="ANOMALY",
                                indi_or_fam="FAMILY",
                                user_story_id="US20",
                                gedcom_line=line_num,
                                indi_or_fam_id=fam.id,
                                message=f"Spouse {h.name} is an aunt to {w.name}"
                            ))
    return out

def validate_us23_unique_name_and_birthday(individuals: Dict[str, Individual]) -> List[ErrorAnomaly]:
    """
    US23: Unique name and birth date.
    Build a map keyed by (normalized name, birthday string). If a key has >1 person,
    add ONE anomaly listing all conflicting IDs for that (name, birthday).
    """
    out: List[ErrorAnomaly] = []

    idx: Dict[Tuple[str, str], List[Individual]] = {}
    for p in individuals.values():
        name_norm = (p.name or "").strip().lower()
        bday_raw = (p.birthday or "").strip()
        if not name_norm or not bday_raw:
            continue
        idx.setdefault((name_norm, bday_raw), []).append(p)

    for (name_norm, bday_raw), people in idx.items():
        if len(people) > 1:
            first = people[0]
            line_num = find_ged_line("DATE", first.birthday, "BIRT", first.ged_line_start, first.ged_line_end) or first.ged_line_start
            ids = ", ".join(sorted([p.id for p in people], key=_id_sort_key))
            human_name = people[0].name  
            out.append(ErrorAnomaly(
                error_or_anomaly="ANOMALY",
                indi_or_fam="INDIVIDUAL",
                user_story_id="US23",
                gedcom_line=line_num,
                indi_or_fam_id=ids,
                message=f"Duplicate Name+Birthday: '{human_name}' with birth '{bday_raw}' appears for IDs [{ids}]"
            ))
    return out

def validate_us24_unique_families_by_spouses(families: Dict[str, Family]) -> List[ErrorAnomaly]:
    """No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file"""
    out: List[ErrorAnomaly] = []

    unique_fam_info = {}
    for fam_id, fam in families.items():
        husb_id = fam.husband_id
        wife_id = fam.wife_id
        marr_dt = fam.married
        fam_info = (husb_id, wife_id, marr_dt)
        if fam_info in unique_fam_info:
            unique_fam_info[fam_info].append(fam_id)
        else:
            unique_fam_info[fam_info] = [fam_id]
    for attrs, fam_ids in unique_fam_info.items():
        if len(fam_ids) > 1 and attrs[0] and attrs[1] and attrs[2] and attrs[2] != "NA":
            #add error for each fam, list other fam ids
            for fam_id in fam_ids:
                fam = families.get(fam_id)
                line_num = find_ged_line("FAM", fam_id, None, fam.ged_line_start, fam.ged_line_end)
                out.append(ErrorAnomaly(
                    error_or_anomaly="ERROR",
                    indi_or_fam="FAMILY",
                    user_story_id="US24",
                    gedcom_line=line_num,
                    indi_or_fam_id=fam.id,
                    message=f"Duplicate family with same husband ({attrs[0]}), wife ({attrs[1]}), and marriage date ({attrs[2]}) exists: {', '.join(item for item in fam_ids if item != fam_id)}"
                ))
    return out

def validate_us21_correct_gender_for_role(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    """Husband in family should be male and wife in family should be female"""
    out: List[ErrorAnomaly] = []
    for fam in families.values():
        h = individuals.get(fam.husband_id) if fam.husband_id else None
        w = individuals.get(fam.wife_id) if fam.wife_id else None
        if h and h.sex != 'M':
            line_num = find_ged_line("HUSB", h.id, None, fam.ged_line_start, fam.ged_line_end)  # or fam.ged_line_start
            out.append(ErrorAnomaly(
                error_or_anomaly="ANOMALY",
                indi_or_fam="FAMILY",
                user_story_id="US21",
                gedcom_line=str(line_num),
                indi_or_fam_id=fam.id,
                message=f"Husband {h.name} is not listed as M sex"
            ))
        if w and w.sex != 'F':
            line_num = find_ged_line("WIFE", w.id, None, fam.ged_line_start, fam.ged_line_end) #or fam.ged_line_start
            out.append(ErrorAnomaly(
                error_or_anomaly="ANOMALY",
                indi_or_fam="FAMILY",
                user_story_id="US21",
                gedcom_line=str(line_num),
                indi_or_fam_id=fam.id,
                message=f"Wife {w.name} is not listed as F sex"
            ))
    return out

def validate_us26_corresponding_entries(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    """Husband in family should be male and wife in family should be female"""
    out: List[ErrorAnomaly] = []
    for individual in individuals.values():
        if len(individual.spouse) > 0:
            for fams in individual.spouse:
                indi_fam = families.get(fams)
                h = indi_fam.husband_id == individual.id
                w = indi_fam.wife_id == individual.id
                if h or w:
                    continue
                line_num = find_ged_line("FAMS", fams, None, individual.ged_line_start, individual.ged_line_end)
                out.append(ErrorAnomaly(
                    error_or_anomaly="ERROR",
                    indi_or_fam="INDIVIDUAL",
                    user_story_id="US26",
                    gedcom_line=str(line_num),
                    indi_or_fam_id=individual.id,
                    message=f"Individual {individual.name} FAMS does not have a corresponding entry HUSB/WIFE in Family {indi_fam.id}"
                ))
        if len(individual.child) > 0:
            for famc in individual.child:
                indi_fam = families.get(famc)
                h = indi_fam.husband_id == individual.id
                w = indi_fam.wife_id == individual.id
                if h or w:
                    continue
                line_num = find_ged_line("FAMC", famc, None, individual.ged_line_start, individual.ged_line_end)
                out.append(ErrorAnomaly(
                    error_or_anomaly="ERROR",
                    indi_or_fam="INDIVIDUAL",
                    user_story_id="US26",
                    gedcom_line=str(line_num),
                    indi_or_fam_id=individual.id,
                    message=f"Individual {individual.name} FAMC does not have a corresponding entry CHIL in Family {indi_fam.id}"
                ))
    for family in families.values():
        if family.husband_id != '':
            h = individuals.get(family.husband_id)
            if not h:
                line_num = find_ged_line("HUSB", family.husband_id, None, family.ged_line_start, family.ged_line_end)
                out.append(ErrorAnomaly(
                    error_or_anomaly="ERROR",
                    indi_or_fam="INDIVIDUAL",
                    user_story_id="US26",
                    gedcom_line=str(line_num),
                    indi_or_fam_id=family.id,
                    message=f"Family {family.id} HUSB does not have a corresponding entry Individual {family.husband_id}"
                ))
            else:
                if not h.spouse.__contains__(family.id):
                    line_num = find_ged_line("HUSB", family.husband_id, None, family.ged_line_start, family.ged_line_end)
                    out.append(ErrorAnomaly(
                        error_or_anomaly="ERROR",
                        indi_or_fam="INDIVIDUAL",
                        user_story_id="US26",
                        gedcom_line=str(line_num),
                        indi_or_fam_id=family.id,
                        message=f"Family {family.id} HUSB does not have a corresponding entry FAMS in Individual {h.id}"
                ))
        if family.wife_id != '':
            w = individuals.get(family.wife_id)
            if not w:
                line_num = find_ged_line("WIFE", family.wife_id, None, family.ged_line_start, family.ged_line_end)
                out.append(ErrorAnomaly(
                    error_or_anomaly="ERROR",
                    indi_or_fam="INDIVIDUAL",
                    user_story_id="US26",
                    gedcom_line=str(line_num),
                    indi_or_fam_id=family.id,
                    message=f"Family {family.id} WIFE does not have a corresponding entry Individual {family.wife_id}"
                ))
            else:
                if not w.spouse.__contains__(family.id):
                    line_num = find_ged_line("WIFE", family.wife_id, None, family.ged_line_start, family.ged_line_end)
                    out.append(ErrorAnomaly(
                        error_or_anomaly="ERROR",
                        indi_or_fam="INDIVIDUAL",
                        user_story_id="US26",
                        gedcom_line=str(line_num),
                        indi_or_fam_id=family.id,
                        message=f"Family {family.id} WIFE does not have a corresponding entry FAMS in Individual {w.id}"
                ))
        if len(family.children) != 0:
            for child in family.children:
                c = individuals.get(child)
                if not c:
                    line_num = find_ged_line("CHIL", child, None, family.ged_line_start, family.ged_line_end)
                    out.append(ErrorAnomaly(
                        error_or_anomaly="ERROR",
                        indi_or_fam="INDIVIDUAL",
                        user_story_id="US26",
                        gedcom_line=str(line_num),
                        indi_or_fam_id=family.id,
                        message=f"Family {family.id} CHIL does not have a corresponding entry Individual {child}"
                    ))
                else:
                    if not c.spouse.__contains__(family.id):
                        line_num = find_ged_line("CHIL", child, None, family.ged_line_start, family.ged_line_end)
                        out.append(ErrorAnomaly(
                            error_or_anomaly="ERROR",
                            indi_or_fam="INDIVIDUAL",
                            user_story_id="US26",
                            gedcom_line=str(line_num),
                            indi_or_fam_id=family.id,
                            message=f"Family {family.id} CHIL does not have a corresponding entry FAMC in Individual {c.id}"
                        ))
    return out

def validate_us22_check_duplicates(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    return ERRORS_ANOMALIES

def validate_us25_unique_first_names_in_families(individuals: Dict[str, Individual], families: Dict[str, Family],) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    for fam in families.values():

        # create a children list of name, birthdays
        children = []

        # list of children is list of their indi ids
        for c in fam.children:
            
            cd = [indi for indi in individuals.values() if indi.id == c]
            if cd:
                c_bd = cd[0].birthday
                c_n = cd[0].name

                if c_bd and c_n:
                    children.append((c_n,c_bd))

        # check for duplicates
        seen = set()
        dups = []

        for elem in children:
            if elem in seen:
                dups.append(elem)
            else:
                seen.add(elem)

        # if there are duplicates
        if len(dups) >= 1:
            for d in dups:

                # try/except for unit tests, where GED_LINES is not available
                try:
                    line_num = find_ged_line("FAM", fam.id, None, fam.ged_line_start, fam.ged_line_end)
                except:
                    line_num = None
                out.append(ErrorAnomaly(
                        error_or_anomaly="ERROR",
                        indi_or_fam="FAMILY",
                        user_story_id="US25",
                        gedcom_line=line_num,
                        indi_or_fam_id=fam.id,
                        message=f"Duplicate child {d[0]} in family {fam.id}"
                    ))
    return out

def validate_us42_reject_illegitimate_dates(individuals: Dict[str, Individual], families: Dict[str, Family],) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []

    # months with 30 days
    mos_30_days = [4, 6, 9, 11]

    # months with 31 days
    mos_31_days = [1, 3, 5, 7, 8, 10, 12]

    prev_tag, prev_value = None, None

    # function to check for leap years
    def is_leap_year(year):
        '''
        Leap year is evenly divisible by 4, unless it is also evenly divisible by 100
        Edge case: leap is evenly divisible by 400
        '''

        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return True
        else:
            return False
    
    # for each date line
    for line in GED_LINES:
        
        # store the previous level 0 tag and value
        if line.level == 0:
            prev_tag = line.tag
            prev_value = line.value

        # if the current line contains a date
        if line.tag == "DATE":

            # try to parse the date
            try:
                parsed_date = _parse_date(line.value)

                # if it exists
                if parsed_date:

                    # initialize vars for day, month, and year
                    day, month, year = None, None, None

                    # try to extract day, month, and year
                    try:
                        day = parsed_date.day
                        month = parsed_date.month
                        year = parsed_date.year

                        # check for illegitimate dates based on month and day
                        if month and day:
                            
                            if month in mos_30_days:
                                if not 0 < day <= 30:
                                    out.append(ErrorAnomaly(
                                    error_or_anomaly="ERROR",
                                    indi_or_fam= prev_tag,
                                    user_story_id="US42",
                                    gedcom_line=line.line_num,
                                    indi_or_fam_id=prev_value,
                                    message=f"Illegitimate date in line {line.line_num}"
                                ))
                                    
                            elif month in mos_31_days:
                                if not 0 < day <= 31:
                                    out.append(ErrorAnomaly(
                                    error_or_anomaly="ERROR",
                                    indi_or_fam= prev_tag,
                                    user_story_id="US42",
                                    gedcom_line=line.line_num,
                                    indi_or_fam_id=prev_value,
                                    message=f"Illegitimate date in line {line.line_num}"
                                ))

                        # when we have day, month, and year, and the month is february
                        # we need to check for leap year
                        if (day and month and year) and (month == 2):
                            flag = is_leap_year(year)

                            # match statement based on leap year flag
                            match flag:
                                case True:
                                    valid_days = 29
                                case False:
                                    valid_days = 28
                                
                            if not 0 < day < valid_days:
                                out.append(ErrorAnomaly(
                                error_or_anomaly="ERROR",
                                indi_or_fam= prev_tag,
                                user_story_id="US42",
                                gedcom_line=line.line_num,
                                indi_or_fam_id=prev_value,
                                message=f"Illegitimate date in line {line.line_num}"
                            ))
                    except:
                        continue
                
                # python datetime automatically rejects invalid dates based on # of days in the month and leap years, with value error
                # our _parse_date function returns None for these
                else: 
                    out.append(ErrorAnomaly(
                    error_or_anomaly="ERROR",
                    indi_or_fam= prev_tag,
                    user_story_id="US42",
                    gedcom_line=line.line_num,
                    indi_or_fam_id=prev_value,
                    message=f"Illegitimate date in line {line.line_num}"
                ))
            except:
                continue
            
    return out

def validate_us33_list_orphans(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    for family in families.values():
        husband = individuals.get(family.husband_id)
        wife = individuals.get(family.wife_id) 
        if(husband and wife and husband.death and wife.death and husband.death != "NA" and wife.death != "NA"):
            for child in family.children:
                orphan = individuals.get(child)
                if(orphan and orphan.age and orphan.age < 18):
                    line_num = find_ged_line("FAM", family.id, "DATE", family.ged_line_start, family.ged_line_end)
                    out.append(ErrorAnomaly(
                    error_or_anomaly="ANOMALY",
                    indi_or_fam= "FAMILY",
                    user_story_id="US33",
                    gedcom_line= line_num,
                    indi_or_fam_id=family.id,
                    message=f"Individual {orphan.id} {orphan.name} is an Orphan"
                    ))
            
    return out

def validate_us38_upcoming_birthdays(individuals: Dict[str, Individual]) -> List[ErrorAnomaly]:
 
    out: List[ErrorAnomaly] = []
    today = date.today()
    for indi in individuals.values():
        if not indi.alive or not indi.birthday:
            continue
        bday = _parse_date(indi.birthday)
        if not bday:
            continue

        next_bday = date(today.year, bday.month, bday.day)
        if next_bday < today:
            next_bday = date(today.year + 1, bday.month, bday.day)

        diff = (next_bday - today).days
        if 0 <= diff <= 30:
            try:
                line_num = find_ged_line("DATE", indi.birthday, "BIRT", indi.ged_line_start, indi.ged_line_end)
            except Exception:
                line_num = 0
            out.append(ErrorAnomaly(
                error_or_anomaly="INFO",
                indi_or_fam="INDIVIDUAL",
                user_story_id="US38",
                gedcom_line=line_num,
                indi_or_fam_id=indi.id,
                message=f"Upcoming birthday for {indi.name} ({indi.id}) on {bday.strftime('%d %b')} ({diff} days away)"
            ))
    return out

def validate_us39_upcoming_anniversaries(families: Dict[str, Family], individuals: Dict[str, Individual]) -> List[ErrorAnomaly]:

    out: List[ErrorAnomaly] = []
    today = date.today()

    for fam in families.values():
        if fam.married in ("NA", "", None):
            continue
        mdate = _parse_date(fam.married)
        if not mdate:
            continue

        h = individuals.get(fam.husband_id)
        w = individuals.get(fam.wife_id)
        if not h or not w or not h.alive or not w.alive:
            continue

        next_anniv = date(today.year, mdate.month, mdate.day)
        if next_anniv < today:
            next_anniv = date(today.year + 1, mdate.month, mdate.day)

        diff = (next_anniv - today).days
        if 0 <= diff <= 30:
            try:
                line_num = find_ged_line("DATE", fam.married, "MARR", fam.ged_line_start, fam.ged_line_end)
            except Exception:
                line_num = 0

            out.append(ErrorAnomaly(
                error_or_anomaly="INFO",
                indi_or_fam="FAMILY",
                user_story_id="US39",
                gedcom_line=line_num,
                indi_or_fam_id=fam.id,
                message=f"Upcoming anniversary for {h.name} and {w.name} ({fam.id}) on {mdate.strftime('%d %b')} ({diff} days away)"
            ))
    return out

def us35_list_recent_births(individuals: Dict[str, Individual]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    today = date.today()
    for indi in individuals.values():
        if indi.birthday:
            bd = indi.birthday
            try:
                bdp = _parse_date(bd)
                diff = today - bdp
                diff = diff.days
                if diff <= 30:
                    out.append(ErrorAnomaly(
                    error_or_anomaly="INFO",
                    indi_or_fam= "INDIVIDUAL",
                    user_story_id="US35",
                    gedcom_line=indi.ged_line_start,
                    indi_or_fam_id=indi.id,
                    message=f"Individual {indi.id} born in the last 30 days."))
            except:
                continue  
    return out

def us36_list_recent_deaths(individuals: Dict[str, Individual]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    today = date.today()
    for indi in individuals.values():
        if indi.death:
            dd = indi.death
            try:
                ddp = _parse_date(dd)
                diff = today - ddp
                diff = diff.days
                if diff <= 30:
                    out.append(ErrorAnomaly(
                    error_or_anomaly="INFO",
                    indi_or_fam= "INDIVIDUAL",
                    user_story_id="US36",
                    gedcom_line=indi.ged_line_start,
                    indi_or_fam_id=indi.id,
                    message=f"Individual {indi.id} died in the last 30 days."))
            except:
                continue  
    return out

def us37_list_recent_survivors(individuals: Dict[str, Individual], families: Dict[str, Family]) -> List[ErrorAnomaly]:
    out: List[ErrorAnomaly] = []
    today = date.today()
    for indi in individuals.values():
        if indi.death:
            dd = indi.death
            try:
                ddp = _parse_date(dd)
                diff = today - ddp
                diff = diff.days
                if diff <= 30:
                    fams = [fam for fam in families.values() if ((fam.husband_id == indi.id) or (fam.wife_id == indi.id))]
                    for fam in fams:

                        # store the indi ids of fam members
                        fam_mems = []
                        
                        # add the spouse to fam member list
                        if fam.husband_id == indi.id:
                            fam_mems.append(fam.wife_id)
                        else:
                            fam_mems.append(fam.husband_id)

                        # add the children to fam member list
                        children = fam.children
                        for child in children:
                            fam_mems.append(child)

                        # final loop - go through each family member and check if alive
                        for memb in fam_mems:
                            temp_indi = individuals.get(memb)
                            if temp_indi.death == 'NA':
                                out.append(ErrorAnomaly(
                                error_or_anomaly="INFO",
                                indi_or_fam= "INDIVIDUAL",
                                user_story_id="US37",
                                gedcom_line=indi.ged_line_start,
                                indi_or_fam_id=temp_indi.id,
                                message=f"Individual {temp_indi.id} is a survivior of {indi.id} who died in the last 30 days."))
            except:
                continue  
    return out

def find_ged_line(tag: str, value: str, prev_tag: str, start:int, end:int) -> int:
    if not tag and not value: 
        return None
    
    min_line = min(GED_LINES, key=lambda gl: gl.line_num).line_num or 0
    max_line = max(GED_LINES, key=lambda gl: gl.line_num).line_num or 0

    if not start:
        start = min_line
    if not end:
        end = max_line
    if start > end:
        return None
    
    ged_lines = [g for g in GED_LINES 
                 if start <= g.line_num <= end 
                    and g.tag == tag 
                    and g.value.replace("@", "") == value 
                    and (not prev_tag 
                            or (min_line < g.line_num < max_line
                                and prev_tag == next((gp for gp in GED_LINES if gp.line_num == g.line_num - 1), None).tag))]
    if ged_lines:
        return ged_lines[0].line_num #First found instance
    else:
        return None

def main():
    #path = "data/TestData.ged"
    path = prompt_user_for_input()
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
    ERRORS_ANOMALIES.extend(validate_us10_marriage_after_14(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us11_no_bigamy(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us02_death_before_marriage(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us03_death_before_birth(individuals))
    ERRORS_ANOMALIES.extend(validate_us12_parents_not_too_old(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us13_siblings_spacing(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us18_siblings_not_marry(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us15_fewer_than_15_siblings(families))
    ERRORS_ANOMALIES.extend(validate_us16_male_last_names(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us14_less_than_five_births(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us20_aunts_and_uncles(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us17_marriage_to_descendants(families))
    ERRORS_ANOMALIES.extend(validate_us19_first_cousins_marry(families))
    ERRORS_ANOMALIES.extend(validate_us23_unique_name_and_birthday(individuals)) 
    ERRORS_ANOMALIES.extend(validate_us24_unique_families_by_spouses(families))
    ERRORS_ANOMALIES.extend(validate_us21_correct_gender_for_role(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us26_corresponding_entries(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us25_unique_first_names_in_families(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us42_reject_illegitimate_dates(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us33_list_orphans(individuals, families))
    ERRORS_ANOMALIES.extend(validate_us38_upcoming_birthdays(individuals))
    ERRORS_ANOMALIES.extend(validate_us39_upcoming_anniversaries(families, individuals))
    ERRORS_ANOMALIES.extend(us35_list_recent_births(individuals))
    ERRORS_ANOMALIES.extend(us36_list_recent_deaths(individuals))
    ERRORS_ANOMALIES.extend(us37_list_recent_survivors(individuals, families))


    sorted_by_user_story = sorted(ERRORS_ANOMALIES, key=lambda sort_key: sort_key.user_story_id)
    i_table = individual_prettytable(individuals)
    f_table = family_prettytable(families, individuals)  
    e_table = error_anomaly_prettytable(sorted_by_user_story)

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

