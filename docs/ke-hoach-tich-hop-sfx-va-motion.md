# KẾ HOẠCH TÍCH HỢP TÀI NGUYÊN TỪ SFX-THƯ-VIỆN VÀ MOTION-GRAPHICS-SKILL-STACK-STORE VÀO STICKMAN-VIDEO-DIRECTOR

> **Tài liệu tham chiếu:** `docs/ke-hoach-tich-hop-sfx-va-motion.md`  
> **Phiên bản áp dụng:** Stickman Video Director v1.3.x  
> **Ngày lập:** 2026-11-11  

---

## 1. MỤC TIÊU & TỔNG QUAN NGUỒN TÀI NGUYÊN

Mục tiêu của kế hoạch này là tích hợp có chọn lọc những tinh hoa từ 2 kho tài nguyên cục bộ:
1. **`D:\Video creator\Hoang Lma\sfx-thu-vien`**: Kho 585 âm thanh bản quyền/sạch (439 hiệu ứng âm thanh SFX phân thành 49 nhóm chủ đề + 146 track nhạc nền BGM), đã được phân tích sẵn siêu dữ liệu:
   - `catalog.json`: Phân loại, thời lượng, đường dẫn.
   - `su_kien.json`: Ánh xạ sự kiện kịch bản với SFX phù hợp.
   - `do_to.json`: Đo lường độ to K-weighted (LUFS/dBFS) và điểm kích hoạt âm thanh thực tế (`onset`).
2. **`D:\Video creator\Hoang Lma\Motion-graphics-skill-stack-store`**: Bộ kỹ năng làm video Motion Graphics chuyên nghiệp (Motion Video Director v3.5.2), bao gồm:
   - 20 phong cách motion đồ họa cao cấp (Comic Book, Blueprint, Retro VHS, Paper Cutout, Cyberpunk, Kinetic Typography...).
   - Bộ công cụ góc máy điện ảnh (Cinematic Toolkit): Punch Zoom, Whip Pan, Dutch Angle, Match Cut, Dynamic Framing.
   - Tiêu chuẩn âm thanh chuẩn YouTube: Loudness -14 LUFS, True Peak < -1 dBTP, quy tắc ducking BGM khi có lời dẫn.

---

## 2. CHỨC NĂNG & TÁC DỤNG CỦA CÁC THÀNH PHẦN TÍCH HỢP

| Thành phần tích hợp | Vị trí file trong dự án | Chức năng chính | Tác dụng đối với Stickman Video |
|---|---|---|---|
| **1. Local SFX Provider & Smart Finder CLI** | `skills/directing-stickman-videos/scripts/sfx-catalog-local.py` | - Quét và lập chỉ mục kho 585 âm thanh.<br>- Tìm kiếm SFX theo hành động, tâm trạng hoặc từ khóa tiếng Việt / tiếng Anh.<br>- Trích xuất thông số `onset` và đề xuất mức gain/ducking chuẩn. | Giúp đạo diễn AI hoặc người dùng chọn ngay SFX chính xác trong kho cục bộ, căn đúng frame va chạm (tránh delay khoảng lặng đầu file), tối ưu âm lượng không lấn át giọng đọc. |
| **2. Local SFX Library Reference** | `skills/directing-stickman-videos/references/local-sfx-thu-vien.md` | - Cung cấp bảng tra cứu toàn diện 49 nhóm SFX tương ứng với 5 sub-styles Stickman (B1–B5).<br>- Hướng dẫn phối âm thanh 3 lớp: BGM + SFX nền + SFX điểm nhấn (Punctuation SFX). | Định hướng AI biên kịch tự động sinh ra chỉ dẫn âm thanh chuẩn xác trong kịch bản Director Mode và Autopilot Mode. |
| **3. Cinematic Motion & Camera Toolkit** | `skills/directing-stickman-videos/references/motion-graphics-cinematic-toolkit.md` | - Tích hợp các kỹ thuật camera điện ảnh (Punch Zoom, Whip Pan, Tracking, Split Screen).<br>- Kế thừa 20 bộ phong cách visual đồ họa chuyển động cho Stickman. | Biến video Stickman từ hoạt hình phẳng 2D đơn điệu thành video có nhịp cắt điện ảnh kịch tính, tăng tỷ lệ giữ chân người xem (Audience Retention). |
| **4. Tích hợp Router & Skill Prompts** | Cập nhật `SKILL.md`, `references/autopilot.md`, `references/autopilot-sound-system.md` | - Định tuyến câu lệnh khi người dùng yêu cầu dùng kho SFX cục bộ hoặc phong cách motion mở rộng. | AI nhận diện ngay khi nào cần gọi thư viện âm thanh máy tính thay vì chỉ dùng âm thanh mặc định trên mạng. |

---

## 3. HƯỚNG DẪN SỬ DỤNG CHI TIẾT

### 3.1. Hướng dẫn sử dụng SFX Finder CLI (`sfx-catalog-local.py`)

Công cụ chạy bằng Python (`py`), hỗ trợ tìm kiếm âm thanh cục bộ:

