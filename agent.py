import os
import datetime
from db import SessionLocal, User, ConstructionUpdate, Interaction, CallLog
from llm_gemma import call_gemma_system
from tts import text_to_speech, get_or_create_canned
from telephony import place_interactive_call

def build_system_prompt(user, construction, is_returning):
    language_instruction = "Reply primarily in natural Hindi/Hinglish." if user.language == "hi" else "Reply in conversational English."
    visit_info = f"Site visits available: {construction.site_visit_available}. Timings: {construction.site_visit_timings}"
    
    user_status = "This is a RETURNING customer. Acknowledge this naturally." if is_returning else "This is a FIRST TIME call to this customer."
    
    if user.site_visit_interest:
        extra_context = "The customer previously showed interest in a site visit."
    else:
        extra_context = ""

    prompt = (
        f"You are Akanksha, a friendly AI calling assistant for Riverwood Projects LLP.\n"
        f"Customer: {user.name} | Project: {user.project}\n"
        f"Status: {user_status}\n"
        f"Previous Context: {extra_context}\n"
        f"Language instruction: {language_instruction}\n"
        f"Latest Update: {construction.current_phase} ({construction.completion_percentage}%) — {construction.recent_milestone}\n"
        f"{visit_info}\n\n"
        "Rules:\n"
        "1. Keep responses VERY concise (1-2 sentences max). You are on a phone call.\n"
        "2. Answer their questions based on the Latest Update.\n"
        "3. If they say goodbye, acknowledge it and say a polite goodbye so the call can end."
    )
    return prompt

def build_first_message(user, is_returning):
    first_name = user.name.split()[0]
    if is_returning:
        if user.language == "hi":
            return f"Namaste {first_name} ji! Main Akanksha bol raha hoon Riverwood se. Aapke project ke naye updates aaye hain. Kya aap free hain baat karne ke liye?"
        return f"Hi {first_name}! Welcome back, it's Akanksha from Riverwood. I have a new construction update for you. Are you free to talk?"
    else:
        if user.language == "hi":
            return f"Namaste! Kya main {first_name} ji se baat kar raha hoon? Main Akanksha hoon Riverwood Projects se."
        return f"Hi {first_name}! I'm Akanksha from Riverwood Projects. Am I speaking with {user.name}?"

async def trigger_outbound_call(user_id: str):
    """Fired when you trigger the call from the terminal."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        # Check if they have been called before
        past_calls = db.query(CallLog).filter(CallLog.user_id == user_id).count()
        is_returning = past_calls > 0
        
        first_message = build_first_message(user, is_returning)

        # Log the AI's opening statement
        db.add(Interaction(user_id=user_id, role="assistant", content=first_message))
        
        # Generate Audio
        lang_code = "hi" if user.language == "hi" else "en"
        audio_path = text_to_speech(first_message, lang=lang_code, filename_hint=f"{user_id}_greeting")

        # Start the Two-Way Twilio Call
        call_sid, call_status = place_interactive_call(audio_path, user_id)

        db.add(CallLog(user_id=user_id, status=call_status, audio_path=audio_path, created_at=datetime.datetime.utcnow()))
        db.commit()

        return {"user_id": user_id, "call_id": call_sid, "status": "Interactive call started"}
    finally:
        db.close()

async def process_user_speech(user_id: str, user_speech: str):
    """Fired every time the user speaks on the phone."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        construction = db.query(ConstructionUpdate).filter(ConstructionUpdate.project == user.project).first()
        
        user_speech_lower = user_speech.lower()
        visit_keywords = [
            "visit",
            "site visit",
            "come to site",
            "dekhne aana",
            "site dekhna",
            "visit karna",
            "haan",
            "yes",
            "sure"
        ]

        should_hangup = False
        lang_code = "hi" if user.language == "hi" else "en"

        # 1. Save what the user just said
        db.add(Interaction(user_id=user_id, role="user", content=user_speech))
        db.commit()

        if any(word in user_speech_lower for word in visit_keywords) and not user.site_visit_interest:
            user.site_visit_interest = True
            db.commit()
            
            # Use canned response for zero-latency confirmation!
            canned_key = f"visit_confirm_{lang_code}"
            assistant_text = "Great! I have noted that you are interested in a site visit. Our team will contact you shortly to schedule it. Goodbye!" if lang_code == "en" else "Bahut achha! Maine aapka site visit note kar liya hai. Hamari team jald aapse sampark karegi. Namaste!"
            
            audio_path = get_or_create_canned(canned_key, lang=lang_code)
            should_hangup = True
            
            db.add(Interaction(user_id=user_id, role="assistant", content=assistant_text))
            db.commit()
            return audio_path, assistant_text, should_hangup
        
        # 2. Rebuild context window (System Prompt + Last 10 messages)
        system_prompt = build_system_prompt(user, construction, is_returning=True)
        recent_history = db.query(Interaction).filter(Interaction.user_id == user_id).order_by(Interaction.timestamp.desc()).limit(10).all()
        recent_history = list(reversed(recent_history)) # Put in chronological order
        
        messages = [{"role": "system", "content": system_prompt}]
        for interaction in recent_history:
            messages.append({"role": interaction.role, "content": interaction.content})
            
        # 3. Get Gemini's reply
        assistant_text = await call_gemma_system(messages)
        
        # 4. Check for goodbye in LLM text to naturally hang up
        lower = assistant_text.lower()
        if any(k in lower for k in ["goodbye", "bye", "see you", "take care", "shukriya", "dhanyavaad", "namaste"]):
            should_hangup = True

        # 5. Save Gemini's reply
        db.add(Interaction(user_id=user_id, role="assistant", content=assistant_text))
        db.commit()
        
        # 6. Generate TTS
        audio_path = text_to_speech(assistant_text, lang=lang_code, filename_hint=user_id)
        
        return audio_path, assistant_text, should_hangup
    finally:
        db.close()