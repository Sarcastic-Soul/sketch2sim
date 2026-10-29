import math
from collections import defaultdict

from backend.config import WORLD_HEIGHT, WORLD_WIDTH
from backend.schemas import (
    Beam,
    Circle,
    Goal,
    LabeledPart,
    Part,
    Physics,
    Scene,
    Segment,
    Sensor,
    World,
)


def to_world(point: tuple[float, float]) -> tuple[float, float]:
    return (float(point[0]), float(WORLD_HEIGHT - point[1]))


def _centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
    if not points:
        return (WORLD_WIDTH / 2, WORLD_HEIGHT / 2)
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def _axis(points: list[tuple[float, float]]) -> tuple[tuple[float, float], tuple[float, float]]:
    if len(points) < 2:
        center = _centroid(points)
        return center, (center[0] + 80, center[1])
    best = max(
        ((a, b) for i, a in enumerate(points) for b in points[i + 1:]),
        key=lambda pair: (pair[0][0] - pair[1][0]) ** 2 + (pair[0][1] - pair[1][1]) ** 2,
    )
    return best


def _radius(points: list[tuple[float, float]], center: tuple[float, float]) -> float:
    if not points:
        return 18.0
    return max(8.0, sum(math.dist(point, center) for point in points) / len(points))


def build_scene(parts: list[LabeledPart], goal_text: str | None = None) -> Scene:
    counters = defaultdict(int)
    built: list[Part] = []
    pivots: list[tuple[float, float]] = []
    for labeled in parts:
        counters[labeled.type] += 1
        part_id = f"{labeled.type}_{counters[labeled.type]}"
        center_px = _centroid(labeled.polygon)
        center = to_world(center_px)
        mass = labeled.mass or float(labeled.extra.get("mass", 10 if labeled.type == "ball" else 5))
        if labeled.type == "ball":
            built.append(Part(id=part_id, type="ball", shape=Circle(kind="circle", x=center[0], y=center[1], r=_radius(labeled.polygon, center_px)), physics=Physics(mass=mass, friction=0.4, elasticity=0.5)))
        elif labeled.type == "bell":
            built.append(Part(id=part_id, type="bell", shape=Sensor(kind="sensor", x=center[0], y=center[1], r=_radius(labeled.polygon, center_px)), physics=Physics(static=True)))
        elif labeled.type == "pivot":
            pivots.append(center)
            built.append(Part(id=part_id, type="pivot", shape=Sensor(kind="sensor", x=center[0], y=center[1], r=8), physics=Physics(static=True)))
        elif labeled.type in {"ramp", "lever"}:
            a_px, b_px = _axis(labeled.polygon)
            a, b = to_world(a_px), to_world(b_px)
            if labeled.type == "ramp":
                built.append(Part(id=part_id, type="ramp", shape=Segment(kind="segment", a=a, b=b, thickness=8), physics=Physics(static=True, friction=0.7)))
            else:
                pivot = pivots[-1] if pivots else center
                built.append(Part(id=part_id, type="lever", shape=Beam(kind="beam", a=a, b=b, thickness=10), pivot=pivot, physics=Physics(mass=mass, friction=0.6)))
        elif labeled.type == "spring":
            anchor = to_world(labeled.polygon[0] if labeled.polygon else center_px)
            built.append(Part(id=part_id, type="spring", shape=Segment(kind="segment", a=anchor, b=center, thickness=4), anchor=anchor, rest_length=math.dist(anchor, center), stiffness=350, physics=Physics(mass=mass)))
    bell = next((part for part in built if part.type == "bell"), None)
    target = bell.id if bell else "bell_1"
    goal = Goal(target=target)
    if goal_text and "target" in goal_text.lower() and bell:
        goal = goal.model_copy(update={"target": bell.id})
    return Scene(world=World(width=WORLD_WIDTH, height=WORLD_HEIGHT), goal=goal, parts=built, provenance={"goal_text": goal_text or ""})
