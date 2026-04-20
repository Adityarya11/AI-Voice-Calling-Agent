import os
import argparse
import httpx
from dotenv import load_dotenv

load_dotenv()


def trigger_call(user_id: str) -> None:
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    url = f"{base_url}/trigger/{user_id}"

    with httpx.Client(timeout=30) as client:
        response = client.post(url)
        response.raise_for_status()
        print(response.json())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger an outbound AI call for a user ID")
    parser.add_argument("--user-id", default="user_001", help="User ID to call")
    args = parser.parse_args()
    trigger_call(args.user_id)
