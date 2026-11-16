# Bộ Kit đồng bộ nhân vật & bối cảnh — Stickman (v3, 2026-11-16)

Nguồn duy nhất của mọi anchor (nhân vật, địa điểm, đạo cụ) cho series
Sống Đáng Tiền và Chú mèo học… — theo mẫu Garden Kit (Visual Bible,
tối đa 3 ảnh ref/cảnh, from_video).

## Trong gói này
- `kit-stickman.json` — 7 nhân vật, 10 địa điểm, 2 đạo cụ (mã CHAR/LOC/PROP,
  mô tả khóa, đường dẫn ảnh ref, công tắc bật/tắt)
- `kit-stickman.py` — 3 lệnh: `bible` / `refs` / `check`
- 12 ảnh ref hiện có (nằm cùng thư mục, đúng đường dẫn trong JSON):
  5 bảng nhân vật (`an, bo, lan, me-lan, bin-tham-chieu-a4.png`)
  + 3 ảnh phố (`pho-vn-sang-tham-chieu.png`,
  `cho-vn-tham-chieu.png`, `hem-vn-tham-chieu.png`)
  + phòng khách (`phong-khach-tham-chieu.png`), quán cà phê
  (`quan-cafe-tham-chieu.png`), ngã tư ban ngày
  (`nga-tu-den-xanh-tham-chieu.png`), ngã tư buổi tối
  (`nga-tu-buoi-toi-tham-chieu.png`)

## Triển khai trên tài khoản Muse khác
1. Giải nén gói này vào `~/workspace/your_files/` — mọi file nằm
   ngay trong `your_files/`, đúng đường dẫn `ref` trong JSON. Nếu để
   ảnh ref ở chỗ khác, sửa trường `ref` trong JSON.
2. Kiểm tra: `python3 ~/workspace/your_files/kit-stickman.py check`
   — liệt kê ref nào còn thiếu (hiện thiếu: Mimi, Bibo, bếp, vườn,
   văn phòng, 2 đạo cụ). Thiếu ref không chặn: tập đó chỉ dùng khóa chữ.
3. Tạo ảnh ref còn thiếu khi cần (bảng nhân vật: 3 dáng + 4 biểu cảm;
   địa điểm: mô tả 3 lớp, không chữ/biển số đọc được), xem thử rồi ghi
   đường dẫn vào JSON.
4. Dùng trong mọi tập: chạy `kit-stickman.py bible`, dán Visual Bible
   lên đầu file Phase B; nhân vật gọi bằng mã CHAR; mỗi clip tối đa
   3 ảnh ref (nhân vật → địa điểm → đạo cụ).

## Quy tắc
- Không gõ lại anchor theo trí nhớ — mọi anchor lấy từ Kit.
- Đổi anchor: sửa 1 lần trong `kit-stickman.json` (ghi ngày + lý do).
- Ảnh ref mới phải được Bepj duyệt mới thành ref chính thức.
- Chi tiết đầy đủ: mục 4b trong file
  `prompt-chuyen-tai-khoan-muse-lam-video.md` và mục "Character &
  Context Kit" trong skill `song_dang_tien_local_draft`.
