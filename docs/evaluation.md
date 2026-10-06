# Thiết kế đánh giá

Phần này quyết định độ tin cậy của toàn bộ đề tài.
Nguyên tắc: **chỉnh hệ thống trên bộ dev, báo cáo trên bộ test; bộ test khóa trước và chỉ chạy một lần.**

## 1. Bộ câu truy vấn — `queries.csv`

| Cột | Ý nghĩa |
|---|---|
| `query_id` | `D01…D05` (dev), `T01…T10` (test) |
| `split` | `dev` / `test` |
| `query` | Câu tiếng Anh đưa vào CLIP |
| `filters` | Bộ lọc metadata, cách nhau bởi `;`. Hỗ trợ `cột=giá_trị` và `n_<vật>>=số`, ví dụ `timeofday=night;weather=rainy;n_pedestrian>=1` |
| `metadata_covers` | `yes` nếu thuộc tính và box có sẵn trả lời được câu hỏi, `no` nếu không. Mỗi nhóm khoảng một nửa số câu test |
| `definition` | Định nghĩa "đúng" bằng tiếng Việt cho người chấm, **viết trước khi xem kết quả** |

Giá trị hợp lệ trong BDD100K:
- `weather`: clear, overcast, partly cloudy, rainy, snowy, foggy, undefined
- `timeofday`: daytime, night, dawn/dusk, undefined
- `scene`: city street, highway, residential, parking lot, gas stations, tunnel, undefined

`queries.csv` hiện có là **bản nháp đề xuất**. D và cả nhóm sửa lại trong tuần 1, rồi khóa vào Chủ nhật tuần 1:

```bash
git add queries.csv judge_guideline.md
git commit -m "Khóa bộ câu test"
git tag queries-locked && git push --tags
git rev-parse --short queries-locked   # ghi mã này vào báo cáo
```

Kiểm tra sau này rằng bộ test chưa bị sửa: `git diff queries-locked -- queries.csv` phải không in ra gì.

## 2. Chọn cấu hình trên bộ dev

| Cấu hình (`search.CONFIGS`) | Ý nghĩa |
|---|---|
| `clip_only` | Chỉ câu truy vấn, không lọc, không gộp mẫu câu |
| `clip_filter` | Lọc metadata trước, rồi xếp hạng bằng CLIP |
| `clip_filter_tpl` | Như trên, kèm gộp `TEMPLATES` |

```bash
python scripts/export_top.py dev -k 20
# chấm trong app, nguồn "Bộ dev" (mỗi query_id có dạng D01|clip_filter)
python scripts/evaluate.py --top results/dev_top20.csv --judgments results/dev_judgments.csv --out results/dev_tuning.csv
```

Chọn cấu hình có P@10/P@20 trung bình cao nhất trên dev và ghi lý do vào báo cáo. Từ đây **không đổi cấu hình** cho tới lần chạy bộ test.
Nếu thử ViT-L-14, chạy lại các bước trên với `CLIP_MODEL=vitl14`.

## 3. Bộ test

```bash
python scripts/export_top.py test --config <cấu_hình_đã_chốt>   # một lần → results/test_top50.csv
```

- Mỗi câu có 2 người chấm độc lập. Mỗi người chấm khoảng 4 câu, mỗi câu 50 ảnh mất khoảng 15–20 phút.
- Lịch chấm mẫu (5 người × 4 câu = 20 lượt = 10 câu × 2 người):

| Người | Câu |
|---|---|
| A | T01, T02, T03, T04 |
| B | T05, T06, T07, T08 |
| C | T09, T10, T01, T02 |
| D | T03, T04, T05, T06 |
| E | T07, T08, T09, T10 |

- `python scripts/evaluate.py`, rồi phân xử `results/disagreements.csv` vào `results/adjudicated.csv`, rồi chạy lại.
- Nhãn cuối: hai người cùng chấm đúng thì là **đúng**; lệch nhau thì theo phân xử; chưa phân xử thì tính **sai**.
- Precision@K = số ảnh đúng trong K ảnh đầu chia cho **K**. Nếu bộ lọc chỉ trả về ít hơn K ảnh, phần thiếu được tính là sai, và cột `n_returned` cho biết điều đó.

## 4. Thí nghiệm bấm giờ

**Câu hỏi:** tìm đủ N = 20 ảnh đúng mất bao lâu khi (a) lọc metadata rồi lướt ảnh (baseline), so với (b) dùng CLIP kết hợp lọc metadata (pilot)?

- Chọn 4 câu test, gồm 2 câu `yes` và 2 câu `no`. Có 4 người thử, mỗi người làm 2 câu baseline + 2 câu pilot, và **không bao giờ làm cùng một câu ở cả hai chế độ**.
- Đổi thứ tự (counterbalancing): nửa số người làm baseline trước, nửa còn lại làm pilot trước.

| Người | Lượt 1 | Lượt 2 | Lượt 3 | Lượt 4 |
|---|---|---|---|---|
| P1 | Q1 baseline | Q2 baseline | Q3 clip | Q4 clip |
| P2 | Q3 baseline | Q4 baseline | Q1 clip | Q2 clip |
| P3 | Q1 clip | Q2 clip | Q3 baseline | Q4 baseline |
| P4 | Q3 clip | Q4 clip | Q1 baseline | Q2 baseline |

- Trong tab **Bấm giờ**: bấm *Bắt đầu đo*, đánh dấu ảnh đúng, chuyển trang, đủ 20 ảnh thì bấm *Kết thúc*. Mỗi lượt giới hạn 15 phút; nếu hết giờ mà chưa đủ 20 ảnh thì vẫn ghi số đã tìm được.
- Cả hai chế độ dùng **cùng bộ lọc** của câu đó. Baseline xáo trộn ảnh ngẫu nhiên với seed cố định.
- `python scripts/timing_summary.py` → `results/timing_summary.csv` (thời gian trung bình, số ảnh đã xem, số ca tìm được, theo chế độ và theo nhóm `yes/no`).
- Đây là thí nghiệm nhỏ (4 người, 8 lượt), nên chỉ trình bày như bằng chứng sơ bộ, không kết luận về ý nghĩa thống kê.

## 5. Phân tích lỗi

Chọn 4–6 ảnh CLIP xếp hạng cao nhưng bị chấm sai, rồi phân loại: vật nhỏ/ở xa, ảnh tối, câu phủ định/đếm số lượng, nhầm khái niệm (ví dụ ô che nắng với ô cầm tay), hoặc nhãn metadata sai. Ghi vào `results/error_analysis.csv` (`query_id,name,rank,category,note`).
