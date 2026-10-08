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

> **Tiến độ:** CP2 đã chạy baseline trên 5 frame KITTI. Xem [CP0](CP0.md), [CP1](CP1.md), [CP2](CP2.md). Benchmark và failure sẽ hoàn thiện ở CP3–CP4.

## 1. Claim

**Giả thuyết CP1, chưa được kiểm chứng:** trên 5 frame KITTI đã chọn, trong ROI LiDAR `x ∈ [0,30] m, y ∈ [-10,10] m, z ∈ [-3,3] m`, tăng ngưỡng khoảng cách tách mặt đất từ **0,10 lên 0,30 m**, giữ voxel **0,20 m** và cùng mặt phẳng ground, làm giảm **ít nhất 10% trung bình số điểm non-ground** so với ngưỡng 0,10 m.

Đo ở ba ngưỡng `0,10 / 0,20 / 0,30 m`; fit RANSAC một lần mỗi frame rồi giữ mặt phẳng cố định trong sweep để tách riêng tác động của ngưỡng. Sweep voxel riêng `0,10 / 0,20 / 0,40 m` với ngưỡng ground 0,10 m; DBSCAN `eps=0,60 m`, `min_points=10`, seed 42.

Metric bổ sung: số cluster, kích thước AABB, khoảng cách ngang tới AABB gần nhất, latency p50/p95 (bỏ warm-up, ≥20 lượt). Điểm non-ground giảm chưa chứng minh bỏ sót vật cản; cần ảnh và phân tích CP4. Chi tiết metric/cấu hình trong [CP1](CP1.md).

## 2. Evidence

Baseline voxel 0,20 m, ground 0,10 m, DBSCAN eps 0,60 m/min_points 10, seed 42. Chi tiết [baseline.csv](../results/baseline.csv), mọi AABB trong [baseline_clusters.csv](../results/baseline_clusters.csv).

| Frame KITTI | Điểm ROI → voxel → non-ground | Cluster | Nearest AABB XY (m) |
|---|---|---:|---:|
| 000001 | 47839 → 8887 → 5364 | 7 | 2,267 |
| 000011 | 52222 → 8031 → 4077 | 22 | 1,558 |
| 000019 | 49770 → 6991 → 4092 | 11 | 0,405 |
| 000025 | 52511 → 9111 → 7386 | 15 | 2,021 |
| 000049 | 41301 → 5537 → 3048 | 29 | 2,449 |

![Demo từng bước frame 000019](../results/figures/demo_000019.png)

Nguồn: KITTI Vision Benchmark Suite. Nearest là khoảng cách tới box dự đoán, chưa xác nhận vật cản thật; mặt đất còn sót và cluster nhập có thể gây sai.

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
.\.venv\Scripts\python.exe -m pip install -r requirements.txt "open3d>=0.18"
.\.venv\Scripts\python.exe -m unittest discover -s src -p "test_*.py"
.\.venv\Scripts\python.exe -m src.experiments demo
.\.venv\Scripts\python.exe -m src.experiments demo --data-root data/synthetic --frames 000000 --out results/synthetic_debug
```

`python -m src.experiments --help` giải thích tham số. Benchmark/failure bổ sung tại CP3–CP4.

## 6. Khai báo sử dụng AI

Ghi rõ đã dùng công cụ AI nào, dùng vào việc gì, và bạn đã tự kiểm chứng kết quả đó bằng cách nào. Nếu không dùng AI, ghi "Không sử dụng". Xem quy định ở `RULES.md` mục 2.

| Công cụ | Dùng cho việc gì | Bạn đã kiểm chứng thế nào |
|---|---|---|
| ChatGPT / Codex | Chuẩn bị CP0–CP1; viết pipeline, test và ảnh demo CP2 | Các lệnh được chạy thật; kết quả nằm trong `results/data_health.csv`, `results/data_health_kitti.csv`, `CP0.md`, `CP1.md` và `CP2.md`. Học viên cần tự xem và kiểm chứng trước khi nộp. |
