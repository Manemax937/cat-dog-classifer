import os
from pathlib import Path


class Config:
    MODEL_PATH = os.getenv("MODEL_PATH", "models/cats_dogs_model.pth")
    NUM_CLASSES = 2

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    MAX_FILE_SIZE = 10*1024*1024
    ALLOWED_EXTENSION = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    CLASS_NAMES = ["cats", "dogs"]
