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
apiBase = "https://cepdnaclk.github.io/api.ce.pdn.ac.lk/"
apiIndex = apiBase + "projects/"

# Where the data is available
apiSource = "https://projects.ce.pdn.ac.lk/api/"
repoSource = "https://github.com/cepdnaclk/"
pageSource = "https://cepdnaclk.github.io/"

studentSource = apiBase + "people/students/all/"

enable_deep_scan = True

def process_team(data):
    # Process, validate, and add missing data from people APIs
    team = {}

    for person in data:
        eNumber = person['eNumber'].upper()
        name = person['name'] if 'name' in person else "#"
        email = person['email'] if 'email' in person else "#"
        github = person['github_profile'] if 'github_profile' in person else "#"
        linkedin = person['linkedin_profile'] if 'linkedin_profile' in person else "#"
        researchgate = person['researchgate_profile'] if 'researchgate_profile' in person else "#"
        website = person['website'] if 'website' in person else "#"
        profile_api = apiBase + "people/students/" + eNumber.replace("E/", "E")

        if eNumber in students:
            person_from_api = students[eNumber]

            if 'emails' in person_from_api:
                # Try faculty email first
                faculty_email = person_from_api['emails']['faculty']
                personal_email = person_from_api['emails']['personal']

                if faculty_email['name'] != "":
                    api_email = faculty_email['name'] + '@' + faculty_email['domain']
                elif personal_email['name'] != "":
                    api_email = personal_email['name'] + '@' + personal_email['domain']
                else:
                    api_email = '#'

            # If student API have nformation, replace the relevent parameters from there
            email = api_email
            github = person_from_api['urls']['github'] if 'github' in person_from_api['urls'] else "#"
            linkedin = person_from_api['urls']['linkedin'] if 'linkedin' in person_from_api['urls'] else "#"
            researchgate = person_from_api['urls']['researchgate'] if 'researchgate' in person_from_api['urls'] else "#"
            website = person_from_api['urls']['website'] if 'website' in person_from_api['urls'] else "#"

        team[eNumber] = {'name':name, 'email':email, 'github':github, 'linkedin':linkedin, 'website':website, 'researchgate':researchgate, 'profile':profile_api}

    return team

def process_supervisors(data):
    # Process, validate, and add missing data from people APIs
    return data

def process_publications(data):
    # TODO: process & validate
    return data

def project_details(page_url):
    data = {}

    try:
        url = page_url + "/data/index.json"
        r = requests.get(url)

        if r.status_code==200:
            # it is available
            try:
                proj_config = json.loads(r.text)
                # print(json.dumps(proj_config, indent = 2))

                data['team'] = process_team(proj_config['team'])
                data['supervisors'] = process_supervisors(proj_config['supervisors'])

                if 'publications' in proj_config:
                    data['publications'] = process_publications(proj_config['publications'])

                # TODO: Add remaining parameters
            except:
                print('parse failed; ' +  url)

    except:
        print('load failed; ' +  url)

    # print(json.dumps(data, indent = 2))
    return data

# Write the /projects/all/index.json
# def write_all(categories):
#     dict = {}
#     for cat in categories:
#         cat_name = cat.replace(' ', '-') #.lower()
#         url = apiBase + 'projects/' + cat_name + '/'
#         count = len(categories[cat].keys())
#         dict[cat] = categories[cat]
#
#     filename = "../projects/all/index.json"
#     os.makedirs(os.path.dirname(filename), exist_ok=True)
#     with open(filename, "w") as f:
#         f.write(json.dumps(dict, indent = 4))

# Write the /projects/index.json
def write_index(category_index, categories):
    filename = "../projects/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(category_index, indent = 4))

# Write the /projects/{category}/index.json files
def write_categories(categories):
    for cat in categories:
        cat_name =  title_to_code[cat]
        filename = "../projects/" + cat_name + "/index.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        data = {}
        sorted_data = {}

        for batch in categories[cat]:
            url =  apiBase + 'projects/' + cat_name + '/' + batch + '/'
            count = len(categories[cat][batch].keys())
            data[batch] = { 'api_url': url, 'project_count': count }

        for key in sorted(data):
            sorted_data[key] = data[key]

        code = category_index[cat_name]['code']
        title = category_index[cat_name]['title']
        description = category_index[cat_name]['description']
        type = category_index[cat_name]['type']

        output = { 'code': code, 'title':title, 'description':description, 'type':type, 'batches': sorted_data }

        with open(filename, "w") as f:
            f.write(json.dumps(output, indent = 4))

