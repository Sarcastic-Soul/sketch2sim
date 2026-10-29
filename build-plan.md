# Sketch2Sim — Detailed Build Plan

A step-by-step implementation spec, written so it can be followed literally,
one file at a time, with no guessing. Read `architecture.md` for the big
picture. This document is the order of operations and the exact contents.

Everything here runs locally and free. The only external calls are to Meta
Model API (paid by the $150 hackathon credits) and, for the repair loop,
Baseten/Modal (their own free credits). A card must be on file at
dev.meta.ai before the API key works; adding it causes a temporary
pre-authorization that is released automatically. No other service costs money.

Golden rule for the implementer: **never call a model without the cache.**
Every model response is cached on disk by a hash of its input, so re-running
the app during development does not spend credits twice.

---

## 0. Conventions used in this document

- All paths are relative to the repo root `sketch2sim/`.
- Python 3.11+. Keep functions small and typed. Use `pydantic` models, not
  loose dicts, for anything that crosses a stage boundary.
- Every model-calling function takes its inputs, computes a cache key, and
  returns the cached result if present. No exceptions.
- When unsure of a Meta API request shape, check the live docs listed in
  section 11 before writing the call. Do not invent endpoints.

---

## 1. Repository skeleton (build this first)

Create exactly this tree. Empty files are fine to start; we fill them in order.

```
sketch2sim/
  README.md
  .env.example
  .gitignore
  requirements.txt
  backend/
    __init__.py
    app.py                 # FastAPI entrypoint
    config.py              # loads .env, constants
    schemas.py             # pydantic Scene JSON models
    meta/
      __init__.py
      client.py            # Meta Model API + Baseten client wrappers
      cache.py             # on-disk response cache
    pipeline/
      __init__.py
      perception.py        # SAM + Spark -> labeled parts
      scene_builder.py     # labeled parts -> Scene JSON  (pure, tested)
      simulate.py          # Scene JSON -> result + frames (pymunk)
      repair.py            # repair loop on Muse Spark Open
      render.py            # Muse Image final illustration
      voice.py             # Muse Voice Transcribe
  frontend/
    index.html
    main.js
    style.css
  tests/
    __init__.py
    test_scene_builder.py
    test_simulate.py
  samples/                 # 5 pre-tested reference sketch images + their goals
  cache/                   # on-disk model cache (gitignored)
```

### 1.1 `.gitignore`
```
.env
cache/
__pycache__/
*.pyc
.venv/
node_modules/
*.mp4
```

### 1.2 `.env.example`
```
META_API_KEY=your_key_here
META_BASE_URL=https://api.meta.ai/v1
BASETEN_API_KEY=your_baseten_key_here
BASETEN_MODEL=meta-models/muse-spark-open-1026
# Model IDs (override if the hackathon publishes different ones)
SPARK_MODEL=muse-spark-1.3
IMAGE_MODEL=muse-image
TRANSCRIBE_MODEL=muse-voice-transcribe
SAM_MODEL=sam-3.1
CACHE_DIR=cache
SPEND_ALERT_USD=150
```

### 1.3 `requirements.txt`
```
fastapi
uvicorn[standard]
pydantic>=2
python-dotenv
openai
httpx
pymunk>=7
pillow
numpy
opencv-python
python-multipart        # file uploads in FastAPI
pytest
ruff
black
```

### 1.4 `requirements` note on SAM client
The official `Meta-SAM` client library parses SAM wire output. If it installs
cleanly, add it. If not, we parse the SAM streaming envelope by hand in
`perception.py` (section 5.2 explains the format). Do not block on it.

---

## 2. `backend/config.py`

Loads environment and exposes typed constants. No logic beyond reading env.

```python
import os
from dotenv import load_dotenv

load_dotenv()

META_API_KEY   = os.environ["META_API_KEY"]
META_BASE_URL  = os.getenv("META_BASE_URL", "https://api.meta.ai/v1")
BASETEN_API_KEY = os.getenv("BASETEN_API_KEY", "")
BASETEN_MODEL  = os.getenv("BASETEN_MODEL", "meta-models/muse-spark-open-1026")

SPARK_MODEL      = os.getenv("SPARK_MODEL", "muse-spark-1.3")
IMAGE_MODEL      = os.getenv("IMAGE_MODEL", "muse-image")
TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL", "muse-voice-transcribe")
SAM_MODEL        = os.getenv("SAM_MODEL", "sam-3.1")

CACHE_DIR = os.getenv("CACHE_DIR", "cache")

# World/simulation constants (tune in one place)
WORLD_WIDTH  = 800
WORLD_HEIGHT = 600
GRAVITY      = -981.0        # px/s^2, downward
PIXELS_PER_METER = 100.0
SIM_FPS      = 60
SIM_MAX_SECONDS = 12
MAX_REPAIR_ATTEMPTS = 4      # hard cap; keeps demo deterministic
PART_TYPES = ["ball", "ramp", "lever", "pivot", "spring", "bell"]
```

