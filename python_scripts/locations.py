# REQUIREMENTS ------------
# pip install requests
# -------------------------

# This script will fetch data from the below Google Sheet
# https://docs.google.com/spreadsheets/d/1b90XI2rIsJJbEYPwvKo24xOvwkHdXG48Nl0vf8Otxmw/edit?usp=sharing

# TODO:
# No validation done by assume everything is ok,
# But better to write validation logic too

import requests
import json
import os
import shutil

from utility import getStaff

# Use SL timezone
os.environ['TZ'] = 'Asia/Colombo'

# Where the API is available
apiBase = "https://api.ce.pdn.ac.lk"

# Where this API locates
apiIndex = 'https://api.ce.pdn.ac.lk/locations/v1'

# Where the staff data available
staffSource = "../people/v1/staff/all/index.json"

# Gather Staff API data
staff_file = open(staffSource)
staff = json.load(staff_file)

enumAccess = {
    "S": ["Staff"],
    "I": ["Instructors"],
    "TO": ["Technical Officers"],
    "UG": ["Undergraduates"],
    "PG": ["Postgraduates"],
    "N": ["None"],
    "ALL": ["Staff", "Instructors", "Technical Officers", "Undergraduates", "Postgraduates"]
}


def del_existing_data():
    dir_path = "../locations/v1/"
    try:
        shutil.rmtree(dir_path)
    except:
        print("Error: Folder Not Found!")


def write_location(data):
    filename = "../locations/v1/{0}/{1}/index.json".format(
        data['floor'], data['id'])
    # print(filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=4))

    # Debug:
    print(data['label'])


del_existing_data()

google_form_link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTr12i7soWZlL1lYDdUMCRs4JAC4W9pnUNuYsCJdyUVB4UPo_MJlFmPVKX2S2YX4d50-KlewwoddYZz/pub?gid=0&single=true&output=tsv"
loc_raw = requests.get(google_form_link, headers={
                       'Cache-Control': 'no-cache'}).text.split("\n")
locations = {}

ID = 0
CATEGORY = 1
NAME = 2
ACCESSIBILITY = 3
TAGS = 4
STAFF = 5
CONTACT_TELE = 6
CONTACT_EMAIL = 7
CAPACITY = 8
URL = 9
DESCRIPTION_1 = 10
DESCRIPTION_2 = 11
DESCRIPTION_3 = 12
FEATURE_1 = 13
FEATURE_2 = 14
FEATURE_3 = 15

FIELD_COUNT = 16

# Skip the header line of the TSV
for line in loc_raw[1:]:
    loc_raw_data = line.replace('\r', '').split("\t")

    # Skip incompatible rows
    if (len(loc_raw_data) != FIELD_COUNT or loc_raw_data[0] == ""):
        continue


    floor_id = loc_raw_data[ID].split("-")[0]
    room_id = loc_raw_data[ID].split("-")[1]
    label = "CE-" + loc_raw_data[ID]

    tag_list = [ t.strip() for t in loc_raw_data[TAGS].split(",") ]

    access_list = []
    for access in [ a.strip() for a in loc_raw_data[ACCESSIBILITY].split(",") ]:
        if access in enumAccess:
            access_list.extend(enumAccess[access])
        elif access != "":
            print("{0}: Unsupported Tag !".format(access))

    description_list = [x for x in list([
            loc_raw_data[DESCRIPTION_1],
            loc_raw_data[DESCRIPTION_2],
            loc_raw_data[DESCRIPTION_3]
        ]) if x != ""]
    
    features_list = [x for x in list([
            loc_raw_data[FEATURE_1],
            loc_raw_data[FEATURE_2],
            loc_raw_data[FEATURE_3]
        ]) if x != ""]

    api_url = "{0}/{1}/{2}/index.json".format(apiIndex, floor_id, room_id)

    # Staff API integration
    if loc_raw_data[CONTACT_EMAIL] != "" :
        staff_id = loc_raw_data[CONTACT_EMAIL].split('@')[0]
        staff_name = staff[staff_id]["name"] if staff_id in staff else ""
        staff_link = staff[staff_id]["profile_url"] if staff_id in staff else ""
    else:
        staff_name = ""
        staff_link = ""

    loc_data = {
        "floor": floor_id,
        "id": room_id,
        "label": label,
        "title": loc_raw_data[NAME],
        "contact": {
            "tele": loc_raw_data[CONTACT_TELE],
            "email": loc_raw_data[CONTACT_EMAIL],
            "name": staff_name,
            "link":  staff_link
        },
        "capacity": "N/A" if loc_raw_data[CAPACITY] == "" else loc_raw_data[CAPACITY],
        "url": "#" if loc_raw_data[URL] == "" else loc_raw_data[URL], 
        "api_url": api_url,
        "description": description_list,
        "features": features_list,
        "tags": sorted(tag_list),
        "accessibility": sorted(list(set(access_list))),
    }

    write_location(loc_data)

    if floor_id not in locations:
        locations[floor_id] = {"title": floor_id, "locations": []}

    locations[floor_id]['locations'].append(loc_data)

# Write index file
location_index = {}
location_total = 0
for floor in locations:
    location_total = location_total + len(locations[floor]['locations'])
    location_index[floor] = {
        "floor": floor,
        "api_url": "{0}/{1}/index.json".format(apiIndex, floor),
        "location_count": len(locations[floor]['locations'])
    }
location_index["all"] = {
    "floor": "N/A",
    "api_url": "{0}/all/index.json".format(apiIndex),
    "location_count": location_total
}

filename = "../locations/v1/index.json"
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w") as f:
    f.write(json.dumps(location_index, indent=4))

# Write all locations
filename = "../locations/v1/all/index.json"
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w") as f:
    f.write(json.dumps(locations, indent=4))

# Write locations by floors
for floor in locations:
    filename = "../locations/v1/{0}/index.json".format(floor)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(locations[floor], indent=4))
