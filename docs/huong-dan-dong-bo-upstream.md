# Hướng Dẫn Đồng Bộ Cập Nhật Từ Upstream (kaomei) Không Ảnh Hưởng Code Tự Làm

Tài liệu này hướng dẫn cách lấy các bản cập nhật, cải tiến và bản vá mới nhất từ kho lưu trữ gốc **[kaomei/stickman-video-director](https://github.com/kaomei/stickman-video-director)** về kho cục bộ của bạn (`origin/main`) mà **không làm mất** các tài liệu tiếng Việt, công cụ tìm kiếm SFX cục bộ (`sfx-catalog-local.py`), cấu hình riêng và các dự án video trong thư mục `projects/`.

---

## 1. Cấu trúc Remote trong Git

Hiện tại dự án có 2 remote chính:
- **`origin`**: Kho cá nhân của bạn trên GitHub (`phongsun01/stickman-video-director`).
- **`upstream`**: Kho gốc của tác giả (`kaomei/stickman-video-director`).

Kiểm tra cấu hình remote bằng lệnh:
```bash
git remote -v
```
Nếu chưa có `upstream`, thêm bằng lệnh:
```bash
git remote add upstream https://github.com/kaomei/stickman-video-director.git
```

---

## 2. Quy trình chuẩn 6 bước khi có bản mới

### Bước 1: Lưu trữ trạng thái làm việc (Clean Working Tree)
Trước khi kéo code mới, đảm bảo thư mục làm việc không có thay đổi dở dang chưa được commit:
```bash
git status
```
Nếu có chỉnh sửa cần lưu:
```bash
git add .
git commit -m "feat/chore: lưu các chỉnh sửa cục bộ trước khi cập nhật upstream"
```
*(Hoặc dùng `git stash` nếu chưa muốn commit ngay).*

### Bước 2: Lấy dữ liệu mới nhất từ tác giả gốc (Fetch Upstream)
```bash
git fetch upstream
```
Lệnh này chỉ tải các commit và tag mới về máy (ví dụ `upstream/main`), chưa làm thay đổi bất kỳ file nào trong thư mục làm việc của bạn.

### Bước 3: Xem trước các cải tiến và commit mới
Để biết tác giả vừa cập nhật những gì:
```bash
# Xem danh sách commit mới
git log --oneline main..upstream/main

# Xem danh sách các file được tác giả thêm mới hoặc chỉnh sửa
git diff --stat main..upstream/main
```

### Bước 4: Hợp nhất vào nhánh chính (Merge Upstream)
Thực hiện merge các thay đổi từ `upstream/main` vào nhánh `main` của bạn:
```bash
git merge upstream/main
```

### Bước 5: Xử lý xung đột (Merge Conflict) nếu có
Hầu hết các file mới (như asset rig mới `jensen-v13`, font `Nunito.ttf`, script kiểm duyệt `b-style-quality.mjs`...) sẽ được tự động tích hợp trơn tru.

Nếu có conflict, thông thường chỉ xảy ra ở 2 file điều phối trung tâm:
1. `skills/directing-stickman-videos/SKILL.md`:
   - **Quy tắc**: Giữ nguyên toàn bộ các tính năng/quy chuẩn mới của upstream (B4 Nunito, B5 Jensen, Quality Gates...) và giữ lại khối mục **Local extensions on this fork** (tiếng Việt, local SFX library 585 âm thanh, cinematic motion toolkit).
2. `skills/directing-stickman-videos/scripts/autopilot.mjs`:
   - **Quy tắc**: Giữ lại bộ cờ CLI mở rộng `--seconds`, `--style`, cảnh báo thời lượng tiếng Việt và kết hợp các hàm kiểm tra mở đầu `opening_visual` của upstream.

Sau khi mở file và giữ lại các đoạn code mong muốn, đánh dấu đã giải quyết và hoàn tất merge:
```bash
git add skills/directing-stickman-videos/SKILL.md skills/directing-stickman-videos/scripts/autopilot.mjs
git commit -m "Merge upstream/main: cập nhật tính năng mới và giữ trọn vẹn tiện ích tiếng Việt"
```

> **Mẹo khẩn cấp**: Nếu quá trình merge bị rối hoặc muốn quay lại trạng thái ban đầu:
> ```bash
> git merge --abort
> ```

### Bước 6: Chạy kiểm thử xác nhận (Verification)
Sau khi merge xong, kiểm tra lại để đảm bảo cả tính năng gốc lẫn tính năng tự làm đều hoạt động ổn định:
```bash
# 1. Kiểm tra bộ công cụ SFX tiếng Việt:
py tests/verify-sfx-catalog-local.py

# 2. Kiểm thử bộ test tự động của Skill:
node --test skills/directing-stickman-videos/tests/*.mjs
```

---

## 3. Cách bảo vệ các thư mục tự làm & dữ liệu dự án

1. **Thư mục `projects/`**:
   - Đã được đưa vào file `.gitignore`. Toàn bộ các kịch bản, ảnh render và video bạn tạo ra trong `projects/` sẽ nằm an toàn trên ổ đĩa nội bộ, không bao giờ bị đẩy lên GitHub cá nhân hay bị upstream ghi đè.
2. **Thư mục `skills/.../examples/b1/output/`**:
   - Cũng đã được đưa vào `.gitignore` để không bị vướng rác build khi chạy lệnh test preview.
3. **Bộ tài liệu tiếng Việt trong `docs/`**:
   - Do phía upstream không có thư mục `docs/ke-hoach-tich-hop-sfx-va-motion.md`, các file này thuộc vùng tên riêng độc lập, upstream sẽ **không bao giờ ghi đè hay xóa mất**.
4. **Script SFX `skills/.../scripts/sfx-catalog-local.py`**:
   - File này có tên riêng biệt so với cấu trúc file của tác giả gốc nên sẽ luôn được bảo toàn trọn vẹn qua các đợt pull/merge.

---

## 4. Đẩy bản cập nhật đã hợp nhất lên GitHub của bạn
Sau khi kiểm tra mọi thứ hoạt động hoàn hảo:
```bash
git push origin main
```
Toàn bộ commit mới từ upstream và các tính năng nội bộ của bạn sẽ được đồng bộ lên repo GitHub cá nhân của bạn.
