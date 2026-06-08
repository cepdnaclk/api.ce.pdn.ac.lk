import logging
import os
import re
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

SENSITIVE_ENV_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "WEBHOOK")
EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def sanitize_text(value: Any) -> str:
    """Remove known secret values from text before logging or notifying."""
    text = str(value)
    for name, secret in os.environ.items():
        if not secret or len(secret) < 8:
            continue
        if any(marker in name.upper() for marker in SENSITIVE_ENV_MARKERS):
            text = text.replace(secret, "***REDACTED***")
    return text


def format_exception(exc: BaseException) -> str:
    """Return a sanitized stack trace for observability without leaking secrets."""
    return sanitize_text(
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    )


def env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def validate_email_address(email: Any) -> bool:
    """Validate an email address using a conservative syntax check."""
    if not isinstance(email, str):
        return False
    candidate = email.strip()
    if len(candidate) > 254:
        return False
    return EMAIL_REGEX.fullmatch(candidate) is not None


def load_text_file(path: Path) -> str:
    """Load a required text file and fail clearly when it is missing."""
    if not path.is_file():
        raise FileNotFoundError(f"Required file does not exist: {path}")
    return path.read_text(encoding="utf-8")


def send_notification(
    notifier: Any, level: str, message: str, description: str = ""
) -> bool:
    """Send a workflow notification and convert notification failures into warnings."""
    try:
        notify = getattr(notifier, level, notifier.info)
        notify(sanitize_text(message), sanitize_text(description))
        return True
    except Exception as exc:  # noqa: BLE001 - notifications must not hide workflow state.
        logging.getLogger("publication_reminder").warning(
            "notification_failed level=%s error=%s",
            level,
            sanitize_text(exc),
            exc_info=True,
        )
        return False


# Get the student JSON object
def getStudent(apiBase, students_dict, eNumber):
    student = {}
    if eNumber in students_dict:
        # Check with the details available in the student API
        person_from_api = students_dict[eNumber]

        # Select the best available name
        if person_from_api["name_with_initials"].strip() != "":
            name = person_from_api["name_with_initials"]
        elif person_from_api["preferred_long_name"].strip() != "":
            name = person_from_api["preferred_long_name"]
        elif person_from_api["full_name"].strip() != "":
            name = person_from_api["full_name"]

        # Construct and select the Email address
        if "emails" in person_from_api:
            # Try faculty email first
            faculty_email = person_from_api["emails"]["faculty"]
            personal_email = person_from_api["emails"]["personal"]

            if faculty_email["name"] != "":
                email = (
                    faculty_email["name"].strip()
                    + "@"
                    + faculty_email["domain"].strip()
                )
            elif personal_email["name"] != "":
                email = (
                    personal_email["name"].strip()
                    + "@"
                    + personal_email["domain"].strip()
                )
            else:
                email = "#"

        # Get the profile image or set a default one
        if "profile_image" in person_from_api:
            if "profile_image" in person_from_api:
                profile_image = person_from_api["profile_image"]
            else:
                profile_image = DEFAULT_PROFILE_IMAGE
        else:
            profile_image = DEFAULT_PROFILE_IMAGE

        profile_url = (
            person_from_api["profile_page"]
            if "profile_page" in person_from_api
            else "#"
        )
        profile_api = apiBase + "/people/v1/students/" + eNumber.replace("E/", "E")

        student = {
            "type": "STUDENT",
            "id": eNumber,
            "name": name.strip(),
            "email": email,
            "profile_image": profile_image.strip(),
            "profile_url": profile_url.strip(),
        }

    else:
        student = None

    return student


# Get the staff JSON object
def getStaff(apiBase, staff_dict, email):
    staff = {}
    email_id = email.split("@")[0]

    if email_id in staff_dict:
        # Check with the details available in the staff API
        person_from_api = staff_dict[email]

        # Get the profile image or set a default one
        if "profile_image" in person_from_api:
            if "profile_image" in person_from_api:
                profile_image = person_from_api["profile_image"]
            else:
                profile_image = DEFAULT_PROFILE_IMAGE
        else:
            profile_image = DEFAULT_PROFILE_IMAGE

        name = person_from_api["name"].strip()
        email = person_from_api["email"].strip()

        profile_url = (
            person_from_api["profile_url"] if "profile_url" in person_from_api else "#"
        )
        profile_api = apiBase + apiBase + "/people/v1/staff/" + email_id

        staff = {
            "type": "STAFF",
            "id": email_id,
            "name": name,
            "email": email,
            "profile_image": profile_image,
            "profile_url": profile_url,
        }

    else:
        staff = None

    return staff


def strip_strings(d):
    for key, value in d.items():
        if isinstance(value, dict):
            strip_strings(value)  # Recursively strip strings in nested dictionaries
        elif isinstance(value, str):
            d[key] = value.strip()  # Strip whitespace characters from string values
