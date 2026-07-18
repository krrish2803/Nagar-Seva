"""Notification utilities for email, SMS, and push delivery."""

from typing import Optional, List
import smtplib
from email.message import EmailMessage
import httpx

from app.config import settings


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> bool:
    """
    Send email notification.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        html_body: Email body (HTML)

    Returns:
        True if successful
    """
    if not settings.enable_email_notifications:
        print(f"[MOCK EMAIL] To: {to_email}")
        print(f"[MOCK EMAIL] Subject: {subject}")
        print(f"[MOCK EMAIL] Body: {body}")
        return True

    try:
        message = EmailMessage()
        message["From"] = settings.smtp_username or "no-reply@nagarseva.local"
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        if html_body:
            message.add_alternative(html_body, subtype="html")

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as smtp:
            smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)

        print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")
        return False


async def send_sms(phone_number: str, message: str) -> bool:
    """
    Send SMS notification.

    Args:
        phone_number: Recipient phone number
        message: SMS message

    Returns:
        True if successful
    """
    if not settings.enable_sms_notifications:
        print(f"[MOCK SMS] To: {phone_number}")
        print(f"[MOCK SMS] Message: {message}")
        return True

    if not settings.sms_api_url or not settings.sms_api_key:
        print("[SMS ERROR] SMS enabled but SMS_API_URL or SMS_API_KEY is missing")
        return False

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                settings.sms_api_url,
                headers={
                    "Authorization": f"Bearer {settings.sms_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "to": phone_number,
                    "message": message,
                    "sender_id": settings.sms_sender_id or "NagarSeva",
                },
            )
            response.raise_for_status()
        print(f"[SMS SENT] To: {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"[SMS ERROR] Failed to send to {phone_number}: {e}")
        return False


async def send_push_notification(
    user_id: str, title: str, body: str, data: Optional[dict] = None
) -> bool:
    """
    Send push notification.

    Args:
        user_id: User ID
        title: Notification title
        body: Notification body
        data: Additional data

    Returns:
        True if successful
    """
    if not settings.enable_push_notifications:
        print(f"[MOCK PUSH] To: {user_id}, Title: {title}, Body: {body}")
        if data:
            print(f"[MOCK PUSH] Data: {data}")
        return True

    if not settings.push_api_url or not settings.push_api_key:
        print("[PUSH ERROR] Push enabled but PUSH_API_URL or PUSH_API_KEY is missing")
        return False

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                settings.push_api_url,
                headers={
                    "Authorization": f"Bearer {settings.push_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "user_id": user_id,
                    "title": title,
                    "body": body,
                    "data": data or {},
                },
            )
            response.raise_for_status()
        print(f"[PUSH SENT] To: {user_id}, Title: {title}")
        return True
    except Exception as e:
        print(f"[PUSH ERROR] Failed to send to {user_id}: {e}")
        return False


async def send_complaint_confirmation(
    citizen_email: str, citizen_name: str, complaint_id: str
) -> bool:
    """
    Send complaint submission confirmation email.

    Args:
        citizen_email: Citizen email
        citizen_name: Citizen name
        complaint_id: Complaint ID

    Returns:
        True if successful
    """
    subject = "Complaint Submitted Successfully - NagarSeva"
    body = f"""
Dear {citizen_name},

Thank you for reporting the civic issue. Your complaint has been successfully submitted and assigned a tracking ID: {complaint_id}

You can track the progress of your complaint at: https://nagarseva.local/complaints/{complaint_id}

We will notify you when your complaint is assigned to an official and updated on progress.

Best regards,
NagarSeva Team
"""
    return await send_email(citizen_email, subject, body)


async def send_assignment_notification(
    official_email: str,
    official_name: str,
    complaint_id: str,
    issue_title: str,
    location: str,
) -> bool:
    """
    Send assignment notification to official.

    Args:
        official_email: Official email
        official_name: Official name
        complaint_id: Complaint ID
        issue_title: Issue title
        location: Location address

    Returns:
        True if successful
    """
    subject = f"New Complaint Assigned - {issue_title}"
    body = f"""
Dear {official_name},

A new complaint has been assigned to you.

Complaint ID: {complaint_id}
Issue: {issue_title}
Location: {location}

Please log in to the NagarSeva system to view details and take action.

Best regards,
NagarSeva System
"""
    return await send_email(official_email, subject, body)


async def send_escalation_notification(
    official_email: str,
    official_name: str,
    complaint_id: str,
    reason: str,
    escalation_level: str,
) -> bool:
    """
    Send escalation notification.

    Args:
        official_email: Official email
        official_name: Official name
        complaint_id: Complaint ID
        reason: Escalation reason
        escalation_level: Escalation level name

    Returns:
        True if successful
    """
    subject = f"Complaint Escalated - {complaint_id}"
    body = f"""
Dear {official_name},

A complaint has been escalated to you due to: {reason}

Complaint ID: {complaint_id}
Escalation Level: {escalation_level}

Please review and take appropriate action.

Best regards,
NagarSeva System
"""
    return await send_email(official_email, subject, body)


async def send_resolution_notification(
    citizen_email: str,
    citizen_name: str,
    complaint_id: str,
    resolution_note: str,
) -> bool:
    """
    Send resolution notification to citizen.

    Args:
        citizen_email: Citizen email
        citizen_name: Citizen name
        complaint_id: Complaint ID
        resolution_note: Resolution details

    Returns:
        True if successful
    """
    subject = f"Your Complaint Has Been Resolved - {complaint_id}"
    body = f"""
Dear {citizen_name},

We are pleased to inform you that your complaint has been resolved.

Complaint ID: {complaint_id}
Resolution Details: {resolution_note}

Please rate our service at: https://nagarseva.local/complaints/{complaint_id}/rate

Thank you for using NagarSeva!

Best regards,
NagarSeva Team
"""
    return await send_email(citizen_email, subject, body)
