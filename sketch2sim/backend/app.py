import asyncio
import json
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.pipeline.perception import read_sketch, run_sam
from backend.pipeline.render import render_machine
from backend.pipeline.repair import repair_loop
from backend.pipeline.scene_builder import build_scene
from backend.pipeline.voice import transcribe_goal

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Sketch2Sim")
app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")
runs: dict[str, object] = {}
renders: dict[str, bytes] = {}


@app.get("/")
async def index():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.post("/upload")
async def upload(file: UploadFile = File(...), goal: str = Form("ring the bell")):
    data = await file.read()
    labeled, detected_goal = read_sketch(data)
    scene = build_scene(labeled, goal or detected_goal)
    run_id = uuid.uuid4().hex
    runs[run_id] = scene
    return {"run_id": run_id, "scene": scene.model_dump(), "masks": [mask.model_dump() for mask in run_sam(data)]}


@app.get("/run/{run_id}/stream")
async def stream(run_id: str):
    scene = runs.get(run_id)
    if scene is None:
        return JSONResponse({"error": "run not found"}, status_code=404)

    async def events():
        final = None
        for attempt in repair_loop(scene):
            final = attempt
            yield f"event: attempt\ndata: {attempt.model_dump_json()}\n\n"
            await asyncio.sleep(0)
        if final and final.result.success:
            renders[run_id] = render_machine(scene)
        yield f"event: done\ndata: {json.dumps({'success': bool(final and final.result.success), 'render_url': f'/run/{run_id}/render'})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/run/{run_id}/render")
async def render(run_id: str):
    image = renders.get(run_id)
    if image is None:
        return JSONResponse({"error": "render is not ready"}, status_code=404)
    return StreamingResponse(iter([image]), media_type="image/png")


@app.post("/voice")
async def voice(file: UploadFile = File(...)):
    return {"text": transcribe_goal(await file.read(), file.filename or "goal.webm")}
