PY := .venv/bin/python

.PHONY: help setup check metadata smoke embed app test lint dev-top test-top eval eval-dev timing plots

help:            ## Liệt kê các lệnh
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

setup:           ## Tạo .venv và cài thư viện
	python3 -m venv .venv && $(PY) -m pip install -U pip && $(PY) -m pip install -r requirements.txt

check:           ## Kiểm tra môi trường + dữ liệu
	$(PY) scripts/check_env.py

metadata:        ## (A) det_val.json -> data/metadata.csv
	$(PY) scripts/build_metadata.py

smoke:           ## (B) thử CLIP trên 5 ảnh
	$(PY) scripts/clip_smoke_test.py

embed:           ## (B) nhúng 10.000 ảnh
	$(PY) scripts/embed_images.py

app:             ## (C) mở demo Streamlit
	.venv/bin/streamlit run app/app.py

dev-top:         ## Xuất top-20 bộ dev cho 3 cấu hình
	$(PY) scripts/export_top.py dev -k 20

test-top:        ## Xuất top-50 bộ test (MỘT LẦN)
	$(PY) scripts/export_top.py test --config clip_filter_tpl

eval:            ## (D) Precision@K + kappa bộ test
	$(PY) scripts/evaluate.py

eval-dev:        ## (D) so 3 cấu hình trên dev
	$(PY) scripts/evaluate.py --top results/dev_top20.csv --judgments results/dev_judgments.csv --out results/dev_tuning.csv

timing:          ## (E) tổng hợp thí nghiệm bấm giờ
	$(PY) scripts/timing_summary.py

plots:           ## Vẽ biểu đồ vào results/figures/
	$(PY) scripts/plot_results.py

test:            ## Chạy pytest
	$(PY) -m pytest -q

lint:            ## Kiểm tra code bằng ruff
	$(PY) -m ruff check .
