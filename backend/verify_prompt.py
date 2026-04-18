import httpx
import json

response = httpx.get("http://localhost:8000/api/prospectos/24/prompt")
if response.status_code == 200:
    data = response.json()
    print("--- PROMPT START ---")
    print(data.get("prompt"))
    print("--- PROMPT END ---")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
