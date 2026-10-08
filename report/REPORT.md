# Báo cáo Day 6: Phát hiện vật cản cho robot/drone

> Thay **mọi** ô có chữ ĐIỀN nằm trong ngoặc vuông bằng nội dung của bạn, xoá luôn cả dấu ngoặc vuông. Lệnh `python tools/check_submission.py` sẽ báo FAIL nếu còn sót bất kỳ chỗ nào.

- **Họ tên:** Nguyễn Trọng Phúc
- **MSSV:** 2A202602552
- **Lớp:** Track 4 — VinUni AI20K (chưa cung cấp mã lớp cụ thể)
- **Link repo:** https://github.com/Wrxhard/NguyenTrongPhuc-2A202602552-Track4-Day21
- **Topic:** D — Robot/drone obstacle
- **Dataset:** `data/kitti_mini` (thí nghiệm chính); `data/synthetic` (kiểm tra dữ liệu/debug).
- **Các frame đã dùng:** synthetic `000000–000004` (CP0); KITTI `000001, 000011, 000019, 000025, 000049` (CP1: kiểm tra dữ liệu, dự kiến dùng CP2–CP4).

> Hãy viết ngắn: mỗi mục từ 3 đến 8 dòng, ưu tiên số liệu và hình ảnh.

> **Tiến độ:** CP3 đã hoàn thành benchmark và kiểm tra tái lập. [CP0](CP0.md) · [CP1](CP1.md) · [CP2](CP2.md) · [CP3](CP3.md). Failure sẽ phân tích ở CP4.

## 1. Claim

**Claim được ủng hộ trên 5 frame KITTI:** trong ROI x=[0,30], y=[−10,10], z=[−3,3] m, voxel 0,20 m và cùng mặt phẳng ground mỗi frame, tăng ground threshold từ 0,10 lên 0,30 m giảm **13,32%** trung bình số điểm non-ground (**4781,8 → 4145,0**), vượt giả thuyết CP1 ≥10%.

D = 100 × (mean N₀․₁ − mean N₀․₃) / mean N₀․₁. RANSAC fit ở 0,10 m, 1000 iterations, probability=1, seed 42, Open3D threads=1. Giảm điểm không đồng nghĩa tăng accuracy hoặc đã bỏ sót vật cản; chỉ kết luận trong mẫu/ROI này. Thiết kế ban đầu: [CP1](CP1.md).

## 2. Evidence

Hai sweep độc lập, 5 frame cố định. DBSCAN eps=0,60 m/min_points=10; ground sweep cố định voxel 0,20 m và plane, voxel sweep cố định ground 0,10 m.

| Sweep | Mức (m) | Mean non-ground | Mean cluster | Mean nearest (m) | p50 / p95 (ms) |
|---|---:|---:|---:|---:|---:|
| ground | 0.1 | 4781.8 | 16.6 | 1.740 | 48.41 / 77.00 |
| ground | 0.2 | 4374.2 | 16.8 | 2.454 | 49.19 / 79.08 |
| ground | 0.3 | 4145.0 | 16.0 | 2.751 | 45.37 / 82.79 |
| voxel | 0.1 | 11080.0 | 19.6 | 1.649 | 304.41 / 483.15 |
| voxel | 0.2 | 4781.8 | 16.6 | 1.740 | 99.50 / 160.20 |
| voxel | 0.4 | 1668.6 | 20.6 | 2.669 | 51.24 / 74.41 |

![Sweep hai tham số](../results/figures/obstacle_sweep.png)

![Demo từng bước frame 000019](../results/figures/demo_000019.png)

CSV [từng frame/config](../results/obstacle_sweep.csv), [tổng hợp](../results/obstacle_summary.csv), [kích thước từng cluster](../results/sweep_clusters.csv), [600 lượt latency](../results/latency_samples.csv). Warm-up bỏ 1 lượt, đo 20 lượt/frame/config; p50/p95 trong bảng pooled trên 100 lượt/config. CPU i5-10300H, Windows, Open3D 0.20/1 thread. Ground latency **không gồm fit plane tham chiếu**, voxel latency **có fit**; cả hai bỏ I/O/vẽ ảnh, không so tốc độ chéo hai sweep. Nearest là tới AABB dự đoán, không phải ground truth.

Nguồn: KITTI Vision Benchmark Suite. 30/30 hình học frame/config khớp chính xác khi chạy mới; latency dao động theo máy/tải. Chi tiết [CP3](CP3.md).

## 3. Failure case

Nêu khi nào hệ thống hoặc phương pháp fail, vì sao fail, và liên hệ tới lớp nào trong 6 lớp debug: I/O, Geometry, Time, Preprocess, Model, Metric.

![failure](../results/figures/fail_[ĐIỀN].png)

[ĐIỀN]

## 4. Khuyến nghị nếu triển khai thật

Use-case cụ thể (ADAS / robot / drone), trade-off và bước tiếp theo.

[ĐIỀN]

## 5. Cách chạy lại

Từ gốc repo, Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m unittest discover -s src -p "test_*.py"
.\.venv\Scripts\python.exe -m src.experiments demo
.\.venv\Scripts\python.exe -m src.benchmark
.\.venv\Scripts\python.exe -m src.verify_geometry
.\.venv\Scripts\python.exe -m src.experiments demo --data-root data/synthetic --frames 000000 --out results/synthetic_debug
```

`python -m src.experiments --help` giải thích tham số. Benchmark cần vài phút; failure sẽ bổ sung ở CP4.

## 6. Khai báo sử dụng AI

Ghi rõ đã dùng công cụ AI nào, dùng vào việc gì, và bạn đã tự kiểm chứng kết quả đó bằng cách nào. Nếu không dùng AI, ghi "Không sử dụng". Xem quy định ở `RULES.md` mục 2.

| Công cụ | Dùng cho việc gì | Bạn đã kiểm chứng thế nào |
|---|---|---|
| ChatGPT / Codex | Chuẩn bị CP0–CP1; viết pipeline, test, demo và benchmark CP2–CP3 | Các lệnh được chạy thật; kết quả nằm trong `results/data_health.csv`, `results/data_health_kitti.csv`, `CP0.md`, `CP1.md` và `CP2.md`. Học viên cần tự xem và kiểm chứng trước khi nộp. |
