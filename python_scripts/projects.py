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
apiBase = "http://api.ce.pdn.ac.lk"


# Where the student data available
studentSource = "../people/v1/students/all/index.json"

# Where the project data available
apiSource = "https://projects.ce.pdn.ac.lk/api/"

# Source addresses for the repositories
repoSource = "https://github.com/cepdnaclk/"
pageSource = "https://cepdnaclk.github.io/"

# If this is enabled, the individual project config files also fetch
enable_deep_scan = True

# Delete the existing files first
def del_old_files():
    dir_path = "../projects/v1/"
    try:
        shutil.rmtree(dir_path)
    except:
        print("Error: Folder Not Found!")

def project_key(title):
    return title.replace(' ', '-')

# Pre-process the team data
def process_team(data):
    team = {}

    for person in data:
        eNumber = person['eNumber'].upper()
        name = person['name'] if 'name' in person else "#"
        email = person['email'] if 'email' in person else "#"
        github = person['github_profile'] if 'github_profile' in person else "#"
        linkedin = person['linkedin_profile'] if 'linkedin_profile' in person else "#"
        researchgate = person['researchgate_profile'] if 'researchgate_profile' in person else "#"
        website = person['website'] if 'website' in person else "#"
        profile_api = apiBase + "/people/students/" + eNumber.replace("E/", "E")

        if eNumber in students:
            # Check with the details available in the student API
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

            # If student API has information, replace the relevent parameter with it
            # (assume the API has the latest info)
            email = api_email
            github = person_from_api['urls']['github'] if 'github' in person_from_api['urls'] else "#"
            linkedin = person_from_api['urls']['linkedin'] if 'linkedin' in person_from_api['urls'] else "#"
            researchgate = person_from_api['urls']['researchgate'] if 'researchgate' in person_from_api['urls'] else "#"
            website = person_from_api['urls']['website'] if 'website' in person_from_api['urls'] else "#"

        team[eNumber] = {
            'name':name, 'email':email, 'website':website,
            'github':github, 'linkedin':linkedin,
            'researchgate':researchgate, 'api_url':profile_api
        }

    return team

# Pre-process the supervisor data
def process_supervisors(data):
    # TODO: Process, validate, and add missing data from people APIs
    return data

def process_publications(data):
    # TODO: process & validate
    pub = []
    for publication in data:
        if publication['title']!="Paper Title" and publication['url']!='#':
            pub.append(publication)

    return pub

def project_details(page_url):
    data = {}

    try:
        url = page_url + "/data/index.json"
        r = requests.get(url)

        if r.status_code==200:
            # it is available
            try:
                proj_config = json.loads(r.text)

                try:
                    if 'team' in proj_config:
                        data['team'] = process_team(proj_config['team'])
                except Exception as e:
                    print('parse failed, team; ' + url, e)

                try:
                    if 'supervisors' in proj_config:
                        data['supervisors'] = process_supervisors(proj_config['supervisors'])
                except Exception as e:
                    print('parse failed, supervisors; ' + url, e)

                try:
                    if 'publications' in proj_config:
                        publications = process_publications(proj_config['publications'])
                        if len(publications)>0:
                            data['publications'] = publications
                except Exception as e:
                    print('parse failed, publications; ' + url, e)

                # TODO: Add remaining parameters
            except:
                print('parse failed; ' +  url)
    except:
        print('load failed; ' +  url)

    return data

# Write the /projects/v1/all/index.json
def write_all(categories):
    dict = {}

    # For each category
    for cat in categories:
        cat_name = title_to_code[cat]
        url = apiBase + '/projects/v1/' + cat_name + '/'
        category_count = len(categories[cat].keys())

        # For each batch
        for b in categories[cat]:
            batch = categories[cat][b]
            batch_api = '{0}/projects/v1/{1}/{2}/'.format(apiBase,cat_name,b)
            proj_count = len(categories[cat][b].keys())
            proj = {}

            # For each project
            for p in batch:
                proj_key = project_key(batch[p]['title'])
                batch[p]['api_url'] = '{0}/projects/v1/{1}/{2}/{3}/'.format(apiBase,cat_name,b,proj_key)
                proj[proj_key] = batch[p]

            categories[cat][b] = {
                'api_url': batch_api,
                'project_count': proj_count,
                'projects': proj
            }

        dict[cat] = {
            'api_url': url,
            'batch_count': category_count,
            'batches': categories[cat]
        }

    filename = "../projects/v1/all/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(dict, indent = 4))

# Write the /projects/v1/index.json
def write_index(category_index, categories):
    filename = "../projects/v1/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(category_index, indent = 4))

