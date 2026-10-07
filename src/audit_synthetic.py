"""[B6] Quét toàn bộ lỗi cài sẵn trong data/synthetic."""
from starter.datasets import load_frame
import numpy as np

with open("data/synthetic/training/timestamps.txt") as f:
    ts = [float(x.strip()) for x in f if x.strip()]

print("Timestamps:", ts)
gaps = np.diff(ts)
print("Time gaps:", np.round(gaps, 3))

for i in range(5):
    fid = f"{i:06d}"
    fr = load_frame("data/synthetic", fid)
    pts = fr["points"]
    finite_mask = np.isfinite(pts).all(axis=1)
    nan_count = len(pts) - finite_mask.sum()
    labels = [(o.type, o.bbox.tolist(), o.location.tolist()) for o in fr["labels"]]
    print(f"Frame {fid}: N={len(pts)}, NaN={nan_count} ({nan_count/len(pts):.2%}), Labels={len(labels)}")
