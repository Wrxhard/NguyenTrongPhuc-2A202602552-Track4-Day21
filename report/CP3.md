# CP3 — Benchmark và kiểm chứng claim

## Kết quả chạy thật

| Sweep | Mức (m) | Mean non-ground | Mean cluster | Mean nearest (m) | p50 / p95 (ms) |
|---|---:|---:|---:|---:|---:|
| ground | 0.1 | 4781.8 | 16.6 | 1.740 | 48.41 / 77.00 |
| ground | 0.2 | 4374.2 | 16.8 | 2.454 | 49.19 / 79.08 |
| ground | 0.3 | 4145.0 | 16.0 | 2.751 | 45.37 / 82.79 |
| voxel | 0.1 | 11080.0 | 19.6 | 1.649 | 304.41 / 483.15 |
| voxel | 0.2 | 4781.8 | 16.6 | 1.740 | 99.50 / 160.20 |
| voxel | 0.4 | 1668.6 | 20.6 | 2.669 | 51.24 / 74.41 |

![Benchmark](../results/figures/obstacle_sweep.png)

Trung bình non-ground giảm 4781,8 → 4145,0, D=13,31716090175248%; claim CP1 ≥10% được ủng hộ trên 5 frame. Ground mean cluster thay đổi 16,6 →16,8 →16,0, không đơn điệu; nearest tăng 1,740 →2,454 →2,751 m. Voxel lớn giảm điểm và giảm latency trong sweep voxel nhưng số cluster không đơn điệu (19,6/16,6/20,6); chưa kết luận recall/accuracy vì chưa đối chiếu GT.

## Kiểm soát thí nghiệm

- Cùng 5 frame/ROI/class-agnostic DBSCAN/seed42. Ground sweep giữ voxel0,20 và plane tham chiếu mỗi frame; voxel sweep giữ ground0,10, fit lại plane từng voxel.
- DBSCAN eps0,60/min_points10; RANSAC fit threshold0,10, ransac_n3, iterations1000, probability1. Open3D threads1.
- CPU Intel Core i5-10300H @2,50GHz; Windows 11; Python3.13.6, Open3D0.20, NumPy2.5.3. Cấu hình đầy đủ [benchmark_config.json](../results/benchmark_config.json).
- [obstacle_sweep.csv](../results/obstacle_sweep.csv): 30 dòng frame/config, metric và p50/p95 riêng mỗi frame; [summary](../results/obstacle_summary.csv): 6 cấu hình; [cluster dimensions](../results/sweep_clusters.csv): mọi AABB.
- [latency_samples.csv](../results/latency_samples.csv): 6×5×20=600 lượt đo thật, mỗi cặp bỏ một warm-up. Bảng dùng percentile tuyến tính NumPy, pooled 100 lượt/config. Ground timing bỏ fit plane cache; voxel timing gồm fit. Không so chéo scope. Cả hai bỏ I/O, imports, plot/CSV và hash check.
- Mọi lượt đo kiểm tra fingerprint sau timer. Chạy lại độc lập `src.verify_geometry`: **30/30 geometry khớp chính xác**. Chỉ kiểm tra hình học, không yêu cầu latency lặp y hệt.

## Lỗi tái lập tìm thấy và sửa

CP2 dùng seed và OMP_NUM_THREADS nhưng Open3D0.20 dùng TBB, nên RANSAC còn cho plane khác giữa các lượt. Test thật trên KITTI000001 đã FAIL trước sửa; sau `set_max_threads(1)` và `probability=1.0` (đủ 1000 lượt) suite **10/10 PASS**. Đã tái tạo toàn bộ baseline CSV/ảnh; số CP2 trong commit cũ là lịch sử chạy ban đầu, không phải bản benchmark cuối. Baseline hiện tại có 7/21/11/15/29 cluster.

Nguồn kỹ thuật: [Open3D changelog](https://github.com/isl-org/Open3D/blob/main/CHANGELOG.md), [plane segmentation và probability](https://open3d.org/docs/latest/tutorial/t_geometry/pointcloud.html). Code tham khảo API, tự viết với Codex. Môi trường khóa trong requirements-lock.txt.

## Chạy lại

```powershell
.\.venv\Scripts\python.exe -m src.benchmark
.\.venv\Scripts\python.exe -m src.verify_geometry
.\.venv\Scripts\python.exe -m unittest discover -s src -p "test_*.py"
```
