"""Thử nhanh CLIP trên vài ảnh (người B, tối thứ Hai tuần 1).

    python scripts/clip_smoke_test.py                 # lấy 5 ảnh đầu trong data/
    python scripts/clip_smoke_test.py anh1.jpg anh2.jpg
"""
import sys

import open_clip
import torch
from PIL import Image

from config import IMG_DIR, MODEL_KEY, MODELS, device

LABELS = ["a street at night", "a street in daytime", "a rainy road",
          "a snowy road", "a highway", "a city street with pedestrians"]

paths = sys.argv[1:] or sorted(str(p) for p in IMG_DIR.glob("*.jpg"))[:5]
if not paths:
    raise SystemExit("Không có ảnh. Truyền đường dẫn ảnh hoặc giải nén BDD100K trước.")

name, pretrained, _ = MODELS[MODEL_KEY]
dev = device()
model, _, preprocess = open_clip.create_model_and_transforms(name, pretrained=pretrained)
tokenizer = open_clip.get_tokenizer(name)
model = model.to(dev).eval()
print(f"{name}/{pretrained} trên {dev}")

texts = tokenizer(LABELS).to(dev)
with torch.no_grad():
    t = model.encode_text(texts)
    t = t / t.norm(dim=-1, keepdim=True)
    for p in paths:
        img = preprocess(Image.open(p).convert("RGB")).unsqueeze(0).to(dev)
        i = model.encode_image(img)
        i = i / i.norm(dim=-1, keepdim=True)
        prob = (100 * i @ t.T).softmax(dim=-1)[0].cpu()
        best = prob.argsort(descending=True)[:3]
        print(p.split("/")[-1], "->", ", ".join(f"{LABELS[j]} ({prob[j]:.2f})" for j in best))
