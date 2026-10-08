# Báo cáo Day 6: Phát hiện vật cản cho robot/drone

> Thay **mọi** ô có chữ ĐIỀN nằm trong ngoặc vuông bằng nội dung của bạn, xoá luôn cả dấu ngoặc vuông. Lệnh `python tools/check_submission.py` sẽ báo FAIL nếu còn sót bất kỳ chỗ nào.

- **Họ tên:** Nguyễn Trọng Phúc
- **MSSV:** 2A202602552
- **Lớp:** Track 4 — VinUni AI20K (chưa cung cấp mã lớp cụ thể)
- **Link repo:** https://github.com/Wrxhard/NguyenTrongPhuc-2A202602552-Track4-Day21
- **Topic:** D — Robot/drone obstacle
- **Dataset:** [ĐIỀN một hoặc nhiều trong: data/synthetic, data/kitti_mini, data/nuscenes_mini_subset, log riêng]
- **Các frame đã dùng:** [ĐIỀN danh sách frame id, ví dụ 000011, 000049 hoặc scene-0103_010]

> Hãy viết ngắn: mỗi mục từ 3 đến 8 dòng, ưu tiên số liệu và hình ảnh.

> **Tiến độ:** CP0 đã qua kiểm tra môi trường và dữ liệu. Đây là báo cáo theo checkpoint, chưa phải bản nộp cuối; các mục thí nghiệm sẽ được điền tại CP1–CP5. Xem [báo cáo CP0](CP0.md).

## 1. Claim

Một câu khẳng định kỹ thuật có thể kiểm chứng. Ví dụ: *"Lệch yaw 1° làm 12% điểm LiDAR rơi ra khỏi vật thể ở 30 m, phát hiện được bằng edge-alignment score với ngưỡng X."*

[ĐIỀN]

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
| ChatGPT / Codex | Đọc yêu cầu, chuẩn bị môi trường, chạy kiểm tra CP0 và cập nhật báo cáo | Các lệnh được chạy thật; kết quả nằm trong `results/data_health.csv` và `CP0.md`. Học viên cần tự xem và kiểm chứng trước khi nộp. |
