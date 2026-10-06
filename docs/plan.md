# Kế hoạch 3 tuần

Bắt đầu vào thứ Hai tuần 1 và kết thúc vào Chủ nhật tuần 3. Ngày thường mỗi người làm khoảng 2 giờ buổi tối, cuối tuần khoảng 6 giờ/ngày, tổng khoảng 66 giờ/người. Nếu ngày bắt đầu khác, giữ nguyên thứ tự công việc và dịch lịch.
Các mốc **in đậm** là điểm kiểm tra: chưa đạt thì cả nhóm dồn sức gỡ trước khi đi tiếp.
Họp 15 phút vào tối thứ Hai, thứ Tư và thứ Sáu.

## Sản phẩm cần nộp

| Sản phẩm | Nội dung tối thiểu |
|---|---|
| Báo cáo | Bài toán, dữ liệu, phương pháp CLIP + metadata, cách đánh giá, Precision@K và thời gian, ca thất bại, giới hạn ([dàn ý](report_outline.md)) |
| Demo | App Streamlit chạy trên Mac: gõ câu, chọn bộ lọc, xem lưới ảnh; README cho người khác chạy lại |
| Slide | 8–10 trang, có ảnh kết quả thật và bảng baseline so với pilot ([dàn ý](slides_outline.md)) |

## Tuần 1 · Dựng hệ thống chạy được

| Ngày | A · Dữ liệu | B · CLIP | C · Demo | D · Đánh giá | E · Điều phối |
|---|---|---|---|---|---|
| T2 | Đăng ký BDD100K, bắt đầu tải | Cài môi trường, `clip_smoke_test.py` | Cài môi trường, chạy Streamlit "hello" | Đọc đề, liệt kê 25 ý tưởng ca hiếm | Tạo repo, bảo vệ nhánh `main` |
| T3 | Giải nén, kiểm tra 10.000 ảnh | `embed_images.py` | Phác giao diện | Chia ý tưởng thành 2 nhóm: metadata trả lời được / không | Lịch họp, bảng theo dõi việc |
| **T3 tối** | **Cả 5 máy chạy được `check_env.py`** | | | | |
| T4 | `build_metadata.py` → `metadata.csv` | Embedding 10.000 ảnh | App đọc metadata, lọc ảnh | Nháp guideline | Thiết kế thí nghiệm bấm giờ |
| T5 | Thống kê, gửi cho E | `search.py` | Nối search vào app | Chọn 5 câu dev + 10 câu test | Gỡ vướng cài đặt |
| T6 | Hỗ trợ B, C | Thử 3 cách viết câu trên dev | Chế độ baseline | Hoàn thiện guideline | Họp tiến độ |
| **T7** | **Cả nhóm: demo v1 chạy trên một Mac; thử 5 câu dev** | | | | |
| **CN** | **Cả nhóm: khóa 10 câu test (commit + tag `queries-locked`); calibration trên 1 câu dev** | | | | |

## Tuần 2 · Đo lường

| Ngày | A | B | C | D | E |
|---|---|---|---|---|---|
| T2 | Hỗ trợ embedding model 2 | ViT-L-14 trên Colab (tùy chọn) | Kiểm tra tab Chấm | Chia lịch chấm | Kiểm tra tab Bấm giờ |
| T3 | `export_top.py test` (1 lần) | Chốt cấu hình **chỉ dựa trên dev** | Kiểm tra log thời gian | Chạy thử `evaluate.py` | Khung báo cáo |
| T4 | Chấm lượt 1 | Chấm lượt 1 | Chấm lượt 2 | Chấm lượt 2 | Chấm lượt 1 |
| T5 | Chấm tiếp | Chấm tiếp | Chấm tiếp | Phân xử ảnh lệch | Chấm tiếp |
| T6 | Phân tích ca CLIP sai | Phân tích ca CLIP sai | Sửa lỗi app | Số liệu sơ bộ | Họp tiến độ |
| **T7** | **Cả nhóm: thí nghiệm bấm giờ baseline so với CLIP** ([thiết kế](evaluation.md#thí-nghiệm-bấm-giờ)) | | | | |
| **CN** | **Cả nhóm: bảng số liệu đầy đủ; chọn 6–8 ảnh minh họa** | | | | |

## Tuần 3 · Cải tiến, báo cáo, slide

| Ngày | A | B | C | D | E |
|---|---|---|---|---|---|
| T2 | Viết mục Dữ liệu | Thử cải tiến trên dev | Đóng gói app, kiểm tra README | Viết mục Đánh giá | Ghép báo cáo |
| T3 | Kiểm tra số liệu | Nếu dev tốt: chạy 1 lần trên test (báo cáo riêng) | Quay video demo dự phòng | Cập nhật bảng | Nháp slide |
| T4 | Viết mục Giới hạn | Viết mục Phương pháp | Chụp màn hình app | `plot_results.py` | Hoàn thiện báo cáo |
| T5 | Góp ý slide | Góp ý slide | Góp ý slide | Góp ý slide | Hoàn thiện slide |
| **T6** | **Người ngoài nhóm chạy app theo README** | | | | Họp chốt |
| T7 | Tập thuyết trình 2 lượt | | | | |
| CN | Dự phòng; nộp bài | | | | |

## Rủi ro

| Rủi ro | Dấu hiệu | Cách xử lý |
|---|---|---|
| Tải BDD100K chậm / lỗi | Tối T3 tuần 1 chưa có ảnh | Dùng Chrome; thử bản lưu trữ ETH; một người tải rồi chia nội bộ |
| Cài thư viện lỗi | `import open_clip` báo lỗi | Xóa `.venv`, tạo lại; vẫn lỗi thì người đó dùng Colab |
| Embedding quá chậm | Ước tính trên 3 giờ | `--batch 32`, chạy qua đêm, hoặc chạy Colab |
| Thiếu thời gian chấm | T5 tuần 2 chưa chấm xong | Giảm còn top 20 (`evaluate.py --ks 10,20`) |
| CLIP kém hơn kỳ vọng | P@10 thấp ở nhiều câu | Vẫn là kết quả hợp lệ: báo cáo trung thực, phân tích nguyên nhân; **không đổi bộ test** |

## Checklist trước khi nộp

- [ ] README chạy lại được từ đầu trên Mac
- [ ] Một người ngoài nhóm đã chạy được app theo README
- [ ] `queries.csv` khóa từ tuần 1, mã commit ghi trong báo cáo
- [ ] `judgments.csv`, `precision_at_k.csv`, `timing.csv` có trong `results/`
- [ ] Mọi con số trong báo cáo và slide truy được về một file trong `results/`
- [ ] Không có ảnh BDD100K nào trong repo; slide ghi nguồn BDD100K
- [ ] Có video demo dự phòng
