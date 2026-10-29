# Sketch2Sim

Sketch2Sim turns a hand-drawn mechanism into a structured scene, runs it through a deterministic 2D physics verifier, and gives an agent bounded chances to repair it.

## Run locally

```bash
cd sketch2sim
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn backend.app:app --reload
```

Open http://127.0.0.1:8000. Without API keys, the app uses a deterministic fallback sketch and repair path so the simulation can be tested offline. Add credentials from `.env.example` to enable Meta model calls. Every external response is cached in `cache/`.

## Pipeline

1. SAM 3.1 finds geometry and Muse Spark reads labels and annotations.
2. The scene builder converts the result into validated Pydantic models.
3. Pymunk runs a fixed-timestep simulation and acts as the verifier.
4. Muse Spark Open proposes bounded JSON edits from the simulation log.
5. Muse Image renders the verified machine. Muse Voice Transcribe accepts spoken goals.

The repair loop never applies a free-form scene rewrite. Each edit is validated before the next deterministic simulation.
