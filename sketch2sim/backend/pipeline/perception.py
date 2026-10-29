import json
from io import BytesIO

from PIL import Image

from backend import config
from backend.meta import client
from backend.schemas import LabeledPart, Mask


def _fallback_parts(image_bytes: bytes) -> list[LabeledPart]:
    image = Image.open(BytesIO(image_bytes))
    w, h = image.size
    return [
        LabeledPart(type="ball", polygon=[(w * .12, h * .18), (w * .16, h * .18), (w * .14, h * .22)], box=(w*.1, h*.15, w*.08, h*.1)),
        LabeledPart(type="ramp", polygon=[(w*.1, h*.55), (w*.55, h*.72)], box=(w*.1, h*.5, w*.5, h*.25)),
        LabeledPart(type="bell", polygon=[(w*.82, h*.35), (w*.88, h*.42)], box=(w*.8, h*.3, w*.1, h*.15)),
    ]


def run_sam(image_bytes: bytes) -> list[Mask]:
    if not config.META_API_KEY:
        return [Mask(type_hint=p.type, box=p.box, polygon=p.polygon, confidence=.5) for p in _fallback_parts(image_bytes)]
    raw = client.segment(image_bytes, config.PART_TYPES)
    items = raw.get("masks", raw if isinstance(raw, list) else [])
    return [Mask.model_validate(item) for item in items]


def label_with_spark(image_bytes: bytes, masks: list[Mask]) -> list[LabeledPart]:
    if not config.META_API_KEY:
        return _fallback_parts(image_bytes)
    prompt = """Read this mechanism sketch. Return strict JSON only: {\"parts\":[{\"mask_index\":0,\"type\":\"ball|ramp|lever|pivot|spring|bell\",\"mass\":null}],\"goal_text\":\"ring the bell\"}. Use only the allowed types."""
    parsed = json.loads(client.chat_vision(image_bytes, prompt))
    result = []
    for item in parsed.get("parts", []):
        index = int(item["mask_index"])
        mask = masks[index]
        result.append(LabeledPart(type=item["type"], polygon=mask.polygon, box=mask.box, mass=item.get("mass"), extra={"goal_text": parsed.get("goal_text", "")}))
    return result


def read_sketch(image_bytes: bytes) -> tuple[list[LabeledPart], str]:
    masks = run_sam(image_bytes)
    labeled = label_with_spark(image_bytes, masks)
    goal = next((str(part.extra["goal_text"]) for part in labeled if "goal_text" in part.extra), "ring the bell")
    return labeled, goal
