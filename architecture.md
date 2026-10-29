# Sketch2Sim — Architecture & Tech Stack

Finalized project for the Meta Global AI Developer Hackathon (Indie track,
solo, Push the Frontier theme). This document is the build contract: it fixes
what we are building, the stack, the data contracts between stages, and how
the Meta models are wired in. Read `README.md` for event rules and `ideas.md`
for the scoring rationale.

## 1. The product in one paragraph

Photograph a hand-drawn mechanism (ramps, levers, pivots, springs, a ball, a
bell). An agent reads the sketch into a structured scene, runs it as a live 2D
physics simulation, checks whether it reaches the stated goal, and when it
fails, edits the scene and retries — showing its reasoning each attempt. On
success it renders a clean illustration of the working machine. A second input
path lets the user state the goal by voice.

The judged artifact is a 3-minute demo video; the thing that makes it win is
the **closed agentic loop with a real verifier** (the physics sim is the
oracle), not a one-shot generation.

## 2. Why this fits the rubric

- **Impact (30%)** — weakest axis. Framed for students, teachers, and makers:
  turn a napkin idea into something you can test without building it. Keep the
  framing concrete in the demo.
- **Use of Meta tooling (25%)** — five Meta capabilities, each doing a job only
  it can do (segmentation, multimodal reading, open-weight agent loop, voice,
  image). Not a single chat call.
- **Demo (25%)** — masks lighting up, a sim running, the agent failing then
  fixing itself, the bell ringing. Visually legible in 3 minutes.
- **Technical depth (20%)** — SAM masks → geometry extraction → physics scene →
  verifier → repair loop is genuine engineering, not prompt glue.

Bonus targets: Best Agentic Use-Case (primary), Best Build on Open Weights
(repair loop runs on Muse Spark Open), Most Viral (sketch→machine clips),
Best Creative Build (Muse Image render).

## 3. System overview

```
                        ┌─────────────────────────────────────────┐
                        │              Browser UI                  │
                        │  upload sketch · voice goal · live sim    │
                        │  canvas · attempt log · final render      │
                        └───────────────┬───────────────┬──────────┘
                                        │ REST + SSE     │
                        ┌───────────────▼───────────────▼──────────┐
                        │            FastAPI backend                │
                        │  orchestrates the pipeline, streams events│
                        └───┬────────┬────────┬────────┬────────┬───┘
                            │        │        │        │        │
                 ┌──────────▼──┐ ┌───▼────┐ ┌─▼──────┐ ┌▼──────┐ ┌▼────────┐
                 │  Perception │ │ Scene  │ │ Physics│ │Repair │ │ Render  │
                 │  SAM + Spark│ │ builder│ │ pymunk │ │ agent │ │  Image  │
                 └──────┬──────┘ └───┬────┘ └───┬────┘ └──┬────┘ └────┬────┘
                        │            │          │         │          │
                 ┌──────▼────────────▼──────────▼─────────▼──────────▼──────┐
                 │               Meta Model API (api.meta.ai/v1)            │
                 │  SAM 3.1 · Muse Spark (vision) · Voice Transcribe ·      │
                 │  Muse Image     +    Muse Spark Open via Baseten/Modal   │
                 └──────────────────────────────────────────────────────────┘
```

## 4. The pipeline (data contract between stages)

The whole system is a pipeline with one canonical artifact passed between
stages: the **Scene JSON**. Every stage reads it, writes it, or renders it.

### Stage A — Perception (sketch → parts)
- **Input**: uploaded photo of the sketch (JPEG/PNG), optional voice goal.
- **SAM 3.1** segments the drawing. We drive it two ways:
  1. text noun-phrase prompts for the ~6 known part types ("ramp", "ball",
     "lever", "pivot", "spring", "bell"), and
  2. point/box prompts as a fallback where the text prompt is ambiguous.
  Output: per-object masks + bounding boxes + confidence.
- **Muse Spark (multimodal)** gets the original image + the SAM masks and
  returns a labeled, typed reading: which mask is which part type, plus any
  handwritten annotations ("10 kg", "goal: ring the bell"). Spark is the
  semantic reader; SAM is the geometry.

