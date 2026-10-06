# Quy trình làm việc

## Nhánh
- `main` luôn chạy được. Không push thẳng lên `main` (bật *Branch protection* trên GitHub: yêu cầu 1 review + CI xanh).
- Mỗi người làm trên nhánh riêng, đặt tên theo vai và việc: `a/build-metadata`, `b/search-templates`, `c/app-timing-tab`, `d/guideline`, `e/report`.

```bash
git checkout main && git pull
git checkout -b b/search-templates
# … sửa code …
git add -p && git commit -m "search: gộp mẫu câu"
git push -u origin b/search-templates     # rồi mở Pull Request trên GitHub
```

- PR cần **một người khác xem lại** rồi mới merge. Ưu tiên *Squash and merge*.

## Không bao giờ commit
- Ảnh BDD100K, `data/`, file `*.npy`, `*.zip` (giấy phép không cho phân phối lại). `.gitignore` đã chặn, nhưng vẫn kiểm tra `git status` trước khi commit.
- Video demo: để trên Drive của nhóm, chỉ dán link vào README hoặc báo cáo.

## Được commit
- `results/*.csv`: judgments, timing, bảng kết quả. Đây là bằng chứng cho mọi con số trong báo cáo.
- `results/figures/*.png`: biểu đồ (không chứa ảnh BDD100K).

## File CSV: giữ nguyên tên cột
`evaluate.py` và `timing_summary.py` đọc theo đúng tên cột. Xem [results/README.md](results/README.md).

## Bộ test
Sau khi có tag `queries-locked`, **không sửa** các dòng `split=test` trong `queries.csv`. CI sẽ báo lỗi nếu bộ test bị thay đổi so với tag.

## Trước khi mở PR
```bash
make lint && make test
```
