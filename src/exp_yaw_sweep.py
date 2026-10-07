"""Topic A: Lệch yaw bao nhiêu độ thì điểm LiDAR rơi ra khỏi 2D box của vật thể.
Hỗ trợ cả KITTI và nuScenes, tách theo class và khoảng cách.

Chạy từ gốc repo:
    python -m src.exp_yaw_sweep --data-root data/kitti_mini --frames 000008 000011 000049
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from starter.datasets import dataset_type, load_frame
from starter.projection import perturb_extrinsic, project_velo_to_image, velo_to_cam

CLASSES = ("Car", "Van", "Truck", "Pedestrian", "Cyclist", "Bicycle")


def points_in_box(points_cam: np.ndarray, obj) -> np.ndarray:
    """Mask (N,) các điểm (đã ở camera frame) nằm trong 3D box của label."""
    h, w, l = obj.dimensions
    c, s = np.cos(obj.rotation_y), np.sin(obj.rotation_y)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    local = (points_cam - obj.location) @ R
    return (
        (np.abs(local[:, 0]) <= l / 2)
        & (local[:, 1] <= 0)
        & (local[:, 1] >= -h)
        & (np.abs(local[:, 2]) <= w / 2)
    )


def run_one(fr: dict, yaw_deg: float) -> dict:
    pts = fr["points"][np.isfinite(fr["points"]).all(axis=1)]
    cam_true = velo_to_cam(pts[:, :3], fr["calib"])
    calib = perturb_extrinsic(fr["calib"], yaw_deg=yaw_deg)
    uv, _, mask = project_velo_to_image(pts, calib, fr["image"].shape)
    uv_all = np.full((len(pts), 2), np.nan)
    uv_all[mask] = uv

    obj_pts = hits = 0
    car_pts = car_hits = 0
    ped_pts = ped_hits = 0

    near_pts = near_hits = 0      # < 15m
    mid_pts = mid_hits = 0        # 15 - 30m
    far_pts = far_hits = 0        # > 30m

    for obj in fr["labels"]:
        if obj.type not in CLASSES:
            continue
        sel = points_in_box(cam_true, obj) & mask
        if not np.any(sel):
            continue
        u, v = uv_all[sel, 0], uv_all[sel, 1]
        x1, y1, x2, y2 = obj.bbox
        in_2d = (u >= x1) & (u <= x2) & (v >= y1) & (v <= y2)
        n_hits = int(in_2d.sum())
        n_sel = int(sel.sum())

        hits += n_hits
        obj_pts += n_sel

        # Theo class
        if obj.type in ("Car", "Van", "Truck"):
            car_pts += n_sel
            car_hits += n_hits
        elif obj.type in ("Pedestrian", "Cyclist", "Bicycle"):
            ped_pts += n_sel
            ped_hits += n_hits

        # Theo khoảng cách (dùng depth z của location)
        dist = float(np.linalg.norm(obj.location))
        if dist < 15.0:
            near_pts += n_sel
            near_hits += n_hits
        elif dist < 30.0:
            mid_pts += n_sel
            mid_hits += n_hits
        else:
            far_pts += n_sel
            far_hits += n_hits

    def _ratio(h, t):
        return round(h / t, 4) if t > 0 else float("nan")

    return {
        "n_points": len(pts),
        "inside_image": int(mask.sum()),
        "object_points": obj_pts,
        "hit_ratio": _ratio(hits, obj_pts),
        "hit_ratio_car": _ratio(car_hits, car_pts),
        "hit_ratio_ped": _ratio(ped_hits, ped_pts),
        "hit_ratio_near": _ratio(near_hits, near_pts),
        "hit_ratio_mid": _ratio(mid_hits, mid_pts),
        "hit_ratio_far": _ratio(far_hits, far_pts),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Quét góc lệch yaw, đo % điểm vật thể trong 2D box")
    ap.add_argument("--data-root", default="data/kitti_mini")
    ap.add_argument("--frames", nargs="+", default=["000008", "000011", "000049"])
    ap.add_argument("--yaw-levels", nargs="+", type=float, default=[0.0, 0.5, 1.0, 2.0, 3.0])
    ap.add_argument("--out", default="results/yaw_perturb_sweep.csv")
    args = ap.parse_args()

    rows = []
    is_nusc = dataset_type(args.data_root) == "nuscenes"
    for frame in args.frames:
        kwargs = {"use_ego_motion": True} if is_nusc else {}
        fr = load_frame(args.data_root, frame, **kwargs)
        for yaw in args.yaw_levels:
            metrics = run_one(fr, yaw)
            row = {
                "dataset": Path(args.data_root).name,
                "frame": frame,
                "yaw_deg": yaw,
                **metrics,
            }
            rows.append(row)
            print(
                f"{row['dataset']} {row['frame']} yaw={yaw:3.1f}° | "
                f"hit={row['hit_ratio']:.4f} "
                f"car={row['hit_ratio_car']:.4f} ped={row['hit_ratio_ped']:.4f}"
            )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"-> {out} ({len(rows)} dòng)")


if __name__ == "__main__":
    main()
