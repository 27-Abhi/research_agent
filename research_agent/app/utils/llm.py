import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL_ID = os.getenv("HF_MODEL_ID", "katanemo/Arch-Router-1.5B")
PROVIDER = os.getenv("HF_PROVIDER", "hf-inference")
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").lower()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
OLLAMA_TIMEOUT_SEC = int(os.getenv("OLLAMA_TIMEOUT_SEC", "600"))
OLLAMA_MAX_PROMPT_CHARS = int(os.getenv("OLLAMA_MAX_PROMPT_CHARS", "12000"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "300"))
DEFAULT_MODEL_URLS = [
    "https://router.huggingface.co/v1/chat/completions",
    f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}",
]


def _extract_text(data: Any) -> str:
    def _clean(text: str) -> str:
        value = text.strip()
        if value.startswith("```") and value.endswith("```"):
            lines = value.splitlines()
            if len(lines) >= 3:
                value = "\n".join(lines[1:-1]).strip()
        if value.lower().startswith("markdown\n"):
            value = value.split("\n", 1)[1].strip()
        return value

    if isinstance(data, list):
        if not data:
            return ""
        first = data[0]
        if isinstance(first, dict):
            return _clean(str(
                first.get("generated_text")
                or first.get("summary_text")
                or first.get("answer")
                or first
            ))
        return _clean(str(first))

    if isinstance(data, dict):
        if data.get("choices"):
            first_choice = data["choices"][0]
            if isinstance(first_choice, dict):
                message = first_choice.get("message", {})
                if isinstance(message, dict) and "content" in message:
                    return _clean(str(message["content"]))
                if "text" in first_choice:
                    return _clean(str(first_choice["text"]))
        if "generated_text" in data:
            return _clean(str(data["generated_text"]))
        if "summary_text" in data:
            return _clean(str(data["summary_text"]))
        if "error" in data:
            return f"HF Error: {data['error']}"
        return _clean(str(data))

    return _clean(str(data))


def call_llm(prompt: str) -> str:
    print(f"\n[LLM CALL START] backend={LLM_BACKEND}")
    print(f"[LLM REQUEST] prompt_chars={len(prompt)}")
    if LLM_BACKEND == "ollama":
        return _call_ollama(prompt)

    return _call_hf(prompt)


def _call_ollama(prompt: str) -> str:
    bounded_prompt = prompt
    if len(prompt) > OLLAMA_MAX_PROMPT_CHARS:
        bounded_prompt = prompt[:OLLAMA_MAX_PROMPT_CHARS]
        print(
            f"[LLM REQUEST] prompt_truncated=true "
            f"| original_chars={len(prompt)} | sent_chars={len(bounded_prompt)}"
        )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Always answer using only the given prompt "
                    "content. Never ask the user for more input. Do your best with available data."
                ),
            },
            {"role": "user", "content": bounded_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": OLLAMA_NUM_PREDICT,
        },
    }

    try:
        print(f"Trying Ollama endpoint: {OLLAMA_URL}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT_SEC)
        print("STATUS:", response.status_code)
        print("RAW TEXT:", response.text[:200])

        if response.status_code != 200:
            print(f"[LLM RESPONSE] status={response.status_code} | endpoint_failed")
            return f"Ollama Error: {response.text}"

        data = response.json()
        message = data.get("message", {})
        output = str(message.get("content", "")).strip()
        print(f"[LLM RESPONSE] status=200 | output_chars={len(output)}")
        return output
    except Exception as e:
        print("[OLLAMA LLM ERROR]:", e)
        print("[LLM CALL END] status=exception")
        return f"Ollama Error: {e}"


def _call_hf(prompt: str) -> str:
    hf_api_key = os.getenv("HF_API_KEY")
    if not hf_api_key:
        print("[LLM RESPONSE] status=error | reason=missing_api_key")
        return "HF Error: HF_API_KEY is not set. Please add it to your .env or environment variables."

    headers = {
        "Authorization": f"Bearer {hf_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": f"{MODEL_ID}:{PROVIDER}",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Always answer using only the given prompt "
                    "content. Never ask the user for more input. Do your best with available data."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 300,
        "temperature": 0.3,
    }
    urls = [os.getenv("HF_MODEL_URL")] if os.getenv("HF_MODEL_URL") else DEFAULT_MODEL_URLS
    last_error = "Unknown error"

    try:
        for endpoint in urls:
            if not endpoint:
                continue

            print(f"Trying HF endpoint: {endpoint}")
            endpoint_payload = payload
            if endpoint.endswith(f"/models/{MODEL_ID}"):
                endpoint_payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 300,
                        "temperature": 0.3,
                        "return_full_text": False,
                    },
                }

            response = requests.post(endpoint, headers=headers, json=endpoint_payload, timeout=90)

            print("STATUS:", response.status_code)
            print("RAW TEXT:", response.text[:200])

            if response.status_code == 200:
                output = _extract_text(response.json())
                print(f"[LLM RESPONSE] status=200 | output_chars={len(output)}")
                return output

            last_error = response.text
            print(f"[LLM RESPONSE] status={response.status_code} | endpoint_failed")

        print("[LLM CALL END] status=failed_all_endpoints")
        return f"HF Error: {last_error}"
    except Exception as e:
        print("[HF LLM ERROR]:", e)
        print("[LLM CALL END] status=exception")
        return f"HF Error: {e}"
