import sys
from prettytable import PrettyTable
individuals = {}
families = {}

try:
     gedFile = open("data/My-Family-3-Sep-2025-122409406.ged")
except:
     print("Cannot open file. Please try again.")
     exit()

readingIndividual = False
readingFamily = False
for line in gedFile:
     splitLine = line.strip().split()

     level = splitLine[0]
     if(len(splitLine) == 3 and (splitLine[2] == 'FAM' or splitLine[2] == 'INDI')):
          tag = splitLine[2]
     else:  
          tag = splitLine[1]

     if(tag == "INDI"):
          id = splitLine[1].strip("@")
          emptySet1 = set()
          emptySet2 = set()
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
          readingIndividual = True
          readingFamily = False
     elif(tag == "FAM"):
          id = splitLine[1].strip("@")
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
          readingIndividual = False
          readingFamily = True
     elif(readingIndividual):

          if tag == "NAME":
               individuals[id]["name"] = splitLine[2] + " " + splitLine[3]
          elif tag == "SEX":
               individuals[id]["sex"] = splitLine[2]
          elif tag == "BIRT":
               birthDateLine = next(gedFile).strip().split()
               individuals[id]["birthday"] = (','.join(str (x) for x in birthDateLine[2:]))
          elif tag == "DEAT":
               deathDateLine = next(gedFile).strip().split()
               individuals[id]["death"] = (','.join(str (x) for x in deathDateLine[2:]))
               individuals["alive"]  = False
     elif(readingFamily):
          if tag == "HUSB":
               husbandId = splitLine[2].strip("@")
               families[id]["husband_id"] = husbandId
               families[id]["husband_name"] = individuals[husbandId]["name"]
               individuals[husbandId]["spouse"].append(id)
          elif tag == "WIFE":
               wifeId = splitLine[2].strip("@")
               families[id]["wife_id"] = wifeId
               families[id]["wife_name"] = individuals[wifeId]["name"]
               individuals[wifeId]["spouse"].append(id)
          elif tag == "CHIL":
               childId = splitLine[2].strip("@")
               families[id]["children"].append(childId)
               individuals[childId]["child"].append(id)
          elif tag == "MARR":
               marriageDateLine = next(gedFile).strip().split()
               families[id]["married"] = (','.join(str (x) for x in marriageDateLine[2:]))
          elif tag == "DIV":
               divorceDateLine = next(gedFile).strip().split()
               families[id]["divorced"] = (','.join(str (x) for x in divorceDateLine[2:]))

print(individuals)
print(families)
