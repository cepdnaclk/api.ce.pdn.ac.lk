---
layout: default
permalink: '/docs/students'
title: 'Students Data API'

---

<h1>{{ page.title }}</h1>

### Batch Information:
You can access the batch information via following API

```bash
GET: {{ site.url }}/people/students/
```

#### Example:

API Endpoint:
<a href="{{ '/people/students/' | relative_url }}" target="_blank">
{{ site.url }}/people/students/</a>

##### Request
```bash
GET: {{ site.url }}/people/students/
```

##### Response
```json
{
    "E14": {
        "batch": "E14",
        "url": "https://cepdnaclk.github.io/api.ce.pdn.ac.lk/students/E14/",
        "count": 62
    },
    ...
}
```

##### Format

| Parameter 	| Description 	| Example 	|
|---	|---	|---	|
| batch 	| Batch ID  	| E14 	|
| url 	| API endpoint that can be used to get students in the selected batch 	| https://cepdnaclk.github.io/api.ce.pdn.ac.lk/students/E14/ 	|
| count 	| Number of students in the selected batch 	| 62 	|
{: .mb-5 .table .table-striped .table-bordered }

### Batch-wise Student Information:

You can access the student details via following API  

```bash
GET: {{ site.url }}/people/students/{batch}/
```

#### Example:

API Endpoint:
<a href="{{ '/people/students/E15' | relative_url }}" target="_blank">
{{ site.url }}/people/students/E15/</a>

##### Request
```bash
GET: {{ site.url }}/people/students/E15/
```
##### Response
```json
{
    "E/15/999": {
        "eNumber": "E/15/999",
        "batch": "E15",
        "honorific": "Mr.",
        "full_name": "Herath Mudiyanselage Amal Herath",
        "name_with_initials": "Herath H.M.A.",
        "preferred_short_name": "Amal",
        "preferred_long_name": "Amal Herath",
        "emails": {
           "personal": {"name": "amal96", "domain": "gmail.com"},
           "faculty": {"name": "e15999", "domain": "eng.pdn.ac.lk"}
        },
        "location": "",
        "profile_image": "https://cepdnaclk.github.io/people.ce.pdn.ac.lk/images/students/e15/e15999.jpg",
        "urls": {
           "cv": "https://amalherath.com/cv.pdf",
           "website": "https://amalherath.com/",
           "linkedin": "https://www.linkedin.com/in/amal-herath/",
           "github": "https://github.com/AmalH/",
           "facebook": "#",
           "researchgate": "#",
           "twitter": "#"
        }
    },
    ...
}
```

##### Format

| Parameter 	| Description 	| Example 	|
|---	|---	|---	|
| eNumber 	| E Number  	| E/15/999	|
| batch 	| Batch ID  	| E15 	|
| honorific	| Title   | Mr.
| full_name	|    | Herath Mudiyanselage Amal Herath
| name_with_initials	|    | Herath H.M.A.
| preferred_short_name	|    | Amal
| preferred_long_name	|    | Amal Herath
| emails.personal	| Personal Email Address   | {"name": "amal96", "domain": "gmail.com"}
| emails.faculty	| Faculty Email Address   | {"name": "e15999", "domain": "eng.pdn.ac.lk"}
| location	| Home Town (optional)   |
| profile_image	| URL of the profile picture  |
| urls.cv	| URL to the CV  | https://amalherath.com/cv.pdf
| urls.website	| URL to the personal website (optional)   |
| urls.linkedin	| Linkedin profile URL | https://www.linkedin.com/in/amal-herath/
| urls.github	| GitHub profile URL | https://github.com/AmalH/
| urls.researchgate	| Researchgate profile URL (optional) |
| urls.facebook	| Facebook profile URL (optional) |
| urls.twitter	| Twitter profile URL (optional) |
{: .mb-5 .table .table-striped .table-bordered }
