import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")
GEMMA_API_URL = os.getenv("GEMMA_API_URL", f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMMA_API_KEY}")

async def call_gemma_system(messages):
    if not GEMMA_API_KEY:
        return "Hi — this is a prototype reply. Set GEMMA_API_KEY to see real AI responses."

    formatted_contents = []
    system_instruction = None

    for msg in messages:
        if msg["role"] == "system":
            system_instruction = {"parts": [{"text": msg["content"]}]}
        else:
            role = "user" if msg["role"] == "user" else "model"
            formatted_contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

    payload = {"contents": formatted_contents}
    if system_instruction:
        payload["systemInstruction"] = system_instruction

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(GEMMA_API_URL, json=payload, headers={"Content-Type": "application/json"})
        if r.status_code != 200:
            print("ERROR RESPONSE:", r.text)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]