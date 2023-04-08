# REQUIREMENTS ------------
# pip install requests
# -------------------------

import requests
import json
import os


class Notifications:
    def __init__(self, author, workflow):
        self.author = author
        self.workflow = workflow

    def get_webhook_url(self):
        return os.environ['webhook_url']

    def post_discord_message(self, data):
        headers = {
            'Content-Type': 'application/json'
        }
        # print(json.dumps(data, indent=4))
        response = requests.post(
            self.get_webhook_url(), headers=headers, data=json.dumps(data))
        if response.status_code == 204:
            print("Message sent successfully!")
        else:
            print("Error sending message. Response:")
            print(response)

    def send(self, log_level, author, workflow, msg, description):
        notification_type = {
            "warning": {
                "color": 15258703,
                "icon": ":flushed:"
            },
            "error": {
                "color": 16056320,
                "icon": ":smiling_imp:"
            },
            "info": {
                "color": 62830,
                "icon": ":bulb:"
            }
        }
        level = log_level if log_level in notification_type else "info"

        data = {
            "username": "GitHub Actions",
            "embeds": [
                {
                    "title": "{0} {1}".format(notification_type[level]["icon"], workflow),
                    "url": "",
                    "description": msg,
                    "color": notification_type[level]["color"],
                    "fields": [
                        {
                            "name": "Desc: ",
                            "value": description,
                            "inline": True
                        }
                    ]
                }
            ]
        }
        self.post_discord_message(data)

    def log(self, msg, description=''):
        self.send("log", self.author, self.workflow, msg, description)

    def warning(self, msg, description=''):
        self.send("warning", self.author, self.workflow, msg, description)

    def debug(self, msg, description=''):
        self.send("debug", self.author, self.workflow, msg, description)
