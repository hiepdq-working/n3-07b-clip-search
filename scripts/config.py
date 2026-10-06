"""Cấu hình dùng chung cho mọi script và app.

Mọi đường dẫn tính từ thư mục gốc repo, nên script chạy được dù gọi từ đâu.
Đổi model bằng biến môi trường, không cần sửa code:

    CLIP_MODEL=vitl14 python scripts/search.py
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
IMG_DIR = DATA / "bdd100k" / "images" / "100k" / "val"
LABELS = DATA / "bdd100k" / "labels" / "det_20" / "det_val.json"
METADATA = DATA / "metadata.csv"

RESULTS = ROOT / "results"
QUERIES = ROOT / "queries.csv"

# key -> (tên model trong OpenCLIP, bộ trọng số, file embedding)
MODELS = {
    "vitb32": ("ViT-B-32", "laion2b_s34b_b79k", DATA / "emb_vitb32.npy"),
    "vitl14": ("ViT-L-14", "laion2b_s32b_b82k", DATA / "emb_vitl14.npy"),
    "vitb32_openai": ("ViT-B-32", "openai", DATA / "emb_vitb32_openai.npy"),
}
MODEL_KEY = os.environ.get("CLIP_MODEL", "vitb32")

# Các cách viết câu được gộp (trung bình vector) khi bật use_templates
TEMPLATES = ["a dashcam photo of {}", "a photo of {} taken from a car", "{}"]

# Các cột metadata dùng làm bộ lọc trong app
FILTER_COLS = ["timeofday", "weather", "scene"]
CATS = ["pedestrian", "rider", "car", "truck", "bus", "train",
        "motorcycle", "bicycle", "traffic light", "traffic sign"]


def device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"
