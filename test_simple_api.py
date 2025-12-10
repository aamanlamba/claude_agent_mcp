
import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic
import anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

try:
    print("Attempting to call Claude API with claude-3-opus-20240229...")
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Hello, world"}
        ]
    )
    print("Success!")
    print(message.content[0].text)
except Exception as e:
    print("Failed to call API")
    print(f"Error: {e}")
