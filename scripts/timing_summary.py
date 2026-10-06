"""Tổng hợp thí nghiệm bấm giờ (người E): results/timing.csv -> results/timing_summary.csv

    python scripts/timing_summary.py

Đây là thí nghiệm nhỏ (4 người, 8 lượt): chỉ là bằng chứng sơ bộ, không kết luận thống kê.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import QUERIES, RESULTS  # noqa: E402

t = pd.read_csv(RESULTS / "timing.csv")
q = pd.read_csv(QUERIES)[["query_id", "metadata_covers"]]
t = t.merge(q, on="query_id", how="left")
t["minutes"] = t.seconds / 60
t["reached_20"] = t.found >= 20
t["found_per_min"] = t.found / t.minutes

# Kiểm tra thiết kế: không ai làm cùng một câu ở cả hai chế độ
dup = t.groupby(["tester", "query_id"]).mode.nunique()
if (dup > 1).any():
    print("! Vi phạm thiết kế (cùng người, cùng câu, hai chế độ):")
    print(dup[dup > 1])

agg = dict(runs=("seconds", "size"), minutes_mean=("minutes", "mean"),
           viewed_mean=("viewed", "mean"), found_mean=("found", "mean"),
           reached_20=("reached_20", "sum"), found_per_min=("found_per_min", "mean"))
summary = pd.concat([
    t.groupby("mode").agg(**agg).assign(metadata_covers="all").reset_index(),
    t.groupby(["mode", "metadata_covers"]).agg(**agg).reset_index(),
]).round(2)
summary.to_csv(RESULTS / "timing_summary.csv", index=False)
print(summary.to_string(index=False))
