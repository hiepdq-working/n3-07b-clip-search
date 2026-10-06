"""Bước 1 (người A): đọc det_val.json -> data/metadata.csv + bảng thống kê.

Chạy từ thư mục gốc repo:  python scripts/build_metadata.py
"""
import json
from collections import Counter

import pandas as pd

from config import CATS, IMG_DIR, LABELS, METADATA, RESULTS


def main():
    if not LABELS.exists():
        raise SystemExit(f"Không thấy {LABELS}. Xem README mục 'Tải dữ liệu'.")
    if not IMG_DIR.exists():
        raise SystemExit(f"Không thấy thư mục ảnh {IMG_DIR}.")

    rows = []
    with open(LABELS) as fh:
        items = json.load(fh)
    for item in items:
        attr = item.get("attributes", {})
        count = Counter(lb["category"] for lb in (item.get("labels") or []))
        row = {"name": item["name"],
               "weather": attr.get("weather"),
               "timeofday": attr.get("timeofday"),
               "scene": attr.get("scene")}
        row.update({f"n_{c.replace(' ', '_')}": count[c] for c in CATS})
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df[df["name"].map(lambda n: (IMG_DIR / n).exists())].reset_index(drop=True)
    df.to_csv(METADATA, index=False)
    print(len(df), "ảnh có file ->", METADATA)

    # Bảng thống kê cho báo cáo (results/ được commit, metadata.csv thì không)
    RESULTS.mkdir(exist_ok=True)
    stats = []
    for col in ["weather", "timeofday", "scene"]:
        vc = df[col].fillna("(trống)").value_counts()
        print(vc, "\n")
        stats += [{"attribute": col, "value": v, "count": n, "pct": round(100 * n / len(df), 2)}
                  for v, n in vc.items()]
    pd.DataFrame(stats).to_csv(RESULTS / "data_stats.csv", index=False)

    # Độ "hiếm" của các lát cắt khó
    night_rain = df[(df.timeofday == "night") & (df.weather == "rainy")]
    rare = pd.DataFrame([
        {"slice": "night", "count": int((df.timeofday == "night").sum())},
        {"slice": "night & rainy", "count": len(night_rain)},
        {"slice": "night & rainy & >=1 pedestrian", "count": int((night_rain.n_pedestrian >= 1).sum())},
        {"slice": "snowy", "count": int((df.weather == "snowy").sum())},
        {"slice": "foggy", "count": int((df.weather == "foggy").sum())},
        {"slice": "tunnel", "count": int((df.scene == "tunnel").sum())},
    ])
    rare["pct"] = (100 * rare["count"] / len(df)).round(2)
    rare.to_csv(RESULTS / "rare_slices.csv", index=False)
    print(rare.to_string(index=False))


if __name__ == "__main__":
    main()
