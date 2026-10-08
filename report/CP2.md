# CP2 — Baseline chạy thật

Triển khai trong src/, không sửa starter/ và data/. Pipeline: lọc hữu hạn → ROI → voxel → RANSAC → ground mask → DBSCAN → AABB. Fit plane ở 0,10 m, 1000 iterations, seed 42; nhận plane khi normal lệch z ≤15°. Kiểm tra hướng không xác nhận toàn bộ mặt đường phẳng.

## Minh chứng

- [baseline.csv](../results/baseline.csv): 5 frame, cấu hình, số điểm từng bước, cluster/noise, nearest và plane tilt.
- [baseline_clusters.csv](../results/baseline_clusters.csv): mọi AABB có min/max/extent và số điểm.
- Ảnh từng bước: [000001](../results/figures/demo_000001.png), [000011](../results/figures/demo_000011.png), [000019](../results/figures/demo_000019.png), [000025](../results/figures/demo_000025.png), [000049](../results/figures/demo_000049.png).
- [Synthetic](../results/synthetic_debug/figures/demo_000000.png): lọc 23 điểm lỗi; ROI 7442 → voxel 4295 → non-ground 815, 7 cluster.
- 6/6 test PASS: ROI inclusive/NaN, normalized plane, nearest rectangle, empty/noise, vertical rejection, two obstacles on flat ground.

KITTI cho 7/22/11/15/29 cluster; plane tilt 0,680/1,980/2,610/0,643/1,515°. Frame 000019 nearest 0,405 m; ảnh còn điểm gần mặt đường và box lớn, chưa coi là khoảng cách vật cản thật. CP4 sẽ kiểm tra failure.

## Chạy lại

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s src -p "test_*.py"
.\.venv\Scripts\python.exe -m src.experiments demo
.\.venv\Scripts\python.exe -m src.experiments demo --data-root data/synthetic --frames 000000 --out results/synthetic_debug
```

API tham khảo: [Open3D tutorial](https://www.open3d.org/docs/release/tutorial/geometry/pointcloud.html). Code tự viết có hỗ trợ Codex. Lỗi escape newline trong tiêu đề đã được xác định qua SyntaxError và sửa; demo sau sửa chạy thành công. CP2 chưa có benchmark/failure hoàn chỉnh.

## Cập nhật tại CP3

CP3 phát hiện/sửa RANSAC chưa tái lập, đã tạo lại các CSV/ảnh ở đường dẫn trên. Số baseline cuối là 7/21/11/15/29 cluster; tham khảo CP3 và baseline.csv hiện tại. Các số cũ trong phần trên là kết quả ban đầu ở commit CP2, được thay thế cho bản nộp cuối.
