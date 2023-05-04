# REQUIREMENTS ------------
# pip install requests
# -------------------------

# TODO:
# No validation done by assume everything is ok,
# But better to write validation logic too

import requests
import json
import os
import shutil

from utility import strip_strings

# Where the API is available
apiIndex = 'https://api.ce.pdn.ac.lk/people/v1'
# apiIndex = 'http://localhost:4001/people'

# Where the data is available
apiSource = 'https://people.ce.pdn.ac.lk/api/staff/'

# Split the email address into 2 fields


def emailFilter(email):
    if email != "":
        words = email.split('@')
        return {'name': words[0], 'domain': words[1]}
    else:
        return {'name': "", 'domain': ""}

# Delete the existing files first


def del_old_files():
    dir_path = "../people/v1/staff/"
    try:
        shutil.rmtree(dir_path)
    except:
        print("Error on deleting old files!")

# Write the /staff/index.json


def write_index(staff_list):
    dictionary = {}

    for email in staff_list:
        raw = staff_list[email]
        email_id = email.split('@')[0]
        url = '{0}/staff/{1}/'.format(apiIndex, email_id)
        dictionary[email] = {
            'name': raw['name'],
            'url': url,
            'designation':  raw['designation']
        }
    filename = "../people/v1/staff/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(dictionary, indent=4))

# Write the /staff/{email_id}/index.json files
def write_staff_pages(staff_list):
    for email in staff_list:
        raw_data = staff_list[email]
        email_id = email.split('@')[0]

        print("Page Write: " + raw_data['name'])

        filename = "../people/v1/staff/" + email_id + "/index.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        data = {
            'name': raw_data['name'],
            'designation': raw_data['designation'],
            'email': raw_data['email'],
            'profile_url': raw_data['link'],
            'profile_image': raw_data['profile_image'],
            'urls': raw_data['urls'],
            'research_interests': raw_data['research_interests'],
        }

        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=4))

# Write the /staff/all/index.json file
def write_all(staff_list, temp_staff_list, support_staff_list, visiting_staff_list):
    data_all = {}
    sorted_data_all = {}

    filename = "../people/v1/staff/all/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Temporary Academic Staff
    for email in temp_staff_list:
        raw_data = temp_staff_list[email]
        email_id = email.split('@')[0]

        raw_data = temp_staff_list[email]
        data = {
            'name': raw_data['name'],
            'designation': raw_data['designation'],
            'email': raw_data['email'],
            'profile_url': raw_data['link'],
            'profile_image': raw_data['profile_image'],
            'urls': {},
            'research_interests': [],
        }
        data_all[email_id] = data

    # Academic Staff
    for email in staff_list:
        raw_data = staff_list[email]
        email_id = email.split('@')[0]

        raw_data = staff_list[email]
        data = {
            'name': raw_data['name'],
            'designation': raw_data['designation'],
            'email': raw_data['email'],
            'profile_url': raw_data['link'],
            'profile_image': raw_data['profile_image'],
            'urls': raw_data['urls'],
            'research_interests': raw_data['research_interests'],
        }
        data_all[email_id] = data

    # Visiting Staff 
    for email in visiting_staff_list:
        raw_data = visiting_staff_list[email]
        email_id = email.split('@')[0]

        raw_data = visiting_staff_list[email]
        data = {
            'name': raw_data['name'],
            'designation': raw_data['designation'],
            'email': raw_data['email'],
            'profile_url': raw_data['link'],
            'profile_image': raw_data['profile_image'],
            'urls': raw_data['urls'],
            'research_interests': [],
        }
        data_all[email_id] = data

    # Sort in alphabatical order
    for key in sorted(data_all):
        sorted_data_all[key] = data_all[key]

    with open(filename, "w") as f:
        f.write(json.dumps(sorted_data_all, indent=4))


# ------------------------------------------------------------------------------

# Delete the existing files first
del_old_files()

r = requests.get(apiSource)
staff_list = {}

# Fetch data from the people.ce.pdn.ac.lk
if r.status_code == 200:
    all_staff_list = json.loads(r.text)

    # Academic Staff -----------------------------------------------------------
    staff_list = all_staff_list['academic']
    strip_strings(staff_list)

    # Write the index file for the academic staff
    write_index(staff_list)

    # Create files for each academic staff member
    print("Building: Academic Staff details")
    write_staff_pages(staff_list)

    # Temporary Academic and Academic Support Staff ----------------------------
    # No individual pages for them
    print("Building: Temporary and NonAcademic staff details")
    temp_staff_list = all_staff_list['temporary-academic']
    support_staff_list = all_staff_list['support-academic']
    strip_strings(temp_staff_list)
    strip_strings(support_staff_list)

    # Visiting Staff -----------------------------------------------------------
    # No individual pages for them
    print("Building: Visiting staff details")
    visiting_staff_list = all_staff_list['visiting'] if "visiting" in all_staff_list else []

    # Create the aggregated index file
    print("Generating: all/index.json")
    write_all(staff_list, temp_staff_list, support_staff_list, visiting_staff_list)
