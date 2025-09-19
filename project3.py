"""
Course: 2025F SSW 555–WN Agile Methods for Software Development
Professor: Dr. Richard Ens
Group 2 GEDCOM Program
GitHub: cs555-gedcom-Group2
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
import re
import sys

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


def _parse_date(s: str) -> Optional[date]:
    """Parse GEDCOM-like date 'D MON YYYY' -> date or None."""
    try:
        return datetime.strptime(s.strip(), "%d %b %Y").date()
    except Exception:
        return None

def _compute_age(birth: Optional[date], end: Optional[date] = None):
    if not birth:
        return "NA"
    end = end or date.today()
    years = end.year - birth.year
    if (end.month, end.day) < (birth.month, birth.day):
        years -= 1
    return years

def _id_sort_key(x: str) -> int:
    m = re.search(r"\d+", x or "")
    return int(m.group()) if m else 0


VALID_TAGS = {
    "HEAD","TRLR","NOTE","INDI","FAM","NAME","SEX","BIRT","DEAT","DATE",
    "FAMC","FAMS","HUSB","WIFE","CHIL","MARR","DIV"
}

def parse_individuals_family_data(ged_file) -> Tuple[Dict[str, Individual], Dict[str, Family]]:
    individuals: Dict[str, Individual] = {}
    families: Dict[str, Family] = {}

    current_person: Optional[Individual] = None
    current_family: Optional[Family] = None
    pending_date_for: Optional[str] = None  

    for raw in ged_file:
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
            if len(parts) >= 3 and parts[1].startswith("@") and parts[2] in {"INDI", "FAM"}:
                tag = parts[2]
                args = parts[1]               
            else:
                tag = parts[1]
                args = " ".join(parts[2:]) if len(parts) > 2 else ""

        if tag not in VALID_TAGS:
            pending_date_for = None
            continue

        if level == 0:
            pending_date_for = None
            current_person = None
            current_family = None
            if tag == "INDI":
                pid = args                             
                current_person = individuals.get(pid) or Individual(id=pid)
                individuals[pid] = current_person
            elif tag == "FAM":
                fid = args                              
                current_family = families.get(fid) or Family(id=fid)
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
                pending_date_for = None
            elif tag == "FAMC" and level == 1:
                fam_id = args.strip()
                if fam_id:
                    current_person.child.append(fam_id)
            elif tag == "FAMS" and level == 1:
                fam_id = args.strip()
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
                current_family.husband_id = args.strip()
            elif tag == "WIFE" and level == 1:
                current_family.wife_id = args.strip()
            elif tag == "CHIL" and level == 1:
                cid = args.strip()
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

def main():
    path = "data/TestData.ged"
    if len(sys.argv) > 1:
        path = sys.argv[1]

    try:
        with open(path, "r", encoding="utf-8") as fh:
            individuals, families = parse_individuals_family_data(fh)
    except Exception as e:
        print("Cannot open GEDCOM file:", path)
        print(e)
        sys.exit(1)

    i_table = individual_prettytable(individuals)
    f_table = family_prettytable(families)

    print("Individuals")
    print(i_table)
    print("\nFamilies")
    print(f_table)

    with open("run_output.txt", "w", encoding="utf-8") as out:
        out.write("Individuals\n")
        out.write(str(i_table))
        out.write("\n\nFamilies\n")
        out.write(str(f_table))
        out.write("\n")

if __name__ == "__main__":
    main()

