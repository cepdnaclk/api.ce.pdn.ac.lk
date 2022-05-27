
# Get the student JSON object
def getStudent(apiBase, students_dict, eNumber):
    student = {}
    if eNumber in students_dict:
        # Check with the details available in the student API
        person_from_api = students_dict[eNumber]

        # Select the best available name
        if(person_from_api['name_with_initials'] != ""):
            name = person_from_api["name_with_initials"]
        elif(person_from_api['preferred_long_name'] != ""):
            name = person_from_api["preferred_long_name"]
        elif(person_from_api['full_name'] != ""):
            name = person_from_api["full_name"]

        # Construct and select the Email address
        if 'emails' in person_from_api:
            # Try faculty email first
            faculty_email = person_from_api['emails']['faculty']
            personal_email = person_from_api['emails']['personal']

            if faculty_email['name'] != "":
                email = faculty_email['name'] + '@' + faculty_email['domain']
            elif personal_email['name'] != "":
                email = personal_email['name'] + '@' + personal_email['domain']
            else:
                email = '#'

        # Get the profile image or set a default one
        if 'profile_image' in person_from_api:
            if 'profile_image' in person_from_api:
                profile_image = person_from_api['profile_image']
            else:
                profile_image = DEFAULT_PROFILE_IMAGE
        else:
            profile_image = DEFAULT_PROFILE_IMAGE

        profile_url = person_from_api['profile_page'] if 'profile_page' in person_from_api else "#"
        profile_api = apiBase + "/people/v1/students/" + eNumber.replace("E/", "E")

        student = {
            'type': 'STUDENT', 'id': eNumber,
            'name':name, 'email':email,
            'profile_image':profile_image , 'profile_url':profile_url
        }

    else:
        student = None

    return student


# Get the staff JSON object
def getStaff(apiBase, staff_dict, email):
    staff = {}
    email_id = email.split('@')[0]

    if email_id in staff_dict:
        # Check with the details available in the staff API
        person_from_api = staff_dict[email]

        # Get the profile image or set a default one
        if 'profile_image' in person_from_api:
            if 'profile_image' in person_from_api:
                profile_image = person_from_api['profile_image']
            else:
                profile_image = DEFAULT_PROFILE_IMAGE
        else:
            profile_image = DEFAULT_PROFILE_IMAGE

        name = person_from_api['name']
        email = person_from_api['email']

        profile_url = person_from_api['profile_url'] if 'profile_url' in person_from_api else "#"
        profile_api = apiBase + apiBase + "/people/v1/staff/" + email_id

        staff = {
            'type': 'STAFF', 'id': email_id,
            'name':name, 'email':email,
            'profile_image':profile_image , 'profile_url':profile_url
        }

    else:
        staff = None

    return staff
