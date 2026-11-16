# Tiêu Chuẩn Âm Lượng EBU R128 (-14 LUFS) & Kỹ Thuật Smart Ducking BGM

Tài liệu này hướng dẫn đo kiểm âm lượng, chuẩn hóa theo chuẩn công nghiệp **EBU R128 / ITU-R BS.1770-4 (-14 LUFS)** và áp dụng **Smart Audio Ducking** cho video Stickman.

---

## 1. Tại Sao Cần Chuẩn Âm Lượng -14 LUFS?

### Vấn đề thường gặp:
- **Quá nhỏ (ví dụ -24 LUFS đến -30 LUFS)**: Người xem trên điện thoại hoặc môi trường ồn ào không nghe rõ lời thoại, buộc phải vặn max volume.
- **Quá to (ví dụ -8 LUFS đến -10 LUFS)**: Âm thanh bị vỡ hạt (clipping, méo tiếng), và các nền tảng (YouTube, TikTok, Meta Reels, Spotify) sẽ tự động kích hoạt bộ nén **Loudness Penalty** ép âm lượng xuống, làm âm thanh bị bẹp dí (flat).
- **Âm lượng không đồng đều giữa các tập**: Người xem giật mình vì tập trước bé, tập sau quá to.

### Tiêu chuẩn công nghiệp:
- **Integrated Loudness**: `-14.0 LUFS` (dung sai cho phép: $\pm 1.0$ LUFS).
- **Maximum True-Peak**: $\le -1.5\text{ dBFS}$ (đảm bảo không bị méo tiếng khi YouTube/TikTok nén sang chuẩn AAC 128k/192k).
- **Loudness Range (LRA)**: $\approx 5 - 11\text{ LU}$ (giữ độ tương phản âm thanh tự nhiên giữa thoại và SFX).

---

## 2. Kỹ Thuật Smart Audio Ducking (Hạ Nhạc Nền Thông Minh)

### Vấn đề:
Khi trộn nhạc nền (BGM) và giọng đọc (Voice-over):
- Nếu để âm lượng BGM cố định ở mức vừa nghe, khi nhân vật nói, nhạc nền sẽ át lời thoại.
- Nếu vặn nhỏ BGM toàn bài, các đoạn không thoại (chuyển cảnh, intro, outro) nghe rất buồn tẻ, thiếu năng lượng.

### Giải pháp kỹ thuật (Sidechain Compression):
Trong quá trình render, hệ thống tách kênh Voice thành luồng phát và luồng điều khiển sidechain (`sidechaincompress`):
- **Khi nhân vật bắt đầu nói**: Nhạc nền tự động hạ xuống `-14 dB` trong vòng `200ms` (Attack), nhường toàn bộ sự tập trung cho lời thoại.
- **Khi dứt câu thoại (khoảng lặng > 0.3s)**: Nhạc nền từ từ dâng lên âm lượng gốc trong vòng `450ms` (Release), lấp đầy không gian âm thanh mà không gây giật cục.

---

## 3. Cấu Hình Trong `project.json`

Engine render của Stickman Autopilot (`autopilot-render.mjs`) tự động kích hoạt Smart Ducking và EBU R128 Loudness Normalization:

```json
{
  "music": {
    "path": "bgm/lofi_study.mp3",
    "gain": 0.4
  },
  "smart_ducking": true
}
```

*(Nếu muốn tắt ducking và giữ âm lượng nhạc phẳng như cũ, đặt `"smart_ducking": false"`)*.

---

## 4. Đo Kiểm EBU R128 Tự Động Sau Render

Mỗi khi chạy `preview` hoặc `render`, Stickman tự động đo đạc toàn bộ timeline thành phẩm và ghi thông số vào `preview-report.json` / `film-report.json`:

```json
{
  "audio_loudness": {
    "integrated_lufs": -14.02,
    "loudness_range_lra": 6.8,
    "true_peak_dbfs": -1.5,
    "target_lufs": -14.0,
    "target_true_peak": -1.5,
    "standard": "ITU-R BS.1770-4 / EBU R128",
    "status": "pass"
  }
}
```

### Các trạng thái kiểm định (`status`):
- `pass`: Đạt chuẩn tuyệt đối ($-16.0 \le \text{LUFS} \le -12.0$ và $\text{True-Peak} \le -1.0\text{ dBFS}$).
- `too_quiet`: Âm lượng tổng thể quá nhỏ ($< -16.0\text{ LUFS}$).
- `too_loud`: Âm lượng tổng thể quá to ($> -12.0\text{ LUFS}$).
- `peak_exceeded`: Đỉnh âm thanh vượt quá giới hạn an toàn ($> -1.0\text{ dBFS}$).

---

## 5. Hướng Dẫn Sử Dụng Dòng Lệnh Độc Lập

### 1. Đo kiểm âm lượng của một video hoặc file audio:
```bash
node scripts/autopilot.mjs measure-audio my_video.mp4
# hoặc
python3 scripts/audio-master-lufs.py --measure my_video.mp4
```

### 2. Chuẩn hóa 2-pass (Loudness Normalization) về -14 LUFS:
```bash
node scripts/autopilot.mjs normalize-audio raw_audio.wav normalized.wav
# hoặc
python3 scripts/audio-master-lufs.py --normalize --input raw_audio.wav --output normalized.wav --target-lufs -14.0
```

### 3. Trộn Voice + BGM với Smart Ducking độc lập:
```bash
python3 scripts/audio-master-lufs.py --duck \
    --voice narration.wav \
    --bgm background_music.mp3 \
    --output final_master.wav \
    --duck-db -14.0 \
    --fade-ms 250
```

---

## 6. Liên Kết Tài Liệu Liên Quan
- [Vietnamese Autopilot Pipeline](file:///Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/vietnamese-autopilot.md)
- [VieNeu Voice Catalog](file:///Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/vieneu-voice-catalog.md)
- [Báo Cáo Cải Tiến từ xStudio](file:///Users/xitrum/Documents/Dev/stickman/docs/bao-cao-cai-tien-tu-xstudio.md)
