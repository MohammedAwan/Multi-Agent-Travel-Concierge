import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
models = client.models.list()

print("--- Available Models on Your Groq Key ---")
for m in models.data:
    if "llama" in m.id or "mixtral" in m.id or "gemma" in m.id:
        print(f"• {m.id}")