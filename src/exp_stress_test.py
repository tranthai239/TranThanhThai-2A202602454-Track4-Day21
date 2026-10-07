"""[B2] Stress test suy giảm dữ liệu (dropout + gaussian noise) lên projection QA.
Chạy từ gốc repo: python -m src.exp_stress_test
"""
from pathlib import Path
import csv
import numpy as np

from starter.datasets import load_frame
from starter.perturb import gaussian_noise, random_dropout
from src.exp_yaw_sweep import points_in_box, CLASSES
from starter.projection import perturb_extrinsic, project_velo_to_image, velo_to_cam

fr = load_frame("data/kitti_mini", "000011")

records = []

# Thử nghiệm 1: Random dropout x yaw drift
for keep in [1.0, 0.7, 0.5, 0.3]:
    pts_pert = random_dropout(fr["points"], keep_ratio=keep, seed=42)
    cam_true = velo_to_cam(pts_pert[:, :3], fr["calib"])
    for yaw in [0.0, 1.0, 2.0]:
        calib = perturb_extrinsic(fr["calib"], yaw_deg=yaw)
        uv, _, mask = project_velo_to_image(pts_pert, calib, fr["image"].shape)
        uv_all = np.full((len(pts_pert), 2), np.nan)
        uv_all[mask] = uv

        hits = tot = 0
        for obj in fr["labels"]:
            if obj.type not in CLASSES:
                continue
            sel = points_in_box(cam_true, obj) & mask
            if not np.any(sel):
                continue
            u, v = uv_all[sel, 0], uv_all[sel, 1]
            x1, y1, x2, y2 = obj.bbox
            hits += int(((u >= x1) & (u <= x2) & (v >= y1) & (v <= y2)).sum())
            tot += int(sel.sum())

        ratio = round(hits / tot, 4) if tot > 0 else 0.0
        records.append({
            "test_type": "dropout",
            "param_value": keep,
            "yaw_deg": yaw,
            "object_points": tot,
            "hit_ratio": ratio,
        })

# Thử nghiệm 2: Gaussian noise x yaw drift
for sigma in [0.0, 0.02, 0.05, 0.10]:
    pts_pert = gaussian_noise(fr["points"], sigma_xyz_m=sigma, seed=42)
    cam_true = velo_to_cam(pts_pert[:, :3], fr["calib"])
    for yaw in [0.0, 1.0, 2.0]:
        calib = perturb_extrinsic(fr["calib"], yaw_deg=yaw)
        uv, _, mask = project_velo_to_image(pts_pert, calib, fr["image"].shape)
        uv_all = np.full((len(pts_pert), 2), np.nan)
        uv_all[mask] = uv

        hits = tot = 0
        for obj in fr["labels"]:
            if obj.type not in CLASSES:
                continue
            sel = points_in_box(cam_true, obj) & mask
            if not np.any(sel):
                continue
            u, v = uv_all[sel, 0], uv_all[sel, 1]
            x1, y1, x2, y2 = obj.bbox
            hits += int(((u >= x1) & (u <= x2) & (v >= y1) & (v <= y2)).sum())
            tot += int(sel.sum())

        ratio = round(hits / tot, 4) if tot > 0 else 0.0
        records.append({
            "test_type": "gaussian_noise",
            "param_value": sigma,
            "yaw_deg": yaw,
            "object_points": tot,
            "hit_ratio": ratio,
        })

out_csv = Path("results/stress_test_degradation.csv")
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)

print(f"-> Saved stress test results: {out_csv} ({len(records)} dòng)")
