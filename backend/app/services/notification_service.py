import os
from dotenv import load_dotenv

# Load env variables before initializing module-level vars
load_dotenv()

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Conditionally import twilio - server won't crash if not installed
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TwilioClient = None
    TWILIO_AVAILABLE = False

# Configure logger for notifications
logger = logging.getLogger(__name__)

# --- Email Configuration ---
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "civicapp@noreply.com")

# --- SMS Configuration ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip('"\' ')
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip('"\' ')
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "").strip('"\' ')
TWILIO_MESSAGING_SERVICE_SID = os.getenv("TWILIO_MESSAGING_SERVICE_SID", "").strip('"\' ')

def send_email(to_email: str, subject: str, body: str):
    """Send an email using SMTP or fallback to terminal mock."""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning(f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {body}")
        print(f"\n--- [MOCK NOTIFICATION: EMAIL] ---\nTo: {to_email}\nSubject: {subject}\nBody: {body}\n----------------------------------\n")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_sms(to_phone: str, body: str):
    """Send an SMS using Twilio or fallback to terminal mock."""
    if not TWILIO_AVAILABLE:
        print(f"\n--- [MOCK NOTIFICATION: SMS (twilio not installed)] ---\nTo: {to_phone}\nBody: {body}\n--------------------------------\n")
        return True
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        logger.warning(f"[MOCK SMS] To: {to_phone} | Body: {body}")
        print(f"\n--- [MOCK NOTIFICATION: SMS] ---\nTo: {to_phone}\nBody: {body}\n--------------------------------\n")
        return True

    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Use Messaging Service SID if available, otherwise use Phone Number
        message_params = {
            "body": body,
            "to": to_phone
        }
        
        if TWILIO_MESSAGING_SERVICE_SID:
            message_params["messaging_service_sid"] = TWILIO_MESSAGING_SERVICE_SID
        else:
            message_params["from_"] = TWILIO_PHONE_NUMBER
            
        message = client.messages.create(**message_params)
        logger.info(f"SMS sent successfully to {to_phone}. SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS to {to_phone}: {str(e)}")
        return False

def notify_status_change(complaint_id: int, new_status: str, user_email: str, user_phone: str = None):
    """
    Constructs the message payload and dispatches both Email and SMS notifications.
    Intended to be run as a background task.
    """
    subject = f"CivicApp Update: Complaint #{complaint_id} Status Changed"
    
    email_body = f"""
    <html>
        <body>
            <h3>CivicApp Notification</h3>
            <p>Your civic issue complaint (<strong>#{complaint_id}</strong>) has a new status update.</p>
            <p>Current Status: <strong style="color: #2e7d32;">{new_status}</strong></p>
            <br/>
            <p>You can track the full progress of your complaint on your <a href="http://localhost:5173/track">Dashboard Timeline</a>.</p>
            <p>Thank you for helping keep our city clean and safe!</p>
            <p><em>- The Civic Issue Management Team</em></p>
        </body>
    </html>
    """
    
    sms_body = f"CivicApp Update: Your complaint #{complaint_id} is now '{new_status}'. Check your dashboard for details."

    # 1. Dispatch Email (if we have an email)
    if user_email and "@" in user_email:
        send_email(user_email, subject, email_body)
        
    # 2. Dispatch SMS
    if user_phone:
        # Clean the phone number (remove spaces, hyphens, parentheses)
        clean_phone = "".join(filter(str.isdigit, user_phone))
        
        # If it doesn't already have the + prefix, handle it
        if user_phone.startswith('+'):
            formatted_phone = user_phone.replace(" ", "").replace("-", "")
        else:
            # Assume India (+91) if no country code provided, but handle 10-digit vs full
            if len(clean_phone) == 10:
                formatted_phone = f"+91{clean_phone}"
            else:
                formatted_phone = f"+{clean_phone}"
                
        send_sms(formatted_phone, sms_body)
    else:
        logger.warning(f"No phone number on file for Complaint #{complaint_id}. Skipping real SMS and printing mock.")
        print(f"\n--- [MOCK NOTIFICATION: SMS] ---\nTo: (No Phone Provided in Profile)\nBody: {sms_body}\n--------------------------------\n")
    
    return True
