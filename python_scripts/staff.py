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

# Where the API is available
apiIndex = 'https://api.ce.pdn.ac.lk/people/v1'
# apiIndex = 'http://localhost:4001/people'

# Where the data is available
apiSource = 'https://people.ce.pdn.ac.lk/api/staff/'

# Split the email address into 2 fields
def emailFilter(email):
    if email != "":
        words = email.split('@')
        return { 'name':words[0], 'domain':words[1] }
    else:
        return { 'name': "", 'domain': "" }

# Delete the existing files first
def del_old_files():
    dir_path = "../people/v1/staff/"
    try:
        shutil.rmtree(dir_path)
    except error as e:
        print("Error !")

# Write the /staff/index.json
def write_index(staff_list):
    dict = {}

    for email in staff_list:
        raw = staff_list[email]
        url = '{0}/staff/{1}/'.format(apiIndex,email)
        dict[email] = {
            'name': raw['name'],
            'url': url,
            'designation':  raw['designation']
        }

    filename = "../people/v1/staff/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(dict, indent = 4))

# Write the /staff/{email}/index.json files
def write_staff_pages(staff_list):
    for email in staff_list:
        raw_data = staff_list[email]
        filename = "../people/v1/staff/" + email + "/index.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        data = {
            'name': raw_data['name'],
            'designation': raw_data['designation'],
            'page_url': raw_data['link'],
            'email': raw_data['email'],
            'profile_image': raw_data['profile_image'],
            'urls': raw_data['urls'],
            'research_interests': raw_data['research_interests'],
        }

        with open(filename, "w") as f:
            f.write(json.dumps(data, indent = 4))

# ------------------------------------------------------------------------------

# Delete the existing files first
del_old_files()

r = requests.get(apiSource)
staff_list = {}

# Fetch data from the people.ce.pdn.ac.lk
if r.status_code==200:
    staff_list = json.loads(r.text)
    # print(staff_list)

    # Write the index file for the staff
    write_index(staff_list)

    # Create files for each batch
    write_staff_pages(staff_list)
