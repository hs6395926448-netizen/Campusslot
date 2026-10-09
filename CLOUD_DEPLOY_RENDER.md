# CampusSlot: Render deployment and email setup

## 1. Configure email using the HTTPS API (recommended)

The project supports Resend's HTTPS API, which avoids SMTP port restrictions common on cloud hosts.

1. Create a Resend account and create an API key.
2. Verify a domain you control in Resend. Use a sender address on that verified domain (for example `CampusSlot <notifications@yourdomain.com>`). The `onboarding@resend.dev` sender is only suitable for limited testing and is not a production sender.
3. In Render → `campusslot` web service → Environment, set:
   - `BASE_URL`: the exact public HTTPS URL of the web service, without a trailing slash.
   - `RESEND_API_KEY`: your private Resend API key.
   - `RESEND_FROM_EMAIL`: the sender address/domain verified in Resend.
4. Save changes and redeploy. Do not commit the API key to GitHub or share it in chat.
5. Check Render logs for `CampusSlot EMAIL SENT` or `CampusSlot EMAIL FAILED`.

SMTP remains as a fallback for local development. If you use it, use a Gmail App Password rather than your normal Gmail password. Cloud SMTP may be blocked by the host; the Resend API is preferred.

## 2. Background email queue (optional, for faster buttons)

The web app supports Celery + Redis. When `CELERY_BROKER_URL` is blank, local development sends email synchronously (easy to debug). When it is set, normal booking/rescheduling/cancellation and registration notification emails are queued so the web request does not wait for the provider response. The admin's explicit "test notification" action stays synchronous and reports the actual result.

1. Create a Redis instance with a reachable TLS URL from your hosting provider. Copy its private connection URL; do not use a public Redis URL.
2. Deploy the `campusslot-email-worker` background worker defined in `render.yaml` (worker hosting may incur a charge). If using Blueprint deployment, fill in the worker's `DATABASE_URL`, `SECRET_KEY`, `ADMIN_SECRET_KEY`, `BASE_URL`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, and `CELERY_BROKER_URL` using the same values as the web service.
3. Set `CELERY_BROKER_URL` to the Redis connection URL on BOTH the web service and worker. Redeploy both.
4. Verify the worker logs show it connected to Redis and is consuming `campusslot.send_appointment_notification` or `campusslot.send_registration_notification` tasks.
5. If no broker is configured, the app falls back to synchronous email delivery rather than silently dropping notifications.

Queued tasks retry transient delivery errors up to three times. A queue improves request responsiveness, but it cannot guarantee delivery if Redis/worker/provider configuration is wrong; monitor logs and the notification log.

## 3. Database and public links

- The app uses PostgreSQL on Render through `DATABASE_URL`; local development can use SQLite.
- `BASE_URL` must be the public HTTPS URL. A link containing `localhost` or `127.0.0.1` in an email will not open the deployed app from a phone.
- Render free web instances can spin down when idle, and limited CPU/RAM can make the first request slower. A queue avoids waiting for email delivery, but it does not remove database latency or cold starts.
- The blueprint uses a free web service/database and a Starter background worker. Check current Render pricing and database retention before deploying; plans/pricing can change.
- Never commit `.env`, provider credentials, secret keys, or real user data.