---

## 3. `backend/meta/cache.py` (build before any model call)

A dead-simple disk cache. Key = sha256 of (namespace + payload bytes).
Value = the model's JSON/binary response. Build this now so every model
function can use it from day one.

```python
import hashlib, json, os
from pathlib import Path
from backend.config import CACHE_DIR

def _key(namespace: str, payload: bytes) -> str:
    h = hashlib.sha256()
    h.update(namespace.encode())
    h.update(payload)
    return h.hexdigest()

def cache_path(namespace: str, payload: bytes, ext: str) -> Path:
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
    return Path(CACHE_DIR) / f"{namespace}_{_key(namespace, payload)}.{ext}"

def get_json(namespace: str, payload: bytes):
    p = cache_path(namespace, payload, "json")
    if p.exists():
        return json.loads(p.read_text())
    return None

def put_json(namespace: str, payload: bytes, value) -> None:
    cache_path(namespace, payload, "json").write_text(json.dumps(value))

def get_bytes(namespace: str, payload: bytes, ext: str):
    p = cache_path(namespace, payload, ext)
    return p.read_bytes() if p.exists() else None

def put_bytes(namespace: str, payload: bytes, value: bytes, ext: str) -> None:
    cache_path(namespace, payload, ext).write_bytes(value)
```

Pattern every model function follows:
```python
payload = <stable bytes describing the request>   # image bytes + prompt, etc.
cached = cache.get_json("spark_label", payload)
if cached is not None:
    return cached
result = <actual model call>
cache.put_json("spark_label", payload, result)
return result
```

---

## 4. `backend/schemas.py` — the Scene JSON (build before pipeline)

This is the contract every stage reads and writes. Define it with pydantic so
invalid scenes fail loudly.

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class Circle(BaseModel):
    kind: Literal["circle"]
    x: float; y: float; r: float

class Segment(BaseModel):
    kind: Literal["segment"]
    a: tuple[float, float]; b: tuple[float, float]; thickness: float = 6

class Beam(BaseModel):
    kind: Literal["beam"]
    a: tuple[float, float]; b: tuple[float, float]; thickness: float = 8

class Sensor(BaseModel):
    kind: Literal["sensor"]
    x: float; y: float; r: float

Shape = Circle | Segment | Beam | Sensor

class Physics(BaseModel):
    mass: float = 1.0
    friction: float = 0.5
    elasticity: float = 0.3
    static: bool = False

class Part(BaseModel):
    id: str
    type: Literal["ball","ramp","lever","pivot","spring","bell"]
    shape: Shape = Field(discriminator="kind")
    physics: Physics = Physics()
    pivot: Optional[tuple[float, float]] = None   # for lever
    anchor: Optional[tuple[float, float]] = None  # for spring
    stiffness: Optional[float] = None             # for spring
    rest_length: Optional[float] = None           # for spring

class World(BaseModel):
    width: int = 800; height: int = 600
    gravity: float = -981.0; scale: float = 0.01

class Goal(BaseModel):
    type: Literal["ring_bell","reach_target"] = "ring_bell"
    target: str = "bell_1"
    within_seconds: float = 10

class Scene(BaseModel):
    world: World = World()
    goal: Goal = Goal()
    parts: list[Part]
    provenance: dict = {}
```

---

## 5. Stage A — `backend/pipeline/perception.py`

Turns a sketch photo into a list of labeled, typed parts. Two model calls:
SAM for geometry, Spark for semantics. Both cached.

### 5.1 Function shape
```python
def read_sketch(image_bytes: bytes) -> list[LabeledPart]:
    masks = run_sam(image_bytes)          # geometry
    labeled = label_with_spark(image_bytes, masks)  # semantics
    return labeled
