from pathlib import Path

import httpx
import streamlit as st


st.set_page_config(
    page_title="AI Voice Calling Agent Dashboard",
    page_icon="AV",
    layout="wide",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');

:root {
    --bg1: #070b14;
    --bg2: #111827;
    --bg3: #101a2f;
    --text: #e5edf9;
    --accent: #14b8a6;
    --accent-soft: rgba(20, 184, 166, 0.14);
    --panel: rgba(8, 14, 28, 0.72);
}

html, body, [data-testid="stAppViewContainer"] {
  font-family: 'Space Grotesk', sans-serif;
  color: var(--text);
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 12% 8%, rgba(20, 184, 166, 0.20) 0%, transparent 40%),
        radial-gradient(circle at 90% 14%, rgba(56, 189, 248, 0.18) 0%, transparent 34%),
        radial-gradient(circle at 22% 90%, rgba(15, 23, 42, 0.45) 0%, transparent 38%),
        linear-gradient(135deg, var(--bg1), var(--bg2) 45%, var(--bg3));
}

h1, h2, h3 {
  letter-spacing: 0.2px;
    color: #f8fbff;
}

.block-card {
    border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 14px;
  padding: 16px 18px;
  background: var(--panel);
    backdrop-filter: blur(9px);
    box-shadow: 0 10px 28px rgba(2, 6, 23, 0.45);
}

.label-pill {
  display: inline-block;
    border: 1px solid rgba(20, 184, 166, 0.4);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  background: var(--accent-soft);
    color: #7ff5e9;
  margin-right: 8px;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"] {
    color: #d4deee;
}

[data-testid="stTextInputRootElement"] > div,
[data-testid="stTextAreaRootElement"] > div {
    background-color: rgba(15, 23, 42, 0.45);
}

[data-testid="stForm"] {
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 14px;
    padding: 12px;
    background: rgba(9, 15, 30, 0.45);
}
</style>
""",
    unsafe_allow_html=True,
)


st.title("AI Voice Calling Agent")
st.caption("Dashboard for demo configuration, key injection, and project walkthrough")

st.markdown(
    """
<div class="label-pill">Stateful Memory</div>
<div class="label-pill">Concurrency Pipeline</div>
<div class="label-pill">Voice + LLM Orchestration</div>
""",
    unsafe_allow_html=True,
)


col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        """
<div class="block-card">
  <h3>Memory Layer</h3>
  <p>Hot context on Redis + durable persistence on SQLite for returning-user continuity and low-latency retrieval.</p>
</div>
""",
        unsafe_allow_html=True,
    )
with col_b:
    st.markdown(
        """
<div class="block-card">
  <h3>Concurrency Layer</h3>
  <p>Celery workers on Redis queue for scalable outbound dispatch and non-blocking call workflow execution.</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()
st.subheader("Runtime Key Configuration")
st.write("Provide your own external credentials to run or evaluate the project.")

