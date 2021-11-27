# REQUIREMENTS ------------
# pip install requests
# -------------------------

import requests
import json
import os

# Where the API is available
apiIndex = 'https://cepdnaclk.github.io/api.ce.pdn.ac.lk/students/'

# Where the data is available
apiSource = 'https://cepdnaclk.github.io/people.ce.pdn.ac.lk/api/all/'

def write_index(batch_groups):
    # Generate the dictionary
    dict = {}
    for batch in batch_groups:
        # print(batch)
        url = apiIndex + batch + '/'
        count = len(batch_groups[batch].keys())
        dict[batch] = { 'batch': batch, 'url': url, 'count': count }

    filename = "../people/students/index.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(dict, indent = 4))

def write_batches(batch_groups):
    for batch in batch_groups:
        # print(batch)
        filename = "../people/students/" + batch + "/index.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # print(json.dumps(batch_groups[batch], indent = 4))

        with open(filename, "w") as f:
            f.write(json.dumps(batch_groups[batch], indent = 4))

def emailFilter(email):
    if email != "":
        words = email.split('@')
        return { 'name':words[0], 'domain':words[1] }
    else:
        return ""

# ------------------------------------------------------------------------------
r = requests.get(apiSource)
batch_groups = {}

# Fetch data
if r.status_code==200:
    data = json.loads(r.text)
    # print(data)

    for eNumber in data:
        # print(data[eNumber])

        # Split the email address to avoid spaming
        data[eNumber]['emails']['personal'] = emailFilter(data[eNumber]['emails']['personal'])
        data[eNumber]['emails']['faculty'] = emailFilter(data[eNumber]['emails']['faculty'])

        batch = data[eNumber]['batch']
        if batch not in batch_groups: batch_groups[batch] = {}
        batch_groups[batch][eNumber] = data[eNumber]


# Write the index file for the students
write_index(batch_groups)

# Create files for each batch
write_batches(batch_groups)
