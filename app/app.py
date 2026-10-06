"""Bước 4 (người C): demo Streamlit — 3 tab: Tìm kiếm, Bấm giờ, Chấm kết quả.

Chạy từ thư mục gốc repo:
    streamlit run app/app.py

Giữ nguyên tên cột của các file CSV trong results/ vì evaluate.py đọc theo đúng tên đó.
"""
import csv
import random
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="N3-07B · Tìm ca hiếm bằng CLIP", layout="wide")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from config import FILTER_COLS, IMG_DIR, METADATA, MODEL_KEY, MODELS, QUERIES, RESULTS  # noqa: E402

RESULTS.mkdir(exist_ok=True)
PAGE = 20
TIME_LIMIT = 15 * 60
ALL = "(tất cả)"

# ---------------------------------------------------------------- kiểm tra dữ liệu
missing = [p for p in (METADATA, MODELS[MODEL_KEY][2], IMG_DIR) if not p.exists()]
if missing:
    st.error("Thiếu dữ liệu: " + ", ".join(str(p.relative_to(METADATA.parents[1])) for p in missing)
             + ". Làm theo README (bước 1–2) trước khi mở app.")
    st.stop()


@st.cache_resource(show_spinner="Đang nạp CLIP…")
def load():
    import search
    search.search("warm up", k=1)
    return search


S = load()
meta = S.meta
queries = pd.read_csv(QUERIES) if QUERIES.exists() else pd.DataFrame(
    columns=["query_id", "split", "query", "filters", "metadata_covers", "definition"])


def append_csv(path, header, rows):
    new = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(header)
        w.writerows(rows)


def filter_ui(key, defaults=None):
    defaults = defaults or {}
    f = {}
    cols = st.columns(len(FILTER_COLS) + 1)
    for col, c in zip(FILTER_COLS, cols):
        opts = [ALL] + sorted(meta[col].dropna().unique())
        idx = opts.index(defaults[col]) if defaults.get(col) in opts else 0
        v = c.selectbox(col, opts, index=idx, key=f"{key}_{col}")
        if v != ALL:
            f[col] = v
    n_ped = cols[-1].number_input("≥ số người đi bộ", 0, 20, 0, key=f"{key}_nped")
    return f, ({"n_pedestrian": n_ped} if n_ped else {})


def grid(names, key, ncol=5, check=False, captions=None, state=None):
    """Lưới ảnh. check=True thêm ô 'đúng'; state (dict) giữ trạng thái qua các trang."""
    cols = st.columns(ncol)
    for i, name in enumerate(names):
        c = cols[i % ncol]
        c.image(str(IMG_DIR / name), caption=captions[i] if captions else name,
                width="stretch")
        if check:
            v = c.checkbox("đúng", key=f"{key}_{name}", value=bool(state and state.get(name)))
            if state is not None:
                state[name] = v


tab_search, tab_time, tab_judge = st.tabs(["🔎 Tìm kiếm", "⏱ Bấm giờ", "✅ Chấm kết quả"])

# ---------------------------------------------------------------- Tìm kiếm (demo)
with tab_search:
    st.subheader("Tìm ca hiếm trong 10.000 ảnh BDD100K")
    st.caption(f"Model: {MODELS[MODEL_KEY][0]} / {MODELS[MODEL_KEY][1]} · "
               "câu truy vấn viết bằng tiếng Anh, ngắn, mô tả thứ nhìn thấy được")
    with st.form("search"):
        q = st.text_input("Mô tả ca cần tìm", "pedestrian crossing the street")
        f, mc = filter_ui("s")
        c1, c2 = st.columns([3, 1])
        k = c1.slider("Số ảnh", 10, 100, 30, 10)
        tpl = c2.checkbox("Gộp mẫu câu", value=True,
                          help="Trung bình vector của nhiều cách viết câu (TEMPLATES)")
        go = st.form_submit_button("Tìm", type="primary")
    if go:
        n_pool = int(S.build_mask(meta, f, mc).sum())
        t0 = time.perf_counter()
        res = S.search(q, k=k, filters=f, min_counts=mc, use_templates=tpl)
        ms = (time.perf_counter() - t0) * 1000
        st.caption(f"{len(res)} ảnh · {ms:.0f} ms · {n_pool} ảnh thỏa bộ lọc")
        caps = [f"{r.score:.3f} · {r.timeofday}/{r.weather}/{r.scene}" for r in res.itertuples()]
        grid(res["name"].tolist(), "s", captions=caps)

