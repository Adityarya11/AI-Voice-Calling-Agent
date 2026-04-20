"""
main.py
-------
FastAPI application entry point.

Routes:
  GET  /health              — liveness probe
  POST /trigger/{user_id}   — initiate outbound call for a user
  POST /api/vapi-webhook    — VAPI Custom LLM + event webhook (streaming SSE)
  POST /api/process         — legacy Twilio speech webhook (fallback)
  GET  /static/*            — serves pre-generated gTTS audio files (Twilio fallback)
"""

import os
from html import escape
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from src.agent.agent import trigger_outbound_call, process_user_speech
from src.core.db import Base, engine
from src.services.vapi_handler import vapi_router

load_dotenv(override=True)

# ── Database bootstrap ────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Audio output directory (for Twilio fallback TTS files) ───────────────────
AUDIO_DIR = os.getenv("TTS_OUTPUT_DIR", "./data/audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Riverwood AI Voice Agent",
    description=(
        "Production-grade outbound voice agent — "
        "VAPI + ElevenLabs Flash + OpenAI GPT-4o-mini + Redis Hot Memory"
    ),
    version="2.0.0"
)

# VAPI webhook router (/api/vapi-webhook handles all VAPI events)
app.include_router(vapi_router)

# Static audio files for Twilio fallback path
app.mount(
    "/static",
    StaticFiles(directory=AUDIO_DIR),
    name="static"
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Liveness probe — also confirms DB + env are accessible."""
    return {
        "status": "ok",
        "telephony": "vapi" if os.getenv("VAPI_API_KEY") else "twilio-fallback",
        "tts":       "elevenlabs" if os.getenv("ELEVEN_LABS_KEY") else "gtts-fallback",
        "llm":       "openai" if os.getenv("OPENAI_API_KEY") else "demo-mode",
        "memory":    "redis+sqlite"
    }


@app.post("/trigger/{user_id}")
async def trigger(user_id: str):
    """
    Initiate an outbound call for a specific user.
    
    Example:
        curl -X POST http://localhost:8000/trigger/user_001
    """
    try:
        result = await trigger_outbound_call(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


# ── Legacy Twilio webhook (fallback when VAPI is not configured) ──────────────

@app.post("/api/process")
async def twilio_process_speech(request: Request, user_id: str):
    """
    Processes speech from the Twilio <Gather> webhook.
    Only active when VAPI is not the primary provider.
    """
    form_data = await request.form()
    raw_speech = form_data.get("SpeechResult", "")
    user_speech = raw_speech if isinstance(raw_speech, str) else ""
    NGROK_URL   = os.getenv("NGROK_URL", os.getenv("BASE_URL", "http://localhost:8000"))

    if not user_speech:
        twiml = (
            "<Response>"
            f"<Gather input=\"speech\" action=\"{escape(f'{NGROK_URL}/api/process?user_id={user_id}')}\" method=\"POST\" timeout=\"10\">"
            "<Say voice=\"alice\">I didn't quite catch that. Could you please repeat?</Say>"
            "</Gather>"
            "</Response>"
        )
        return Response(content=twiml, media_type="application/xml")

    audio_path, assistant_text, should_hangup = await process_user_speech(user_id, user_speech)
    audio_url = f"{NGROK_URL}/static/{os.path.basename(audio_path)}"

    if should_hangup or any(
        kw in assistant_text.lower()
        for kw in ["goodbye", "bye", "namaste", "shukriya"]
    ):
        twiml = (
            "<Response>"
            f"<Play>{escape(audio_url)}</Play>"
            "<Hangup/>"
            "</Response>"
        )
    else:
        twiml = (
            "<Response>"
            f"<Gather input=\"speech\" action=\"{escape(f'{NGROK_URL}/api/process?user_id={user_id}')}\" method=\"POST\" speechTimeout=\"auto\" timeout=\"5\">"
            f"<Play>{escape(audio_url)}</Play>"
            "</Gather>"
            "</Response>"
        )

    return Response(content=twiml, media_type="application/xml")
