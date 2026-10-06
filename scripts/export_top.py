"""Xuất danh sách top-K để chấm.

  Bộ dev — so 3 cấu hình (người B, tuần 1):
    python scripts/export_top.py dev  -k 20   -> results/dev_top20.csv
  Bộ test — CHỈ CHẠY MỘT LẦN với cấu hình đã chốt (tuần 2):
    python scripts/export_top.py test --config clip_filter_tpl -> results/test_top50.csv

query_id trong file dev có dạng "D01|clip_filter" để chấm riêng từng cấu hình.
"""
import argparse
import subprocess

import pandas as pd

from config import MODEL_KEY, QUERIES, RESULTS
from search import CONFIGS, search_config


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("split", choices=["dev", "test"])
    ap.add_argument("-k", type=int, default=None, help="mặc định: dev 20, test 50")
    ap.add_argument("--config", default="clip_filter_tpl", choices=list(CONFIGS))
    ap.add_argument("--force", action="store_true", help="ghi đè test_top50.csv đã có")
    a = ap.parse_args()

    k = a.k or (20 if a.split == "dev" else 50)
    q = pd.read_csv(QUERIES)
    q = q[q.split == a.split]
    configs = list(CONFIGS) if a.split == "dev" else [a.config]
    out = RESULTS / f"{a.split}_top{k}.csv"
    if a.split == "test" and out.exists() and not a.force:
        raise SystemExit(f"{out} đã tồn tại. Bộ test chỉ xuất một lần; dùng --force nếu thật sự cần.")

    rows = []
    for _, r in q.iterrows():
        for cfg in configs:
            res = search_config(r.query, r.filters, cfg, k=k)
            qid = r.query_id if a.split == "test" else f"{r.query_id}|{cfg}"
            for rk, (name, score) in enumerate(zip(res.name, res.score), 1):
                rows.append({"query_id": qid, "rank": rk, "name": name, "score": round(float(score), 5)})
            print(f"{qid}: {len(res)} ảnh")

    RESULTS.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    with open(RESULTS / "run_log.txt", "a") as fh:
        fh.write(f"{pd.Timestamp.now():%Y-%m-%d %H:%M} split={a.split} k={k} configs={configs} "
                 f"model={MODEL_KEY} commit={git_commit()} -> {out.name}\n")
    print("->", out)


if __name__ == "__main__":
    main()
