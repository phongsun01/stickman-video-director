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

## 3. BẢN CHẤT CỦA LAYER OVERLAY & DYNAMIC BACKGROUND

### 1. Dynamic Background (Lớp Nền Chuyển Động)
- **Vị trí**: Nằm ở tầng **DƯỚI CÙNG (Backdrop)**, phía sau nhân vật người que.
- **Tác dụng**: Thay thế nền trắng đơn điệu hoặc lưới caro tĩnh bằng một không gian sống động:
  - Lưới kỹ thuật **Blueprint** trôi nhẹ phía sau khi Stickman giải thích thuật toán/logic.
  - Sóng chuyển sắc **Gradient Mesh** êm ái khi Stickman chia sẻ tâm sự, bài học cuộc sống.
  - Bảng hiệu **Neon Glow** nhấp nháy trong đêm ở cảnh thành phố cyberpunk.
  - Phòng game 8-bit **Pixel Art** khi Stickman vượt chướng ngại vật vui nhộn.
- **Chế độ hòa trộn (Blend Mode)**: `Normal` (vẽ trực tiếp trước khi vẽ nhân vật).

### 2. Transparent Layer Overlay (Lớp Phủ Trong Suốt Lên Trên)
- **Vị trí**: Nằm ở tầng **TRÊN CÙNG (Foreground / Overlay)**, phủ lên trên nhân vật hoặc lồng giữa các lớp.
- **Đặc tính**: Được xuất với **kênh trong suốt (Alpha Channel - WebM yuva420p / ProRes 4444)**:
  - **Particles Overlay**: Bụi sáng, đốm sao lấp lánh bay lơ lửng xung quanh nhân vật (Blend mode `Screen`).
  - **Retro VHS Scanlines**: Sọc quét màn hình CRT, hạt nhiễu từ analog tạo cảm giác phóng sự bí ẩn (Blend mode `Screen`).
  - **Halftone Print Dots**: Hạt in báo chấm bi vintage phủ lên cảnh báo chí / hồi tưởng (Blend mode `Overlay`).
  - **Comic Speedlines**: Tia tốc độ và khung viền truyện tranh hành động (Blend mode `Multiply`).

---

## 4. DANH MỤC 20 PHONG CÁCH MOTION GRAPHICS TEMPLATES

Bộ tài nguyên 20 styles nằm tại `/Users/xitrum/Documents/Dev/library/Motion-graphics-skill-stack-store/20-reference-motion-styles`:

| Mã Style | Tên Phong Cách | Loại Tối Ưu | Ứng Dụng Trong Hoạt Hình Stickman | Phong Cách Hợp |
| :--- | :--- | :---: | :--- | :---: |
| `particles` | Particles Swarm | **Overlay** | Bụi sao lấp lánh, phép thuật, không gian trầm tư | **B1, B2, B4** |
| `retro-vhs` | 80s Retro VHS CRT | **Overlay** | Sọc quét màn hình TV, nhiễu analog, phóng sự điều tra | **B3, B4** |
| `blueprint` | Technical Blueprint | **Background** | Bản vẽ kỹ thuật xanh neon, phân tích logic, công nghệ | **B2, B1** |
| `neon-glow` | Flickering Neon | **Background** | Đèn neon nhấp nháy, đêm cyberpunk, tiêu đề mở màn | **B2, B3** |
| `comic-book` | Comic Book Halftone | **Cả hai** | Khung truyện tranh, tia tốc độ đấm nổ, reaction meme | **B1, B6** |
| `kinetic-type` | Kinetic Typography | **Overlay** | Chữ nảy TikTok, text chạy rượt đuổi, nhấn mạnh từ khóa | **B1, B2, B6** |
| `wireframe-3d` | 3D Wireframe | **Background** | Khung dây 3D xoay chiều, không gian ảo Metaverse | **B2, B4** |
| `gradient-mesh` | Flowing Mesh | **Background** | Sóng màu pastel êm dịu, hiện đại, phong cách tâm tình | **B2, B5** |
| `halftone` | Halftone Print | **Overlay** | Chấm in báo cổ điển vintage, tư liệu tài liệu | **B1, B3** |
| `pixel-art` | 8-bit Retro Pixel | **Background** | Thế giới game 8-bit Mario, vượt ải, nhận thưởng | **B1, B6** |
| `liquid-morph` | Liquid Chrome | **Background** | Chất lỏng kim loại biến hình, sáng tạo không giới hạn | **B2, B5** |
| `holographic` | Holographic Foil | **Cả hai** | Vòng hào quang 3D lấp lánh, huy hiệu chứng nhận | **B2, B4** |
| `glassmorphism` | Frosted Glass UI | **Overlay** | Thẻ kính mờ lơ lửng, widget thông số, biểu đồ | **B2, B5** |
| `isometric` | Isometric Block | **Background** | Thành phố khối hộp 3D, bất động sản, hệ thống | **B2** |
| `clay-3d` | Claymorphism 3D | **Background** | Đồ chơi đất nặn bồng bềnh, vui nhộn, tâm lý | **B1, B5** |
| `ascii-art` | Terminal ASCII | **Background** | Màn hình hacker ma trận, ký tự xanh lá rơi | **B2, B4** |
| `split-flap` | Split-Flap Board | **Cả hai** | Bảng lật số sân bay lách cách, đếm ngược sự kiện | **B2, B3** |
| `bauhaus` | Bauhaus Grid | **Background** | Hình học tối giản Bauhaus, tư duy thiết kế | **B1, B2** |
| `art-deco` | Art Deco Gold | **Background** | Họa tiết mạ vàng hoàng gia sang trọng | **B4, B3** |
| `neo-brutalism` | Neo-Brutalism | **Cả hai** | Viền đen dày, bóng gắt 100%, màu neon Gen Z | **B1, B6** |

---

## 5. HƯỚNG DẪN SỬ DỤNG DÒNG LỆNH (CLI)

```bash
# Xem danh sách đầy đủ 20 styles và vai trò
node scripts/autopilot.mjs motion-template --list

# Xuất 1 background video Blueprint (5 giây, 720x1280)
node scripts/autopilot.mjs motion-template --style blueprint --mode background --dur 5 --output bg_blueprint.mp4

# Xuất 1 transparent overlay sọc quét VHS trong suốt (WebM yuva420p)
node scripts/autopilot.mjs motion-template --style retro-vhs --mode overlay --dur 5 --output overlay_vhs.webm
```

---

## 6. BẢNG MẪU KỊCH BẢN CHUẨN ĐIỆN ẢNH (CINEMATIC SHOT TEMPLATE)

```markdown
### Shot 01 (00:00 - 00:02.50) [HOOK]
- **Narration:** "Bạn có biết 90% số người đang lãng phí buổi sáng của họ?"
- **Visual:** Stickman nằm bẹp trên giường, đồng hồ chuông reo inh ỏi.
- **Motion Style:** Comic Book (chữ "RINGGGG" rung lắc trên đầu đồng hồ).
- **Camera:** Punch zoom vào mặt Stickman tại 00:01.80 khi mắt mở to thảng thốt.
- **SFX:** `062_Ticking clock intense` (00:00) -> `044_Pop sound` (00:01.80, onset: 12ms).
- **BGM:** Suspense beat (-24 dB ducking).
```

