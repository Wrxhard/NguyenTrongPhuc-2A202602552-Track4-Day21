# CP6 — Chuẩn bị trình bày 3 phút

Đã chuẩn bị nội dung và minh chứng để học viên trình bày. **Chưa xác nhận học viên đã tập nói hoặc demo trước lớp.** Khung thời gian dưới đây là dự kiến, cần bấm giờ khi tập thật.

## Kịch bản và ảnh mở sẵn

### 0:00–0:25 — Câu hỏi

Em làm topic D, phát hiện vật cản cho robot bằng point cloud, không deep learning. Em muốn biết tham số ground và voxel ảnh hưởng số điểm, cluster và tốc độ như thế nào. Em dùng năm frame KITTI có người đi bộ, cyclist, vật gần và che khuất; vùng xử lý phía trước30m, ngang±10m.

### 0:25–0:55 — Pipeline

Mở [ảnh demo000019](../results/figures/demo_000019.png).

Em lọc điểm lỗi, crop ROI, voxel downsample, fit ground bằng RANSAC rồi dùng DBSCAN và AABB. Ví dụ frame000019 từ49770 điểm ROI xuống6991 voxel và4092 non-ground, được11 cluster. Điểm LiDAR có hệ trục x trước, y trái, z lên; box xuất theo mét. Em giữ seed42, Open3D một thread, RANSAC probability1 và1000 iterations để tái lập.

### 0:55–1:35 — Claim và benchmark

Mở [plot sweep](../results/figures/obstacle_sweep.png).

Em sweep ground0,10/0,20/0,30m trên cùng plane, giữ voxel0,20m. Trung bình non-ground giảm4781,8 xuống4145,0, tức13,32%, ủng hộ claim nháp giảm ít nhất10%. Đây là giảm điểm, không phải tăng recall. Sweep voxel riêng0,10/0,20/0,40m; số cluster không đơn điệu. Trên CPU i5-10300H, voxel0,20 có latency đầy đủ p50≈99,50ms vàp95≈160,20ms. Em bỏ warm-up, đo20 lần mỗi frame/config. Ground sweep cache plane nên latency khác scope, không so chéo.

### 1:35–2:20 — Failure

Mở [ảnh failure](../results/figures/fail_01_dbscan_pedestrian.png).

Cùng43 điểm non-ground nằm trong GT box pedestrian frame000011, giảm eps0,60 xuống0,20m khiến tất cả43 điểm thành noise. Tại eps0,20 mỗi điểm có tối đa7 hàng xóm, dưới min_points10; object có43 điểm tổng vẫn không đủ mật độ cục bộ. Ở eps0,30 còn11 core point và9 noise, đã bị phân mảnh. Lỗi thuộc Preprocess, và Metric nếu chỉ nhìn tổng cluster. Em kiểm tra GT đúng camera bottom-center/yaw rồi đổi hệ tọa độ, không giả định label nằm trong LiDAR.

### 2:20–3:00 — Triển khai và kết luận

Mở [occupancy](../results/figures/occupancy_000019.png).

Robot nên log ground fit, noise/core theo range, cluster size, nearest vàp95. Em giữ cả điểm noise trong occupancy cảnh báo: có1239 ô ở cell0,20m trên frame000019. Ô không có bằng chứng vẫn là unknown. Cần hiệu chỉnh với GT của kho, vật thấp và nền dốc; một plane toàn cảnh chưa đủ. Drone cần occupancy3D vì BEV làm mất chiều cao. Em đã kiểm tra tái lập hình học và có failure chạy thật; chưa khẳng định an toàn triển khai.

## Hỏi đáp 1 phút

| Câu hỏi | Trả lời ngắn |
|---|---|
| Claim sai khi nào? | Dataset/ROI/voxel/plane khác, hoặc mức giảm dưới10%; đây là kết quả5 frame, không quy luật cho mọi scene. Ground sai có thể loại vật thật dù count giảm đẹp. |
| Vì sao ground sweep cố định plane? | Nếu vừa đổi threshold vừa fit lại plane thì không tách được tác động của phân loại ground; voxel sweep fit lại vì thay downsample là điều đang nghiên cứu. |
| Số cluster nhiều hơn có tốt hơn? | Không: có thể phân mảnh/ground sót; cần matching GT hoặc phân tích failure. Nearest AABB cũng không phải GT clearance. |
| Tham số nào làm mất vật thấp? | Ground threshold lớn có thể gộp vật thấp vào slab ground; voxel lớn có thể giảm điểm, sau đó DBSCAN eps/min_points làm vật nhỏ thành noise. Chưa có thí nghiệm pallet riêng nên không gán ngưỡng tối ưu cho pallet. |
| Đổi sang nuScenes32 beam? | Chưa chạy pipeline benchmark trên nuScenes. Trục LiDAR nuScenes x phải/y trước khác KITTI; phải chuẩn hóa ROI, sau đó kiểm tra lại density/eps/min_points và ground, không dùng nguyên kết quả này. |
| Vì sao eps nhỏ mất người dù43≥10? | min_points áp dụng số hàng xóm trong bán kính eps, không phải tổng điểm của object; case eps0,20 max7, không có core và tất cảnoise. |
| Tăng eps có giải quyết hết? | Không: có thể nhập nhiều vật/ground vào một cluster. Cần kiểm tra boxsize, điểm bridge, matchingGT hoặc tham số thích nghi range. |
| Không có cluster thì robot đi được? | Không. Có thể toàn bộ điểm thành noise, sensor bị hỏng hoặc ground fit sai; no_cluster/NA phải là trạng thái cần kiểm tra. |
| Có dùng AI không? | Có: Codex hỗ trợ toàn bộ triển khai, test và report; khai báo mục6. Dữ liệu/ảnh được tạo từ code chạy thật. Học viên phải tự kiểm chứng và giải thích được. |

## Mở demo trong30 giây

Mở REPORT.md, obstacle_sweep.png, fail_01_dbscan_pedestrian.png và demo_000019.png trước khi được gọi. Dùng ảnh đã lưu để tránh chờ benchmark vài phút. Nếu cần chạy live, từ gốc repo:

```powershell
.\.venv\Scripts\python.exe -m src.experiments demo --frames 000019 --out .venv/live_demo
.\.venv\Scripts\python.exe -m src.failure --out .venv/live_failure
```

Lưu live output trong .venv để không ghi đè baseline5 frame đã nộp. Tập nói thật một lần bằng đồng hồ; kiểm tra có thể giải thích số liệu trong mục2 và công thức claim.

## Xác minh sau CP5

Checkout sạch của b18fb27:15/15 tests PASS,30/30 geometry hash khớp; demo/failure chạy lại cho7/7 PNG và4 CSV (baseline_clusters, failure_density, failure_gt_membership, occupancy_cells) giống hệt bản đã lưu. check_submission trên checkout sạch10/10 PASS. Môi trường dùng cùng .venv đã khóa, không gọi là thử cài trên máy mới.

## Nộp LMS

Dùng link repo https://github.com/Wrxhard/NguyenTrongPhuc-2A202602552-Track4-Day21 và commit hash cuối sau CP6:

```powershell
git rev-parse HEAD
```

Repo đã được push theo từng checkpoint. **Việc nộp LMS, tự tập nói và trình bày trước lớp do học viên thực hiện; không ghi là đã làm thay.**
