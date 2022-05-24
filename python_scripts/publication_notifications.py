# REQUIREMENTS ------------
# pip install discordwebhook

# TODO:
# No validation done by assume everything is ok,
# But better to write validation logic too

import json
import os
import requests
from datetime import date, datetime

os.environ['TZ'] = 'Asia/Colombo'
today = datetime.now()

# The time threshold considered for a notification generation
NOTIFICATION_THRESHOLD = 60*60*24

ENDPOINT = "https://discord.com/api/webhooks/978648828565659678/yXTWwVlybPTrzdJ-zFQi_4e7iSrGcJMbcF-ocJ_fStbylGiPi5mSLwju2KlmabPQIZ4A"

# ------------------------------------------------------------------------------

def publish_discord(title, venue, year, authors, doi, tags):
    data = {
        "content": "A new research publication !",
        "username": "api.ce.pdn.ac.lk",
        "avatar_url": "https://api.ce.pdn.ac.lk/assets/img/bot_logo.png",
        "embeds": []
    }
    tag_string = ", ".join(tags)
    authors_string = ", ".join(authors)
    venue_string = venue + "," + year

    embed = {"title": title, "color": "16735232", "fields": []}
    embed['fields'].append({"name": "Published at", "value": venue_string})
    embed['fields'].append({"name": "Authors", "value": authors_string})
    embed['fields'].append({"name": "DOI", "value": doi})
    embed['fields'].append({"name": "Tags", "value": tag_string})

    data['embeds'].append(embed)
    print(json.dumps(data, indent = 4))
    response = requests.post(ENDPOINT, json=data)
    print(response.status_code)
    print(response.content)

# ------------------------------------------------------------------------------

# Gather Publications API data
publications_url = '../publications/v1/all/index.json'

with open(publications_url, 'r') as f:
    publications = json.load(f)

    for pub in publications:

        created_time = datetime.strptime(pub['submitted'], "%Y/%m/%d %H:%M:%S")
        title = pub['title']
        venue = pub['venue']
        year = pub['year']
        authors = pub['authors']
        doi = pub['doi']
        tags = pub['tags']

        duration = today - created_time

        # This is a temp line for testing
        # publish_discord(title, venue, year, authors, doi, tags)
        # break; # Only one so far

        # The publication was submitted within last 24 hours, will send into the Discord Channel, 'publications'
        # TODO: Create a seperate Discord Channel
        if (duration.total_seconds() <= NOTIFICATION_THRESHOLD):
            publish_discord(title, venue, year, authors, doi, tags)
