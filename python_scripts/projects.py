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
apiSource = "https://projects.ce.pdn.ac.lk/api/all/"
repoSource = "https://github.com/cepdnaclk/"
pageSource = "https://cepdnaclk.github.io/"

studentSource = apiBase + "people/students/all/"

enable_deep_scan = False

def process_team(data):
    # Process, validate, and add missing data from people APIs
    team = {}

    for person in data:
        eNumber = person['eNumber']
        name = person['name'] if 'name' in person else "#"
        email = person['email'] if 'email' in person else "#"
        github = person['github_profile'] if 'github_profile' in person else "#"
        linkedin = person['linkedin_profile'] if 'linkedin_profile' in person else "#"
        researchgate = person['researchgate_profile'] if 'researchgate_profile' in person else "#"
        website = person['website'] if 'website' in person else "#"
        profile_api = apiBase + "people/students/" + eNumber.replace("E/", "E")

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
def write_all(categories):
    dict = {}
    for cat in categories:
        cat_name = cat.replace(' ', '-') #.lower()
        url = apiIndex + 'projects/' + cat_name + '/'
        count = len(categories[cat].keys())
        dict[cat] = categories[cat]

    filename = "../projects/all/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(dict, indent = 4))

# Write the /projects/index.json
def write_index(categories):
    dict = {}
    for cat in categories:
        cat_name = cat.replace(' ', '-') #.lower()
        url = apiIndex + 'projects/' + cat_name + '/'
        count = len(categories[cat].keys())
        dict[cat] = { 'category': cat, 'url': url, 'batches': count }

    filename = "../projects/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(dict, indent = 4))

# Write the /projects/{category}/index.json files
def write_batches(categories):
    for cat in categories:
        cat_name = cat.replace(' ', '-') #.lower()
        filename = "../projects/" + cat_name + "/index.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        data = {}
        sorted_data = {}

        for batch in categories[cat]:
            url =  apiIndex + 'projects/' + cat_name + '/' + batch + '/'
            count = len(categories[cat][batch].keys())
            data[batch] = { 'url': url, 'projects': count }

        for key in sorted(data):
            sorted_data[key] = data[key]

        with open(filename, "w") as f:
            f.write(json.dumps(sorted_data, indent = 4))

# Write the /students/{batch}/{regNumber}/index.json files
def write_project(categories):
    for cat in categories:
        cat_name = cat.replace(' ', '-') #.lower()
        for batch in categories[cat]:
            for project in categories[cat][batch]:
                proj_name = project.replace(' ', '-') #.lower()
                filename = "../projects/" + cat_name + "/" + batch + "/" + proj_name + "/index.json"

                data = categories[cat][batch][project]

                if(enable_deep_scan and data['page_url'] != "#"):
                    # Load proj configuration details
                    additionalData = project_details(data['page_url'])
                    for details in additionalData:
                        data[details] = additionalData[details]

                    # print(json.dumps(data, indent = 4))
                    # return

                # print(filename)
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                # print(json.dumps(categories[student], indent = 4))
                with open(filename, "w") as f:
                    f.write(json.dumps(data, indent = 4))


# ------------------------------------------------------------------------------
r = requests.get(apiSource)
categories = {}

# Fetch data from the people.ce.pdn.ac.lk
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

# Write the index file for the projects, including all the projects
write_index(categories)

# Create files for batches, in each category
write_batches(categories)

# Create files for each project
write_project(categories)

# Write all the project details into one file
write_all(categories)
