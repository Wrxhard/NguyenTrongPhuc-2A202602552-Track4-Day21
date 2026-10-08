# CP5 — Báo cáo và kiểm tra bản nộp

## Kết quả kiểm tra

- REPORT chính đủ6 mục, thông tin/topic/dataset/frame/claim đã điền, không còn placeholder; mọi link ảnh/CSV nội bộ tồn tại.
- Suite cuối **15/15 PASS**; biên ROI/NaN, plane normalization, empty/noise, CSV empty, GT yaw/bottom-center/translation, occupancy và KITTI RANSAC repeat có test.
- Checkout sạch của commit d94e926: chạy lại toàn bộ benchmark6 cấu hình×5 frame×20 lượt. **30/30 dòng khớp mọi cột không phải latency** với bản đã lưu, gồm hash và metric; latency được đo lại, không ép giống. Checkout dùng cùng .venv đã cài và khóa phiên bản, chưa thử cài trên máy hoàn toàn mới.
- Reviewer độc lập đọc code và đối chiếu:30 metric rows,600 timing rows,531 cluster rows,6 summary rows; xác nhận GT transform, mật độ DBSCAN và scope timing.
- Hai lỗi biên được test FAIL trước sửa rồi PASS: tilt từ plane truyền vào chưa normalize; CSV cluster rỗng. CLI demo all-noise chạy thành công với min_points100000, xuất header-only cluster CSV, nearest=NA/no_cluster=True.
- `git diff bce73ad --stat -- data starter` rỗng: dữ liệu/starter gốc không bị sửa. Không thêm raw data/model/secret; lock môi trường requirements-lock.txt.
- `python tools/check_submission.py`: **10/10 PASS**, cuối dòng **KẾT QUẢ: SẴN SÀNG NỘP**. Log tóm tắt [verification.json](../results/verification.json).

## Đối chiếu rubric

| Sản phẩm | Minh chứng |
|---|---|
| Claim | REPORT mục1: ground threshold tăng, non-ground giảm13,32% |
| Demo chạy thật | 5 ảnh demo trong results/figures, baseline CSV và kích thước cluster |
| Benchmark | 2 sweep độc lập×3 mức,30 dòng frame/config,600 timing samples,summary/plot |
| Failure | fail_01_dbscan_pedestrian.png, density/GT CSV; lỗi Preprocess/Metric |
| Khuyến nghị | REPORT mục4: vật thấp, noise/core, ground cục bộ, unknown occupancy, drone3D |
| Khai báo AI | REPORT mục6: toàn bộ phạm vi hỗ trợ và phân biệt kiểm chứng Codex/học viên |
| Mức Advanced D | Occupancy BEV2D và CSV occupied candidates |
| B3/B4 có bằng chứng | p50/p95 đo đúng cách và CLI tái sử dụng có --help; điểm do giảng viên quyết định |

## Quyết định kỹ thuật khi review

Reviewer gọi hai lỗi biên là Minor vì default evidence không bị ảnh hưởng. Tôi xử lý như lỗi cần sửa: API nhận scaled plane phải có metric đúng, và dataset không có cluster phải xuất được CSV. Đổi phạm vi hẹp, không đổi thuật toán/frame/config của thí nghiệm; nếu nhận định scope sai thì chi phí chỉ là hai sửa nhỏ đã có test. Không bỏ lại lỗi đã phát hiện.

Ground sweep cache fit plane, voxel sweep fit lại; chỉ so latency trong cùng sweep, đã ghi rõ trong REPORT/figure/config. Giữ kết quả13,32% như claim có điều kiện, không gọi là recall/safety. Các mục reviewer chưa đánh giá: cài thư viện máy mới, layout ảnh, triển khai thực tế, CP5/CP6; tôi kiểm tra ảnh và bản checkout, còn triển khai/học viên nói/LMS là việc ngoài minh chứng repo.

## Nộp LMS

Repo https://github.com/Wrxhard/NguyenTrongPhuc-2A202602552-Track4-Day21. Sau CP6 dùng commit hash cuối đã push để nộp cùng link trên LMS Day6 Lab. Chưa nộp LMS tự động. Ngày thực hiện08/10/2026, hạn nộp muộn23:59UTC+7 theo SUBMISSION/RULES; không ghi lùi ngày hoặc force-push. CP6 sẽ cung cấp nội dung trình bày, không giả lập việc học viên đã nói trước lớp.

## Kiểm tra bổ sung bản sau sửa

Trong CP6 đã clone sạch b18fb27 và chạy lại:15/15 test,30/30 geometry,7 PNG và4 CSV minh chứng giống hệt; check_submission10/10 PASS. Xem CP6 và verification.json.