```

### 5.2 `run_sam(image_bytes)`
- Call SAM 3.1 on the Meta API with text noun-phrase prompts for each part
  type in `PART_TYPES` ("ball", "ramp", ...). SAM supports a short noun-phrase
  prompt and also box/point prompts.
- SAM returns a streaming envelope: per-object `box` (x,y,w,h), a `mask`
  (run-length or polygon depending on format), and a `confidence`. Parse each
  line into `{type_hint, box, mask, confidence}`.
- If the text prompt returns nothing for a part type, that is fine — Spark can
  still catch it from the raw image in 5.3.
- Cache namespace `"sam"`, payload = image_bytes.

Define:
```python
class Mask(BaseModel):
    type_hint: str
    box: tuple[float,float,float,float]   # x, y, w, h (pixels)
    polygon: list[tuple[float,float]]     # simplified contour in pixels
    confidence: float
```

### 5.3 `label_with_spark(image_bytes, masks)`
- Send the original image + a compact description of each mask (box + type
  hint) to Muse Spark (multimodal). Ask it to return STRICT JSON:
  ```json
  { "parts": [ {"mask_index": 0, "type": "ramp", "notes": {"angle_hint": null}} ],
    "goal_text": "ring the bell",
    "annotations": [ {"text": "10 kg", "near_mask": 2} ] }
  ```
- System prompt must pin the 6 allowed types and forbid prose outside JSON.
- Parse into `LabeledPart`:
  ```python
  class LabeledPart(BaseModel):
      type: str
      polygon: list[tuple[float,float]]
      box: tuple[float,float,float,float]
      mass: Optional[float] = None
      extra: dict = {}
  ```
- Cache namespace `"spark_label"`, payload = image_bytes + masks digest.

Day-1 gate lives here: run 5 sample images through `read_sketch`, print the
labeled parts, eyeball them. If wrong, we switch to the backup idea.

---

## 6. Stage B — `backend/pipeline/scene_builder.py` (pure, no model calls)

Converts `list[LabeledPart]` into a validated `Scene`. This is deterministic
and fully unit-tested. No network.

### 6.1 Coordinate mapping
- SAM returns pixel coords with origin top-left, y down. pymunk uses y up.
- Provide one helper: `to_world(px, py) -> (wx, wy)` that flips y:
  `wy = WORLD_HEIGHT - py`. Keep x as-is. Apply to every point once, here.

### 6.2 Per-type construction rules
```python
def build_scene(parts: list[LabeledPart], goal_text: str | None) -> Scene:
```
- **ball**: fit a circle to the polygon (center = centroid, r = mean radius).
  Dynamic body. mass from label or default 10.
- **ramp**: fit a straight segment to the polygon's longest axis. Static.
- **lever**: fit a beam (longest axis). pivot = polygon centroid (or the
  nearest detected `pivot` part). Dynamic, with a pivot constraint added in
  the simulator.
- **pivot**: a point only; stored as an anchor other parts reference.
- **spring**: anchor = top point, rest length = polygon length, stiffness
  default.
- **bell**: a sensor circle at the centroid. Never collides physically; only
  triggers the goal.
- **goal**: parse `goal_text` → `Goal(type="ring_bell", target=<bell id>)`.
  Default to ring_bell if a bell exists.

### 6.3 Output
A `Scene` with stable ids (`ball_1`, `ramp_1`, ...). Store the raw masks in
`provenance` so the UI can draw overlays and the repair agent has context.

---

## 7. Stage C — `backend/pipeline/simulate.py` (pymunk, the verifier)

Builds a pymunk `Space` from a `Scene`, steps it deterministically, records
frames, and checks the goal. No model calls. This is the oracle the agent
trusts.

### 7.1 Function shape
```python
class SimResult(BaseModel):
    success: bool
    seconds: float
    log: list[str]              # human-readable events for the agent
    frames: list[dict]          # per-frame body positions for the canvas
    metrics: dict               # e.g. {"closest_ball_bell_dist": 7.9}

def simulate(scene: Scene) -> SimResult:
```

### 7.2 Build rules
- `space = pymunk.Space()`, `space.gravity = (0, scene.world.gravity)`.
- Create bodies/shapes per part. Static parts use `space.static_body` segments.
- Lever: dynamic beam + `PivotJoint` at `part.pivot`.
- Spring: `DampedSpring` between anchor and attached body.
- Bell: a `Shape` with `sensor=True`; register a collision handler that sets a
  `rang` flag on begin.

### 7.3 Stepping (deterministic!)
- Fixed timestep `dt = 1/SIM_FPS`. Step `SIM_FPS * SIM_MAX_SECONDS` times max.
- Every step (or every few steps) append body positions to `frames`.
- Track `metrics["closest_ball_bell_dist"]` = min distance ball↔bell over time.
- Stop early when the bell rings → `success=True`.
- Append readable log lines: `"t=2.1s ball left the ramp"`,
  `"t=4.0s lever did not rotate (torque too low)"`,
  `"ended: ball came to rest 7.9cm short of the bell"`. These lines are what
  the repair agent reads, so make them specific and quantitative.

Determinism matters: same scene in → same result out. No randomness, no
wall-clock timing. This is what keeps the live demo from flaking.

---

## 8. Stage D — `backend/pipeline/repair.py` (the agentic loop)

The centerpiece. Runs Muse Spark Open (open weight, via Baseten) to edit the
Scene JSON based on the sim log, then re-simulates, up to `MAX_REPAIR_ATTEMPTS`.

### 8.1 Function shape
```python
class Attempt(BaseModel):
    n: int
    reasoning: str          # the agent's short explanation this turn
    edits: list[dict]       # structured edits it applied
    result: SimResult

