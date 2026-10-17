import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key or api_key == "your_actual_api_key_here":
    print("API key missing. Check your .env file.")
else:
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": "Reply with: Groq API is working!"
                }
            ],
        )
        print(response.choices[0].message.content)
    except Exception as error:
        print("API test failed:", error)