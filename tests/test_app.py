from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from backend.app import app


def test_offline_upload_and_stream():
    image = BytesIO()
    Image.new("RGB", (320, 240), "white").save(image, format="PNG")
    image.seek(0)
    with TestClient(app) as client:
        response = client.post("/upload", files={"file": ("sketch.png", image, "image/png")}, data={"goal": "ring the bell"})
        assert response.status_code == 200
        run_id = response.json()["run_id"]
        stream = client.get(f"/run/{run_id}/stream")
        assert stream.status_code == 200
        assert "event: attempt" in stream.text
        assert "event: done" in stream.text


def test_missing_run_is_not_found():
    with TestClient(app) as client:
        assert client.get("/run/missing/stream").status_code == 404
