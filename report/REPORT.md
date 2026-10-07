# Báo cáo Day 6: Độ nhạy của projection với calibration drift (yaw)

> Thay **mọi** ô có chữ ĐIỀN nằm trong ngoặc vuông bằng nội dung của bạn, xoá luôn cả dấu ngoặc vuông. Lệnh `python tools/check_submission.py` sẽ báo FAIL nếu còn sót bất kỳ chỗ nào.

- **Họ tên:** Trần Thanh Thái
- **MSSV:** 2A202602454
- **Lớp:** AI20K-T4
- **Link repo:** https://github.com/tranthai239/TranThanhThai-2A202602454-Track4-Day21
- **Topic:** A — LiDAR-camera projection QA
- **Dataset:** data/kitti_mini, data/nuscenes_mini_subset
- **Các frame đã dùng:** 000008, 000011, 000015, 000048, scene-0103_010, scene-1094_010

> Hãy viết ngắn: mỗi mục từ 3 đến 8 dòng, ưu tiên số liệu và hình ảnh.

## 1. Claim

Lệch yaw 1° làm tỉ lệ điểm LiDAR của người đi bộ rơi đúng vào 2D box giảm hơn 20 điểm phần trăm so với 0°, trong khi với xe con chỉ giảm dưới 5 điểm phần trăm. Hiệu ứng này nhất quán giữa KITTI (64 beam) và nuScenes (32 beam).

## 2. Evidence

File số liệu: `results/yaw_perturb_sweep.csv` (KITTI) và `results/yaw_perturb_sweep_nusc.csv` (nuScenes).

### Bảng 1. Tỉ lệ điểm vật thể rơi đúng vào 2D box (hit_ratio) trên KITTI

| Lệch yaw | Frame 000008 (đông xe) | Frame 000011 (tổng) | 000011 (Car) | 000011 (Pedestrian) | Frame 000049 (nhiều vật che) |
|---|---|---|---|---|---|
| 0.0° | 99.63% | 99.45% | 99.28% | 99.67% | 99.25% |
| 0.5° | 99.57% | 91.88% | 96.87% | 85.67% | 97.46% |
| 1.0° | 98.62% | 77.44% | 91.12% | 61.89% | 93.50% |
| 2.0° | 94.81% | 45.44% | 71.58% | 21.17% | 84.74% |
| 3.0° | 90.98% | 21.23% | 42.61% | 5.21% | 74.32% |

### Bảng 2. So sánh với nuScenes (Bonus B5)

| Lệch yaw | nuScenes scene-0103_010 (ngày) | nuScenes scene-1094_010 (đêm) |
|---|---|---|
| 0.0° | 100.00% | 100.00% |
| 0.5° | 97.09% | 100.00% |
| 1.0° | 90.10% | 96.76% |
| 2.0° | 72.92% | 85.71% |
| 3.0° | 62.37% | 74.57% |

![yaw sweep](../results/figures/yaw_sweep.png)

**Nhận xét:**
1. Lệch yaw ảnh hưởng mạnh nhất tới người đi bộ (vật hẹp): ở 1°, hit_ratio của Pedestrian trong frame 000011 giảm mạnh từ 99.67% xuống 61.89% (giảm 37.78 điểm %), trong khi Car chỉ giảm từ 99.28% xuống 91.12% (giảm 8.16 điểm %). Đến 3°, Pedestrian chỉ còn 5.21% điểm rơi đúng box.
2. Frame 000008 (chủ yếu là xe con kích thước lớn) rất bền vững với lệch góc: ở 1° vẫn giữ 98.62%, đến 3° vẫn còn 90.98%.
3. So sánh KITTI vs nuScenes (Bonus B5): nuScenes (32-beam, thưa hơn 3 lần) có độ nhạy tương tự về xu hướng nhưng số điểm tuyệt đối trên mỗi vật ít hơn nhiều, khiến việc mất điểm ở góc lệch lớn gây nguy hiểm cao hơn cho khâu sensor fusion.

## 3. Failure case

Nêu khi nào hệ thống hoặc phương pháp fail, vì sao fail, và liên hệ tới lớp nào trong 6 lớp debug: I/O, Geometry, Time, Preprocess, Model, Metric.

![failure](../results/figures/fail_[ĐIỀN].png)

[ĐIỀN]

## 4. Khuyến nghị nếu triển khai thật

Use-case cụ thể (ADAS / robot / drone), trade-off và bước tiếp theo.

[ĐIỀN]

## 5. Cách chạy lại

Các lệnh tái tạo lại toàn bộ kết quả từ repo sạch.

```bash
# 1. Tự kiểm tra phép chiếu
python -m src.test_projection

# 2. Demo overlay gốc (0° drift) trên 3 frame (gần, vừa, xa)
python -m starter.projection --data-root data/kitti_mini --frame 000019
python -m starter.projection --data-root data/kitti_mini --frame 000011
python -m starter.projection --data-root data/kitti_mini --frame 000004

# 3. Demo overlay nuScenes
python -m starter.projection --data-root data/nuscenes_mini_subset --frame scene-0103_010

# 4. Thí nghiệm quét yaw (KITTI + nuScenes)
python -m src.exp_yaw_sweep --data-root data/kitti_mini --frames 000008 000011 000049 --out results/yaw_perturb_sweep.csv
python -m src.exp_yaw_sweep --data-root data/nuscenes_mini_subset --frames scene-0103_010 scene-1094_010 --out results/yaw_perturb_sweep_nusc.csv

# 5. Vẽ biểu đồ benchmark
python -m src.plot_yaw_sweep
```

## 6. Khai báo sử dụng AI

Ghi rõ đã dùng công cụ AI nào, dùng vào việc gì, và bạn đã tự kiểm chứng kết quả đó bằng cách nào. Nếu không dùng AI, ghi "Không sử dụng". Xem quy định ở `RULES.md` mục 2.

| Công cụ | Dùng cho việc gì | Bạn đã kiểm chứng thế nào |
|---|---|---|
| [ĐIỀN] | | |
