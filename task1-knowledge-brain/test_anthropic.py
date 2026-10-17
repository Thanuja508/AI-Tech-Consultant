import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path, override=True)

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("ERROR: Claude API key not found in .env")
else:
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Reply with: Claude API is working!"
            }
        ],
    )

    print(response.content[0].text)