"""
Course: 2025F SSW 555-WN Agile Methods for Software Development
Professor: Dr. Richard Ens
Group 2 GEDCOM Program
GitHub: cs555-gedcom-Group2
"""

""" 
TODO 1: Need to sort the returning dictionaries from the parse_individuals_family_data function
TODO 2: Need to calculate the age of individuals
TODO 3: Aren't we supposed to keep the code from week 2 in here?
"""

from prettytable import PrettyTable

def parse_individuals_family_data(ged_file):
     """
     This function will parse the GEDCOM file and return dictionaries with individuals and families data.
     :param ged_file: GEDCOM file
     :return: individuals dictionary and families dictionary
     """
     individuals = {}
     families = {}
     reading_individual = False
     reading_family = False

     for line in ged_file:
          split_line = line.strip().split()

          if len(split_line) == 3 and (split_line[2] == 'FAM' or split_line[2] == 'INDI'):
               tag = split_line[2]
          else:
               tag = split_line[1]

          if tag == "INDI":
               id = split_line[1].strip("@")
               individuals[id] = {
                    "id": id,
                    "name": "",
                    "sex": "",
                    "birthday": "",
                    "age": 0,
                    "alive": True,
                    "death": "N/A",
                    "child": [],
                    "spouse": []
               }
               reading_individual = True
               reading_family = False
          elif tag == "FAM":
               id = split_line[1].strip("@")
               families[id] = {
                    "id": id,
                    "married": "",
                    "divorced": "NA",
                    "husband_id": "",
                    "husband_name": "",
                    "wife_id": "",
                    "wife_name": "",
                    "children": []
               }
               reading_individual = False
               reading_family = True
          elif reading_individual:
               if tag == "NAME":
                    individuals[id]["name"] = split_line[2] + " " + split_line[3]
               elif tag == "SEX":
                    individuals[id]["sex"] = split_line[2]
               elif tag == "BIRT":
                    birth_date_line = next(gedFile).strip().split()
                    individuals[id]["birthday"] = (','.join(str(x) for x in birth_date_line[2:]))
               elif tag == "DEAT":
                    death_date_line = next(gedFile).strip().split()
                    individuals[id]["death"] = (','.join(str(x) for x in death_date_line[2:]))
                    individuals[id]["alive"] = False
          elif reading_family:
               if tag == "HUSB":
                    husband_id = split_line[2].strip("@")
                    families[id]["husband_id"] = husband_id
                    families[id]["husband_name"] = individuals[husband_id]["name"]
                    individuals[husband_id]["spouse"].append(id)
               elif tag == "WIFE":
                    wife_id = split_line[2].strip("@")
                    families[id]["wife_id"] = wife_id
                    families[id]["wife_name"] = individuals[wife_id]["name"]
                    individuals[wife_id]["spouse"].append(id)
               elif tag == "CHIL":
                    child_id = split_line[2].strip("@")
                    families[id]["children"].append(child_id)
                    individuals[child_id]["child"].append(id)
               elif tag == "MARR":
                    marriage_date_line = next(gedFile).strip().split()
                    families[id]["married"] = (','.join(str(x) for x in marriage_date_line[2:]))
               elif tag == "DIV":
                    divorce_date_line = next(gedFile).strip().split()
                    families[id]["divorced"] = (','.join(str(x) for x in divorce_date_line[2:]))
     return individuals, families

def individual_prettytable(individual_data):
     """
     This function will take a dictionary of individuals data and return a formatted PrettyTable table.
     :param individual_data: dictionary of individuals with data
     :return: table formatted with individuals data
     """
     print("Individuals")
     table = PrettyTable()
     table.field_names = ['ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse']
     for val in individual_data.values():
          table.add_row([val['id'], val['name'], val['sex'], val['birthday'], val['age'], val['alive'], val['death'], val['child'], val['spouse']])

     return table

def family_prettytable(family_data):
     """
     This function will take a dictionary of families data and return a formatted PrettyTable table.
     :param family_data: dictionary of individuals with data
     :return: table formatted with families data
     """
     print("Families")
     table = PrettyTable()
     table.field_names = ['ID', 'Married', 'Divorced', 'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children']
     for val in family_data.values():
          table.add_row([val['id'], val['married'], val['divorced'], val['husband_id'], val['husband_name'], val['wife_id'], val['wife_name'], val['children']])

     return table

#Main

try:
     gedFile = open("data/TestData.ged")
except Exception as e:
     print("Cannot open file. Please try again.")
     print(e)
     exit()

individuals_data, families_data = parse_individuals_family_data(gedFile)

gedFile.close()

print(individual_prettytable(individuals_data))

print(family_prettytable(families_data))