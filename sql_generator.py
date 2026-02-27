import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-coder:6.7b"


def generate_sql(prompt: str) -> str:
    payload = {
    "model": MODEL_NAME,
    "messages": [{"role": "user", "content": prompt}],
    "stream": False,
    "options": {
        "temperature": 0
    }
}

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60  # prevents hanging forever
        )
        response.raise_for_status()

        content = response.json()["message"]["content"].strip()

        # ---- Remove accidental markdown formatting ----
        if content.startswith("```"):
            content = content.replace("```sql", "")
            content = content.replace("```", "")
            content = content.strip()

        return content

    except requests.exceptions.RequestException as e:
        return f"LLM_CONNECTION_ERROR: {str(e)}"