# ---------------------------------------------------------------- Bấm giờ
with tab_time:
    st.subheader("Thí nghiệm: tìm đủ 20 ảnh đúng mất bao lâu?")
    st.caption("Không làm cùng một câu ở cả hai chế độ. Giới hạn 15 phút mỗi lượt.")
    ss = st.session_state
    c1, c2, c3 = st.columns(3)
    tester = c1.text_input("Người thử", key="t_tester")
    test_q = queries[queries.split == "test"]
    qid = c2.selectbox("Câu truy vấn", test_q.query_id.tolist() or ["—"], key="t_qid")
    mode = c3.radio("Chế độ", ["baseline", "clip"], horizontal=True, key="t_mode")
    row = test_q[test_q.query_id == qid].iloc[0] if qid in set(test_q.query_id) else None
    if row is not None:
        st.info(f"**Định nghĩa:** {row.definition}")
    q = st.text_input("Câu truy vấn (chỉ dùng ở chế độ clip)",
                      row.query if row is not None else "", key="t_q", disabled=mode == "baseline")
    f, mc = filter_ui("t")

    b1, b2 = st.columns(2)
    if b1.button("▶ Bắt đầu đo", type="primary", disabled=not tester):
        ss.t0, ss.run = time.time(), ss.get("run", 0) + 1
        ss.marks, ss.max_page = {}, 1

    if "t0" in ss:
        elapsed = time.time() - ss.t0
        found = sum(ss.marks.values())
        st.metric("Đã đánh dấu đúng", f"{found} / 20",
                  help="Thời gian tính từ lúc bấm Bắt đầu; app chỉ cập nhật khi bạn thao tác")
        if elapsed > TIME_LIMIT:
            st.warning("Đã quá 15 phút — bấm Kết thúc để ghi số đã tìm được.")

        if mode == "baseline":
            pool = meta[S.build_mask(meta, f, mc)]
            names = pool["name"].tolist()
            random.Random(0).shuffle(names)
        else:
            names = S.search(q, k=1000, filters=f, min_counts=mc)["name"].tolist() if q else []
        n_pages = max(1, -(-len(names) // PAGE))
        page = st.number_input(f"Trang (20 ảnh/trang, {n_pages} trang)", 1, n_pages, 1,
                               key=f"t_page_{ss.run}")
        ss.max_page = max(ss.max_page, page)
        grid(names[(page - 1) * PAGE: page * PAGE], f"t{ss.run}", check=True, state=ss.marks)

        if b2.button("■ Kết thúc"):
            secs = round(time.time() - ss.t0, 1)
            found = sum(ss.marks.values())
            append_csv(RESULTS / "timing.csv",
                       ["tester", "query_id", "mode", "seconds", "viewed", "found", "timestamp"],
                       [[tester, qid, mode, secs, min(ss.max_page * PAGE, len(names)), found,
                         pd.Timestamp.now().isoformat(timespec="seconds")]])
            st.success(f"Đã ghi: {secs}s, {found} ảnh đúng → results/timing.csv")
            del ss.t0

# ---------------------------------------------------------------- Chấm kết quả
with tab_judge:
    st.subheader("Chấm top-K (đúng/sai) theo judge_guideline.md")
    sources = {"Bộ test (test_top50.csv)": ("test_top50.csv", "judgments.csv"),
               "Bộ dev (dev_top20.csv)": ("dev_top20.csv", "dev_judgments.csv")}
    c1, c2 = st.columns(2)
    judge = c1.text_input("Người chấm", key="j_judge")
    src = c2.selectbox("Nguồn", list(sources), key="j_src")
    top_file, jfile = (RESULTS / x for x in sources[src])

    if not top_file.exists():
        st.warning(f"Chưa có results/{top_file.name}. Chạy `python scripts/export_top.py "
                   f"{'test' if 'test' in top_file.name else 'dev'}` trước.")
    elif judge:
        top = pd.read_csv(top_file)
        qid = st.selectbox("Câu truy vấn", sorted(top["query_id"].unique()), key="j_qid")
        base = qid.split("|")[0]
        qrow = queries[queries.query_id == base]
        if len(qrow):
            st.info(f"**{qrow.iloc[0].query}** — {qrow.iloc[0].definition}\n\n"
                    "Không chắc thì chấm **sai**.")
        if jfile.exists():
            done = pd.read_csv(jfile)
            if ((done.query_id == qid) & (done.judge == judge)).any():
                st.warning("Bạn đã lưu câu này rồi. Lưu lại sẽ thêm dòng mới "
                           "(evaluate.py lấy lần lưu cuối).")
        names = top[top["query_id"] == qid].sort_values("rank")["name"].tolist()
        marks = {}
        # không hiện điểm/thứ hạng để người chấm không bị ảnh hưởng
        grid(names, f"j_{judge}_{qid}", check=True, state=marks,
             captions=[f"#{i + 1}" for i in range(len(names))])
        st.caption(f"Đang đánh dấu đúng {sum(marks.values())}/{len(names)}")
        if st.button("💾 Lưu chấm", type="primary"):
            append_csv(jfile, ["query_id", "name", "judge", "rel"],
                       [[qid, n, judge, int(marks.get(n, False))] for n in names])
            st.success(f"Đã lưu {len(names)} ảnh → results/{jfile.name}")
