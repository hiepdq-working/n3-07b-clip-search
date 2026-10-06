"""Các hàm thuần (không cần torch/CLIP) — dễ kiểm thử, dùng chung cho search, app, evaluate."""
import numpy as np
import pandas as pd


def parse_filters(s):
    """'timeofday=night;weather=rainy' -> {'timeofday': 'night', 'weather': 'rainy'}.

    Ô trống / NaN -> {}. Khóa bắt đầu bằng 'n_' (vd 'n_pedestrian>=1') được hiểu là
    số lượng tối thiểu và trả về ở dict thứ hai.
    """
    filters, min_counts = {}, {}
    if not isinstance(s, str) or not s.strip():
        return filters, min_counts
    for part in s.split(";"):
        part = part.strip()
        if not part:
            continue
        if ">=" in part:
            col, val = part.split(">=", 1)
            min_counts[col.strip()] = int(val)
        else:
            col, val = part.split("=", 1)
            filters[col.strip()] = val.strip()
    return filters, min_counts


def build_mask(meta, filters=None, min_counts=None):
    """Mảng bool: ảnh nào thỏa mọi điều kiện lọc."""
    mask = np.ones(len(meta), dtype=bool)
    for col, val in (filters or {}).items():
        mask &= (meta[col] == val).to_numpy()
    for col, n in (min_counts or {}).items():
        mask &= (meta[col] >= n).to_numpy()
    return mask


def rank(emb, meta, qvec, k=50, filters=None, min_counts=None):
    """Lọc metadata trước, rồi xếp hạng theo cosine (emb đã chuẩn hóa L2)."""
    idx = np.flatnonzero(build_mask(meta, filters, min_counts))
    if len(idx) == 0:
        return meta.iloc[[]].assign(score=pd.Series(dtype="float32"))
    scores = emb[idx] @ qvec
    order = np.argsort(-scores)[:k]
    return meta.iloc[idx[order]].assign(score=scores[order])


def precision_at_k(rels, ks=(10, 20, 50)):
    """rels: dãy 0/1 theo thứ tự hạng. Thiếu ảnh (top < k) tính như sai."""
    rels = list(rels)
    return {f"P@{k}": sum(rels[:k]) / k for k in ks}
