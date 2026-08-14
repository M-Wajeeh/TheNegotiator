import base64
import logging
import smtplib
from email.mime.text import MIMEText
from app.config import settings

logger = logging.getLogger(__name__)

def send_via_smtp(to_email: str, subject: str, body_text: str) -> dict | None:
    if not (settings.SMTP_SERVER and settings.SMTP_USERNAME and settings.SMTP_PASSWORD):
        return None
    try:
        message = MIMEText(body_text, "plain", "utf-8")
        message["to"] = to_email
        message["from"] = settings.GMAIL_SENDER_EMAIL or settings.SMTP_USERNAME
        message["subject"] = subject

        clean_password = settings.SMTP_PASSWORD.replace(" ", "")

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, clean_password)
            server.send_message(message)

        logger.info(f"SMTP email sent successfully to {to_email}")
        return {
            "status": "sent",
            "message_id": f"smtp-{to_email}",
            "thread_id": "smtp-thread-1",
            "to": to_email,
            "subject": subject
        }
    except Exception as e:
        logger.error(f"Error sending SMTP email: {e}")
        return {"status": "error", "error": str(e)}

def get_gmail_service():
    """
    Initializes and returns the Gmail API service instance using configured credentials.
    Returns None if credentials are not configured (fallback mode).
    """
    if not settings.GMAIL_CREDENTIALS_PATH:
        logger.info("Gmail credentials path not set. Gmail API operating in simulation/mock mode.")
        return None

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(settings.GMAIL_CREDENTIALS_PATH)
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Gmail API client: {e}")
        return None

def create_email_draft(to_email: str, subject: str, body_text: str) -> dict:
    """
    Creates a draft email in Gmail for human review prior to sending.
    """
    service = get_gmail_service()
    if not service:
        logger.info(f"[SIMULATION] Draft created for {to_email}: '{subject}'")
        return {
            "status": "draft_created",
            "simulation": True,
            "draft_id": "simulated-draft-id",
            "to": to_email,
            "subject": subject,
            "body": body_text,
        }

    try:
        message = MIMEText(body_text)
        message["to"] = to_email
        message["from"] = settings.GMAIL_SENDER_EMAIL or "me"
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        draft = service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw_message}}
        ).execute()

        logger.info(f"Gmail Draft successfully created: {draft.get('id')}")
        return {"status": "draft_created", "draft_id": draft.get("id"), "to": to_email, "subject": subject}
    except Exception as e:
        logger.error(f"Error creating Gmail draft: {e}")
        return {"status": "error", "error": str(e)}

def send_vendor_email(to_email: str, subject: str, body_text: str, thread_id: str | None = None) -> dict:
    """
    Sends an automated negotiation email directly to a vendor.
    """
    service = get_gmail_service()
    if service:
        try:
            message = MIMEText(body_text)
            message["to"] = to_email
            message["from"] = settings.GMAIL_SENDER_EMAIL or "me"
            message["subject"] = subject
            
            msg_body = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")}
            if thread_id:
                msg_body["threadId"] = thread_id

            sent_msg = service.users().messages().send(
                userId="me",
                body=msg_body
            ).execute()

            logger.info(f"Gmail negotiation email sent successfully: {sent_msg.get('id')}")
            return {
                "status": "sent",
                "message_id": sent_msg.get("id"),
                "thread_id": sent_msg.get("threadId"),
                "to": to_email,
                "subject": subject
            }
        except Exception as e:
            logger.error(f"Error sending Gmail message via API: {e}")

    # Fallback to SMTP if configured
    if settings.SMTP_SERVER and settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
        return send_via_smtp(to_email, subject, body_text)

    # Simulation fallback
    logger.info(f"[SIMULATION] Email sent to {to_email}: '{subject}'")
    return {
        "status": "sent",
        "simulation": True,
        "message_id": "simulated-msg-id",
        "thread_id": thread_id or "simulated-thread-id",
        "to": to_email,
        "subject": subject,
        "body": body_text,
    }

def check_vendor_responses(thread_id: str) -> dict:
    """
    Polls a specific Gmail thread for vendor counter-offers or replies.
    """
    service = get_gmail_service()
    if not service:
        logger.info(f"[SIMULATION] Checking vendor responses for thread {thread_id}")
        return {
            "status": "completed",
            "simulation": True,
            "thread_id": thread_id,
            "has_new_reply": True,
            "latest_reply": "Vendor: We can offer a discounted rate of $310 for immediate commitment.",
        }

    try:
        thread = service.users().threads().get(userId="me", id=thread_id).execute()
        messages = thread.get("messages", [])
        latest_msg = messages[-1] if messages else {}
        snippet = latest_msg.get("snippet", "")

        return {
            "status": "completed",
            "thread_id": thread_id,
            "message_count": len(messages),
            "snippet": snippet,
        }
    except Exception as e:
        logger.error(f"Error fetching Gmail thread {thread_id}: {e}")
        return {"status": "error", "error": str(e)}
