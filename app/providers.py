import os
from typing import Any

import httpx


class ProviderError(RuntimeError):
    pass


def provider_config() -> dict[str, str]:
    return {
        "provider": os.getenv("AI_PROVIDER", "openai-compatible").strip().lower(),
        "api_key": os.getenv("AI_API_KEY", "").strip(),
        "base_url": os.getenv("AI_BASE_URL", "").strip(),
        "model": os.getenv("AI_MODEL", "").strip(),
    }


async def generate_reply(messages: list[dict[str, str]]) -> tuple[str, str, str]:
    cfg = provider_config()
    provider, key, model = cfg["provider"], cfg["api_key"], cfg["model"]
    if not key or not model:
        raise ProviderError("AI provider is not configured. Add AI_API_KEY and AI_MODEL in the server environment.")

    timeout = httpx.Timeout(60.0, connect=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        if provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            contents = []
            for item in messages:
                role = "model" if item["role"] == "assistant" else "user"
                contents.append({"role": role, "parts": [{"text": item["content"]}]})
            response = await client.post(url, params={"key": key}, json={"contents": contents})
            data = _json_response(response)
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError):
                raise ProviderError("Gemini returned no text candidate.")
            return text, provider, model

        if provider == "anthropic":
            system = "\n".join(m["content"] for m in messages if m["role"] == "system")
            turns = [{"role": m["role"], "content": m["content"]}
                     for m in messages if m["role"] != "system"]
            headers = {"x-api-key": key, "anthropic-version": "2023-06-01",
                       "content-type": "application/json"}
            payload: dict[str, Any] = {"model": model, "max_tokens": 1200, "messages": turns}
            if system:
                payload["system"] = system
            response = await client.post("https://api.anthropic.com/v1/messages",
                                         headers=headers, json=payload)
            data = _json_response(response)
            text = "".join(block.get("text", "") for block in data.get("content", []))
            if not text:
                raise ProviderError("Anthropic returned an empty response.")
            return text, provider, model

        if provider == "openai-compatible":
            base = cfg["base_url"] or "https://api.openai.com/v1"
            url = base.rstrip("/") + "/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {"model": model, "messages": messages, "temperature": 0.4}
            response = await client.post(url, headers=headers, json=payload)
            data = _json_response(response)
            try:
                text = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError):
                raise ProviderError("Provider returned no assistant message.")
            if not isinstance(text, str):
                raise ProviderError("Provider returned a non-text response.")
            return text, provider, model

    raise ProviderError(f"Unsupported provider: {provider}")


def _json_response(response: httpx.Response) -> dict[str, Any]:
    if response.is_error:
        detail = response.text[:1000]
        raise ProviderError(f"Provider request failed ({response.status_code}): {detail}")
    try:
        return response.json()
    except ValueError:
        raise ProviderError("Provider returned invalid JSON.")
