# Visual Bible Kit — kiểm tra kỹ thuật và nghiệm thu thị giác

Cập nhật: 2026-11-17. Pack: `vietnamese-daily@3.1.1`.

## 1. Kiểm tra kỹ thuật đã thực hiện

Lệnh từ repository root:

```bash
python3 -m unittest discover -s skills/directing-stickman-videos/tests -p test_visual_bible_kit.py -v
node skills/directing-stickman-videos/scripts/autopilot.mjs kit audit --pack vietnamese-daily
node skills/directing-stickman-videos/scripts/autopilot.mjs kit check --project skills/directing-stickman-videos/examples/benchmark-sequence-6shot.json
node skills/directing-stickman-videos/scripts/autopilot.mjs kit compile --project skills/directing-stickman-videos/examples/project-benchmark-2shot.json --shot S01 --draft --output /tmp/visual-shot-S01.json
```

Kết quả lần chạy hiện tại:

- **38/38 test Visual Bible pass.** Log: [visual-bible-automated.txt](visual-bible-automated.txt).
- Audit: 21 thực thể, 12/12 ảnh ref tồn tại và hash khớp; không có lỗi schema hoặc xung đột được khai báo. Trạng thái draft của ENS và các thiết kế chưa có ref vẫn được giữ, không phải đã nghiệm thu.
- Hai benchmark đã chuyển sang `op/time_s`, state vật lý chuẩn hóa và lockfile/snapshot thực tế. Chuỗi 6 shot pass linter; snapshot được dùng chung theo hash và có cả JSON lẫn ảnh.
- CLI Node xuất thành công gói JSON preview gồm prompt và manifest attachment; thông tin đường dẫn/hash/vai trò ảnh nằm riêng với chuỗi gửi model.

Phạm vi hồi quy đã kiểm tra: thiếu lock/dependency, revision sai, sửa mô tả kit sau lock, sửa snapshot/ảnh snapshot, thiếu required ref, ID không hợp lệ, hash sai, quota/deduplicate/ENS, dependency draft/deprecated, lighting buổi tối, unknown op/actor/time, nhấc sai vị trí, sự kiện không tạo trạng thái cuối đã khai báo, fill_fraction, tay/người giữ, handover/putdown, capacity anchor và continuity qua cut/jump.

Test production happy path dùng fixture nhỏ và capability **giả lập** trong thư mục tạm. Nó chứng minh gate hoạt động theo dữ liệu khai báo, không xác minh năng lực dịch vụ AI thực tế.

### Kiểm tra Node rộng hơn

Đã chạy thêm `b-style-workflow.test.mjs` và `b-style-reference-cli.test.mjs`: **13 pass / 29 fail**. Các failure gồm thiếu dependency `@napi-rs/canvas` và lỗi parser `--ratio` của workflow hiện hữu. Đã đối chiếu CLI tại Git HEAD: cả HEAD và bản hiện tại đều trả `16:9` khi yêu cầu workflow B1 `--ratio 9:16`. Đây là hạn chế ngoài phần Visual Bible; không ghi cả bộ Node là pass. Chưa sửa renderer hoặc workflow style khác trong thay đổi này.

## 2. Nghiệm thu ảnh/video sinh thực tế — CHƯA THỰC HIỆN

Chưa có bộ ảnh/video đầu ra cùng bằng chứng kiểm tra cho 6 shot trong thay đổi này. Các PNG trong kit/snapshot là **ảnh tham chiếu đầu vào**, không phải kết quả benchmark.

| Shot | Cần kiểm tra trên sản phẩm sinh ra | Trạng thái |
| :--- | :--- | :--- |
| S01 toàn thân | Tỷ lệ An/Bố, thân trắng, chân nét đơn | Chưa nghiệm thu |
| S02 cận mặt | Tóc, nếp nhăn, mắt và phong cách | Chưa nghiệm thu |
| S03 đổi góc | Hình khối, chi, tỷ lệ qua góc nhìn | Chưa nghiệm thu |
| S04 nhấc tách | Tiếp xúc tay, cup_01 rời vị trí cũ, không nhân bản | Chưa nghiệm thu |
| S05 cảnh nhóm | Đúng người, không tráo tạo hình, giữ cup_01; hiện dùng ảnh đơn, ENS chưa có ảnh | Chưa nghiệm thu |
| S06 quay lại phòng | Cấu trúc phòng, nhấp trà rồi đặt tách, lượng trà còn lại | Chưa nghiệm thu |

Chỉ ghi đạt khi có file đầu ra cụ thể, target/model thực tế, prompt/manifest đã dùng và ghi nhận đánh giá. Cảnh nhóm với hai ảnh đơn không chứng minh chất lượng của ENS. Không suy ra tính nhất quán hình ảnh từ việc prompt chứa đầy đủ anchor hoặc linter pass.

## 3. Trạng thái sử dụng

Các lỗi kỹ thuật đã xác nhận trong review đã được sửa và có test hồi quy. Có thể dùng kit để biên soạn và kiểm tra prompt preview cục bộ. **Chưa chứng nhận Production Ready hoặc giữ hình qua model thực tế.** Hai benchmark dùng target giả lập chưa verified, nên production compile phải từ chối. Cần chọn/xác minh provider/model/mode thực tế và hoàn thành mục 2; ảnh ENS là công việc riêng nếu cần dùng.

Báo cáo này thay thế các kết luận “ĐẠT CHUẨN”/“Production Ready” trước đó vốn chỉ dựa vào prompt và linter.
