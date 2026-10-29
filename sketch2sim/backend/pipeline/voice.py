from backend import config
from backend.meta import client


def transcribe_goal(audio_bytes: bytes, filename: str = "goal.webm") -> str:
    if not config.META_API_KEY:
        return "ring the bell"
    return client.transcribe(audio_bytes, filename)
