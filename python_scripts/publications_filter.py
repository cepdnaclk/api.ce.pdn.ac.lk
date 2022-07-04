# REQUIREMENTS ------------
# pip install requests
# -------------------------

# TODO:
# No validation done by assume everything is ok,
# But better to write validation logic too

import requests
import json
import os

# Where the API is available
apiBase = "https://api.ce.pdn.ac.lk"
apiIndex = apiBase + "/publications/"

student_author_dict = {}
staff_author_dict = {}
tag_dict = {}
research_group_dict = {}

# Gather Student API data
students_url = '../people/v1/students/all/index.json'
with open(students_url, 'r') as f:
    students = json.load(f)

# Gather Publications API data
publications_url = '../publications/v1/all/index.json'
with open(publications_url, 'r') as f:
    publications = json.load(f)

for pub in publications:

    # read the publication information from the publication's index file
    filename = pub['api_url'].replace('https://api.ce.pdn.ac.lk', '..') + "index.json"
    pub_data = json.load(open(filename, "r"))

    edit_url = pub['api_url'].replace("https://api.ce.pdn.ac.lk/", "https://github.com/cepdnaclk/api.ce.pdn.ac.lk/blob/main/") + "index.json"

    # Prepare a subset of the publication data
    pub_info = {
        'title': pub_data['title'],
        'venue': pub_data['venue'],
        'year': pub_data['year'],
        'abstract': pub_data['abstract'],
        'authors': pub_data['authors'],
        'doi': pub_data['doi'],
        'preprint': pub_data['preprint_url'] or "#",
        'pdf': pub_data['pdf_url'] or"#",
        'presentation': pub_data['presentation_url'] or "#",
        'project': pub_data['project_url'] or "#",
        'codebase': pub_data['codebase'] or "#",
        'researchgroups': pub_data['research_groups'],
        'funding': pub_data['funding'],
        'tags': pub_data['tags'],
        'api_url': pub_data['api_url'],
        'edit_url': edit_url
    }

    print(pub_data['title'])

    # Add the project_tag info into the student, staff indexes
    if 'author_info' in pub_data:
        for author in pub_data['author_info']:
            author_id = author['id']

            if author_id!="" and author['type'] == 'STUDENT':
                # Student
                if author_id not in student_author_dict: student_author_dict[author_id] = []

                # Delete the Abstract
                temp_pub_info = pub_info.copy()
                temp_pub_info.pop('abstract')

                student_author_dict[author_id].append(temp_pub_info)
                print('  > Student:', author_id)

            elif author_id!="" and author['type'] == 'STAFF':
                # Staff
                # NOTE: This need to be handle carefully !
                key = author_id + '@eng.pdn.ac.lk'
                if key not in staff_author_dict: staff_author_dict[key] = []

                # Delete the Abstract
                temp_pub_info = pub_info.copy()
                temp_pub_info.pop('abstract')

                staff_author_dict[key].append(temp_pub_info)
                print('  > Staff:', author_id)

    # Add the project_tag info into the tag indexes
    if 'tags' in pub_data:
        for tag in pub_data['tags']:
            if tag !="":
                if tag not in tag_dict: tag_dict[tag] = []
                tag_dict[tag].append(pub_info)
                print('  > Tag:', tag)

    if 'research_groups' in pub_data:
        for tag in pub_data['research_groups']:
            if tag !="":
                if tag not in research_group_dict: research_group_dict[tag] = []
                research_group_dict[tag].append(pub_info)
                print('  > Research Group:', tag)

    # TODO: implement an API to get publications by research group

# ------------------------------------------------------------------------------
# Students
students_sorted = {}
for key in sorted(student_author_dict):
    students_sorted[key] = student_author_dict[key]

# ------------------------------------------------------------------------------
# Students and Staff

# TODO: In supervisor list, publications should be grouped by years too
# TODO: Before last 5 years, others should be grouped in one tab (GUI requirement)
studentFilter_filename = "../publications/v1/filter/students/index.json"
os.makedirs(os.path.dirname(studentFilter_filename), exist_ok=True)
with open(studentFilter_filename, "w") as f:
    f.write(json.dumps(students_sorted, indent = 4))

staff_sorted = {}
for key in sorted(staff_author_dict):
    staff_sorted[key] = staff_author_dict[key]

staffFilter_filename = "../publications/v1/filter/staff/index.json"
os.makedirs(os.path.dirname(staffFilter_filename), exist_ok=True)
with open(staffFilter_filename, "w") as f:
    f.write(json.dumps(staff_sorted, indent = 4))

# ------------------------------------------------------------------------------
# Tags

tag_dict_sorted = {}
for key in sorted(tag_dict):
    tag_dict_sorted[key] = tag_dict[key]

tagFilter_filename = "../publications/v1/filter/tags/index.json"
os.makedirs(os.path.dirname(tagFilter_filename), exist_ok=True)
with open(tagFilter_filename, "w") as f:
    f.write(json.dumps(tag_dict_sorted, indent = 4))

# ------------------------------------------------------------------------------
# Research groups

research_group_dict_sorted = {}
for key in sorted(research_group_dict):
    research_group_dict_sorted[key] = research_group_dict[key]

researchGroupFilter_filename = "../publications/v1/filter/research-groups/index.json"
os.makedirs(os.path.dirname(researchGroupFilter_filename), exist_ok=True)
with open(researchGroupFilter_filename, "w") as f:
    f.write(json.dumps(research_group_dict_sorted, indent = 4))
