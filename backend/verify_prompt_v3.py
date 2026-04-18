import httpx
import json

response = httpx.get("http://localhost:8000/api/prospectos/24/prompt")
with open("c:/xampp/htdocs/buscaclientes/backend/prompt_check_utf8.txt", "w", encoding="utf-8") as f:
    if response.status_code == 200:
        data = response.json()
        f.write(data.get("prompt"))
    else:
        f.write(f"Error: {response.status_code}\n")
        f.write(response.text)
