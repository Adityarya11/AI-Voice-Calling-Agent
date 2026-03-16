import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from twilio.twiml.voice_response import VoiceResponse, Gather
from agent import trigger_outbound_call, process_user_speech
from db import Base, engine
from dotenv import load_dotenv

load_dotenv()
Base.metadata.create_all(bind=engine)

os.makedirs(os.getenv("TTS_OUTPUT_DIR", "./audio"), exist_ok=True)

app = FastAPI(title="Riverwood Voice Agent Prototype")
app.mount("/static", StaticFiles(directory=os.getenv("TTS_OUTPUT_DIR", "./audio")), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/trigger/{user_id}")
async def trigger(user_id: str):
    try:
        result = await trigger_outbound_call(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

@app.post("/api/process")
async def twilio_process_speech(request: Request, user_id: str):
    """Webhook Twilio calls after the user speaks."""
    form_data = await request.form()
    user_speech = form_data.get('SpeechResult', '')
    
    NGROK_URL = os.getenv("NGROK_URL", os.getenv("BASE_URL"))
    response = VoiceResponse()
    
    # If Twilio didn't hear anything, loop back
    if not user_speech:
        gather = Gather(input='speech', action=f'{NGROK_URL}/api/process?user_id={user_id}', method='POST', timeout=10)
        # Fallback to TwiML's built-in Alice voice just for the error message
        gather.say("I didn't quite catch that. Could you repeat?", voice='alice')
        response.append(gather)
        # Twilio requires XML format
        return Response(content=str(response), media_type="application/xml")
        
    # Send text to Gemini and get audio response back
    audio_path, assistant_text, should_hangup = await process_user_speech(user_id, user_speech)
    audio_url = f"{NGROK_URL}/static/{os.path.basename(audio_path)}"
    
    # Check if AI naturally ended the conversation or marked it for hangup
    if should_hangup or "goodbye" in assistant_text.lower() or "bye" in assistant_text.lower() or "namaste" in assistant_text.lower():
        response.play(audio_url)
        response.hangup()
    else:
        # Continue the conversation loop
        gather = Gather(input='speech', action=f'{NGROK_URL}/api/process?user_id={user_id}', method='POST', speechTimeout='auto', timeout=5)
        gather.play(audio_url)
        response.append(gather)
        
    return Response(content=str(response), media_type="application/xml")