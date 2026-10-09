"""Email-only notification dispatcher for CampusSlot."""
from flask import current_app
from app.services.email_service import send_appointment_email, send_registration_email
from app import db
from app.models.notification_log import NotificationLog


def notify_appointment(appointment, event="confirmed"):
    result = {"email": {"sent": 0, "attempted": 0, "errors": []}}
    try:
        result["email"] = send_appointment_email(appointment, event)
    except Exception as exc:
        result["email"]["errors"] = [str(exc)]
        current_app.logger.exception("CampusSlot email dispatcher failed | appointment=%s | event=%s", appointment.tracking_id, event)
    try:
        channel_result = result["email"]
        errors = channel_result.get("errors") or []
        attempted = int(channel_result.get("attempted") or 0)
        sent = int(channel_result.get("sent") or 0)
        status = "sent" if sent else ("failed" if errors else "skipped")
        db.session.add(NotificationLog(
            appointment_id=appointment.id, channel="email",
            recipient="multiple" if attempted > 1 else "configured-recipient",
            event=event, status=status,
            error_message=" | ".join(errors[:5]) if errors else None,
            attempt_count=max(attempted, 1),
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("CampusSlot email audit logging failed | appointment=%s | event=%s", appointment.tracking_id, event)
    current_app.logger.info("CampusSlot EMAIL RESULT | appointment=%s | event=%s | email=%s/%s", appointment.tracking_id, event, result["email"]["sent"], result["email"]["attempted"])
    return result


def notify_registration(record, event="submitted"):
    try:
        return {"email": send_registration_email(record, event)}
    except Exception as exc:
        current_app.logger.exception("CampusSlot registration email failed | registration=%s | event=%s", getattr(record, "registration_id", None), event)
        return {"email": {"sent": 0, "attempted": 1, "errors": [str(exc)]}}


def enqueue_appointment_notification(appointment, event="confirmed"):
    """Queue email after the booking transaction; fall back to synchronous delivery locally."""
    broker_url = current_app.config.get("CELERY_BROKER_URL")
    if not broker_url:
        return notify_appointment(appointment, event)
    try:
        from celery_app import send_appointment_notification_task
        send_appointment_notification_task.delay(appointment.id, event)
        current_app.logger.info(
            "CampusSlot email queued | appointment=%s | event=%s",
            appointment.tracking_id, event,
        )
        return {"email": {"sent": 0, "attempted": 0, "errors": [], "queued": True}}
    except Exception:
        # Do not silently lose notifications if the broker is misconfigured.
        current_app.logger.exception("Email queue unavailable; falling back to direct send")
        return notify_appointment(appointment, event)


def enqueue_registration_notification(record, event="submitted"):
    """Queue registration email by stable database ID, never by passing ORM objects."""
    broker_url = current_app.config.get("CELERY_BROKER_URL")
    if not broker_url:
        return notify_registration(record, event)
    role = "teacher" if record.__class__.__name__ == "Business" else "student"
    try:
        from celery_app import send_registration_notification_task
        send_registration_notification_task.delay(role, record.id, event)
        current_app.logger.info(
            "CampusSlot registration email queued | role=%s | id=%s | event=%s",
            role, record.id, event,
        )
        return {"email": {"sent": 0, "attempted": 0, "errors": [], "queued": True}}
    except Exception:
        current_app.logger.exception("Registration email queue unavailable; falling back to direct send")
        return notify_registration(record, event)
