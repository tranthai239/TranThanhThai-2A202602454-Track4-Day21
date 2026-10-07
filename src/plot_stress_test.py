"""Vẽ biểu đồ stress test suy giảm dữ liệu cho Bonus B2."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("results/stress_test_degradation.csv")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

# Plot 1: Dropout
df_drop = df[df["test_type"] == "dropout"]
for yaw, g in df_drop.groupby("yaw_deg"):
    ax1.plot(g["param_value"], 100 * g["hit_ratio"], marker="o", label=f"yaw {yaw}°")
ax1.set_title("(a) Ảnh hưởng của Random Dropout")
ax1.set_xlabel("Tỉ lệ điểm giữ lại (keep_ratio)")
ax1.set_ylabel("% điểm rơi đúng trong 2D box")
ax1.set_ylim(0, 105)
ax1.grid(alpha=0.3)
ax1.legend()

# Plot 2: Noise
df_noise = df[df["test_type"] == "gaussian_noise"]
for yaw, g in df_noise.groupby("yaw_deg"):
    ax2.plot(g["param_value"], 100 * g["hit_ratio"], marker="s", label=f"yaw {yaw}°")
ax2.set_title("(b) Ảnh hưởng của Gaussian Noise")
ax2.set_xlabel("Độ lệch chuẩn nhiễu sigma (m)")
ax2.set_ylabel("% điểm rơi đúng trong 2D box")
ax2.set_ylim(0, 105)
ax2.grid(alpha=0.3)
ax2.legend()

fig.tight_layout()
out = Path("results/figures/stress_test_sweep.png")
fig.savefig(out, dpi=150)
print(f"-> {out}")
