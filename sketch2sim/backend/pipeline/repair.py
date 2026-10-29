import json
import math
from collections.abc import Iterator

from backend import config
from backend.meta import client
from backend.pipeline.simulate import simulate
from backend.schemas import Attempt, Scene, SimResult


def _parse_response(text: str) -> tuple[str, list[dict]]:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return "No valid edit returned", []
    data = json.loads(text[start:end + 1])
    return str(data.get("reasoning", "adjusting the machine")), data.get("edits", [])


def propose_edit(scene: Scene, result: SimResult) -> tuple[str, list[dict]]:
    prompt = "Return strict JSON with reasoning and edits. Allowed edits: rotate part degrees, move part dx/dy, set part field value. Do not rewrite the scene.\nSCENE=" + scene.model_dump_json() + "\nRESULT=" + result.model_dump_json()
    if config.BASETEN_API_KEY:
        text = client.baseten_text(prompt)
    elif config.META_API_KEY:
        text = client.chat_text(prompt, namespace="repair_fallback")
    else:
        # Offline mode keeps the demo and tests deterministic while credentials
        # are unavailable. It makes a small, safe correction toward the bell.
        bell = next((p for p in scene.parts if p.id == scene.goal.target), None)
        ball = next((p for p in scene.parts if p.type == "ball"), None)
        if bell and ball and hasattr(ball.shape, "x") and hasattr(bell.shape, "x"):
            dx = bell.shape.x - ball.shape.x
            return "offline fallback moved the ball toward the target", [{"op": "move", "part": ball.id, "dx": dx * .75, "dy": 0}]
        return "no safe offline edit available", []
    return _parse_response(text)


def apply_edits(scene: Scene, edits: list[dict]) -> Scene:
    updated = scene.model_copy(deep=True)
    by_id = {part.id: part for part in updated.parts}
    for edit in edits:
        part = by_id.get(edit.get("part"))
        if not part:
            continue
        shape = part.shape
        op = edit.get("op")
        if op == "move" and hasattr(shape, "x"):
            part.shape = shape.model_copy(update={"x": shape.x + float(edit.get("dx", 0)), "y": shape.y + float(edit.get("dy", 0))})
        elif op == "move" and hasattr(shape, "a"):
            dx, dy = float(edit.get("dx", 0)), float(edit.get("dy", 0))
            part.shape = shape.model_copy(update={"a": (shape.a[0]+dx, shape.a[1]+dy), "b": (shape.b[0]+dx, shape.b[1]+dy)})
        elif op == "set":
            field = edit.get("field", "")
            if field == "physics.mass":
                part.physics = part.physics.model_copy(update={"mass": max(.1, float(edit.get("value", part.physics.mass)))})
        elif op == "rotate" and hasattr(shape, "a"):
            angle = math.radians(float(edit.get("degrees", 0)))
            cx, cy = shape.a
            x, y = shape.b[0] - cx, shape.b[1] - cy
            rotated_b = (cx + x * math.cos(angle) - y * math.sin(angle), cy + x * math.sin(angle) + y * math.cos(angle))
            part.shape = shape.model_copy(update={"b": rotated_b})
    return Scene.model_validate(updated.model_dump())


def repair_loop(scene: Scene) -> Iterator[Attempt]:
    current = scene
    result = simulate(current)
    yield Attempt(n=0, reasoning="initial simulation", edits=[], result=result)
    for number in range(1, config.MAX_REPAIR_ATTEMPTS + 1):
        if result.success:
            break
        reasoning, edits = propose_edit(current, result)
        current = apply_edits(current, edits)
        scene.parts = current.parts
        scene.goal = current.goal
        result = simulate(current)
        yield Attempt(n=number, reasoning=reasoning, edits=edits, result=result)
        if result.success:
            break
