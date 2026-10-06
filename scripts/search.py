"""Bước 3 (người B): tìm kiếm bằng câu văn bản, kết hợp lọc metadata.

Với 10.000 vector, nhân ma trận NumPy chỉ mất vài mili giây nên không cần FAISS.
Model được nạp lười (lần gọi đầu tiên), nên import module này rất nhẹ.

    python scripts/search.py "pedestrian crossing the street" --filters "timeofday=night;weather=rainy"
"""
import argparse
import time
from functools import lru_cache

import numpy as np
import pandas as pd

from config import METADATA, MODEL_KEY, MODELS, TEMPLATES
from core import build_mask, parse_filters, rank  # noqa: F401  (app dùng build_mask)

meta = pd.read_csv(METADATA)


@lru_cache(maxsize=1)
def _load():
    import open_clip
    import torch  # noqa: F401

    from config import device

    name, pretrained, emb_path = MODELS[MODEL_KEY]
    dev = device()
    model, _, _ = open_clip.create_model_and_transforms(name, pretrained=pretrained)
    model = model.to(dev).eval()
    tokenizer = open_clip.get_tokenizer(name)
    emb = np.load(emb_path)
    if len(emb) != len(meta):
        raise RuntimeError(f"{emb_path.name} có {len(emb)} dòng nhưng metadata có {len(meta)}.")
    return model, tokenizer, emb, dev


def get_embeddings():
    return _load()[2]


def encode_text(query, use_templates=True):
    import torch
    model, tokenizer, _, dev = _load()
    templates = TEMPLATES if use_templates else ["{}"]
    toks = tokenizer([t.format(query) for t in templates]).to(dev)
    with torch.no_grad():
        t = model.encode_text(toks)
        t = t / t.norm(dim=-1, keepdim=True)
        t = t.mean(dim=0)                      # gộp nhiều cách viết câu
        t = t / t.norm()
    return t.cpu().numpy().astype("float32")


def search(query, k=50, filters=None, min_counts=None, use_templates=True):
    """filters: {'timeofday': 'night', 'weather': 'rainy'}; min_counts: {'n_pedestrian': 1}"""
    return rank(get_embeddings(), meta, encode_text(query, use_templates),
                k=k, filters=filters, min_counts=min_counts)


# Ba cấu hình so sánh trên bộ dev (mục 7 của kế hoạch)
CONFIGS = {
    "clip_only": dict(use_filters=False, use_templates=False),
    "clip_filter": dict(use_filters=True, use_templates=False),
    "clip_filter_tpl": dict(use_filters=True, use_templates=True),
}


def search_config(query, filter_str, config, k=50):
    c = CONFIGS[config]
    f, mc = parse_filters(filter_str) if c["use_filters"] else ({}, {})
    return search(query, k=k, filters=f, min_counts=mc, use_templates=c["use_templates"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="pedestrian crossing the street")
    ap.add_argument("--filters", default="timeofday=night;weather=rainy")
    ap.add_argument("-k", type=int, default=10)
    ap.add_argument("--no-templates", action="store_true")
    a = ap.parse_args()
    f, mc = parse_filters(a.filters)
    search(a.query, k=1, filters=f, min_counts=mc)       # khởi động model
    t0 = time.perf_counter()
    res = search(a.query, k=a.k, filters=f, min_counts=mc, use_templates=not a.no_templates)
    print(res[["name", "weather", "timeofday", "scene", "n_pedestrian", "score"]].to_string(index=False))
    print(f"\n{(time.perf_counter() - t0) * 1000:.1f} ms / truy vấn")