# Write the /projects/v1/{category}/index.json files
def write_categories(categories):
    for cat in categories:
        cat_name =  title_to_code[cat]
        data = {}
        sorted_data = {}

        # Generate the project list
        for batch in categories[cat]:
            url =  '{0}/projects/v1/{1}/{2}/'.format(apiBase,cat_name,batch)
            proj_count = len(categories[cat][batch].keys())
            data[batch] = { 'api_url': url, 'project_count': proj_count }

        # Sort the projects in alphabatical order
        for key in sorted(data):
            sorted_data[key] = data[key]

        code = category_index[cat_name]['code']
        title = category_index[cat_name]['title']
        description = category_index[cat_name]['description']
        type = category_index[cat_name]['type']

        output = {
            'code': code, 'title':title, 'description':description,
            'type':type, 'batches': sorted_data
        }

        filename = "../projects/v1/{0}/index.json".format(cat_name)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(json.dumps(output, indent = 4))

# Write the /projects/v1/{category}/{batch}/index.json files
def write_batches(categories):
    # For each category
    for cat in categories:
        cat_name =  title_to_code[cat]

        # For each batch
        for batch in categories[cat]:
            raw_data = categories[cat][batch]
            data = {}
            sorted_data = {}

            # For each project
            for proj in raw_data:
                project = raw_data[proj]
                category_code = title_to_code[project['category']]
                proj_name = project_key(project['title'])

                api_url =  '{0}/projects/v1/{1}/{2}/{3}/'.format(apiBase,cat_name,batch,proj_name)
                category_api_url = '{0}/projects/v1/{1}/'.format(apiBase,cat_name)

                data[proj] = {
                        'title': project['title'],
                        'description': project['description'],
                        'category': {
                            'title': project['category'],
                            'code': category_code,
                            'api_url': category_api_url
                        },
                        'project_url': project['project_url'],
                        'repo_url': project['repo_url'],
                        'page_url': project['page_url'],
                        'api_url': api_url,
                }

            # Sort by the project name
            for key in sorted(data):
                sorted_data[key] = data[key]

            filename = "../projects/v1/{0}/{1}/index.json".format(cat_name,batch)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(json.dumps(sorted_data, indent = 4))

# Write the /projects/v1/{category}/{batch}/{project}/index.json files
def write_projects(categories):
    for cat in categories:
        print('_' + cat)

        for batch in categories[cat]:
            print('__' + batch)
            for project in categories[cat][batch]:
                raw_data = categories[cat][batch][project]

                proj_name = project_key(raw_data['title'])
                cat_code = title_to_code[raw_data['category']]
                cat_api_url ='{0}/projects/v1/{1}/'.format(apiBase,cat_code)

                data = {
                    'title': raw_data['title'],
                    'description': raw_data['description'],
                    'category': {
                        'title': raw_data['category'],
                        'code': cat_code,
                        'api_url': cat_api_url
                    },
                    'project_url': raw_data['project_url'],
                    'repo_url': raw_data['repo_url'],
                    'page_url': raw_data['page_url']
                    }

                if(enable_deep_scan and data['page_url'] != "#"):
                    # Load proj configuration details from the GitHub pages
                    additionalData = project_details(data['page_url'])
                    for details in additionalData:
                        data[details] = additionalData[details]

                    # print(json.dumps(data, indent = 4))
                    # return

                filename = "../projects/v1/{0}/{1}/{2}/index.json".format(cat_code,batch,proj_name)
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w") as f:
                    f.write(json.dumps(data, indent = 4))


# ------------------------------------------------------------------------------

# Delete the existing files first
del_old_files()

category_index = {}
categories = {}
title_to_code = {} #  translate title to category code
students = {}

# Gather Student API data
student_file = open(studentSource)
students = json.load(student_file)

# Fetch category data from the people.ce.pdn.ac.lk
req_category = requests.get(apiSource + "categories/")
if req_category.status_code==200:
    category_data = json.loads(req_category.text)

    for category in category_data:
        title = category['title']
        code = category['code']
        type = category['type']
        description = category['description']

        page = category['page_url']
        api ='{0}/projects/v1/{1}/'.format(apiBase,code)

        category_index[code] = {
            'code':code, 'title':title, 'description':description,
            'type':type,'page_url':page, 'api_url':api
        }
        title_to_code[title] = code


# Fetch project data from the people.ce.pdn.ac.lk
req_projects = requests.get(apiSource + "all/")
if req_projects.status_code==200:
    data = json.loads(req_projects.text)

    for project in data:
        category = project['category']
        batch = project['batch']
        title = project['repo_url'].replace(repoSource, "")

        # Create dictionary keys if not exists
        if category not in categories: categories[category] = {}
        if batch not in categories[category]: categories[category][batch] = {}

        categories[category][batch][title] = project


# Write the index file for the projects, including all the projects
print("Generating the index");
write_index(category_index, categories)

# Create files for categories
print("Generating the categories");
write_categories(categories)

# Create files for category/batch
print("Generating the batches");
write_batches(categories)

# Create files for each project
print("Generating the projects");
write_projects(categories)

# Write all the project details into one file
print("Generating the all projects file");
write_all(categories)
