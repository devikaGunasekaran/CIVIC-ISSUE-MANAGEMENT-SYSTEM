import os
from dotenv import load_dotenv

# Force load latest .env
load_dotenv()

from app.services.notification_service import send_email, send_sms

# Get the keys to check
smtp_user = os.getenv("SMTP_USERNAME")
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
sender_email = os.getenv("SENDER_EMAIL")

print("--------------------------------------------------")
print("TESTING LIVE NOTIFICATION CREDENTIALS")
print("--------------------------------------------------")
print(f"SMTP Username loaded: {'Yes' if smtp_user else 'No'}")
print(f"Twilio SID loaded: {'Yes' if twilio_sid else 'No'}")
print(f"Sender Email loaded: {'Yes' if sender_email else 'No'}")
print("--------------------------------------------------")

if smtp_user and "@" in smtp_user:
    print(f"\n[1/2] Attempting to send test email to {smtp_user}...")
    success = send_email(
        to_email=smtp_user, 
        subject="CivicApp Configuration Test", 
        body="<h1>It Works!</h1><p>Your SMTP credentials are successfully paired with CivicApp!</p>"
    )
    if success:
        print("✅ SUCCESS: Test email dispatched! Check your inbox.")
    else:
        print("❌ FAILED: Could not send test email. Check your console logs or App Password.")
else:
    print("\n[1/2] Skipping email test - no valid SMTP_USERNAME email provided.")

print("\n[2/2] Note: SMS testing via script is skipped as it requires a verified destination number on Twilio Trial accounts.")
print("To test SMS, please register an account on the frontend with a real phone number and update a complaint status.")
print("--------------------------------------------------")
