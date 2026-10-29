import math
from typing import Any

import pymunk

from backend.config import SIM_FPS, SIM_MAX_SECONDS
from backend.schemas import Beam, Circle, Part, Scene, Segment, Sensor, SimResult


def _body_frame(body_map: dict[str, pymunk.Body]) -> dict[str, dict[str, float]]:
    return {
        name: {"x": body.position.x, "y": body.position.y, "angle": body.angle}
        for name, body in body_map.items()
    }


def simulate(scene: Scene) -> SimResult:
    space = pymunk.Space()
    space.gravity = (0, scene.world.gravity)
    body_map: dict[str, pymunk.Body] = {}
    ball_body: pymunk.Body | None = None
    for part in scene.parts:
        shape = part.shape
        if part.type in {"ramp", "pivot", "bell"} or part.physics.static:
            body = space.static_body
        else:
            body = pymunk.Body(max(0.01, part.physics.mass), moment_for(part))
            body_map[part.id] = body
            space.add(body)
        if isinstance(shape, Circle):
            if body.body_type != pymunk.Body.STATIC:
                body.position = (shape.x, shape.y)
                pymunk_shape = pymunk.Circle(body, shape.r)
            else:
                pymunk_shape = pymunk.Circle(body, shape.r, offset=(shape.x, shape.y))
            if part.type == "ball":
                ball_body = body
        elif isinstance(shape, (Segment, Beam)):
            pymunk_shape = pymunk.Segment(body, shape.a, shape.b, shape.thickness / 2)
        else:
            pymunk_shape = pymunk.Circle(body, shape.r, offset=(shape.x, shape.y))
            pymunk_shape.sensor = True
        pymunk_shape.friction = part.physics.friction
        pymunk_shape.elasticity = part.physics.elasticity
        pymunk_shape.collision_type = 2 if part.type == "bell" else 1
        space.add(pymunk_shape)
        if part.type == "lever" and part.pivot and body.body_type != pymunk.Body.STATIC:
            space.add(pymunk.PivotJoint(body, space.static_body, part.pivot))
    bell = next((shape for part in scene.parts if part.id == scene.goal.target and isinstance(shape := part.shape, Sensor)), None)
    logs: list[str] = []
    frames: list[dict[str, Any]] = []
    success = False
    closest = float("inf")
    dt = 1 / SIM_FPS
    for step in range(int(SIM_FPS * SIM_MAX_SECONDS)):
        space.step(dt)
        if step % 3 == 0:
            frames.append({"t": round(step * dt, 3), "bodies": _body_frame(body_map)})
        if ball_body and bell:
            distance = math.dist(ball_body.position, (bell.x, bell.y))
            closest = min(closest, distance)
            if distance <= bell.r + 18:
                success = True
                logs.append(f"t={step * dt:.1f}s ball reached {scene.goal.target}")
                break
    seconds = (step + 1) * dt
    if not success:
        if closest == float("inf"):
            logs.append("no ball and bell pair was available to verify")
            closest = -1
        else:
            logs.append(f"ended: ball stopped {closest:.1f}px from the bell")
    return SimResult(success=success, seconds=seconds, log=logs, frames=frames, metrics={"closest_ball_bell_dist": closest})


def moment_for(part: Part) -> float:
    shape = part.shape
    if isinstance(shape, (Beam, Segment)):
        length = math.dist(shape.a, shape.b)
        return max(1.0, part.physics.mass * length * length / 12)
    if isinstance(shape, Circle):
        return max(1.0, part.physics.mass * shape.r * shape.r / 2)
    return 1.0
