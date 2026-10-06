"""Bước 2 (người B): nhúng toàn bộ ảnh bằng CLIP, chạy MỘT lần.

    python scripts/embed_images.py                      # ViT-B-32 (mặc định)
    CLIP_MODEL=vitl14 python scripts/embed_images.py    # ViT-L-14 (nên chạy Colab GPU)
    python scripts/embed_images.py --batch 32           # nếu thiếu bộ nhớ

Thứ tự dòng của file .npy trùng thứ tự trong metadata.csv:
KHÔNG sắp xếp lại metadata.csv sau bước này.
"""
import argparse
import time

import numpy as np
import open_clip
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from config import IMG_DIR, METADATA, MODEL_KEY, MODELS, device


class Images(Dataset):
    def __init__(self, names, preprocess):
        self.names, self.preprocess = names, preprocess

    def __len__(self):
        return len(self.names)

    def __getitem__(self, i):
        return self.preprocess(Image.open(IMG_DIR / self.names[i]).convert("RGB"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    name, pretrained, out = MODELS[MODEL_KEY]
    dev = device()
    print(f"{name}/{pretrained} trên {dev} -> {out}")

    model, _, preprocess = open_clip.create_model_and_transforms(name, pretrained=pretrained)
    model = model.to(dev).eval()
    names = pd.read_csv(METADATA)["name"].tolist()
    loader = DataLoader(Images(names, preprocess), batch_size=args.batch,
                        num_workers=args.workers, shuffle=False)

    chunks, t0 = [], time.time()
    with torch.no_grad():
        for batch in tqdm(loader):
            e = model.encode_image(batch.to(dev))
            e = e / e.norm(dim=-1, keepdim=True)
            chunks.append(e.cpu().numpy().astype("float32"))

    emb = np.concatenate(chunks)
    assert len(emb) == len(names), "Số vector khác số dòng metadata!"
    np.save(out, emb)
    print(emb.shape, f"— {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
