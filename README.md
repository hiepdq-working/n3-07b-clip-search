# N3-07B · Tìm ca hiếm trong ảnh xe tự lái bằng truy vấn văn bản (CLIP)

Gõ một câu tiếng Anh như **"pedestrian crossing at night in the rain"** để tìm trong 10.000 ảnh camera hành trình [BDD100K](https://www.vis.xyz/bdd100k/), kết hợp lọc theo metadata (thời tiết, thời gian, bối cảnh, số vật thể).
Không huấn luyện mô hình. Phần việc chính là xử lý dữ liệu, dựng hệ thống tìm kiếm và **đánh giá có số liệu**: Precision@K do hai người chấm độc lập, và thí nghiệm bấm giờ so baseline với CLIP.

```
 ảnh BDD100K ──► (1) build_metadata ──► metadata.csv ─────────────┐
      │                                                           ▼
      └──────► (2) embed_images (CLIP, 1 lần) ──► emb_*.npy ──► (3) search: lọc metadata
                                                                  → cosine(câu, ảnh) → top-K
 câu truy vấn ──► CLIP text encoder (gộp mẫu câu) ────────────────┘        │
                                                                           ▼
                                        (4) app Streamlit: Tìm kiếm · Bấm giờ · Chấm kết quả
                                                                           │
                                        (5) evaluate: Precision@K, kappa ◄─┘   timing_summary
```

Mỗi ảnh chỉ đi qua CLIP **một lần** (bước 2). Mỗi truy vấn sau đó chỉ so một vector câu với 10.000 vector ảnh bằng một phép nhân ma trận NumPy, mất vài mili giây, nên không cần FAISS.

---

## Cấu trúc repo

```
n3-07b-clip-search/
├── data/                    # KHÔNG commit (.gitignore) — mỗi người tự tải
│   ├── bdd100k/images/100k/val/*.jpg
│   ├── bdd100k/labels/det_20/det_val.json
│   ├── metadata.csv
│   └── emb_vitb32.npy
├── scripts/
│   ├── config.py            # đường dẫn, model, mẫu câu (sửa ở đây nếu khác)
│   ├── core.py              # hàm thuần: lọc, xếp hạng, Precision@K (có test)
│   ├── check_env.py         # kiểm tra môi trường + dữ liệu
│   ├── build_metadata.py    # (A) det_val.json → metadata.csv + thống kê
│   ├── clip_smoke_test.py   # (B) thử CLIP trên vài ảnh
│   ├── embed_images.py      # (B) nhúng ảnh → emb_*.npy
│   ├── search.py            # (B) tìm kiếm + 3 cấu hình so sánh
│   ├── export_top.py        # xuất top-K của bộ dev / test để chấm
│   ├── evaluate.py          # (D) kappa, Precision@K, ảnh lệch
│   ├── timing_summary.py    # (E) tổng hợp thí nghiệm bấm giờ
│   └── plot_results.py      # biểu đồ cho báo cáo / slide
├── app/app.py               # (C) demo Streamlit
├── queries.csv              # bộ câu truy vấn dev + test (khóa CN tuần 1)
├── judge_guideline.md       # guideline chấm
├── results/                 # judgments, timing, bảng kết quả, figures/ — CÓ commit
├── docs/                    # kế hoạch, thiết kế thí nghiệm, dàn ý báo cáo & slide
├── tests/                   # pytest cho core + evaluate (không cần torch)
├── Makefile                 # lệnh tắt
├── requirements.txt
└── requirements-dev.txt
```

---

## Chạy lại từ đầu trên Mac

Đã thử trên macOS với chip Apple M1/M2/M3, Python 3.10–3.12. Máy Intel/Linux/Windows vẫn chạy được, nhưng sẽ dùng CPU nên chậm hơn.

### 0. Cài môi trường

```bash
git clone https://github.com/<ten-nhom>/n3-07b-clip-search.git
cd n3-07b-clip-search
python3 -m venv .venv
source .venv/bin/activate          # mỗi lần mở terminal mới
pip install --upgrade pip
pip install -r requirements.txt    # hoặc requirements-lock.txt nếu đã có
python scripts/check_env.py        # phải thấy dấu ✓ và "MPS: True"
```

`MPS: False` không phải lỗi: code vẫn chạy trên CPU, chỉ chậm hơn.

### 1. Tải BDD100K (chỉ tập val, 10.000 ảnh)

1. Đăng ký tài khoản miễn phí tại <https://bdd-data.berkeley.edu/> (nên dùng Chrome). Mô tả các file có ở <https://doc.bdd100k.com/download.html>.
2. Tải đúng 2 file:
   - **100K Images → val**: `100k_images_val.zip`
   - **Detection 2020 Labels**: `bdd100k_det_20_labels_trainval.zip`
3. Nếu cổng tải lỗi, dùng bản lưu trữ chính thức tại ETH Zurich: <https://dl.cv.ethz.ch/bdd100k/data/>. **Không** dùng bản tải lại trên Kaggle, Hugging Face hay Drive cá nhân.
4. Giải nén:

```bash
mkdir -p data && cd data
unzip -q ~/Downloads/100k_images_val.zip
unzip -q ~/Downloads/bdd100k_det_20_labels_trainval.zip
find . -name "det_val.json"
ls bdd100k/images/100k/val | wc -l     # phải in 10000
cd ..
```

Nếu đường dẫn sau khi giải nén khác (ví dụ thừa một tầng thư mục), sửa `IMG_DIR` / `LABELS` trong [`scripts/config.py`](scripts/config.py). Đừng di chuyển file.

### 2. Tạo metadata và embedding

```bash
python scripts/build_metadata.py      # → data/metadata.csv, results/data_stats.csv, results/rare_slices.csv
python scripts/clip_smoke_test.py     # thử CLIP trên 5 ảnh (lần đầu tự tải trọng số ~600 MB)
python scripts/embed_images.py        # → data/emb_vitb32.npy, shape (10000, 512); thiếu RAM thì thêm --batch 32
```

> Chỉ cần **một người** chạy `embed_images.py` rồi gửi file `.npy` qua ổ chia sẻ nội bộ của nhóm.
> **Không sắp xếp lại `metadata.csv`** sau bước này, vì thứ tự dòng phải trùng với thứ tự vector.

Thử tìm kiếm từ dòng lệnh:

```bash
python scripts/search.py "pedestrian crossing the street" --filters "timeofday=night;weather=rainy"
```

### 3. Mở app demo

```bash
streamlit run app/app.py              # trình duyệt tự mở http://localhost:8501
```

| Tab | Dùng để |
|---|---|
| 🔎 Tìm kiếm | Demo: gõ câu, chọn bộ lọc, xem lưới ảnh kèm điểm và thời gian truy vấn |
| ⏱ Bấm giờ | Thí nghiệm baseline (lọc rồi lướt ngẫu nhiên) so với CLIP. Ghi vào `results/timing.csv` |
| ✅ Chấm kết quả | Chấm đúng/sai top-K của bộ test hoặc dev. Ghi vào `results/judgments.csv` / `dev_judgments.csv` |

### 4. Đánh giá

```bash
# Bộ dev: so 3 cấu hình (clip_only, clip_filter, clip_filter_tpl)
python scripts/export_top.py dev -k 20
#   … chấm trong app (nguồn: Bộ dev) …
python scripts/evaluate.py --top results/dev_top20.csv --judgments results/dev_judgments.csv --out results/dev_tuning.csv

# Bộ test: CHỈ CHẠY MỘT LẦN với cấu hình đã chốt trên dev
python scripts/export_top.py test --config clip_filter_tpl
#   … mỗi câu 2 người chấm độc lập trong app …
python scripts/evaluate.py            # → results/precision_at_k.csv, *_kappa.csv, disagreements.csv
python scripts/timing_summary.py      # → results/timing_summary.csv
python scripts/plot_results.py        # → results/figures/*.png
```

Đổi model mà không cần sửa code: `CLIP_MODEL=vitl14 python scripts/embed_images.py`. Các key hợp lệ là `vitb32` (mặc định), `vitl14`, `vitb32_openai`. Xem thêm [docs/colab_vitl14.md](docs/colab_vitl14.md).

Có thể dùng các lệnh tắt: `make help`.

---

## Nguyên tắc đánh giá

- **Chỉnh trên dev, báo cáo trên test.** `queries.csv` được khóa vào Chủ nhật tuần 1, và mã commit đó được ghi vào báo cáo. Bộ test chỉ chạy một lần (`export_top.py test` từ chối ghi đè nếu không có `--force`).
- Mỗi câu test có **2 người chấm độc lập**. Báo cáo Cohen's κ theo từng câu. Ảnh hai người chấm lệch nhau được phân xử vào `results/adjudicated.csv`.
- Báo cáo Precision@10/20/50 **theo từng câu** và tách theo `metadata_covers = yes/no`, không chỉ đưa ra một con số trung bình.
- Thí nghiệm bấm giờ chỉ có 4 người và 8 lượt, nên chỉ được trình bày như **bằng chứng sơ bộ**.
- Mọi con số trong báo cáo và slide phải truy được về một file trong `results/`.

Chi tiết xem [docs/evaluation.md](docs/evaluation.md) và [judge_guideline.md](judge_guideline.md).

## Nhóm

| Vai | Người | Phụ trách |
|---|---|---|
| A · Dữ liệu | _[tên]_ | BDD100K, `metadata.csv`, thống kê |
| B · CLIP & tìm kiếm | _[tên]_ | embedding, `search.py`, chọn cấu hình |
| C · Demo | _[tên]_ | `app/app.py`, README chạy lại, video dự phòng |
| D · Đánh giá | _[tên]_ | `queries.csv`, guideline, Precision@K, kappa |
| E · Điều phối & báo cáo | _[tên]_ | lịch, repo, thí nghiệm bấm giờ, báo cáo, slide |

Kế hoạch theo ngày: [docs/plan.md](docs/plan.md). Quy trình làm việc với Git: [CONTRIBUTING.md](CONTRIBUTING.md).

## Dữ liệu và giấy phép

- Code trong repo dùng giấy phép [MIT](LICENSE).
- **BDD100K không nằm trong repo.** Giấy phép BDD100K chỉ cho phép dùng để nghiên cứu/học tập và **không cho phân phối lại**. Thư mục `data/` và mọi file `*.jpg`/`*.npy` đều nằm trong `.gitignore`. Slide chỉ dùng vài ảnh minh họa và phải ghi nguồn:
  > Yu et al., *BDD100K: A Diverse Driving Dataset for Heterogeneous Multitask Learning*, CVPR 2020.
- CLIP: [OpenCLIP](https://github.com/mlfoundations/open_clip) với trọng số LAION-2B. Trọng số được tự tải về `~/.cache/huggingface` ở lần chạy đầu.
