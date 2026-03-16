import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Ensure these are in your .env file
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER') # e.g., +1234567890
MY_PHONE_NUMBER = os.getenv('MY_PHONE_NUMBER')         # Your verified Indian number
NGROK_URL = os.getenv('BASE_URL')                      # e.g., https://xyz.ngrok-free.app

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def make_call():
    call = client.calls.create(
        to=MY_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{NGROK_URL}/api/voice",
        method="POST"
    )
    print(f"Call initiated! SID: {call.sid}")

if __name__ == "__main__":
    make_call()
