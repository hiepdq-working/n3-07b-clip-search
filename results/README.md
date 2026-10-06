# results/

Thư mục này **có commit**: mọi con số trong báo cáo và slide phải truy được về một file ở đây.
Không đổi tên cột, vì các script đọc theo đúng tên.

| File | Tạo bởi | Cột |
|---|---|---|
| `data_stats.csv` | `build_metadata.py` | attribute, value, count, pct |
| `rare_slices.csv` | `build_metadata.py` | slice, count, pct |
| `dev_top20.csv` | `export_top.py dev` | query_id (`D01\|config`), rank, name, score |
| `test_top50.csv` | `export_top.py test` (một lần) | query_id, rank, name, score |
| `run_log.txt` | `export_top.py` | thời điểm, model, commit của mỗi lần xuất |
| `judgments.csv` / `dev_judgments.csv` | app, tab Chấm kết quả | query_id, name, judge, rel (0/1) |
| `disagreements.csv` | `evaluate.py` | query_id, name: ảnh lệch chưa phân xử |
| `adjudicated.csv` | D ghi tay | query_id, name, rel |
| `precision_at_k.csv` | `evaluate.py` | query_id, P@10, P@20, P@50, n_returned, split, query, metadata_covers |
| `precision_at_k_kappa.csv` | `evaluate.py` | query_id, judges, n, agree_pct, kappa |
| `dev_tuning.csv` | `evaluate.py --out …` | như trên, thêm cột config |
| `timing.csv` | app, tab Bấm giờ | tester, query_id, mode, seconds, viewed, found, timestamp |
| `timing_summary.csv` | `timing_summary.py` | mode, metadata_covers, runs, minutes_mean, viewed_mean, found_mean, reached_20, found_per_min |
| `error_analysis.csv` | ghi tay | query_id, name, rank, category, note |
| `figures/*.png` | `plot_results.py` | biểu đồ |

Bấm nhầm khi chấm thì **không xóa dòng**. Chỉ cần chấm lại và lưu lại, vì `evaluate.py` lấy lần lưu cuối của mỗi người cho mỗi ảnh.
