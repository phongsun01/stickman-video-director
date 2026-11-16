# Báo Cáo Kiểm Định Chất Lượng Tự Động (Post-Render QC Engine)

Tài liệu này hướng dẫn hệ thống kiểm định chất lượng video tự động (**Quality Control - QC Engine**) kế thừa từ kiến trúc của **xStudio (iContent Studio v0.8.1)**, giúp phát hiện sớm các lỗi kỹ thuật và biên tập trước khi đăng tải lên mạng xã hội.

---

## 1. Tổng Quan

Sau khi render video (`preview` hoặc `render`), hệ thống tự động chạy một lượt giải mã chẩn đoán nhanh (Single-pass Diagnostic Decoding qua FFmpeg 320p) và đối chiếu với `project.json` để phát hiện 4 nhóm lỗi phổ biến:

| Hạng mục kiểm tra | Bộ lọc / Thuật toán | Ngưỡng cảnh báo | Mức độ phạt |
| :--- | :--- | :--- | :--- |
| **Đứng hình (`freeze_frame`)** | FFmpeg `freezedetect` | Đứng hình liên tục $\ge 2.5\text{s}$ ($\ge 5\text{s}$ coi là lỗi nghiêm trọng) | `warn`: -8đ / `bad`: -25đ |
| **Đoạn câm (`audio_silence`)** | FFmpeg `silencedetect` | Mất tiếng, không thoại, không SFX, không BGM $> 1.5\text{s}$ | `warn`: -8đ / `bad`: -25đ |
| **Màn đen (`black_screen`)** | FFmpeg `blackdetect` | Màn hình đen không chủ đích ở thân video $\ge 0.4\text{s}$ | `warn`: -8đ / `bad`: -25đ |
| **Độ to chuẩn (`loudness`)** | FFmpeg `ebur128` | Lệch quá $\pm 2.0\text{ LUFS}$ so với chuẩn `-14.0 LUFS` | `warn`: -8đ / `bad`: -25đ |
| **Vỡ tiếng (`peak_clipped`)** | True-Peak limiter | True-Peak $\ge -0.1\text{ dBFS}$ (vỡ tiếng) hoặc $> -1.0\text{ dBFS}$ | `warn`: -8đ / `bad`: -25đ |
| **Va chạm phụ đề (`caption_collision`)** | Bounding-box Analyzer | Nhân vật / pose / presenter che lấp dải phụ đề an toàn ở đáy | `info` / `warn`: -8đ |

---

## 2. Hệ Thống Điểm Số & Tiêu Chuẩn Phê Duyệt (`QA Passed`)

- **Điểm xuất phát**: `100 điểm`.
- **Trừ điểm theo mức độ**:
  - `bad`: Trừ 25 điểm mỗi lỗi (lỗi nghiêm trọng: clip tiếng, mất video, đứng hình $> 5$s).
  - `warn`: Trừ 8 điểm mỗi lỗi (cần lưu ý: tiếng hơi to/nhỏ, đứng hình ngắn, phụ đề hơi sát).
  - `info`: 0 điểm (thông tin tham khảo).
- **Điều kiện Đạt (`qa_passed: true`)**:
  - Điểm tổng thể: $\text{Score} \ge 80$.
  - Không có bất kỳ lỗi `bad` nào.

---

## 3. Cấu Trúc File Báo Cáo `verification.json`

File được tạo tự động bên cạnh video thành phẩm (ví dụ `productions/my-video/film-verification.json` hoặc `verification.json`):

```json
{
  "file": "/Users/xitrum/Documents/Dev/stickman/productions/my-video/film.mp4",
  "duration_seconds": 32.5,
  "stream_info": {
    "duration": 32.5,
    "size_bytes": 4581204,
    "video": {
      "codec": "h264",
      "width": 720,
      "height": 1280,
      "duration": 32.5
    },
    "audio": {
      "codec": "aac",
      "channels": 1,
      "sample_rate": 48000,
      "duration": 32.5
    }
  },
  "audio_metrics": {
    "integrated_lufs": -14.0,
    "loudness_range_lra": 6.8,
    "true_peak_dbfs": -1.5,
    "target_lufs": -14.0
  },
  "qc_evaluation": {
    "qa_passed": true,
    "score": 100,
    "standard": "EBU R128 / ITU-R BS.1770-4 / Mobile Safe Zones",
    "summary": {
      "findings_count": 0,
      "bad": 0,
      "warn": 0,
      "info": 0
    },
    "findings": []
  }
}
```

---

## 4. Hướng Dẫn Sử Dụng Dòng Lệnh Nhanh

### 1. Kiểm định trực tiếp một video hoặc project:
```bash
node scripts/autopilot.mjs qc my_video.mp4
# hoặc truyền thư mục dự án
node scripts/autopilot.mjs qc productions/my-video
```

### 2. Chạy qua Python script với tùy chọn nâng cao:
```bash
python3 scripts/qc-verification.py \
    --video productions/my-video/film.mp4 \
    --project productions/my-video/project.json \
    --output productions/my-video/custom_qc.json
```

---

## 5. Liên Kết Tài Liệu Liên Quan
- [Chuẩn Âm Lượng EBU R128 & Smart Ducking](file:///Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/audio-loudness-and-ducking.md)
- [Báo Cáo Cải Tiến từ xStudio](file:///Users/xitrum/Documents/Dev/stickman/docs/bao-cao-cai-tien-tu-xstudio.md)
- [Vietnamese Autopilot Pipeline](file:///Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/vietnamese-autopilot.md)