with st.form("keys_form"):
    left, right = st.columns(2)

    with left:
        openai_api_key = st.text_input("OPENAI_API_KEY", type="password", placeholder="sk-...")
        vapi_api_key = st.text_input("VAPI_API_KEY", type="password", placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        eleven_labs_key = st.text_input("ELEVEN_LABS_KEY", type="password", placeholder="sk_...")
        eleven_labs_voice_id = st.text_input("ELEVEN_LABS_VOICE_ID", value="ThT5KcBeYPX3keUQqHPh")
        ngrok_url = st.text_input("NGROK_URL", placeholder="https://your-public-url.example.com")

    with right:
        twilio_account_sid = st.text_input("TWILIO_ACCOUNT_SID", type="password", placeholder="ACxxxxxxxxxxxxxxxx")
        twilio_auth_token = st.text_input("TWILIO_AUTH_TOKEN", type="password", placeholder="xxxxxxxx")
        twilio_phone_number = st.text_input("TWILIO_PHONE_NUMBER", placeholder="+10000000000")
        my_phone_number = st.text_input("MY_PHONE_NUMBER", placeholder="+10000000000")
        redis_url = st.text_input("REDIS_URL", value="redis://localhost:6379/0")
        base_url = st.text_input("BASE_URL", value="http://localhost:8000")

    submitted = st.form_submit_button("Generate .env Preview")

if submitted:
    required = {
        "OPENAI_API_KEY": openai_api_key,
        "VAPI_API_KEY": vapi_api_key,
        "ELEVEN_LABS_KEY": eleven_labs_key,
        "TWILIO_ACCOUNT_SID": twilio_account_sid,
        "TWILIO_AUTH_TOKEN": twilio_auth_token,
        "TWILIO_PHONE_NUMBER": twilio_phone_number,
        "MY_PHONE_NUMBER": my_phone_number,
        "NGROK_URL": ngrok_url,
    }

    missing = [k for k, v in required.items() if not v]

    env_preview = "\n".join(
        [
            f"OPENAI_API_KEY={openai_api_key}",
            f"VAPI_API_KEY={vapi_api_key}",
            f"ELEVEN_LABS_KEY={eleven_labs_key}",
            f"ELEVEN_LABS_VOICE_ID={eleven_labs_voice_id}",
            f"TWILIO_ACCOUNT_SID={twilio_account_sid}",
            f"TWILIO_AUTH_TOKEN={twilio_auth_token}",
            f"TWILIO_PHONE_NUMBER={twilio_phone_number}",
            f"MY_PHONE_NUMBER={my_phone_number}",
            f"NGROK_URL={ngrok_url}",
            f"BASE_URL={base_url}",
            "DATABASE_URL=sqlite:///./riverwood.db",
            f"REDIS_URL={redis_url}",
            "TTS_OUTPUT_DIR=./data/audio",
            "SIMULATE_TELEPHONY=false",
        ]
    )

    if missing:
        st.warning("Missing required keys: " + ", ".join(missing))
    else:
        st.success("All required runtime keys look present.")

    st.code(env_preview, language="dotenv")

st.divider()


docs_base_url = st.text_input("FastAPI URL for Docs", value="http://localhost:8000")
docs_url = f"{docs_base_url.rstrip('/')}/docs"
openapi_url = f"{docs_base_url.rstrip('/')}/openapi.json"

st.link_button("Open Swagger UI", docs_url)

if st.button("Fetch OpenAPI Endpoints"):
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(openapi_url)
            response.raise_for_status()
            schema = response.json()

        paths = sorted(schema.get("paths", {}).keys())
        st.success(f"Connected successfully. Found {len(paths)} API routes.")
        if paths:
            st.code("\n".join(paths), language="text")
        else:
            st.warning("OpenAPI loaded, but no routes were listed.")
    except Exception as exc:
        st.error(f"Unable to fetch OpenAPI schema from {openapi_url}: {exc}")

st.divider()
st.subheader("Trigger Call by User ID")
st.info("Currently there exists only one user in the scripts/seed_db.py. If you want to call someone or test please change the phone number and details and test.")


call_user_id = st.text_input("User ID", value="user_001", help="Example: user_001")
call_api_base_url = st.text_input("FastAPI URL for Trigger", value="http://localhost:8000")

if st.button("Trigger User Call"):
    trigger_url = f"{call_api_base_url.rstrip('/')}/trigger/{call_user_id.strip()}"
    if not call_user_id.strip():
        st.warning("Please enter a valid user ID.")
    else:
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(trigger_url)
                response.raise_for_status()
                payload = response.json()
            st.success("Call trigger request submitted successfully.")
            st.json(payload)
        except Exception as exc:
            st.error(f"Failed to trigger call for user_id '{call_user_id}': {exc}")

st.divider()
st.subheader("Demo Video")


video_path = Path("assets/demo_video.mov")
if video_path.exists():
    st.video(str(video_path))
else:
    st.info("Demo file not found at assets/demo_video.mp4")
    st.caption("You can still paste a video URL below as a temporary placeholder.")
    video_url = st.text_input("Optional demo URL", placeholder="https://...")
    if video_url:
        st.video(video_url)

st.divider()
st.info("This project was an introduction to AI agents and autonomous calling system for me. Some of the things are still in progress and I need to figure out.")
