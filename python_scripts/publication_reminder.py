"""Monthly academic staff publication update reminder workflow."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests
from notifications import Notifications
from utility import (
    env_bool,
    format_exception,
    load_text_file,
    send_notification,
    validate_email_address,
)

notify = Notifications("api.ce.pdn.ac.lk", "Reminder Workflow")


DEFAULT_EMAIL_API_URL = "https://portal.ce.pdn.ac.lk/api/email/v1/send"

STATUS_SUCCESS = "success"
STATUS_PARTIAL_SUCCESS = "partial_success"
STATUS_FAILED = "failed"

# Workflow configuration. Secrets and deployment-specific values are injected by
# GitHub Actions as environment variables.
TAXONOMY_API_URL = (
    "https://portal.ce.pdn.ac.lk/api/taxonomy/v2/cepdnaclk/term/academic-staff"
)
EMAIL_API_URL = "https://portal.ce.pdn.ac.lk/api/email/v1/send"
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "")

EMAIL_TO = "webmaster.github.ce@eng.pdn.ac.lk"
REPLY_TO = "webmaster.github.ce@eng.pdn.ac.lk"
EMAIL_SUBJECT = "Monthly publication update reminder"
EMAIL_TEMPLATE_PATH = (
    Path(__file__).resolve().parent / "res" / "publication_reminder_email.html"
)
TIMEOUT_SECONDS = 15

# When DRY_RUN is enabled, the workflow will go through all the steps except the final email sending,
DRY_RUN = env_bool("DRY_RUN", False)

# When FORCE_RUN is enabled, the workflow will run regardless of the date check for the first Monday of the month in Sri Lanka.
FORCE_RUN = env_bool("FORCE_RUN", False)


def is_first_monday_lk(now: datetime | None = None) -> bool:
    """Return True when the given Sri Lanka date is the first Monday of its month."""
    lk_now = now or datetime.now(ZoneInfo("Asia/Colombo"))
    return lk_now.weekday() == 0 and 1 <= lk_now.day <= 7


def extract_staff_list() -> list[dict[str, Any]]:
    """
    Extract staff records from common taxonomy API response containers,
    and prepare a list of email addresses for on-duty staff members.
    """

    response = requests.get(TAXONOMY_API_URL, timeout=TIMEOUT_SECONDS)
    staff_list = []

    print(">> Fetching staff data from taxonomy API...")
    if response.status_code == 200:
        # it is available
        try:
            staff_data = json.loads(response.text)
            for staff_category in staff_data.get("data", {}).get("terms", []):
                print(f"\t Category: {staff_category.get('name')}")

                for staff_member in staff_category.get("terms", {}):
                    staff_name = staff_member.get("name")
                    is_on_duty = (
                        staff_member.get("metadata", {}).get("on_duty") or False
                    )
                    staff_email = staff_member.get("metadata", {}).get("email")

                    print(f"\t\t{staff_name} (On Duty={is_on_duty})")
                    if is_on_duty:
                        if validate_email_address(staff_email):
                            staff_list.append(staff_email)

        except json.JSONDecodeError as exc:
            description = f"Failed to parse taxonomy API response as JSON. Status code: {response.status_code}, Response: {response.text[:500]}"
            send_notification(notify, "error", "FAILED", description)
            raise ValueError(f"Expected JSON response from {TAXONOMY_API_URL}") from exc

    return staff_list


def run_workflow() -> dict[str, Any]:
    """Run the publication reminder workflow and return summary metrics."""

    summary: dict[str, Any] = {
        "eligible_recipients": 0,
        "status": STATUS_FAILED,
        "dry_run": DRY_RUN,
        "force_run": FORCE_RUN,
    }

    print("Starting publication reminder workflow...")
    print(f" Force run: {FORCE_RUN}, Dry run: {DRY_RUN}")

    # Validate the scheduled date
    if not FORCE_RUN and not is_first_monday_lk():
        summary["status"] = STATUS_SUCCESS
        description = "Skipped Publication Reminder because today is not the first Monday in Asia/Colombo."
        send_notification(notify, "info", "SUCCESS", description)
        return summary

    # Validate the configs
    if not DRY_RUN and not EMAIL_API_KEY:
        raise ValueError("EMAIL_API_KEY is required when dry-run mode is disabled")
    if not DRY_RUN and not validate_email_address(EMAIL_TO):
        raise ValueError("'EMAIL_TO' must be a valid email address")
    if REPLY_TO and not validate_email_address(REPLY_TO):
        raise ValueError("'REPLY_TO' must be a valid email address")

    # Email Template
    html_body = load_text_file(EMAIL_TEMPLATE_PATH)

    # Read the staff members list from Taxonomy API
    staff_members = extract_staff_list()
    summary["eligible_recipients"] = len(staff_members)

    print(f"Eligible recipients: {summary['eligible_recipients']}")
    bcc = staff_members.copy()

    payload: dict[str, Any] = {
        "to": ["nuwanjaliyagoda@eng.pdn.ac.lk"],
        # "to": [EMAIL_TO],
        # "bcc": ",".join(staff_members),
        "subject": EMAIL_SUBJECT,
        "reply_to": REPLY_TO,
        "body": html_body,
        "metadata": {
            "workflow": "publication-update",
            "recipient_count": len(bcc),
            "dry_run": DRY_RUN,
            "force_run": FORCE_RUN,
        },
    }

    if DRY_RUN:
        summary["status"] = STATUS_PARTIAL_SUCCESS
        description = (
            f"Dry run mode enabled. Workflow completed without sending emails. "
            f"Eligible recipients: {len(bcc)}."
        )
        send_notification(notify, "warning", "PARTIAL SUCCESS", description)
    else:
        email_response = requests.post(
            EMAIL_API_URL,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": EMAIL_API_KEY,
            },
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )

        if email_response.status_code in {200, 201, 202}:
            summary["emails_sent"] = len(bcc)
            summary["status"] = STATUS_SUCCESS
            description = f"Sent reminder emails to {len(bcc)} recipients."
            send_notification(notify, "info", "SUCCESS", description)
        else:
            summary["emails_failed"] = len(bcc)
            summary["status"] = STATUS_FAILED
            description = (
                f"Failed to send reminder emails. Status code: {email_response.status_code}, "
                f"Response: {email_response.text[:500]}"
            )
            send_notification(notify, "error", "FAILED", description)

    return summary


def main() -> int:
    """CLI entry point."""
    global DRY_RUN, FORCE_RUN

    try:
        summary = run_workflow()
    except Exception as exc:  # noqa: BLE001
        details = format_exception(exc)
        error_payload = {
            "status": "FAILED",
            "message": "Publication reminder workflow failed",
            "details": details[:3500],
        }
        send_notification(
            notify, "error", "FAILED", json.dumps(error_payload, sort_keys=True)
        )
        return 1

    print(json.dumps(summary, indent=2, sort_keys=True))

    if summary["status"] == STATUS_FAILED:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
