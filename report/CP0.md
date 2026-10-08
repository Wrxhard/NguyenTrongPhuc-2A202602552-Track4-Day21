# CP0 — Chuẩn bị môi trường và kiểm tra dữ liệu

- Học viên: Nguyễn Trọng Phúc — 2A202602552 — Track 4, VinUni AI20K. Mã lớp cụ thể chưa được cung cấp.
- Topic đã chọn: **D — Robot/drone obstacle**.
- Repo: https://github.com/Wrxhard/NguyenTrongPhuc-2A202602552-Track4-Day21
- Ngày thực hiện: 08/10/2026 (UTC+7). Không ghi lùi ngày cho checkpoint.

## Yêu cầu đã đọc

Đã đọc README, RULES, RUBRIC, SUBMISSION, TOPICS, CHECKPOINTS và data/README. Topic D cần voxel downsample → RANSAC ground removal → DBSCAN → bounding box; mức Good sweep hai tham số, mỗi sweep chỉ thay một yếu tố. Benchmark phải có ít nhất ba mức, seed cố định, latency bỏ lượt đầu và đo ít nhất 20 lượt (p50/p95). Failure phải có ảnh `fail_*.png`, nguyên nhân và lớp debug.

Code tự viết đặt trong `src/`; dữ liệu gốc không được sửa. CP2 topic D được bỏ qua hai TODO projection khi không dùng camera. Mỗi checkpoint cập nhật report, commit dạng `CPx: ...` rồi push theo yêu cầu học viên.

## Môi trường đã kiểm tra

Python 3.13.6 trong `.venv`; NumPy 2.5.3, OpenCV 5.0.0, Matplotlib 3.11.2, pandas 3.0.6, Open3D 0.20.0. `pip check` trả về `No broken requirements found.` Open3D smoke test với bốn điểm trên z=0: RANSAC tìm mặt phẳng `[0, 0, 1, 0]` có bốn inlier; DBSCAN trả cùng cluster 0; voxel giữ bốn điểm; AABB có extent `[1, 1, 0]`. Đây là kiểm tra thư viện, chưa phải demo trên dataset.

## Kết quả kiểm tra dữ liệu

| Kiểm tra | Kết quả chạy thật |
|---|---|
| KITTI mini | PASS — 80/80 file đúng, 55,0 MB |
| nuScenes mini subset | PASS — 173/173 file đúng, 74,0 MB |
| Synthetic data health | 5 frame: 000000–000004; đã tạo `results/data_health.csv` |

| Frame | Số điểm | Điểm không hợp lệ (%) | Range p95 (m) |
|---|---:|---:|---:|
| 000000 | 23953 | 0,0960 | 57,76 |
| 000001 | 23781 | 0,0967 | 58,34 |
| 000002 | 23790 | 0,0967 | 58,21 |
| 000003 | 22063 | 0,0997 | 58,34 |
| 000004 | 23760 | 0,0968 | 58,56 |

Các frame đều có điểm lỗi; pipeline cần lọc điểm không hữu hạn. CP0 chỉ mô tả thống kê quan sát được, chưa kết luận nguyên nhân bất thường và chưa có kết quả phát hiện vật cản.

## Cách chạy lại

Từ thư mục gốc repo trên Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install "open3d>=0.18"
.\.venv\Scripts\python.exe tools/verify_data.py --data-root data/kitti_mini
.\.venv\Scripts\python.exe tools/verify_data.py --data-root data/nuscenes_mini_subset
.\.venv\Scripts\python.exe -m starter.data_health --data-root data/synthetic
```

## Nộp bài và tiến độ tiếp theo

CP1 sẽ chọn danh sách frame, vùng xử lý, metric và claim có thể kiểm chứng. CP2 mới chạy pipeline và tạo ảnh demo; CP3 benchmark; CP4 failure; CP5 kiểm tra bản nộp; CP6 chuẩn bị nội dung trình bày, việc tập nói và demo do học viên thực hiện. Bài chưa sẵn sàng nộp ở CP0.

Theo tài liệu, 08/10/2026 là ngày nộp muộn bị trừ 10 điểm; hạn chót 23:59 (UTC+7). Ngoài push, LMS cần link repo và commit hash cuối; thời điểm muộn hơn trong hai mốc push/LMS được dùng để tính nộp bài.

AI: ChatGPT / Codex hỗ trợ đọc yêu cầu, chạy kiểm tra và soạn báo cáo. Số liệu lấy từ các lệnh chạy thật và CSV, không tự đặt số. Học viên cần tự kiểm chứng và giải thích được kết quả trước khi nộp.
