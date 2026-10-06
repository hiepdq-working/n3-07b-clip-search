import numpy as np
import pandas as pd
import pytest

from core import build_mask, parse_filters, precision_at_k, rank


@pytest.fixture
def meta():
    return pd.DataFrame({
        "name": ["a.jpg", "b.jpg", "c.jpg", "d.jpg"],
        "timeofday": ["night", "night", "daytime", "night"],
        "weather": ["rainy", "clear", "rainy", "rainy"],
        "n_pedestrian": [2, 0, 1, 0],
    })


def test_parse_filters():
    assert parse_filters("timeofday=night;weather=rainy") == (
        {"timeofday": "night", "weather": "rainy"}, {})
    assert parse_filters("scene=city street;n_pedestrian>=1") == (
        {"scene": "city street"}, {"n_pedestrian": 1})
    assert parse_filters("") == ({}, {})
    assert parse_filters(float("nan")) == ({}, {})


def test_build_mask(meta):
    m = build_mask(meta, {"timeofday": "night", "weather": "rainy"})
    assert m.tolist() == [True, False, False, True]
    m = build_mask(meta, {"timeofday": "night"}, {"n_pedestrian": 1})
    assert m.tolist() == [True, False, False, False]
    assert build_mask(meta).all()


def test_rank_filters_then_sorts(meta):
    emb = np.eye(4, dtype="float32")
    q = np.array([0.1, 0.9, 0.5, 0.7], dtype="float32")
    res = rank(emb, meta, q, k=10)
    assert res.name.tolist() == ["b.jpg", "d.jpg", "c.jpg", "a.jpg"]
    res = rank(emb, meta, q, k=10, filters={"weather": "rainy"})
    assert res.name.tolist() == ["d.jpg", "c.jpg", "a.jpg"]
    assert res.score.is_monotonic_decreasing
    assert rank(emb, meta, q, k=1, filters={"weather": "rainy"}).name.tolist() == ["d.jpg"]


def test_rank_empty(meta):
    res = rank(np.eye(4, dtype="float32"), meta, np.ones(4, dtype="float32"),
               filters={"weather": "snowy"})
    assert len(res) == 0 and "score" in res


def test_precision_at_k():
    p = precision_at_k([1, 0, 1, 1, 0, 0, 0, 0, 0, 0], ks=(5, 10))
    assert p == {"P@5": 0.6, "P@10": 0.3}
    # ít hơn K ảnh: phần thiếu tính sai
    assert precision_at_k([1, 1], ks=(10,)) == {"P@10": 0.2}
