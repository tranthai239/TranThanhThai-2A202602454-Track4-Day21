"""Tạo ảnh failure case so sánh trực quan side-by-side.
Chạy từ gốc repo: python -m src.make_failure_cases
"""
from pathlib import Path

import cv2
import numpy as np

from starter.datasets import load_frame
from starter.projection import (
    draw_box2d,
    overlay_points,
    perturb_extrinsic,
    project_velo_to_image,
)


def make_fail_geometry() -> None:
    """Fail 1: Geometry drift (yaw 2.0°) trên frame 000011 (KITTI) - nhóm người đi bộ."""
    fr = load_frame("data/kitti_mini", "000011")

    # Bản chuẩn 0°
    uv0, d0, m0 = project_velo_to_image(fr["points"], fr["calib"], fr["image"].shape)
    img0 = overlay_points(fr["image"], uv0, d0)
    for obj in fr["labels"]:
        img0 = draw_box2d(img0, obj.bbox, label=obj.type)

    # Bản lệch yaw 2°
    calib_drift = perturb_extrinsic(fr["calib"], yaw_deg=2.0)
    uv2, d2, m2 = project_velo_to_image(fr["points"], calib_drift, fr["image"].shape)
    img2 = overlay_points(fr["image"], uv2, d2)
    for obj in fr["labels"]:
        img2 = draw_box2d(img2, obj.bbox, label=obj.type)

    # Crop vùng người đi bộ bên phải (x: 550-900, y: 140-340)
    crop0 = img0[140:340, 550:900]
    crop2 = img2[140:340, 550:900]

    cv2.putText(crop0, "ORIGINAL (yaw 0.0 deg)", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(crop2, "DRIFT (yaw +2.0 deg)", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(crop2, "POINTS SHIFTED OUT OF 2D BOX", (10, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    combined = np.hstack([crop0, crop2])
    out = Path("results/figures/fail_01_yaw_2deg_pedestrian.png")
    cv2.imwrite(str(out), combined)
    print(f"-> {out}")


def make_fail_time() -> None:
    """Fail 2: Time synchronization (tắt ego motion) trên nuScenes scene-0103_010."""
    fr_ego = load_frame("data/nuscenes_mini_subset", "scene-0103_010", use_ego_motion=True)
    uv_ego, d_ego, m_ego = project_velo_to_image(fr_ego["points"], fr_ego["calib"], fr_ego["image"].shape)
    img_ego = overlay_points(fr_ego["image"], uv_ego, d_ego)
    for obj in fr_ego["labels"]:
        img_ego = draw_box2d(img_ego, obj.bbox, label=obj.type)

    fr_noego = load_frame("data/nuscenes_mini_subset", "scene-0103_010", use_ego_motion=False)
    uv_no, d_no, m_no = project_velo_to_image(fr_noego["points"], fr_noego["calib"], fr_noego["image"].shape)
    img_noego = overlay_points(fr_noego["image"], uv_no, d_no)
    for obj in fr_noego["labels"]:
        img_noego = draw_box2d(img_noego, obj.bbox, label=obj.type)

    # Crop vùng xe phía trước (x: 600-1100, y: 400-750)
    crop_ego = img_ego[400:750, 600:1100]
    crop_no = img_noego[400:750, 600:1100]

    cv2.putText(crop_ego, "COMPENSATED (ego deskew ON)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(crop_no, "NO DESKEW (35.6ms uncompensated)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    combined = np.hstack([crop_ego, crop_no])
    out = Path("results/figures/fail_02_nusc_no_ego_motion.png")
    cv2.imwrite(str(out), combined)
    print(f"-> {out}")


if __name__ == "__main__":
    make_fail_geometry()
    make_fail_time()