```bash
# 1. Tìm kiếm SFX theo từ khóa hành động (va chạm, đấm, ngã, bước chân...)
py skills/directing-stickman-videos/scripts/sfx-catalog-local.py search "punch"
py skills/directing-stickman-videos/scripts/sfx-catalog-local.py search "bước chân"

# 2. Liệt kê các nhóm SFX có sẵn trong thư viện
py skills/directing-stickman-videos/scripts/sfx-catalog-local.py categories

# 3. Lấy thông số kỹ thuật âm thanh (onset, loudness, gain đề xuất) của 1 file
py skills/directing-stickman-videos/scripts/sfx-catalog-local.py inspect "punch_comic_01"

# 4. Gợi ý SFX cho một shot kịch bản Stickman theo hành động và mood
py skills/directing-stickman-videos/scripts/sfx-catalog-local.py suggest --action "stickman trượt chân ngã" --mood "hài hước"
```

> **Lưu ý về đường dẫn:**  
> Mặc định script tự động tìm thư mục `D:\Video creator\Hoang Lma\sfx-thu-vien`. Nếu bạn chuyển thư mục sang ổ đĩa khác, chỉ cần đặt biến môi trường:
> `set SFX_THU_VIEN_DIR=E:\MySFX\sfx-thu-vien` hoặc truyền cờ `--lib "D:\path\to\sfx-thu-vien"`.

---

### 3.2. Hướng dẫn áp dụng Cinematic Camera vào kịch bản Stickman (Director Mode)

Khi viết kịch bản ở Director Mode (`A-series`) hoặc Autopilot Mode (`B-series`), bạn có thể thêm các chỉ thị camera từ Cinematic Toolkit vào prompt của từng shot:

1. **Punch Zoom (Phóng to đột ngột 1.25x - 1.5x vào mặt/biểu cảm):**
   - *Mục đích:* Nhấn mạnh khoảnh khắc stickman sốc, bất ngờ, phát hiện ra bí mật.
   - *Cách ghi trong shot:* `Camera: Punch zoom to stickman face at 00:01.20 | SFX: dramatic_hit_02 (offset: onset 120ms)`.
2. **Whip Pan (Chuyển cảnh lia máy cực nhanh với hiệu ứng mờ nhòe):**
   - *Mục đích:* Chuyển giữa 2 bối cảnh đối lập hoặc dòng suy nghĩ của stickman.
   - *Cách ghi trong shot:* `Transition: Whip pan right (duration: 8 frames) | SFX: whoosh_fast_03`.
3. **Dutch Angle (Nghiêng góc máy 10-15 độ):**
   - *Mục đích:* Tạo cảm giác bất an, hoảng loạn hoặc thế giới đảo lộn (rất hợp với B4 - Dark Stickman hoặc B3 - Explainer khi nhân vật gặp bế tắc).
4. **Depth Layering (Phân tầng chiều sâu: Tiền cảnh - Trung cảnh - Hậu cảnh):**
   - *Mục đích:* Thêm các vệt khói, mảnh vỡ hoặc đường lưới mờ ở tiền cảnh để stickman chuyển động ở trung cảnh, tạo cảm giác không gian 3D.

---

### 3.3. Hướng dẫn phối âm thanh chuẩn Loudness (-14 LUFS)

Khi dựng video tổng hợp hoặc xuất lệnh mix FFmpeg:
1. **Narration (Giọng đọc AI):** Giữ ở mức chuẩn **-16 dBFS đến -14 dBFS** (đây là kênh chính, rõ ràng nhất).
2. **SFX (Hiệu ứng va chạm/chuyển cảnh):** Căn đỉnh tối đa **-6 dBFS đến -3 dBFS**, sử dụng thông số `onset` của `sfx-thu-vien` để khớp đúng frame va chạm.
3. **BGM (Nhạc nền):**
   - Đoạn có lời dẫn: Ducking xuống **-24 dBFS đến -28 dBFS** (thấp hơn giọng đọc 10-14 dB).
   - Đoạn chuyển cảnh / nốt lặng: Đẩy lên **-18 dBFS đến -16 dBFS**.

---

## 4. QUY TRÌNH TRIỂN KHAI KỸ THUẬT

1. **Bước 1: Viết script `sfx-catalog-local.py`**:
   - Tải `catalog.json`, `su_kien.json`, `do_to.json` từ thư mục cục bộ.
   - Cung cấp giao diện CLI tìm kiếm, đề xuất theo shot action/mood.
   - Hỗ trợ xuất JSON hoặc Text dễ đọc.
2. **Bước 2: Tạo tài liệu `local-sfx-thu-vien.md`**:
   - Tổng hợp 49 nhóm hiệu ứng, mapping với các sub-styles B1 (Classic), B2 (Minimalist), B3 (Explainer), B4 (Dark), B5 (Viral Meme).
3. **Bước 3: Tạo tài liệu `motion-graphics-cinematic-toolkit.md`**:
   - Trích lọc 20 reference styles và kỹ thuật camera điện ảnh từ `Motion-graphics-skill-stack-store`.
4. **Bước 4: Cập nhật `SKILL.md` và các file tham chiếu**:
   - Bổ sung chỉ mục để AI agent tự động tra cứu khi người dùng nhắc đến sound effects cục bộ hoặc cinematic motion.
5. **Bước 5: Kiểm thử tự động & xác nhận**:
   - Chạy thử nghiệm script Python với nhiều trường hợp tìm kiếm.
   - Chạy test suite của dự án (`node --test`, verify localized READMEs, verify thumbnail kit).
6. **Bước 6: Git Commit & Push**:
   - Commit các thay đổi và đẩy lên GitHub `origin/main`.
