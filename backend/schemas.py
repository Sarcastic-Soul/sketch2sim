from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Circle(BaseModel):
    kind: Literal["circle"]
    x: float
    y: float
    r: float


class Segment(BaseModel):
    kind: Literal["segment"]
    a: tuple[float, float]
    b: tuple[float, float]
    thickness: float = 6


class Beam(BaseModel):
    kind: Literal["beam"]
    a: tuple[float, float]
    b: tuple[float, float]
    thickness: float = 8


class Sensor(BaseModel):
    kind: Literal["sensor"]
    x: float
    y: float
    r: float


Shape = Circle | Segment | Beam | Sensor


class Physics(BaseModel):
    mass: float = 1.0
    friction: float = 0.5
    elasticity: float = 0.3
    static: bool = False


class Part(BaseModel):
    id: str
    type: Literal["ball", "ramp", "lever", "pivot", "spring", "bell"]
    shape: Shape = Field(discriminator="kind")
    physics: Physics = Physics()
    pivot: tuple[float, float] | None = None
    anchor: tuple[float, float] | None = None
    stiffness: float | None = None
    rest_length: float | None = None


class World(BaseModel):
    width: int = 800
    height: int = 600
    gravity: float = -981.0
    scale: float = 0.01


class Goal(BaseModel):
    type: Literal["ring_bell", "reach_target"] = "ring_bell"
    target: str = "bell_1"
    within_seconds: float = 10


class Scene(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    world: World = World()
    goal: Goal = Goal()
    parts: list[Part]
    provenance: dict = {}


class Mask(BaseModel):
    type_hint: str
    box: tuple[float, float, float, float]
    polygon: list[tuple[float, float]]
    confidence: float = 0.0


class LabeledPart(BaseModel):
    type: Literal["ball", "ramp", "lever", "pivot", "spring", "bell"]
    polygon: list[tuple[float, float]]
    box: tuple[float, float, float, float]
    mass: float | None = None
    extra: dict = {}


class SimResult(BaseModel):
    success: bool
    seconds: float
    log: list[str]
    frames: list[dict]
    metrics: dict


class Attempt(BaseModel):
    n: int
    reasoning: str
    edits: list[dict]
    result: SimResult
