import requests
import json
import os
from datetime import date, datetime
from notifications import Notifications

notify = Notifications("api.ce.pdn.ac.lk", "Workflow Status")

organization = "cepdnaclk"
repositories = [
    "api.ce.pdn.ac.lk",
    "projects.ce.pdn.ac.lk",
    "people.ce.pdn.ac.lk",
    "publications",
]
STATUS_LIST = {"100": "PASS", "010": "NO STATUS", "001": "FAILLING"}

workflows = []


def getStatus(badge_url):
    response = requests.request("GET", badge_url, headers={}, data={})

    if response.status_code == 200:
        content = response.text
        isPassing = 1 if content.find("passing") >= 0 else 0
        isNoStatus = 1 if content.find("no status") >= 0 else 0
        isFailling = 1 if content.find("failing") >= 0 else 0
        statusResponse = "{}{}{}".format(isPassing, isNoStatus, isFailling)
        return (
            STATUS_LIST[statusResponse] if statusResponse in STATUS_LIST else "UNKNOWN"
        )
    else:
        return "UNAVAILABLE"


# Collect the workflow data
for repo in repositories:
    print("\n{}".format(repo))

    url = "https://api.github.com/repos/{}/{}/actions/workflows".format(
        organization, repo
    )
    r = requests.get(url)

    if r.status_code == 200:
        data = json.loads(r.text)

        for workflow in data["workflows"]:
            # This is to handle page-build-actions

            badge_url = workflow["badge_url"].replace(
                "workflows/pages-build-deployment",
                "actions/workflows/pages/pages-build-deployment",
            )

            workflow = {
                "id": workflow["id"],
                "repository": repo,
                "name": workflow["name"],
                "state": workflow["state"],
                "urls": {
                    "api": workflow["url"],
                    "html": workflow["html_url"],
                    "badge": badge_url,
                },
                "status": getStatus(badge_url),
            }
            workflows.append(workflow)

            print(">> {} | {}".format(workflow["name"], workflow["status"]))

            # Status Check
            if workflow["status"] == "FAILLING":
                print(
                    "\t Error | Workflow failed:",
                    workflow["name"],
                    workflow["repository"],
                    workflow["urls"]["html"],
                )
                notify.error(
                    "Workflow Build Error",
                    "Workflow `{0}` in the repository, `{1}` got failed last time !\n{2}".format(
                        workflow["name"],
                        workflow["repository"],
                        workflow["urls"]["html"],
                    ),
                )
            elif workflow["status"] == "UNAVAILABLE":
                print("\t Error | Status Unavailable: ", badge_url)
                notify.error(
                    "Workflow Status Reading Error",
                    "Workflow status `{0}` in the repository, `{1}` reading failed.\n{2}".format(
                        workflow["name"], workflow["repository"], badge_url
                    ),
                )
    else:
        print("\t Error | API Unavailable: ", url)
        notify.error(
            "API not available",
            "{} is not accessible. Response code = `{}`".format(url, r.status_code),
        )


# Write the workflow details
filename = "../workflows/v1/index.json"
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w") as f:
    f.write(json.dumps(workflows, indent=4))
