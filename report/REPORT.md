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

> **Tiến độ:** CP0 đã kiểm tra môi trường; CP1 đã chọn dataset/frame và viết claim nháp. Chưa chạy benchmark vật cản. Xem [CP0](CP0.md) và [CP1](CP1.md); các mục kết quả sẽ hoàn thiện tại CP2–CP5.

## 1. Claim

**Giả thuyết CP1, chưa được kiểm chứng:** trên 5 frame KITTI đã chọn, trong ROI LiDAR `x ∈ [0,30] m, y ∈ [-10,10] m, z ∈ [-3,3] m`, tăng ngưỡng khoảng cách tách mặt đất từ **0,10 lên 0,30 m**, giữ voxel **0,20 m** và cùng mặt phẳng ground, làm giảm **ít nhất 10% trung bình số điểm non-ground** so với ngưỡng 0,10 m.

Đo ở ba ngưỡng `0,10 / 0,20 / 0,30 m`; fit RANSAC một lần mỗi frame rồi giữ mặt phẳng cố định trong sweep để tách riêng tác động của ngưỡng. Sweep voxel riêng `0,10 / 0,20 / 0,40 m` với ngưỡng ground 0,10 m; DBSCAN `eps=0,60 m`, `min_points=10`, seed 42.

Metric bổ sung: số cluster, kích thước AABB, khoảng cách ngang tới AABB gần nhất, latency p50/p95 (bỏ warm-up, ≥20 lượt). Điểm non-ground giảm chưa chứng minh bỏ sót vật cản; cần ảnh và phân tích CP4. Chi tiết metric/cấu hình trong [CP1](CP1.md).

## 2. Evidence

Bảng hoặc plot số liệu, kèm ảnh/video demo. Ghi rõ đường dẫn file trong `results/`.

| Cấu hình / mức perturb | Metric 1 | Metric 2 | Ghi chú |
|---|---|---|---|
| [ĐIỀN] | | | |

![demo](../results/figures/[ĐIỀN].png)

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
[ĐIỀN]
```

## 6. Khai báo sử dụng AI

Ghi rõ đã dùng công cụ AI nào, dùng vào việc gì, và bạn đã tự kiểm chứng kết quả đó bằng cách nào. Nếu không dùng AI, ghi "Không sử dụng". Xem quy định ở `RULES.md` mục 2.

| Công cụ | Dùng cho việc gì | Bạn đã kiểm chứng thế nào |
|---|---|---|
| ChatGPT / Codex | Đọc yêu cầu, chuẩn bị CP0, chọn frame/metric và soạn claim CP1 | Các lệnh được chạy thật; kết quả nằm trong `results/data_health.csv`, `results/data_health_kitti.csv`, `CP0.md` và `CP1.md`. Học viên cần tự xem và kiểm chứng trước khi nộp. |
