# CampusSlot email notifications

CampusSlot uses email only. WhatsApp/Twilio integration has been removed.

## Configure Gmail SMTP
1. Copy `.env.example` to `.env`.
2. Set `SMTP_USERNAME` to your Gmail address.
3. Create a Google App Password and put it in `SMTP_PASSWORD` (not your normal Gmail password).
4. Set `MAIL_FROM=CampusSlot <yourgmail@gmail.com>` and `BASE_URL` to the address students and teachers use.
5. Restart the app. Use the admin notification status check and notification test to verify delivery.

## Email actions
New-booking emails include secure, time-limited teacher actions for Confirm, Reject request, Cancel, Complete, and Update date/time. The reschedule form validates future dates, meeting duration, and overlapping slots, then emails both parties with the new schedule. Actions open a review page and require a final confirmation click; link previews cannot change meeting status. Each link is bound to a teacher, appointment, and appointment version, and expires after 72 hours. Teacher and student sign-in links are included, and the teacher dashboard link can be used to manage/update the meeting after signing in.

Email cannot be delivered until real SMTP credentials are configured. Never commit `.env` or publish app passwords.
