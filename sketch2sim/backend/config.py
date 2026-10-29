import os

from dotenv import load_dotenv

load_dotenv()

META_API_KEY = os.getenv("META_API_KEY", "")
META_BASE_URL = os.getenv("META_BASE_URL", "https://api.meta.ai/v1")
BASETEN_API_KEY = os.getenv("BASETEN_API_KEY", "")
BASETEN_MODEL = os.getenv("BASETEN_MODEL", "meta-models/muse-spark-open-1026")
SPARK_MODEL = os.getenv("SPARK_MODEL", "muse-spark-1.3")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "muse-image")
TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL", "muse-voice-transcribe")
SAM_MODEL = os.getenv("SAM_MODEL", "sam-3.1")
CACHE_DIR = os.getenv("CACHE_DIR", "cache")
WORLD_WIDTH = 800
WORLD_HEIGHT = 600
GRAVITY = -981.0
PIXELS_PER_METER = 100.0
SIM_FPS = 60
SIM_MAX_SECONDS = 12
MAX_REPAIR_ATTEMPTS = 4
PART_TYPES = ["ball", "ramp", "lever", "pivot", "spring", "bell"]
