"""[B3] Đo latency phép chiếu projection theo đúng chuẩn p50/p95 (20 lần, bỏ lần đầu).
Chạy từ gốc repo: python -m src.measure_latency
"""
from pathlib import Path
import time
import numpy as np
import pandas as pd

from starter.datasets import load_frame
from starter.projection import project_velo_to_image

fr = load_frame("data/kitti_mini", "000011")
pts = fr["points"]
calib = fr["calib"]
shape = fr["image"].shape

# Chạy warmup 1 lần để bỏ chi phí khởi tạo / cache
_ = project_velo_to_image(pts, calib, shape)

times_ms = []
records = []
for i in range(1, 21):
    t0 = time.perf_counter()
    _ = project_velo_to_image(pts, calib, shape)
    dt_ms = (time.perf_counter() - t0) * 1000.0
    times_ms.append(dt_ms)
    records.append({"run_id": i, "latency_ms": round(dt_ms, 3)})

times_arr = np.array(times_ms)
p50 = float(np.percentile(times_arr, 50))
p95 = float(np.percentile(times_arr, 95))
mean = float(np.mean(times_arr))

df = pd.DataFrame(records)
out_csv = Path("results/latency_benchmark.csv")
df.to_csv(out_csv, index=False)

print(f"Hardware: Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz | 16 GB RAM")
print(f"Points per frame: {len(pts)}")
print(f"p50 = {p50:.2f} ms | p95 = {p95:.2f} ms | mean = {mean:.2f} ms")
print(f"-> Saved latency log: {out_csv}")
