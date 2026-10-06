"""Bước 0: kiểm tra môi trường. Mọi máy phải chạy được trước tối thứ Ba tuần 1.

    python scripts/check_env.py
"""
import importlib
import platform
import sys

from config import IMG_DIR, LABELS, METADATA, MODEL_KEY, MODELS

ok = True
print("Python", sys.version.split()[0], "|", platform.platform())
if not (3, 10) <= sys.version_info[:2] <= (3, 12):
    print("  ! Nên dùng Python 3.10–3.12")

for mod in ["torch", "torchvision", "open_clip", "PIL", "pandas", "numpy",
            "tqdm", "streamlit", "sklearn", "matplotlib"]:
    try:
        m = importlib.import_module(mod)
        print(f"  ✓ {mod} {getattr(m, '__version__', '')}")
    except Exception as e:  # noqa: BLE001
        ok = False
        print(f"  ✗ {mod}: {e}")

try:
    import torch
    print("MPS:", torch.backends.mps.is_available(), "| CUDA:", torch.cuda.is_available())
except Exception:  # noqa: BLE001
    pass

print("\nDữ liệu:")
n_img = len(list(IMG_DIR.glob("*.jpg"))) if IMG_DIR.exists() else 0
print(f"  ảnh val: {n_img} (cần 10000)")
print(f"  det_val.json: {'có' if LABELS.exists() else 'CHƯA có'}")
print(f"  metadata.csv: {'có' if METADATA.exists() else 'CHƯA có'}")
emb = MODELS[MODEL_KEY][2]
print(f"  {emb.name}: {'có' if emb.exists() else 'CHƯA có'}")

sys.exit(0 if ok else 1)
