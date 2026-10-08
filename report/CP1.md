# CP1 — Chọn topic, dataset và claim

Học viên: Nguyễn Trọng Phúc — 2A202602552. Ngày thực hiện: 08/10/2026 (UTC+7).

## Phạm vi

Topic **D — Robot/drone obstacle**, dùng CPU/Open3D, không deep learning. Mục tiêu mức Good: voxel downsample → RANSAC ground removal → DBSCAN → AABB, ảnh từng bước và hai sweep tham số độc lập. KITTI dùng hệ trục LiDAR x trước, y trái, z lên; không dùng camera nên không cần sửa TODO projection. Dữ liệu đường phố dùng để nghiên cứu tham số cho robot mặt đất; không coi kết quả là xác nhận an toàn cho drone hoặc robot kho.

## Dataset và frame

Synthetic `000000–000004` dùng kiểm tra dữ liệu/debug. KITTI dùng 5 frame sau cho baseline và benchmark, chọn trước khi xem kết quả pipeline theo tình huống mô tả trong `data/README.md`:

| Frame | Tình huống theo tài liệu dataset | Điểm gốc | Điểm lỗi | Điểm trong ROI |
|---|---|---:|---:|---:|
| 000001 | Cyclist | 120268 | 0 | 47839 |
| 000011 | Nhiều pedestrian | 108004 | 0 | 52222 |
| 000019 | Vật gần dưới 6 m | 115697 | 0 | 49770 |
| 000025 | Vật gần dưới 6 m | 115780 | 0 | 52511 |
| 000049 | Vật bị che khuất | 113691 | 0 | 41301 |

Số điểm được tính từ code đọc dữ liệu chạy thật; ROI sau lọc hữu hạn: x từ 0 đến 30 m, y từ −10 đến 10 m, z từ −3 đến 3 m, gồm cả biên. Đã chạy data health trên cả 20 frame KITTI: không có điểm không hữu hạn, không có azimuth bin rỗng. CSV: [data_health_kitti.csv](../results/data_health_kitti.csv). Synthetic có khoảng 0,10% điểm lỗi (CP0), nên mọi lần chạy vẫn phải lọc hữu hạn trên cả bốn trường. Thống kê này chưa phát hiện lỗi timestamp/calibration hay xác nhận ground đúng.

## Claim nháp

Trên 5 frame trên, tăng ground distance threshold từ 0,10 lên 0,30 m, giữ voxel 0,20 m và cùng mặt phẳng ground, làm giảm ít nhất 10% trung bình số điểm non-ground trong ROI. Đây là giả thuyết có thể bị bác bỏ, không phải số liệu đã đo.

Gọi N_i(t) là số điểm voxel của frame i nằm xa mặt phẳng ground hơn t. Tính trung bình N(t) trên cùng 5 frame, và mức giảm D = 100 × [N(0,10) − N(0,30)] / N(0,10). Claim được ủng hộ khi D ≥ 10%; bác bỏ khi D < 10%; nếu mẫu số bằng 0 hoặc fit ground không hợp lệ, báo không đánh giá được và giải thích, không thay bằng 0%. Đếm trước DBSCAN để không lẫn tác động clustering.

## Cấu hình và cách so sánh

- ROI cố định như trên; cùng 5 frame, seed NumPy/Open3D 42.
- Baseline: voxel 0,20 m; ground threshold 0,10 m; RANSAC ransac_n=3, num_iterations=1000; DBSCAN eps=0,60 m, min_points=10.
- Sweep ground: 0,10 / 0,20 / 0,30 m. Mỗi frame fit mặt phẳng một lần trên voxel 0,20 m ở baseline, giữ hệ số plane trong cả ba mức rồi phân loại bằng khoảng cách chuẩn hóa. Phải kiểm tra ground phù hợp mặt đường; fit sai sẽ ghi failure.
- Sweep voxel: 0,10 / 0,20 / 0,40 m. Ground threshold cố định 0,10 m; DBSCAN giữ nguyên. Mỗi cấu hình voxel fit lại plane với cùng seed; thay đổi fit là tác động kéo theo downsample. Không trộn hai sweep thành so sánh đổi nhiều yếu tố.
- Đếm mọi cluster DBSCAN có label ≥0; label −1 là noise. AABB trong hệ LiDAR, báo kích thước x/y/z theo mét và số điểm mỗi cluster.
- Khoảng cách gần nhất: khoảng cách Euclidean 2D từ gốc LiDAR đến hình chữ nhật AABB trên XY, không phải tới tâm box. Không có cluster thì ghi NA và cờ no_cluster; metric này chưa xét footprint robot hay braking distance.
- Latency pipeline CPU không gồm đọc file và vẽ ảnh: warm-up bỏ lượt đầu, ít nhất 20 lượt, p50/p95; lưu các lượt đo và phần cứng. Thời gian có dao động; số điểm/cluster phải kiểm tra tái lập với seed.

Metric số điểm, số cluster và nearest distance là mô tả pipeline, chưa phải precision/recall vì chưa đối chiếu ground truth. CP4 phải minh họa một trường hợp sai và giải thích lớp debug; ưu tiên kiểm tra mất vật thấp, cluster nhập hoặc bị tách. Không gán failure trước khi chạy code.

## Cách chạy lại kiểm tra CP1

```powershell
.\.venv\Scripts\python.exe -m starter.data_health --data-root data/kitti_mini --out results/data_health_kitti.csv
```

Để kiểm tra số điểm ROI, từ gốc repo chạy Python:

```python
from starter.datasets import load_points
import numpy as np
for fid in ["000001", "000011", "000019", "000025", "000049"]:
    p = load_points("data/kitti_mini", fid)
    finite = np.isfinite(p).all(axis=1)
    q = p[finite]
    roi = ((q[:, 0] >= 0) & (q[:, 0] <= 30)
           & (np.abs(q[:, 1]) <= 10)
           & (q[:, 2] >= -3) & (q[:, 2] <= 3))
    print(fid, len(p), int((~finite).sum()), int(roi.sum()))
```

## Tự kiểm tra checkpoint

- Đã ghi topic D, dataset và danh sách frame trong REPORT chính.
- Claim có đại lượng (trung bình điểm non-ground), điều kiện (ROI/frame/voxel/plane cố định) và ngưỡng (giảm ≥10%).
- Đã xem CSV CP0, chạy data health KITTI và kiểm tra các frame có dữ liệu trong ROI.
- Có hai sweep độc lập, mỗi sweep ba mức; chưa chạy benchmark và chưa kết luận claim đúng.
- Câu tóm tắt: đo điểm non-ground, cluster, kích thước box, nearest distance và latency trên năm frame, sweep ground 0,10/0,20/0,30 m và voxel 0,10/0,20/0,40 m riêng biệt.

AI: ChatGPT / Codex hỗ trợ chọn thiết kế thí nghiệm, soạn claim và chạy kiểm tra dữ liệu. Học viên cần tự đọc, kiểm chứng và giải thích được; các thông số là cấu hình dự kiến, không phải tham số đã tối ưu.
