"""Vẽ kết quả quét yaw. Chạy từ gốc repo: python -m src.plot_yaw_sweep"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

df_kitti = pd.read_csv("results/yaw_perturb_sweep.csv", dtype={"frame": str})
df_nusc = pd.read_csv("results/yaw_perturb_sweep_nusc.csv", dtype={"frame": str})

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# Subplot 1: KITTI theo từng frame
ax = axes[0]
for frame, g in df_kitti.groupby("frame"):
    desc = {
        "000008": "000008 (đông xe)",
        "000011": "000011 (nhiều người đi bộ)",
        "000049": "000049 (nhiều vật bị che)",
    }.get(frame, frame)
    ax.plot(g["yaw_deg"], 100 * g["hit_ratio"], marker="o", label=desc)
ax.set_title("(a) KITTI: Hit ratio theo frame")
ax.set_xlabel("Lệch yaw (độ)")
ax.set_ylabel("% điểm vật thể nằm trong 2D box")
ax.set_ylim(0, 105)
ax.grid(alpha=0.3)
ax.legend(fontsize=8)

# Subplot 2: Frame 000011 - Car vs Pedestrian
ax = axes[1]
g11 = df_kitti[df_kitti["frame"] == "000011"]
ax.plot(g11["yaw_deg"], 100 * g11["hit_ratio_car"], marker="s", color="tab:blue", label="Car (xe con)")
ax.plot(g11["yaw_deg"], 100 * g11["hit_ratio_ped"], marker="^", color="tab:red", label="Pedestrian (người đi bộ)")
ax.set_title("(b) Frame 000011: Car vs Pedestrian")
ax.set_xlabel("Lệch yaw (độ)")
ax.set_ylabel("% điểm vật thể nằm trong 2D box")
ax.set_ylim(0, 105)
ax.grid(alpha=0.3)
ax.legend()

# Subplot 3: So sánh KITTI 000011 vs nuScenes scene-0103_010 (cả hai có pedestrian)
ax = axes[2]
ax.plot(g11["yaw_deg"], 100 * g11["hit_ratio"], marker="o", label="KITTI 000011 (64-beam)")
gnusc = df_nusc[df_nusc["frame"] == "scene-0103_010"]
ax.plot(gnusc["yaw_deg"], 100 * gnusc["hit_ratio"], marker="D", label="nuScenes scene-0103_010 (32-beam)")
gnusc2 = df_nusc[df_nusc["frame"] == "scene-1094_010"]
ax.plot(gnusc2["yaw_deg"], 100 * gnusc2["hit_ratio"], marker="v", label="nuScenes scene-1094_010 (đêm, 32-beam)")
ax.set_title("(c) So sánh KITTI vs nuScenes (Bonus B5)")
ax.set_xlabel("Lệch yaw (độ)")
ax.set_ylabel("% điểm vật thể nằm trong 2D box")
ax.set_ylim(0, 105)
ax.grid(alpha=0.3)
ax.legend(fontsize=8)

fig.tight_layout()

out = Path("results/figures/yaw_sweep.png")
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=150)
print(f"-> {out}")
