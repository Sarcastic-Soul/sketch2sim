import base64
import json
from io import BytesIO
from typing import Any

from openai import OpenAI

from backend import config
from backend.meta import cache


def _require_key(key: str, service: str) -> None:
    if not key:
        raise RuntimeError(f"{service} is not configured; add its API key to .env")


def _data_url(data: bytes, media_type: str = "image/png") -> str:
    return f"data:{media_type};base64,{base64.b64encode(data).decode()}"


def _meta_client() -> OpenAI:
    _require_key(config.META_API_KEY, "Meta Model API")
    return OpenAI(api_key=config.META_API_KEY, base_url=config.META_BASE_URL)


def chat_text(prompt: str, *, model: str | None = None, namespace: str = "chat") -> str:
    model = model or config.SPARK_MODEL
    payload = json.dumps({"model": model, "prompt": prompt}, sort_keys=True).encode()
    cached = cache.get_json(namespace, payload)
    if cached is not None:
        return cached["text"]
    response = _meta_client().chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0)
    text = response.choices[0].message.content or ""
    cache.put_json(namespace, payload, {"text": text})
    return text


def chat_vision(image: bytes, prompt: str) -> str:
    payload = image + b"\0" + prompt.encode()
    cached = cache.get_json("spark_vision", payload)
    if cached is not None:
        return cached["text"]
    response = _meta_client().chat.completions.create(
        model=config.SPARK_MODEL,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": _data_url(image)}}]}],
        temperature=0,
    )
    text = response.choices[0].message.content or ""
    cache.put_json("spark_vision", payload, {"text": text})
    return text


def segment(image: bytes, prompts: list[str]) -> Any:
    payload = image + b"\0" + json.dumps(prompts).encode()
    cached = cache.get_json("sam", payload)
    if cached is not None:
        return cached
    # The exact SAM wire format can change. Keep this adapter isolated so it can
    # be updated from Meta's current documentation without touching the pipeline.
    response = _meta_client().images.generate(model=config.SAM_MODEL, prompt=", ".join(prompts), response_format="json")
    raw = response.data[0].b64_json or response.data[0].url or "{}"
    result = json.loads(base64.b64decode(raw)) if response.data[0].b64_json else json.loads(raw)
    cache.put_json("sam", payload, result)
    return result


def generate_image(prompt: str) -> bytes:
    payload = prompt.encode()
    cached = cache.get_bytes("image", payload, "png")
    if cached is not None:
        return cached
    response = _meta_client().images.generate(model=config.IMAGE_MODEL, prompt=prompt, size="1024x1024")
    item = response.data[0]
    if item.b64_json:
        result = base64.b64decode(item.b64_json)
    else:
        import httpx
        result = httpx.get(item.url, timeout=30).content
    cache.put_bytes("image", payload, result, "png")
    return result


def transcribe(audio: bytes, filename: str = "goal.webm") -> str:
    payload = audio
    cached = cache.get_json("transcribe", payload)
    if cached is not None:
        return cached["text"]
    response = _meta_client().audio.transcriptions.create(model=config.TRANSCRIBE_MODEL, file=(filename, BytesIO(audio)))
    text = response.text
    cache.put_json("transcribe", payload, {"text": text})
    return text


def baseten_text(prompt: str) -> str:
    payload = prompt.encode()
    cached = cache.get_json("repair", payload)
    if cached is not None:
        return cached["text"]
    _require_key(config.BASETEN_API_KEY, "Baseten")
    client = OpenAI(api_key=config.BASETEN_API_KEY, base_url="https://inference.baseten.co/v1")
    response = client.chat.completions.create(model=config.BASETEN_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0)
    text = response.choices[0].message.content or ""
    cache.put_json("repair", payload, {"text": text})
    return text
