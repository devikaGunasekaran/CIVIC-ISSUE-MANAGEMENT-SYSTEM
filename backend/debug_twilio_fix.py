import os
from dotenv import load_dotenv

load_dotenv()

sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")
phone = os.getenv("TWILIO_PHONE_NUMBER")

print(f"SID: [{sid}] (length: {len(sid) if sid else 0})")
print(f"Token: [{token[:4] if token else 'None'}...] (length: {len(token) if token else 0})")
print(f"From Phone: [{phone}]")

from twilio.rest import Client

try:
    # Manual cleanup in case .env has literal quotes
    clean_sid = sid.strip('"\' ') if sid else ""
    clean_token = token.strip('"\' ') if token else ""
    clean_from = phone.strip('"\' ') if phone else ""
    
    print(f"Clean SID: [{clean_sid}]")
    
    client = Client(clean_sid, clean_token)
    print("Attempting to fetch account details...")
    account = client.api.accounts(clean_sid).fetch()
    print(f"Account Name: {account.friendly_name}")
    print("Credentials verified successfully!")
except Exception as e:
    print(f"Verification Failed: {e}")
