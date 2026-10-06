# Chạy ViT-L-14 trên Colab (tuần 2, tùy chọn)

ViT-L-14 chính xác hơn nhưng nặng hơn ViT-B-32 nhiều, nên chạy trên Colab GPU (T4) thay vì Mac.

1. Đưa `data/metadata.csv` và thư mục `data/bdd100k/images/100k/val/` lên **Google Drive riêng của nhóm** (không chia sẻ công khai).
2. Mở Colab và chọn *Runtime → Change runtime type → T4 GPU*.
3. Chạy lần lượt các cell:

```python
from google.colab import drive
drive.mount("/content/drive")
```

```bash
!git clone https://github.com/<ten-nhom>/n3-07b-clip-search.git
%cd n3-07b-clip-search
!pip -q install open_clip_torch
!mkdir -p data/bdd100k/images/100k
!ln -s "/content/drive/MyDrive/<thu-muc-nhom>/val" data/bdd100k/images/100k/val
!cp "/content/drive/MyDrive/<thu-muc-nhom>/metadata.csv" data/
```

```bash
!CLIP_MODEL=vitl14 python scripts/embed_images.py --batch 128 --workers 2
!cp data/emb_vitl14.npy "/content/drive/MyDrive/<thu-muc-nhom>/"
```

`config.device()` tự chọn `cuda` khi có GPU. Kết quả có shape `(10000, 768)`.

4. Tải `emb_vitl14.npy` về thư mục `data/` trên Mac. Từ đó dùng model này bằng cách thêm `CLIP_MODEL=vitl14` trước mỗi lệnh, ví dụ:

```bash
CLIP_MODEL=vitl14 streamlit run app/app.py
CLIP_MODEL=vitl14 python scripts/export_top.py dev -k 20
```

Lưu ý: `export_top.py dev` ghi đè `results/dev_top20.csv`. Đổi tên file cũ trước, ví dụ `dev_top20_vitb32.csv`.