def repair_loop(scene: Scene):   # generator, yields Attempt per turn
    result = simulate(scene)
    yield Attempt(n=0, reasoning="initial run", edits=[], result=result)
    n = 1
    while not result.success and n <= MAX_REPAIR_ATTEMPTS:
        edits, reasoning = propose_edit(scene, result)   # model call
        scene = apply_edits(scene, edits)                # pure
        result = simulate(scene)
        yield Attempt(n=n, reasoning=reasoning, edits=edits, result=result)
        n += 1
```

### 8.2 `propose_edit(scene, result)` — Muse Spark Open via Baseten
- Prompt: current Scene JSON + the sim log + metrics. Ask for STRICT JSON:
  ```json
  { "reasoning": "ramp too shallow; raise it 12 degrees",
    "edits": [ {"op":"rotate","part":"ramp_1","degrees":12},
               {"op":"set","part":"lever_1","field":"physics.mass","value":8} ] }
  ```
- Allowed ops (keep the set small and safe): `rotate`, `move`, `scale`,
  `set` (a numeric field), `add_part`, `remove_part`.
- The model NEVER rewrites the whole scene freehand — it only emits edits, and
  `apply_edits` validates each against the schema. Reject unknown ops.
- Cache namespace `"repair"`, payload = scene digest + log digest, so a replay
  of the same failing state is free and identical.

### 8.3 `apply_edits(scene, edits) -> Scene` — pure
- Apply each op to a copy of the scene, re-validate with pydantic, return it.
- If an edit makes the scene invalid, skip it and note it in the log.

### 8.4 Baseten client (in `meta/client.py`)
- Baseten exposes an OpenAI-compatible chat endpoint; use the `openai` SDK with
  `base_url` set to the Baseten model URL and `model=BASETEN_MODEL`.
- If Baseten credits have not arrived, fall back: run the repair prompt on
  Muse Spark (hosted) instead, so the loop still works — but note that the
  Open Weights bonus specifically wants Spark Open, so prefer Baseten when
  available. This fallback keeps the project free and unblocked either way.

---

## 9. Stages E & Voice

### 9.1 `backend/pipeline/render.py` — Muse Image
```python
def render_machine(scene: Scene) -> bytes:   # returns PNG bytes, cached
```
- Build a text description of the successful machine from the scene and ask
  Muse Image for one clean illustration. Cache namespace `"image"`, payload =
  scene digest. Pure presentation; failure here must not break the run.

### 9.2 `backend/pipeline/voice.py` — Muse Voice Transcribe
```python
def transcribe_goal(audio_bytes: bytes) -> str:   # cached by audio hash
```
- Send audio to Voice Transcribe, return text. The caller sets/overrides
  `scene.goal` from it before simulating.

---

## 10. `backend/meta/client.py` — one place for all model calls

Centralize clients so the pipeline files stay clean.
```python
from openai import OpenAI
from backend import config

meta = OpenAI(api_key=config.META_API_KEY, base_url=config.META_BASE_URL)

def baseten_client():
    return OpenAI(api_key=config.BASETEN_API_KEY,
                  base_url="<baseten model openai-compatible url>")
