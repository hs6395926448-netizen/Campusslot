"""Static checks for cloud email and background queue wiring."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CloudEmailQueueTests(unittest.TestCase):
    def test_resend_and_queue_configuration_exists(self):
        config = (ROOT / "config.py").read_text(encoding="utf-8")
        render = (ROOT / "render.yaml").read_text(encoding="utf-8")
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("RESEND_API_KEY", config)
        self.assertIn("CELERY_BROKER_URL", config)
        self.assertIn("RESEND_API_KEY", render)
        self.assertIn("CELERY_BROKER_URL", render)
        self.assertIn("celery[redis]", requirements)

    def test_normal_routes_enqueue_notifications(self):
        booking = (ROOT / "app/routes/booking.py").read_text(encoding="utf-8")
        student = (ROOT / "app/routes/student.py").read_text(encoding="utf-8")
        admin = (ROOT / "app/routes/admin.py").read_text(encoding="utf-8")
        self.assertIn("enqueue_appointment_notification", booking)
        self.assertIn("enqueue_appointment_notification", student)
        self.assertIn("enqueue_registration_notification", student)
        # Admin test endpoint remains synchronous so it can show real delivery status.
        self.assertIn("result = notify_appointment(appointment", admin)

    def test_python_sources_parse(self):
        paths = [
            ROOT / "config.py",
            ROOT / "celery_app.py",
            ROOT / "app/services/notification_service.py",
            ROOT / "app/services/email_service.py",
            ROOT / "app/routes/booking.py",
            ROOT / "app/routes/admin.py",
            ROOT / "app/routes/student.py",
        ]
        for path in paths:
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
