# Working Workflow

## End-to-End Run Order

1. Create local environment file

- Copy .env.example to .env.
- Fill all required keys: OpenAI, VAPI, ElevenLabs, Twilio.
- Keep SIMULATE_TELEPHONY=true if you want a dry run.

2. Start Redis

- Redis is required for hot memory and Celery queue.
- Ensure REDIS_URL in .env points to your running Redis instance.

3. Seed database first

- Run: python -m scripts.seed_db
- This creates tables and inserts starter user + construction data.

4. Start FastAPI server

- Run: uvicorn src.core.main:app --reload
- This is the runtime entry for main.py and exposes backend APIs.

5. Open Swagger UI

- Visit: http://localhost:8000/docs
- You can test health and trigger routes from Swagger directly.

6. Start Streamlit dashboard

- Run: streamlit run app.py
- Use Runtime Key Configuration to generate a .env preview.
- Use API Docs Integration section to open /docs and fetch OpenAPI endpoints.

7. Optional: start worker for concurrency pipeline

- Run: celery -A src.core.worker.celery_app worker --loglevel=info
- Needed for queue-backed async workflow and bulk dispatch testing.

8. Trigger test call

- Run: python -m scripts.trigger_call --user-id user_001
- Or trigger from Swagger endpoint: POST /trigger/{user_id}.

9. Optional bulk simulation

- Run: python -m scripts.run_1000_calls
- This validates queue dispatch behavior and concurrency flow.