### Stage B — Scene builder (parts → Scene JSON)
Pure Python. Converts masks + labels into physics-ready geometry:
- mask → simplified polygon / primitive (ramp = angled segment, ball = circle,
  lever = beam + pivot constraint, spring = damped spring, bell = sensor
  target).
- pixel coordinates → simulation world coordinates (fixed scale, y-flip).
- attaches parameters read by Spark (mass, goal).
This is deterministic and cacheable — no model call — so re-runs are free.

### Stage C — Physics simulation (Scene JSON → result + frames)
- **pymunk** (Chipmunk2D binding) builds a `Space`, adds bodies/shapes/
  constraints from the Scene JSON, steps at a fixed timestep.
- A **goal checker** watches for the success condition (e.g. ball overlaps the
  bell sensor within N seconds).
- Output: `{success: bool, log: [...], frames: [...]}`. Frames are rendered
  to the canvas; the log feeds the repair agent.

### Stage D — Repair agent (loop, the centerpiece)
- Runs **Muse Spark Open** (open weight, via Baseten/Modal — this is what wins
  the Open Weights bonus and makes the loop "agentic").
- Input each turn: current Scene JSON + the sim log ("ball fell 8cm short of
  the bell", "lever never rotated"). Output: a **diff/edit to the Scene JSON**
  (raise ramp angle, lengthen lever, add a part), as structured tool-call /
  JSON output — never free-form prose applied blindly.
- Re-run Stage C. Loop until success or a hard cap of 3–4 attempts
  (deterministic, keeps the demo reliable).
- Every attempt is streamed to the UI as a reasoning line.

### Stage E — Render (success → illustration)
- **Muse Image** generates a clean illustration of the final working machine
  from the successful Scene JSON description. Pure presentation; targets the
  Creative bonus.

### Voice path (parallel input)
- **Muse Voice Transcribe** turns a spoken goal ("make it ring the bell
  faster") into text, which sets/overrides the goal in the Scene JSON before
  Stage C.

## 5. Tech stack

### Backend
- **Python 3.11+**
- **FastAPI** + **uvicorn** — REST endpoints and **Server-Sent Events (SSE)**
  to stream sim frames and agent attempts to the browser in real time.
- **pymunk** (7.x) — 2D rigid-body physics (Chipmunk2D). The verifier/oracle.
- **Pillow / numpy / opencv-python** — decode SAM masks, simplify contours to
  polygons, map pixels → world coordinates.
- **pydantic** — the Scene JSON schema, validated at every stage boundary.
- **openai** SDK (OpenAI-compatible) pointed at `https://api.meta.ai/v1` for
  Spark vision, Muse Image, Voice Transcribe.
- **Meta-SAM** official client library for SAM prompt building + mask parsing.
- **httpx** — Baseten/Modal calls for Muse Spark Open where not OpenAI-shaped.

### Frontend
- **Single-page app, plain and fast.** Vite + a light framework (or vanilla +
  HTML canvas — decide Day 2; no heavy framework needed).
- **HTML5 Canvas** renders simulation frames and the SAM mask overlay.
- SSE client consumes the backend event stream (upload → masks → attempts →
  success → render).
- **Icons: Phosphor or Heroicons only — never Lucide.**
- **No blue or purple gradients, no gradient text** (per project UI rules).

### Meta models (the required core)
| Stage | Model | Access | Job |
|---|---|---|---|
| Perception geometry | **SAM 3.1** | Meta Model API | segment parts → masks/boxes |
| Perception semantics | **Muse Spark** (multimodal) | Meta Model API | label parts, read notes → types+params |
| Repair loop | **Muse Spark Open** | Baseten `meta-models/muse-spark-open-1026` (Modal fallback) | edit Scene JSON from sim log |
| Voice goal | **Muse Voice Transcribe** | Meta Model API | spoken goal → text |
| Final render | **Muse Image** | Meta Model API | illustration of working machine |

### Infra / tooling
- **python-dotenv** + `.env` (never committed; ship `.env.example`).
- **Response cache** (on-disk, keyed by image hash + prompt) so dev re-runs do
  not burn the $150 credits. Cache SAM, Spark, Image, Transcribe results.
- **pytest** for the Scene builder and goal checker (pure-Python, fast to test).
- **ruff** + **black** for lint/format.
- Hosting optional; if hosted, rate-limit and cap API usage.

## 6. Scene JSON schema (draft)

```jsonc
{
  "world": { "width": 800, "height": 600, "gravity": -981, "scale": 0.01 },
  "goal": { "type": "ring_bell", "within_seconds": 10, "target": "bell_1" },
  "parts": [
    {
      "id": "ball_1", "type": "ball",
      "shape": { "kind": "circle", "x": 120, "y": 500, "r": 18 },
      "physics": { "mass": 10, "friction": 0.4, "elasticity": 0.5 }
    },
    {
      "id": "ramp_1", "type": "ramp",
      "shape": { "kind": "segment", "a": [100,480], "b": [400,300], "thickness": 6 },
      "physics": { "static": true, "friction": 0.6 }
    },
    {
      "id": "lever_1", "type": "lever",
      "shape": { "kind": "beam", "a": [420,300], "b": [560,300], "thickness": 8 },
      "pivot": [490, 300],
      "physics": { "mass": 5 }
    },
    { "id": "bell_1", "type": "bell",
      "shape": { "kind": "sensor", "x": 700, "y": 260, "r": 24 } }
  ],
  "provenance": { "source_masks": {...}, "spark_notes": [...] }
}
```
Validated by pydantic. The repair agent only ever emits edits to this object.

## 7. Repository layout

```
sketch2sim/
  backend/
    app.py                 # FastAPI, routes + SSE
    pipeline/
      perception.py        # SAM + Spark → labeled parts
      scene_builder.py     # parts → Scene JSON (pure, tested)
      simulate.py          # pymunk space, step, goal checker, frames
      repair.py            # Muse Spark Open loop
      render.py            # Muse Image
      voice.py             # Muse Voice Transcribe
    meta/
      client.py            # Meta Model API client (openai SDK + httpx)
      cache.py             # on-disk response cache
    schemas.py             # pydantic Scene JSON models
  frontend/                # Vite SPA, canvas, SSE client
  tests/                   # scene_builder + goal checker
  samples/                 # 5 pre-tested reference sketches
  .env.example
  README.md
```

## 8. 5-day plan (mapped to stages)

- **Day 1** — *Gate first.* Add card, API key, spend alert. Run 5 real sketches
  through SAM + Spark; confirm masks + labels are usable from India. Confirm
  Voice Transcribe + Muse Image respond. Go/no-go: if sketch reading is poor,
  switch to ShopFront Studio. Then scaffold FastAPI + upload + Stage A.
- **Day 2** — Stage B (scene builder) + Stage C (pymunk sim + canvas renderer).
  Get one sketch running end to end without the agent.
- **Day 3** — Stage D repair loop on Muse Spark Open, sim-log feedback, success
  checks, SSE streaming of attempts. This is the demo's heart.
- **Day 4** — Voice path, Muse Image render, UI polish, gallery of 5 tested
  sketches. Record a backup demo run.
- **Day 5** — Record 3-min video, write README, public repo, X post for Most
  Viral, submit before Nov 4 9:00 PM ET.

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Messy handwriting / bad masks | restrict to ~6 part types; point-prompt fallback; pre-test on real sketches Day 1 |
| Flaky live demo | deterministic sim (fixed timestep/seed), cap loop at 3–4, keep a recorded backup run |
| Fixes look trivial ("toy") | choose goals needing real reasoning (angle + added lever), show the attempt log |
| Open-model latency | cap iterations, cache a known-good backup run |
| Burning credits in dev | on-disk cache keyed by input hash; spend alert at $150 |
| Impact scores low | lead the demo with the student/maker framing, not the tech |

## 10. Hard constraints (from AGENTS.md)

- Everything shown must be built Oct 27–Nov 4; keep git history honest, no AI
  attribution trailers, conventional commits, author = Anish.
- Public repo; never commit secrets; `.env.example` only.
- Must genuinely use Meta models (satisfied: 5 of them, core to the pipeline).
- Avoid banned/generic project types (Sketch2Sim is clear of the list).
