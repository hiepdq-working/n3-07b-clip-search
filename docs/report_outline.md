# Dàn ý báo cáo

> Người chủ trì: E. Mỗi mục ghi rõ người viết. Mọi con số phải dẫn về một file trong `results/`.

## 1. Pain point (E)
- Đội dữ liệu cần tìm ca hiếm như người đi bộ ban đêm dưới mưa, đường ngập hay công trường.
- Cách làm hiện nay là lọc metadata rồi lướt ảnh. Thời gian thực tế lấy từ `results/timing_summary.csv` (baseline).
- Mức độ hiếm: `results/rare_slices.csv`.

## 2. Dữ liệu (A)
- BDD100K val có 10.000 ảnh. Thuộc tính thời tiết, thời gian, bối cảnh và số box theo loại lấy từ `results/data_stats.csv`.
- Giới hạn: dữ liệu chỉ gồm đường phố Mỹ, ảnh 720p, và nhãn thuộc tính có sai sót.

## 3. Phương pháp (B)
- OpenCLIP ViT-B-32 (LAION-2B). Mỗi ảnh được nhúng một lần, vector chuẩn hóa L2.
- Lọc metadata trước, rồi xếp hạng theo cosine. Gộp mẫu câu bằng cách lấy trung bình vector của `TEMPLATES`.
- Lý do chọn cấu hình: bảng `results/dev_tuning.csv` (3 cấu hình, chỉ trên dev).
- Tốc độ: thời gian nhúng 10.000 ảnh và số mili giây cho mỗi truy vấn (`python scripts/search.py`).

## 4. Thiết kế đánh giá (D)
- Bộ dev/test và mã commit khóa bộ test: `git rev-parse --short queries-locked` → `_______`.
- Guideline chấm, hai người chấm độc lập, cách phân xử.
- Thiết kế thí nghiệm bấm giờ (counterbalancing, giới hạn 15 phút).

## 5. Kết quả (D, E)
- Bảng Precision@10/20/50 theo từng câu, kèm `metadata_covers` và `n_returned` (`results/precision_at_k.csv`).
- Trung bình theo nhóm yes/no. Hình: `results/figures/precision_by_group.png`.
- Kappa theo từng câu (`results/precision_at_k_kappa.csv`).
- Bảng thời gian baseline so với pilot (`results/timing_summary.csv`, `figures/timing.png`). Ghi rõ đây là bằng chứng sơ bộ.

## 6. Phân tích lỗi (A, B)
- 4–6 ví dụ CLIP trả sai, xếp theo loại: vật nhỏ, ảnh tối, câu phủ định/đếm, nhầm khái niệm, nhãn sai (`results/error_analysis.csv`).

## 7. Giới hạn và hướng tiếp theo (A)
- Thí nghiệm nhỏ (10 câu test, 4 người thử). Dữ liệu chỉ có ở Mỹ.
- CLIP yếu với câu phủ định và câu đếm số lượng.
- Hướng tiếp theo: cắt ảnh thành ô để tìm vật nhỏ, xếp hạng lại theo phản hồi người dùng, và đo tác động khi dùng ảnh tìm được để huấn luyện detector.

## Phụ lục
- `queries.csv` (bản đã khóa), `judge_guideline.md`, hướng dẫn chạy lại (README).
