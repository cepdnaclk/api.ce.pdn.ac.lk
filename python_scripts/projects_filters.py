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
apiIndex = apiBase + "/projects/"

studentSource = apiBase + "/people/v1/students/all/"
projectSource = apiBase + "/projects/v1/all/"

student_dict = {}
tag_dict = {}

# Gather Student API data
req_students = requests.get(studentSource)
if req_students.status_code==200:
    students = json.loads(req_students.text)

# Gather Project API data
req_projects = requests.get(projectSource)
if req_projects.status_code==200:
    projects = json.loads(req_projects.text)


for p_cat in projects:
    # Each project category
    proj_cat = projects[p_cat]
    print("\n"+ p_cat)

    for batch in proj_cat['batches']:
        # Each batch
        batch_projects = proj_cat['batches'][batch]
        print('- ' + batch)

        for proj in batch_projects['projects']:
            # Each project

            p = batch_projects['projects'][proj]
            print('-- ' + p['title'])

            # read the project information from the project's index file
            filename = p['api_url'].replace('http://api.ce.pdn.ac.lk', '..') + "index.json"

            proj_data = json.load(open(filename, "r"))

            cat_code = proj_data['category']['code']
            cat_title = proj_data['category']['title']
            # print(json.dumps(proj_data, indent = 4))

            # Prepare a subset of the project data
            proj_info = {
                'title': proj_data['title'],
                'category': {
                    'code': cat_code,
                    'title': cat_title,
                    'api_url': apiBase + '/projects/v1/' + cat_code + '/'
                },
                'project_url': proj_data['project_url'],
                'repo_url': proj_data['repo_url'],
                'page_url': proj_data['page_url'],
                'thumbnail_url': proj_data['thumbnail_url'],
                'api_url': p['api_url']
            }

            # Add the project_tag info into the student indexes
            if 'team' in proj_data:
                print('\tStudents: ' + ', '.join(proj_data['team']))
                for student in proj_data['team']:
                    if student!="" and student!="E/YY/XXX":
                        if student not in student_dict: student_dict[student] = []
                        student_dict[student].append(proj_info)

            # Add the project_tag info into the tag indexes
            if 'tags' in proj_data:
                for tag in proj_data['tags']:
                    if tag !="":
                        if tag not in tag_dict: tag_dict[tag] = []
                        tag_dict[tag].append(proj_info)


# print(json.dumps(student_dict, indent = 4))

# Sort the student dictionary according to ENumber (ASC)
student_dict_sorted = {}
for key in sorted(student_dict):
    student_dict_sorted[key] = student_dict[key]

# Write the sorted dict into the API endpoint file
studentFilter_filename = "../projects/v1/filter/students/index.json"
os.makedirs(os.path.dirname(studentFilter_filename), exist_ok=True)
with open(studentFilter_filename, "w") as f:
    f.write(json.dumps(student_dict_sorted, indent = 4))


# Sort the tag dictionary according to Tag Name (ASC)
tag_dict_sorted = {}
for key in sorted(tag_dict):
    tag_dict_sorted[key] = tag_dict[key]

# Write the sorted dict into the API endpoint file
tagFilter_filename = "../projects/v1/filter/tags/index.json"
os.makedirs(os.path.dirname(tagFilter_filename), exist_ok=True)
with open(tagFilter_filename, "w") as f:
    f.write(json.dumps(tag_dict_sorted, indent = 4))
