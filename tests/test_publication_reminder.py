import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python_scripts"))

import publication_reminder as reminder  # noqa: E402


class PublicationReminderTests(TestCase):
    def setUp(self):
        self.original_dry_run = reminder.DRY_RUN
        self.original_force_run = reminder.FORCE_RUN
        self.original_email_api_key = reminder.EMAIL_API_KEY
        self.original_email_to = reminder.EMAIL_TO
        self.original_reply_to = reminder.REPLY_TO
        self.original_template_path = reminder.EMAIL_TEMPLATE_PATH

    def tearDown(self):
        reminder.DRY_RUN = self.original_dry_run
        reminder.FORCE_RUN = self.original_force_run
        reminder.EMAIL_API_KEY = self.original_email_api_key
        reminder.EMAIL_TO = self.original_email_to
        reminder.REPLY_TO = self.original_reply_to
        reminder.EMAIL_TEMPLATE_PATH = self.original_template_path

    def call_silently(self, func, *args, **kwargs):
        with redirect_stdout(io.StringIO()):
            return func(*args, **kwargs)

    def test_is_first_monday_lk(self):
        self.assertTrue(
            reminder.is_first_monday_lk(
                datetime(2026, 6, 1, 6, 0, tzinfo=ZoneInfo("Asia/Colombo"))
            )
        )
        self.assertFalse(
            reminder.is_first_monday_lk(
                datetime(2026, 6, 8, 6, 0, tzinfo=ZoneInfo("Asia/Colombo"))
            )
        )
        self.assertFalse(
            reminder.is_first_monday_lk(
                datetime(2026, 6, 2, 6, 0, tzinfo=ZoneInfo("Asia/Colombo"))
            )
        )

    @patch("publication_reminder.requests.get")
    def test_extract_staff_list_returns_only_on_duty_valid_emails(self, mock_get):
        payload = {
            "data": {
                "terms": [
                    {
                        "name": "Academic Staff",
                        "terms": [
                            {
                                "name": "Valid Staff",
                                "metadata": {
                                    "on_duty": True,
                                    "email": "valid@eng.pdn.ac.lk",
                                },
                            },
                            {
                                "name": "Inactive Staff",
                                "metadata": {
                                    "on_duty": False,
                                    "email": "inactive@eng.pdn.ac.lk",
                                },
                            },
                            {
                                "name": "Invalid Email",
                                "metadata": {
                                    "on_duty": True,
                                    "email": "not-an-email",
                                },
                            },
                            {"name": "Missing Metadata"},
                        ],
                    }
                ]
            }
        }
        mock_get.return_value = SimpleNamespace(
            status_code=200,
            text=json.dumps(payload),
        )

        self.assertEqual(
            self.call_silently(reminder.extract_staff_list),
            ["valid@eng.pdn.ac.lk"],
        )
        mock_get.assert_called_once_with(reminder.TAXONOMY_API_URL, timeout=15)

    @patch("publication_reminder.send_notification")
    @patch("publication_reminder.requests.get")
    def test_extract_staff_list_raises_for_invalid_json(self, mock_get, mock_notify):
        mock_get.return_value = SimpleNamespace(status_code=200, text="{invalid")

        with self.assertRaises(ValueError):
            self.call_silently(reminder.extract_staff_list)

        mock_notify.assert_called_once()
        self.assertEqual(mock_notify.call_args.args[1], "error")
        self.assertEqual(mock_notify.call_args.args[2], "FAILED")

    @patch("publication_reminder.send_notification")
    @patch("publication_reminder.is_first_monday_lk", return_value=False)
    def test_run_workflow_skips_non_first_monday(self, _mock_date, mock_notify):
        reminder.DRY_RUN = False
        reminder.FORCE_RUN = False

        summary = self.call_silently(reminder.run_workflow)

        self.assertEqual(summary["status"], reminder.STATUS_SUCCESS)
        self.assertEqual(summary["eligible_recipients"], 0)
        mock_notify.assert_called_once()
        self.assertEqual(mock_notify.call_args.args[1], "info")
        self.assertEqual(mock_notify.call_args.args[2], "SUCCESS")

    @patch("publication_reminder.send_notification")
    @patch("publication_reminder.extract_staff_list", return_value=["a@eng.pdn.ac.lk"])
    @patch("publication_reminder.load_text_file", return_value="<html></html>")
    @patch("publication_reminder.is_first_monday_lk", return_value=True)
    def test_run_workflow_dry_run_counts_recipients(
        self,
        _mock_date,
        mock_load_template,
        mock_extract_staff,
        mock_notify,
    ):
        reminder.DRY_RUN = True
        reminder.FORCE_RUN = False

        summary = self.call_silently(reminder.run_workflow)

        self.assertEqual(summary["status"], reminder.STATUS_PARTIAL_SUCCESS)
        self.assertEqual(summary["eligible_recipients"], 1)
        self.assertTrue(summary["dry_run"])
        mock_load_template.assert_called_once_with(reminder.EMAIL_TEMPLATE_PATH)
        mock_extract_staff.assert_called_once()
        mock_notify.assert_called_once()
        self.assertEqual(mock_notify.call_args.args[1], "warning")

    @patch("publication_reminder.is_first_monday_lk", return_value=True)
    def test_run_workflow_requires_api_key_for_live_send(self, _mock_date):
        reminder.DRY_RUN = False
        reminder.FORCE_RUN = False
        reminder.EMAIL_API_KEY = ""

        with self.assertRaises(ValueError):
            self.call_silently(reminder.run_workflow)

    @patch("publication_reminder.send_notification")
    @patch("publication_reminder.requests.post")
    @patch(
        "publication_reminder.extract_staff_list",
        return_value=["a@eng.pdn.ac.lk", "b@eng.pdn.ac.lk"],
    )
    @patch("publication_reminder.load_text_file", return_value="<html></html>")
    @patch("publication_reminder.is_first_monday_lk", return_value=True)
    def test_run_workflow_live_send_success(
        self,
        _mock_date,
        _mock_load_template,
        _mock_extract_staff,
        mock_post,
        mock_notify,
    ):
        reminder.DRY_RUN = False
        reminder.FORCE_RUN = False
        reminder.EMAIL_API_KEY = "test-api-key"
        reminder.EMAIL_TO = "webmaster.github.ce@eng.pdn.ac.lk"
        reminder.REPLY_TO = "webmaster.github.ce@eng.pdn.ac.lk"
        mock_post.return_value = SimpleNamespace(status_code=202, text="")

        summary = self.call_silently(reminder.run_workflow)

        self.assertEqual(summary["status"], reminder.STATUS_SUCCESS)
        self.assertEqual(summary["eligible_recipients"], 2)
        self.assertEqual(summary["emails_sent"], 2)
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["X-API-KEY"], "test-api-key")
        self.assertEqual(kwargs["json"]["metadata"]["recipient_count"], 2)
        mock_notify.assert_called_once()
        self.assertEqual(mock_notify.call_args.args[1], "info")
        self.assertEqual(mock_notify.call_args.args[2], "SUCCESS")

    @patch("publication_reminder.send_notification")
    @patch("publication_reminder.requests.post")
    @patch("publication_reminder.extract_staff_list", return_value=["a@eng.pdn.ac.lk"])
    @patch("publication_reminder.load_text_file", return_value="<html></html>")
    @patch("publication_reminder.is_first_monday_lk", return_value=True)
    def test_run_workflow_live_send_failure(
        self,
        _mock_date,
        _mock_load_template,
        _mock_extract_staff,
        mock_post,
        mock_notify,
    ):
        reminder.DRY_RUN = False
        reminder.FORCE_RUN = False
        reminder.EMAIL_API_KEY = "test-api-key"
        reminder.EMAIL_TO = "webmaster.github.ce@eng.pdn.ac.lk"
        reminder.REPLY_TO = "webmaster.github.ce@eng.pdn.ac.lk"
        mock_post.return_value = SimpleNamespace(status_code=500, text="server error")

        summary = self.call_silently(reminder.run_workflow)

        self.assertEqual(summary["status"], reminder.STATUS_FAILED)
        self.assertEqual(summary["eligible_recipients"], 1)
        self.assertEqual(summary["emails_failed"], 1)
        mock_notify.assert_called_once()
        self.assertEqual(mock_notify.call_args.args[1], "error")
        self.assertEqual(mock_notify.call_args.args[2], "FAILED")

    @patch("publication_reminder.run_workflow")
    def test_main_returns_one_for_failed_summary(self, mock_run_workflow):
        mock_run_workflow.return_value = {"status": reminder.STATUS_FAILED}

        self.assertEqual(self.call_silently(reminder.main), 1)

    @patch("publication_reminder.send_notification")
    @patch("publication_reminder.run_workflow", side_effect=RuntimeError("boom"))
    def test_main_reports_exceptions(self, _mock_run_workflow, mock_notify):
        self.assertEqual(self.call_silently(reminder.main), 1)
        mock_notify.assert_called_once()
        self.assertEqual(mock_notify.call_args.args[1], "error")
        self.assertEqual(mock_notify.call_args.args[2], "FAILED")


if __name__ == "__main__":
    main()
