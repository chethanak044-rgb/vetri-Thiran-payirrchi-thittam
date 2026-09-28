from functools import lru_cache
from google import genai
from google.genai import types
from app.config import get_settings


@lru_cache
def get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Copy .env.example to .env and add your key.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_text(model: str, prompt: str, schema=None, temperature: float = 0.9) -> str:
    client = get_client()
    config_kwargs = {"temperature": temperature}
    if schema is not None:
        config_kwargs.update({"response_mime_type": "application/json", "response_schema": schema})
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text
