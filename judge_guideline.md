# Guideline chấm kết quả

> Người phụ trách: **D**. Bản nháp T4 tuần 1 → hoàn thiện T6 tuần 1 → calibration Chủ nhật tuần 1.
> Sau calibration, guideline chỉ được **làm rõ**, không đổi nghĩa định nghĩa trong `queries.csv`.

## Quy tắc chung

1. **Chấm từng ảnh độc lập** theo cột `definition` của câu đó trong `queries.csv`. Không nhìn điểm hay thứ hạng (app đã ẩn), không bàn với người chấm cùng câu trước khi lưu.
2. **Không chắc thì chấm SAI.** Đối tượng phải nhìn thấy được khi xem ảnh ở cỡ bình thường (không phải phóng to mới đoán ra).
3. **Thuộc tính chung của câu** (ban đêm, mưa…) đã được bộ lọc metadata đảm bảo. Chỉ chấm phần mô tả còn lại. Nếu thấy nhãn metadata sai rõ ràng (ví dụ ảnh ban ngày gắn nhãn `night`), vẫn chấm theo định nghĩa và ghi chú vào bảng ca lỗi.
4. Ảnh hỏng, đen hoàn toàn hoặc trùng lặp → **sai**.
5. Mỗi câu chỉ bấm **Lưu chấm** một lần. Bấm nhầm thì báo D (evaluate.py lấy lần lưu cuối của mỗi người).
6. Mỗi câu khoảng 15–20 phút cho 50 ảnh. Nghỉ giữa các câu để tránh mỏi mắt.

## Ví dụ biên chung

| Tình huống | Quyết định |
|---|---|
| Người đi xe máy / xe đạp có tính là "người đi bộ"? | **Không** |
| Người ở rất xa, chỉ vài pixel, chỉ đoán được là người | **Sai** |
| Đối tượng bị che hơn ~70% | **Sai** |
| Đối tượng chỉ thấy qua phản chiếu (gương, kính xe) | **Sai** |
| Ảnh chụp qua kính chắn gió bị mưa làm nhòe nhưng vẫn nhận ra đối tượng | **Đúng** |

## Ví dụ biên theo từng câu

> D bổ sung 2–3 ví dụ biên cho mỗi câu sau buổi calibration. Mẫu:

### D01 · pedestrian crossing the street
- Người đứng chờ trên vỉa hè cạnh vạch qua đường → **sai** (chưa băng qua).
- Người ở giữa lòng đường nhưng không có vạch kẻ → **đúng**.
- Người dắt xe đạp qua đường → **đúng** (đang đi bộ).

### T01 · person holding an umbrella
- Ô che nắng ở quán ven đường, không có người cầm → **sai**.
- Người đi xe máy cầm ô → **đúng**.
- …

### T02 · flooded road
- Mặt đường chỉ ướt, phản chiếu ánh đèn → **sai**.
- …

### T03 – T10
- …

## Quy trình calibration (Chủ nhật tuần 1, trên câu D01)

1. Chạy `python scripts/export_top.py dev -k 20` để có `results/dev_top20.csv`.
2. Hai người chấm **độc lập** câu `D01|clip_filter_tpl` trong tab *Chấm kết quả* (nguồn: Bộ dev).
3. `python scripts/evaluate.py --top results/dev_top20.csv --judgments results/dev_judgments.csv --out results/dev_tuning.csv` → xem kappa và `results/disagreements.csv`.
4. Cả nhóm cùng xem các ảnh lệch, thống nhất cách hiểu, **ghi thêm ví dụ biên vào file này**.
5. Commit guideline cùng commit khóa `queries.csv`.

## Phân xử ảnh lệch (tuần 2)

- Sau khi chạy `evaluate.py`, các ảnh hai người chấm khác nhau nằm trong `results/disagreements.csv`.
- D (hoặc người thứ ba chưa chấm câu đó) xem lại theo guideline, ghi vào `results/adjudicated.csv`:

```csv
query_id,name,rel
T01,b1c66a42-6f7d68ca.jpg,1
```

- Chạy lại `evaluate.py`. Ảnh lệch chưa phân xử được tính là **sai**.

## Mức đồng thuận (kappa)

| Cohen's κ | Diễn giải (Landis & Koch) |
|---|---|
| < 0.40 | Yếu → xem lại định nghĩa của câu đó |
| 0.40 – 0.60 | Trung bình |
| 0.61 – 0.80 | Khá |
| > 0.80 | Rất tốt |

Báo cáo κ theo từng câu, không giấu câu có κ thấp.
