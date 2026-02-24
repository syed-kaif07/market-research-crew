import requests
import os
from dotenv import load_dotenv

load_dotenv()

headers = {"Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}"}
r = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
models = [m["id"] for m in r.json()["data"]]
for m in models:
    print(m)