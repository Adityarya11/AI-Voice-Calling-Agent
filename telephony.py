import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def place_interactive_call(audio_filename: str, user_id: str):
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")
    
    # Check for NGROK_URL or fallback to BASE_URL
    NGROK_URL = os.getenv("NGROK_URL", os.getenv("BASE_URL")) 
    SIMULATE = os.getenv("SIMULATE_TELEPHONY", "true").lower() == "true"

    if SIMULATE or not TWILIO_ACCOUNT_SID:
        print(f"Telephony simulated. Audio file ready: {audio_filename}")
        return "simulated_call_id", "simulated"

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    base_filename = os.path.basename(audio_filename)
    audio_url = f"{NGROK_URL}/static/{base_filename}"
    
    # The URL Twilio will hit with the transcribed user speech
    process_url = f"{NGROK_URL}/api/process?user_id={user_id}"
    
    # TwiML logic: Gather speech, play the greeting, then POST to our API
    twiml = f'''
<Response>
    <Gather
        input="speech"
        action="{process_url}"
        method="POST"
        speechTimeout="auto"
        speechModel="phone_call"
        language="en-IN"
    >
        <Play>{audio_url}</Play>
    </Gather>
</Response>
'''
    
    call = client.calls.create(
        to=MY_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        twiml=twiml
    )
    return call.sid, call.status