```
- Wrap: `chat_vision(image, prompt)`, `chat_text(prompt)`,
  `generate_image(prompt)`, `transcribe(audio)`, `segment(image, prompts)`.
- Each wrapper is the ONLY code that talks to the network, and each goes
  through the cache. If a model id is wrong, fix it in `.env`, not in code.

---

## 11. `backend/app.py` — FastAPI + SSE

Wires the pipeline to the browser.

### 11.1 Endpoints
- `POST /upload` — multipart image (+ optional audio). Runs Stage A→B, returns
  `{run_id, scene, masks}`. Stores the scene server-side keyed by `run_id`.
- `GET /run/{run_id}/stream` — **SSE**. Runs `repair_loop`, emitting one event
  per `Attempt`:
  ```
  event: attempt
  data: {"n":1,"reasoning":"...","result":{"success":false,"frames":[...]}}
  ```
  Final event `event: done` with `{success, image_url}`.
- `GET /run/{run_id}/render` — returns the Muse Image PNG (after success).
- `POST /voice` — audio → transcript (sets the goal).
- `GET /` — serves the frontend.

### 11.2 SSE detail
Use `StreamingResponse` with media type `text/event-stream`. Yield from the
`repair_loop` generator, serializing each `Attempt` to a `data:` line. This is
what gives the demo its live "watch it fix itself" feel.

---

## 12. Frontend — `frontend/`

Keep it minimal and legible on video. No framework required.

### 12.1 `index.html`
- A drop zone / file input for the sketch.
- A `<canvas id="sim">` for the simulation and mask overlay.
- A `<ol id="attempts">` list that fills as SSE events arrive.
- A final `<img id="render">` for the Muse Image illustration.
- Icons: Phosphor or Heroicons only. No blue/purple gradients, no gradient text.

### 12.2 `main.js`
- `POST /upload`, draw the returned masks over the uploaded image on the canvas.
- Open `EventSource("/run/{id}/stream")`. On each `attempt` event: append a line
  to `#attempts` ("Attempt 2: ramp too shallow, raising 12°") and animate the
  returned frames on the canvas.
- On `done`: show the render.

### 12.3 Canvas animation
- A small loop that reads `frames[]` (body id → x,y,angle) and redraws shapes
  each tick. Flip y back for display (canvas y is down).

---

## 13. Tests — `tests/`

Fast, pure, no network. Run with `pytest`.
- `test_scene_builder.py`: feed hand-written `LabeledPart` lists, assert the
  resulting `Scene` has correct types, ids, coordinate flips, and goal.
- `test_simulate.py`: build a known-good scene (ball rolls down a ramp into a
  bell sensor) and assert `success is True`; build a known-short scene and
  assert `success is False` with a sensible `closest_ball_bell_dist`.
- These two files are the safety net that lets the repair loop be trusted.

---

## 14. Build order (do strictly in this order)

1. Skeleton + `.gitignore` + `.env.example` + `requirements.txt` (section 1).
2. `config.py`, `meta/cache.py`, `schemas.py` (sections 2–4). No models yet.
3. `scene_builder.py` + `test_scene_builder.py` (section 6) — pure, testable.
4. `simulate.py` + `test_simulate.py` (section 7) — pure, testable. **Now you
   have a working sim with hand-written scenes, no API needed.**
5. `meta/client.py` wrappers + wire the cache (section 10).
6. `perception.py` (section 5) — first real API use. **Run the Day-1 gate here.**
7. `repair.py` (section 8) — the loop.
8. `render.py`, `voice.py` (section 9).
9. `app.py` SSE + endpoints (section 11).
10. `frontend/` (section 12).
11. `samples/` — 5 sketches that reliably pass; record the backup demo.
12. README + 3-min video + public repo + submit.

Steps 3–4 give you a demoable physics sandbox **before any credit is spent**,
so the hardest engineering is validated while waiting for the API key. Steps
5–8 layer the models on top once credits arrive.

---

## 15. Day mapping (from AGENTS.md, with this plan)

- **Day 1**: steps 1–4 fully (skeleton + schemas + scene builder + sim, all
  tested offline), then the moment the key arrives, step 6 + Day-1 gate.
- **Day 2**: finish perception, start repair loop (steps 6–7).
- **Day 3**: repair loop solid + SSE streaming (steps 7, 9's app part).
- **Day 4**: voice + render + frontend polish + sample gallery (steps 8–11).
- **Day 5**: README, record video, public repo, submit before Nov 4 9pm ET.

---

## 16. Cost & safety checklist

- [ ] All model calls go through `meta/cache.py`. (No uncached call anywhere.)
- [ ] `.env` is gitignored; only `.env.example` is committed.
- [ ] Spend alert set at $150 on dev.meta.ai; card on file.
- [ ] Baseten/Modal used only within their free credits; hosted-Spark fallback
      documented so a missing credit never forces a paid call.
- [ ] pymunk sim is deterministic (fixed dt, no randomness).
- [ ] Repair loop hard-capped at `MAX_REPAIR_ATTEMPTS`.
- [ ] A recorded backup demo exists before the live session.
- [ ] Commits dated Oct 27–Nov 4, conventional style, authored by Anish, no AI
      attribution trailer.
```
