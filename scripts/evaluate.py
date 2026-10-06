"""Bước 5 (người D): mức đồng thuận (Cohen's kappa) và Precision@K.

  Bộ test:  python scripts/evaluate.py
  Bộ dev:   python scripts/evaluate.py --top results/dev_top20.csv \
                --judgments results/dev_judgments.csv --out results/dev_tuning.csv

Nhãn cuối của một ảnh:
  * 2 người chấm giống nhau -> lấy nhãn đó;
  * lệch nhau -> lấy theo results/adjudicated.csv nếu có, chưa phân xử thì tính SAI
    (quy tắc "không chắc thì chấm sai") và ghi ra results/disagreements.csv;
  * chỉ 1 người chấm -> lấy nhãn người đó (cảnh báo);
  * ảnh trong top nhưng chưa ai chấm -> tính SAI (cảnh báo).
"""
import argparse
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import QUERIES, RESULTS  # noqa: E402
from core import precision_at_k  # noqa: E402

JCOLS = ["query_id", "name", "judge", "rel"]


def read_judgments(path):
    j = pd.read_csv(path)
    if list(j.columns) != JCOLS:                 # file cũ không có dòng tiêu đề
        j = pd.read_csv(path, names=JCOLS)
    return j


def final_labels(j, adjudicated=None):
    """-> (DataFrame query_id,name,rel ; DataFrame kappa ; DataFrame ảnh lệch)"""
    # nếu một người lưu nhiều lần cho cùng ảnh, lấy lần cuối
    j = j.drop_duplicates(["query_id", "name", "judge"], keep="last")
    wide = j.pivot_table(index=["query_id", "name"], columns="judge", values="rel", aggfunc="last")

    kappas = []
    for qid, g in wide.groupby(level=0):
        g = g.dropna(axis=1, how="all").dropna()
        if g.shape[1] == 2 and len(g):
            a, b = g.iloc[:, 0], g.iloc[:, 1]
            k = cohen_kappa_score(a, b) if a.nunique() + b.nunique() > 2 else float("nan")
            kappas.append({"query_id": qid, "judges": " vs ".join(g.columns), "n": len(g),
                           "agree_pct": round(100 * (a == b).mean(), 1), "kappa": round(k, 3)})
        elif g.shape[1] != 2:
            print(f"  ! {qid}: có {g.shape[1]} người chấm (cần đúng 2)")

    n_judges = wide.notna().sum(axis=1)
    lo, hi = wide.min(axis=1), wide.max(axis=1)
    final = pd.DataFrame({"rel": lo, "n_judges": n_judges, "disagree": (lo != hi) & (n_judges >= 2)})
    final = final.reset_index()
    disagreements = final[final.disagree][["query_id", "name"]]

    if adjudicated is not None and len(adjudicated):
        adj = adjudicated.drop_duplicates(["query_id", "name"], keep="last")
        final = final.merge(adj[["query_id", "name", "rel"]], on=["query_id", "name"],
                            how="left", suffixes=("", "_adj"))
        final["rel"] = final["rel_adj"].fillna(final["rel"])
        disagreements = disagreements.merge(adj[["query_id", "name"]], how="left", indicator=True)
        disagreements = disagreements[disagreements._merge == "left_only"].drop(columns="_merge")

    single = int((final.n_judges == 1).sum())
    if single:
        print(f"  ! {single} ảnh mới có 1 người chấm")
    return final[["query_id", "name", "rel"]], pd.DataFrame(kappas), disagreements


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", default=RESULTS / "test_top50.csv", type=Path)
    ap.add_argument("--judgments", default=RESULTS / "judgments.csv", type=Path)
    ap.add_argument("--adjudicated", default=RESULTS / "adjudicated.csv", type=Path)
    ap.add_argument("--out", default=RESULTS / "precision_at_k.csv", type=Path)
    ap.add_argument("--ks", default="10,20,50")
    a = ap.parse_args()
    ks = tuple(int(x) for x in a.ks.split(","))

    top = pd.read_csv(a.top)
    adj = pd.read_csv(a.adjudicated) if a.adjudicated.exists() else None
    final, kappas, dis = final_labels(read_judgments(a.judgments), adj)

    if len(kappas):
        print("Mức đồng thuận giữa hai người chấm:")
        print(kappas.to_string(index=False), "\n")
        kappas.to_csv(a.out.with_name(a.out.stem + "_kappa.csv"), index=False)
    if len(dis):
        dis.to_csv(RESULTS / "disagreements.csv", index=False)
        print(f"  ! {len(dis)} ảnh lệch chưa phân xử -> results/disagreements.csv (đang tính là sai)\n")

    m = top.merge(final, on=["query_id", "name"], how="left")
    unjudged = int(m.rel.isna().sum())
    if unjudged:
        print(f"  ! {unjudged} ảnh trong top chưa được chấm (tính là sai)")
    m["rel"] = m["rel"].fillna(0)

    q = pd.read_csv(QUERIES)[["query_id", "split", "query", "metadata_covers"]]
    out = []
    for qid, g in m.sort_values("rank").groupby("query_id"):
        base, _, cfg = qid.partition("|")
        out.append({"query_id": base, "config": cfg or None, **precision_at_k(g.rel, ks),
                    "n_returned": len(g)})
    res = pd.DataFrame(out).merge(q, on="query_id", how="left")
    if res["config"].isna().all():
        res = res.drop(columns="config")
    res.to_csv(a.out, index=False)

    pcols = [f"P@{k}" for k in ks]
    print(res.round(2).to_string(index=False), "\n")
    by = ["config"] if "config" in res else []
    print("Trung bình theo metadata_covers:")
    print(res.groupby(by + ["metadata_covers"])[pcols].mean().round(3), "\n")
    print("Trung bình chung:")
    print(res.groupby(by)[pcols].mean().round(3) if by else res[pcols].mean().round(3))
    print("\n->", a.out)


if __name__ == "__main__":
    main()
