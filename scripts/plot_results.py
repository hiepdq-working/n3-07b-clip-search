"""Vẽ biểu đồ cho báo cáo / slide -> results/figures/*.png

    python scripts/plot_results.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RESULTS  # noqa: E402

FIG = RESULTS / "figures"
FIG.mkdir(parents=True, exist_ok=True)

p = RESULTS / "precision_at_k.csv"
if p.exists():
    df = pd.read_csv(p).sort_values(["metadata_covers", "query_id"])
    cols = [c for c in df.columns if c.startswith("P@")]
    ax = df.set_index("query_id")[cols].plot.bar(figsize=(10, 4), width=0.8)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Precision")
    ax.set_title("Precision@K theo từng câu test")
    for i, (_, r) in enumerate(df.iterrows()):
        ax.text(i, 1.01, r.metadata_covers, ha="center", fontsize=7)
    plt.tight_layout()
    plt.savefig(FIG / "precision_by_query.png", dpi=200)
    plt.close()

    ax = df.groupby("metadata_covers")[cols].mean().T.plot.bar(figsize=(6, 4))
    ax.set_ylim(0, 1)
    ax.set_title("Precision@K: metadata trả lời được (yes) và không (no)")
    plt.tight_layout()
    plt.savefig(FIG / "precision_by_group.png", dpi=200)
    plt.close()
    print("✓ Precision@K")

d = RESULTS / "dev_tuning.csv"
if d.exists():
    df = pd.read_csv(d)
    cols = [c for c in df.columns if c.startswith("P@")]
    ax = df.groupby("config")[cols].mean().plot.bar(figsize=(6, 4), rot=0)
    ax.set_ylim(0, 1)
    ax.set_title("So sánh cấu hình trên bộ dev")
    plt.tight_layout()
    plt.savefig(FIG / "dev_tuning.png", dpi=200)
    plt.close()
    print("✓ dev tuning")

t = RESULTS / "timing.csv"
if t.exists():
    df = pd.read_csv(t)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    df.boxplot(column="seconds", by="mode", ax=axes[0])
    axes[0].set_title("Thời gian mỗi lượt (giây)")
    df.groupby("mode").found.mean().plot.bar(ax=axes[1], rot=0)
    axes[1].set_title("Số ảnh đúng tìm được (TB)")
    fig.suptitle("Baseline (lọc + lướt) so với CLIP + lọc")
    plt.tight_layout()
    plt.savefig(FIG / "timing.png", dpi=200)
    plt.close()
    print("✓ timing")

print("->", FIG)
