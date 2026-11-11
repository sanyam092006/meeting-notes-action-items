import json

from google import genai

from prompts import EXTRACT_SYSTEM
from schemas import MeetingSummary


def to_gemini(messages):
    """Standard [{"role", "content"}] messages -> (system text, Gemini contents)."""
    system = "\n".join(m["content"] for m in messages if m["role"] == "system")
    contents = [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
        for m in messages
        if m["role"] != "system"
    ]
    return system, contents


def call_gemini(messages, api_key, model, schema=None):
    system, contents = to_gemini(messages)
    config = {"system_instruction": system, "temperature": 0.2}
    if schema:
        config["response_mime_type"] = "application/json"
        config["response_schema"] = schema
    client = genai.Client(api_key=api_key)
    return client.models.generate_content(model=model, contents=contents, config=config)


def extract(notes, api_key, model) -> MeetingSummary:
    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM},
        {"role": "user", "content": notes},
    ]
    resp = call_gemini(messages, api_key, model, schema=MeetingSummary)
    return resp.parsed if resp.parsed is not None else MeetingSummary(**json.loads(resp.text))