# Write the /projects/{category}/{batch}/index.json files
def write_batches(categories):
    for cat in categories:
        cat_name =  title_to_code[cat]

        for batch in categories[cat]:
            filename = "../projects/" + cat_name + "/" + batch + "/index.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            raw_data = categories[cat][batch]
            data = {}
            sorted_data = {}

            for proj in raw_data:
                project = raw_data[proj]

                category_code = title_to_code[project['category']]
                proj_name = project['title'].replace(' ', '-') #.lower()
                api_url = apiIndex + cat_name + "/" + batch + "/" + proj_name
                category_api_url = apiIndex + cat_name + "/"

                data[proj] = {
                        'title': project['title'],
                        'description': project['description'],
                        'category': { 'title': project['category'], 'code': category_code, "api_url": category_api_url },
                        'project_url': project['project_url'],
                        'repo_url': project['repo_url'],
                        'page_url': project['page_url'],
                        'api_url': api_url,
                }

            # Sort by the project name
            for key in sorted(data):
                sorted_data[key] = data[key]

            with open(filename, "w") as f:
                f.write(json.dumps(sorted_data, indent = 4))

# Write the /projects/{category}/{batch}/{project}/index.json files
def write_projects(categories):
    for cat in categories:
        cat_name =  title_to_code[cat]
        for batch in categories[cat]:
            for project in categories[cat][batch]:

                raw_data = categories[cat][batch][project]
                category_code = title_to_code[raw_data['category']]
                category_api_url = apiIndex + cat_name + "/"

                data = {
                    'title': raw_data['title'],
                    'description': raw_data['description'],
                    'category': { 'title': raw_data['category'], 'code': category_code, "api_url": category_api_url },
                    'project_url': raw_data['project_url'],
                    'repo_url': raw_data['repo_url'],
                    'page_url': raw_data['page_url']
                    }

                if(enable_deep_scan and data['page_url'] != "#"):
                    # Load proj configuration details
                    additionalData = project_details(data['page_url'])
                    for details in additionalData:
                        data[details] = additionalData[details]

                    # print(json.dumps(data, indent = 4))
                    # return

                proj_name = raw_data['title'].replace(' ', '-') #.lower()
                filename = "../projects/" + cat_name + "/" + batch + "/" + proj_name + "/index.json"

                os.makedirs(os.path.dirname(filename), exist_ok=True)

                # print(json.dumps(categories[student], indent = 4))
                with open(filename, "w") as f:
                    f.write(json.dumps(data, indent = 4))


# ------------------------------------------------------------------------------
r = requests.get(apiSource + "all/")
r2 = requests.get(apiSource + "categories/")
r3 = requests.get(studentSource)


category_index = {}
categories = {}
title_to_code = {} #  translate title to category code
students = {}

if r3.status_code==200:
    students = json.loads(r3.text)

# Fetch project data from the people.ce.pdn.ac.lk
if r.status_code==200:
    data = json.loads(r.text)

    for project in data:
        category = project['category']
        batch = project['batch']
        title = project['repo_url'].replace(repoSource, "")

        # batch = data[eNumber]['batch']
        if category not in categories: categories[category] = {}
        if batch not in categories[category]: categories[category][batch] = {}

        categories[category][batch][title] = project

# Fetch category data from the people.ce.pdn.ac.lk
if r2.status_code==200:
    r2_data = json.loads(r2.text)

    for category in r2_data:
        title = category['title']
        code = category['code']
        type = category['type']
        description = category['description']

        page = category['page_url']
        api = apiIndex + code + "/"

        category_index[code] = {'code':code, 'title':title, 'description':description, 'type':type,'page_url':page, 'api_url':api}
        title_to_code[title] = code

# Write the index file for the projects, including all the projects
write_index(category_index, categories)

# Create files for categories
write_categories(categories)

# Create files for category/batch
write_batches(categories)

# Create files for each project
write_projects(categories)

# # Write all the project details into one file
# write_all(categories)
