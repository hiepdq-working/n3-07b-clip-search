# Dàn ý slide (8–10 trang)

| # | Trang | Nội dung | Nguồn |
|---|---|---|---|
| 1 | Pain point | Ca hiếm khó tìm; lướt tay mất bao lâu | `rare_slices.csv`, `timing_summary.csv` |
| 2 | Dữ liệu | BDD100K val, 10.000 ảnh; biểu đồ thời tiết/thời gian | `data_stats.csv` |
| 3 | Hệ thống | Sơ đồ 5 bước (README); ảnh nhúng một lần | README |
| 4 | Demo | Ảnh chụp app hoặc video; câu "pedestrian crossing at night in the rain" | ảnh chụp app |
| 5 | Cách đo | dev/test khóa trước, 2 người chấm, kappa | `docs/evaluation.md` |
| 6 | Precision@K | Biểu đồ theo câu, tách yes/no | `figures/precision_by_*.png` |
| 7 | Thời gian tìm 20 ca | Bảng baseline so với pilot | `timing_summary.csv` |
| 8 | CLIP làm tốt và làm sai | 3 ảnh tốt + 3 ảnh sai, kèm loại lỗi | `error_analysis.csv` |
| 9 | Giới hạn | Thí nghiệm nhỏ, dữ liệu Mỹ, câu phủ định | |
| 10 | Kết luận | 2–3 câu có số thật (xem bên dưới) | |

Câu kết luận mẫu (điền số thật):

- "Trên 10 câu test, P@10 trung bình là **X**. Với các ca metadata không trả lời được, P@10 là **Y**."
- "Tìm đủ 20 ca mất trung bình **X phút** với CLIP, so với **Y phút** khi lọc rồi lướt tay (4 người, sơ bộ)."

Ảnh BDD100K trên slide phải ghi nguồn: *Ảnh: BDD100K (Yu et al., CVPR 2020)*.
