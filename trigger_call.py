import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Environment Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER') 
MY_PHONE_NUMBER = os.getenv('MY_PHONE_NUMBER')         # Destination contact array
NGROK_URL = os.getenv('BASE_URL')                      

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
