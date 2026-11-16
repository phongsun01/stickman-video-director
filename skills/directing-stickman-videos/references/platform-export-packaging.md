# Hướng dẫn Đóng gói Video Đa Nền Tảng (Multi-Platform Export Packaging) & Auto Motion

Tài liệu này hướng dẫn cách sử dụng công cụ đóng gói video đa nền tảng (`autopilot.mjs package`) cho TikTok, Instagram Reels, YouTube Shorts, YouTube 16:9 và cơ chế tự động hóa đồ họa chuyển động (Motion Graphics Compositing).

---

## 1. CÔNG CỤ ĐÓNG GÓI ĐA NỀN TẢNG (`autopilot.mjs package`)

### 1.1 Mục đích
Sau khi render video `film.mp4`, công cụ này sẽ tự động phân phối và đóng gói video vào từng thư mục riêng cho từng nền tảng kèm đầy đủ:
- Video đã tối ưu tỷ lệ khung hình (Aspect Ratio: 9:16 dọc hoặc 16:9 ngang).
- File tiêu đề (`title.txt`), mô tả (`description.txt`), phụ đề & hook (`caption.txt`).
- File hashtag tối ưu theo từng mạng xã hội (`hashtags.txt`, `tags.txt`).
- **YouTube Chapters / Timestamps tự động** trích xuất từ các shot trong kịch bản.
- Báo cáo tổng hợp manifest `summary.json`.

---

### 1.2 Cấu trúc Thư mục Đóng gói (`package/`)

```
package/
├── summary.json                  # Báo cáo tổng hợp metadata, dung lượng, hash
├── tiktok/
│   ├── video_9x16.mp4            # Tỷ lệ 9:16 dọc (1080x1920 hoặc 720x1280)
│   ├── caption.txt               # Hook ngắn < 150 ký tự, CTA thả tim & follow
│   └── hashtags.txt              # Hashtags TikTok (#stickman #kienthuc #xuhuong #fyp...)
├── reels/
│   ├── video_9x16.mp4            # Video 9:16 cho Instagram Reels
│   ├── caption.txt               # Caption truyền cảm hứng, CTA "Lưu video để xem lại"
│   └── hashtags.txt              # Hashtags Reels tối ưu tiếp cận
├── shorts/
│   ├── video_9x16.mp4            # Video 9:16 cho YouTube Shorts
│   ├── title.txt                 # Tiêu đề ngắn < 100 ký tự có chứa #shorts
│   └── description.txt           # Mô tả ngắn cho Shorts feed
└── youtube/
    ├── video_16x9.mp4            # 16:9 Landscape (1920x1080) với nền mờ Cinema Blur hai bên
    ├── title.txt                 # Tiêu đề SEO YouTube chuẩn
    ├── description.txt           # Mô tả đầy đủ kèm Dấu mốc thời gian (Chapters 00:00)
    └── tags.txt                  # Tags phân tách bằng dấu phẩy
```

---

### 1.3 Cơ chế Xử lý Khung hình Thông minh (Smart Aspect Ratio Adaptation)
- **Nếu video gốc là 9:16 (Dọc)**:
  - Cho TikTok, Reels, Shorts: Sao chép luồng trực tiếp (`-c copy`, cực nhanh, không giảm chất lượng).
  - Cho YouTube 16:9: Áp dụng hiệu ứng **Studio Cinema Blurred Background** (1920x1080): video 9:16 nằm ở trung tâm sắc nét, phía sau là nền video được phóng to và làm mờ (Gaussian/Box blur) thay vì viền đen nhàm chán.
- **Nếu video gốc là 16:9 (Ngang)**:
  - Cho YouTube: Sao chép luồng trực tiếp.
  - Cho TikTok, Reels, Shorts: Tự động scale và lót nền mờ dọc 1080x1920.

---

### 1.4 Hướng dẫn Dòng lệnh (CLI)

```bash
# Đóng gói từ file project.json:
node scripts/autopilot.mjs package productions/my-film/project.json

# Đóng gói từ file video đã render:
node scripts/autopilot.mjs package productions/my-film/outputs/film.mp4 \
  --title "Bí Quyết Quản Lý Thời Gian" \
  --platforms tiktok,reels,shorts,youtube

# Đóng gói với hashtags và thư mục xuất tùy chỉnh:
node scripts/autopilot.mjs package film.mp4 \
  --output dist/package \
  --platforms tiktok,shorts \
  --hashtags "#stickman,#hoathinh,#kienthuc,#xuhuong"
```

---

## 2. QUY TRÌNH MOTION GRAPHICS TỰ ĐỘNG & THÔNG BÁO TRƯỚC RENDER

### 2.1 Thông báo Người dùng Trước khi Render
Trước khi render video, hệ thống luôn in thông báo nổi bật trên console để người dùng biết chính xác những hiệu ứng chuyển động nào đang được áp dụng:

```
================================================================================
🎬 [THÔNG BÁO ĐỒ HỌA CHUYỂN ĐỘNG / MOTION GRAPHICS PIPELINE]
   ► Phong cách chính (Style): B2
   ► Nền động (Dynamic Background): [blueprint] (Độ mờ: 85%)
   ► Lớp phủ động (Layer Overlay):  [particles] (Hòa trộn: screen, Độ mờ: 60%)
   ► Trạng thái: Tự động khởi tạo assets và lồng ghép (composite) vào video đầu ra.
================================================================================
```

### 2.2 Cấu hình trong `project.json`
Bạn có thể cấu hình trực tiếp trong `project.json`:
```json
{
  "style": "B2",
  "motion_background": {
    "style": "blueprint",
    "opacity": 0.85
  },
  "motion_overlay": {
    "style": "particles",
    "blend": "screen",
    "opacity": 0.6
  }
}
```

### 2.3 Kích hoạt Tự động qua Dòng lệnh (`--auto-motion`)
Khi thêm cờ `--auto-motion`, Autopilot sẽ tự động gán bộ chuyển động tối ưu theo từng phong cách phim:
- **B1 (Classic / Action)**: Overlay hạt bụi `particles` hoặc tia truyện tranh `comic-book`.
- **B2 (Tech Explainer)**: Nền kỹ thuật `blueprint`.
- **B3 / B4 (Retro / Thriller)**: Overlay sọc quét TV `retro-vhs`.
- **B5 (Tâm sự / Podcast)**: Nền sóng màu `gradient-mesh`.
- **B6 (Viral Meme)**: Overlay `neo-brutalism` hoặc `comic-book`.

Ví dụ:
```bash
# Render video với chế độ tự động chọn motion theo style:
node scripts/autopilot.mjs render project.json --auto-motion

# Hoặc chỉ định trực tiếp nền và lớp phủ:
node scripts/autopilot.mjs render project.json --motion-bg blueprint --motion-ov retro-vhs
```
