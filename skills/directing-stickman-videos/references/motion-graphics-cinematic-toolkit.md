# Cinematic Camera & Motion Graphics Toolkit Cho Stickman Video Director

> **Tài liệu tham chiếu:** `references/motion-graphics-cinematic-toolkit.md`  
> **Nguồn cảm hứng:** Kế thừa từ `Motion Video Director v3.5.2` (`Motion-graphics-skill-stack-store`)  
> **Áp dụng cho:** Director Mode (`A-series`) & Autopilot Mode (`B-series`)  

---

## 1. NGUYÊN TẮC NHỊP ĐIỆN ẢNH (CINEMATIC RHYTHM & RETENTION)

Để video Stickman giữ chân khán giả trên YouTube Shorts / TikTok / Reels:
- **Quy tắc 3 giây (Micro-movement rule):** Không để hình ảnh đứng yên quá 3 giây. Nếu nhân vật chỉ đứng nói, phải kích hoạt: Punch Zoom, chuyển góc nhìn (reverse angle), hiệu ứng chữ nảy, hoặc chèn motion sticker.
- **Visual Pacing:**
  - Đoạn Hook (0–5s): Nhịp cắt nhanh (1.5s - 2.0s / shot), góc máy cận hoặc trung cận, âm thanh dồn dập.
  - Đoạn Giải thích / Diễn giải (5–45s): Nhịp vừa (2.5s - 4.0s / shot), chuyển cảnh mượt.
  - Đoạn Climax / Chốt hạ (45–60s): Tăng tốc nhịp cắt, phóng to vào biểu cảm nhân vật, bass drop kết hợp camera shake.

---

## 2. BỘ CÔNG CỤ GÓC MÁY ĐIỆN ẢNH (CINEMATIC CAMERA MOVES)

Khi viết prompt tạo kịch bản kẹp cho Stickman, sử dụng các chỉ thị sau:

### 1. Punch Zoom (Zoom giật đột ngột)
- **Cơ chế:** Phóng to tức thì từ Medium Shot (Toàn thân) lên Close-up (Cận mặt) trong 1–3 frame (thay vì zoom từ từ).
- **Mục đích:** Bắt trọn khoảnh khắc nhân vật sốc, hoang mang, nhận ra sự thật hoặc khi voice đọc đến từ khóa quan trọng.
- **Prompt mẫu:**
  ```text
  Camera: Instant punch zoom from medium shot to tight close-up on stickman wide eyes at 00:02.10.
  ```

### 2. Whip Pan (Lia máy siêu tốc)
- **Cơ chế:** Camera lia ngang cực nhanh sang trái hoặc phải kèm vệt mờ chuyển động (motion blur).
- **Mục đích:** Chuyển cảnh giữa 2 địa điểm đối lập (Ví dụ: từ bàn làm việc văn phòng nghèo sang biệt thự giàu có) hoặc chuyển vế đối lập trong câu nói ("Nhưng sự thật là...").
- **Prompt mẫu:**
  ```text
  Transition: Fast whip pan to right with heavy motion blur into Scene 2.
  ```

### 3. Dutch Angle (Góc máy nghiêng lệch)
- **Cơ chế:** Đặt góc máy nghiêng từ 10° đến 20° so với đường chân trời.
- **Mục đích:** Tạo cảm giác bất an, thế giới đảo lộn, nhân vật đang suy sụp hoặc đối mặt với mối đe dọa (cực kỳ hiệu quả trong sub-style B4 - Dark Stickman).
- **Prompt mẫu:**
  ```text
  Camera: 15-degree dutch angle tilted low angle shot, stickman looking up in despair.
  ```

### 4. Parallax Depth Layering (Phân tầng chiều sâu 3 lớp)
- **Cơ chế:**
  - **Tiền cảnh (Foreground):** Mờ nhẹ (bokeh), chuyển động nhanh nhất khi camera pan (ví dụ: vài vệt khói, mảnh giấy bay qua).
  - **Trung cảnh (Midground):** Stickman chuyển động chính, nét căng (in-focus).
  - **Hậu cảnh (Background):** Chuyển động chậm nhất (parallax effect), màu sắc dịu để làm nổi bật stickman.
- **Prompt mẫu:**
  ```text
  Composition: 3-layer parallax depth. Foreground blurred dust particles, midground sharp black stickman running, background distant skyline moving slowly.
  ```

---

## 3. PHONG CÁCH ĐỒ HỌA MỞ RỘNG CHO STICKMAN (20 MOTION STYLES)

Bạn có thể yêu cầu Director Mode kết hợp nét vẽ Stickman với các phong cách motion đồ họa cao cấp:

| Phong cách mở rộng | Đặc điểm nhận dạng thị giác | Sub-style phù hợp |
|---|---|---|
| **Comic Book Stickman** | Hạt halftone chấm bi, viền đen dày, bóng đổ chấm, khung thoại kiểu truyện tranh kèm chữ onomatopoeia lớn ("POW!", "WHAM!"). | B5 (Viral Meme) & B1 |
| **Blueprint Technical** | Nền xanh kỹ thuật (Cyan #0077be), lưới ô vuông trắng, đường kích thước mm, mũi tên chỉ số, số liệu nhảy liên tục. | B3 (Explainer / Finance) |
| **Retro VHS 90s** | Hiệu ứng scanline ngang màn hình, viền nhòe màu sắc (chromatic aberration), vệt nhiễu băng từ, font chữ pixel cam/xanh lá kèm timestamp "REC 1998". | B4 (Dark) & B5 |
| **Paper Cutout / Stop-motion** | Stickman và đạo cụ như được cắt từ bìa carton hoặc giấy báo, có viền mép trắng gồ ghề, bóng đổ nổi 3D, animation giật 12 FPS. | B1 (Classic) & B3 |
| **Cyberpunk Neon Stickman** | Stickman nét vẽ neon phát sáng (Glow cyan/magenta), nền đen huyền bí, đường viền mạch điện tử phát sáng chạy ngầm. | B2 (Minimalist Tech) |

---

## 4. BẢNG MẪU KỊCH BẢN CHUẨN ĐIỆN ẢNH (CINEMATIC SHOT TEMPLATE)

```markdown
### Shot 01 (00:00 - 00:02.50) [HOOK]
- **Narration:** "Bạn có biết 90% số người đang lãng phí buổi sáng của họ?"
- **Visual:** Stickman nằm bẹp trên giường, đồng hồ chuông reo inh ỏi.
- **Motion Style:** Comic Book (chữ "RINGGGG" rung lắc trên đầu đồng hồ).
- **Camera:** Punch zoom vào mặt Stickman tại 00:01.80 khi mắt mở to thảng thốt.
- **SFX:** `062_Ticking clock intense` (00:00) -> `044_Pop sound` (00:01.80, onset: 12ms).
- **BGM:** Suspense beat (-24 dB ducking).
```

