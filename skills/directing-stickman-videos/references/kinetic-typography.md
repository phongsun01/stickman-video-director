# Kinetic Typography & Phụ Đề Động (TikTok / Karaoke / Pop Style)

Tài liệu này hướng dẫn sử dụng hệ thống **Kinetic Typography (Phụ đề chuyển động sinh động)** cho Stickman Video Director, kế thừa từ công nghệ phụ đề nâng cao của **xStudio (iContent Studio v0.8.1)**.

---

## 1. Tại Sao Cần Kinetic Typography Cho Video Ngắn?

Trên các nền tảng video ngắn (TikTok, Facebook Reels, YouTube Shorts):
- **Phụ đề tĩnh thông thường (Static captions)**: Người xem dễ lướt qua vì thiếu kích thích thị giác.
- **Kinetic Typography (Chữ nảy & đổi màu theo nhịp nói)**:
  - Tăng tỷ lệ giữ chân (Retention rate) thêm **25% – 40%**.
  - Dẫn dắt ánh mắt người xem theo từng từ nhân vật đang phát âm.
  - Phù hợp với hơn **70% người dùng xem video trên điện thoại ở chế độ tắt tiếng** (Muted viewing).

---

## 2. Các Phong Cách Phụ Đề Hỗ Trợ (`caption_style`)

| Phong cách | Mã định danh (`caption_style`) | Hiệu ứng thị giác | Khuyên dùng cho |
| :--- | :---: | :--- | :--- |
| **Kinetic Pop** *(Mặc định)* | `kinetic` | Cụm chữ nảy lò xo (`\fscx85 → \fscx100`), **từ đang đọc phóng to 122%** và đổi màu highlight neon rực rỡ | Shorts / TikTok / Reels viral, video năng lượng cao |
| **TikTok Bounce** | `tiktok` | Cụm chữ nảy nhẹ 90%, từ đang đọc đổi màu highlight | Video kể chuyện, tin tức, reaction |
| **Karaoke Fill** | `karaoke` | Chữ tô màu chuyển tiếp dần từ trái qua phải theo từng âm tiết bằng thẻ `\kf` | Video âm nhạc, thơ, rap, lời bài hát |
| **Pop Punchy** | `pop` | Cụm siêu ngắn (2–4 từ), chữ IN HOA cỡ lớn, đập thẳng vào mắt | Video giật gân, câu hỏi hook, sự thật bất ngờ |
| **Box Mờ** | `box` | Hộp nền bo góc mờ mờ (`rgba(0,0,0,0.6)`), chữ trắng viền mỏng | Video tài liệu, explainer nghiêm túc, phong cách tối giản |
| **Classic** | `classic` | Chữ trắng viền đen sắc nét tiêu chuẩn | Phong cách B4 Cinema, video dài |

---

## 3. Cấu Hình Trong `project.json`

Bạn chỉ cần thêm trường `caption_style` và `caption_highlight_color` vào `project.json`:

```json
{
  "caption_style": "kinetic",
  "caption_highlight_color": "#FFD700",
  "captions": [
    {
      "start": 0.5,
      "end": 2.8,
      "text": "Chào mừng bạn đến với video hoạt hình người que"
    }
  ]
}
```

### Bảng màu highlight gợi ý (`caption_highlight_color`):
- **Vàng kim rực rỡ (Gold)**: `#FFD700` (dễ đọc nhất trên mọi nền đen/trắng).
- **Xanh Cyan Neon**: `#00E5FF` (hiện đại, công nghệ, trẻ trung).
- **Cam năng lượng (Orange)**: `#FF6B00` (kích thích, cảnh báo, khẩn cấp).
- **Xanh lá tươi (Lime)**: `#00FF66` (tươi mới, tích cực, tài chính).

---

## 4. Tự Động Xuất File `.ass` Khi Render

Khi chạy lệnh `node scripts/autopilot.mjs render` hoặc `preview`:
- Hệ thống vẽ hiệu ứng nảy và đổi màu trực tiếp lên từng khung hình Canvas.
- Đồng thời tự động sinh file subtitle chuẩn **Advanced SubStation Alpha (`film.ass` / `preview.ass`)** bên cạnh file `.srt` và `.vtt`.
- Bạn có thể lấy file `.ass` này import trực tiếp vào CapCut, Premiere Pro hoặc DaVinci Resolve để tái sử dụng mà không cần gõ lại phụ đề.

---

## 5. Sử Dụng Dòng Lệnh Độc Lập (CLI)

Bạn có thể chuyển đổi bất kỳ file `words.json`, `captions.json` hoặc `project.json` nào thành phụ đề động `.ass`:

```bash
# 1. Tạo phụ đề nảy Kinetic với màu vàng kim #FFD700
node scripts/autopilot.mjs subtitles captions.json output.ass \
  --style kinetic \
  --highlight-color "#FFD700"

# 2. Tạo phụ đề Karaoke tô màu dần
node scripts/autopilot.mjs subtitles captions.json karaoke.ass \
  --style karaoke \
  --highlight-color "#00E5FF"

# 3. Tạo phụ đề Pop giật gân chữ in hoa
node scripts/autopilot.mjs subtitles captions.json pop.ass \
  --style pop
```

---

## 6. Liên Kết Tài Liệu
- [Vietnamese Caption Splitter](file:///Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/vietnamese-autopilot.md)
- [Báo Cáo Cải Tiến từ xStudio](file:///Users/xitrum/Documents/Dev/stickman/docs/bao-cao-cai-tien-tu-xstudio.md)
- [Post-Render QC Engine](file:///Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/post-render-qc.md)
