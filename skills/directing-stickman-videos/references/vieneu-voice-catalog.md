# VieNeu Voice Catalog & Cơ Chế Auto-Fit Atempo Timing

Tài liệu này hướng dẫn chọn giọng đọc tiếng Việt địa phương (VieNeu-TTS v3 Turbo), sử dụng tính năng **Voice Cloning** và cơ chế **Auto-fit atempo timing** để căn chỉnh âm thanh khớp hoàn hảo với timeline video Stickman.

---

## 1. Tổng quan về VieNeu-TTS v3 Turbo

- **Mô hình**: VieNeu-TTS v3 Turbo (chạy hoàn toàn offline / local qua ONNX Runtime CPU, Apache-2.0).
- **Đặc tính**:
  - Không cần GPU rời (chạy mượt trên CPU máy trạm, RAM ~4GB).
  - Không cần API key, không phụ thuộc dịch vụ đám mây (Gemini/ElevenLabs/Azure), không lo rate-limit.
  - Ngữ điệu tự nhiên, chuẩn thanh điệu tiếng Việt (Bắc / Trung / Nam).
  - Hỗ trợ Zero-shot Voice Cloning từ file mẫu âm thanh ngắn (3–8 giây).

---

## 2. Bảng Catalog Giọng Đọc Tiếng Việt (12 Preset Chuẩn)

VieNeu cung cấp sẵn các preset giọng đọc tối ưu cho từng thể loại nội dung và vai diễn trong phim hoạt hình Stickman:

| ID Giọng | Giới tính | Miền | Đặc tính âm sắc & Phong cách | Phân vai Stickman đề xuất |
| :--- | :--- | :--- | :--- | :--- |
| **Thiện Minh** | Nam | Bắc | Trầm ấm, truyền cảm, phong thái thuyết minh chính kịch | **Người dẫn chuyện (Narrator)**, Thầy giáo, Chuyên gia phân tích, Stickman triết lý |
| **Trúc Ly** | Nữ | Bắc | Tự nhiên, trong trẻo, phong cách hiện đại | **Nữ chính**, Người dẫn dắt hiện đại, Cô bạn đồng hành thông minh |
| **Hải Đăng** *(Mặc định)* | Nam | Bắc | Sôi nổi, dứt khoát, trẻ trung, tự tin | **Nhân vật chính Stickman**, Đối đáp nhanh, Bình luận hài hước, Viral/Trending |
| **Mai Anh** | Nữ | Bắc | Dịu dàng, nhẹ nhàng, ấm áp, tâm tình | Cảnh hồi tưởng, Tâm sự sâu lắng, Lời khuyên ấm áp, Nhân vật mẹ/chị |
| **Quang Sơn** | Nam | Nam | Điềm đạm, rõ ràng, phong thái phóng khoáng Nam Bộ | Người dẫn chuyện giọng Nam, Stickman chững chạc, Kỹ sư/Thương nhân |
| **Ngọc Huyền** | Nữ | Nam | Năng động, tươi vui, biểu cảm cao | Nữ nhân vật tinh nghịch, Tình huống bất ngờ, Shorts / TikTok meme |
| **Quỳnh Giang** | Nữ | Bắc | Trầm tĩnh, học thuật, chuẩn mực khoa học | Video giải thích kiến thức, Explainer video, Tài liệu số liệu |
| **Minh Quang** | Nam | Bắc | Trầm vang, đĩnh đạc, quyền uy | **Trùm phản diện (Boss)**, Giám đốc, Nhân vật quyền lực |
| **Bảo Ngọc** | Nữ | Nam | Trẻ con, nhí nhảnh, ngây thơ | Nhân vật em bé Stickman, Nhân vật ngây thơ bị troll, Hoạt hình vui nhộn |
| **Đức Huy** | Nam | Nam | Hài hước, dí dỏm, tếu táo đời thường | **Nhân vật ngớ ngẩn (Silly Stickman)**, Tấu hài, Reaction |
| **Thanh Hương** | Nữ | Bắc | Chuẩn mực, thời sự, nghiêm túc | **Bản tin Stickman News**, Báo cáo tình huống khẩn cấp, Parody tin tức |
| **Tiến Cường** | Nam | Bắc | Hào hùng, kịch tính, đầy năng lượng | Cảnh hành động, Trận chiến Stickman, Kêu gọi hành động (CTA), Cao trào kịch |

---

## 3. Cơ Chế Voice Cloning (Giọng Tùy Biến)

VieNeu v3 Turbo hỗ trợ trích xuất đặc trưng âm sắc (timbre) và phong cách từ một file âm thanh mẫu ngắn thông qua cờ `--ref-audio`.

### Yêu cầu file mẫu:
- **Thời lượng lý tưởng**: 3 – 8 giây (đoạn nói rõ ràng, không ngắt quãng quá dài).
- **Định dạng**: WAV mono, 24kHz hoặc 44.1kHz.
- **Chất lượng**: Thu âm sạch, ít tạp âm nền (không có nhạc nền BGM).

### Câu lệnh mẫu:
```bash
python3 skills/directing-stickman-videos/scripts/vieneu-local.py \
    --text "Chào mừng các bạn đã quay trở lại với series hoạt hình người que!" \
    --output productions/audio/clone_intro.wav \
    --ref-audio samples/director_voice.wav
```
*(Nếu file mẫu là tiếng nước ngoài và chỉ muốn lấy âm sắc để đọc tiếng Việt chuẩn, thêm cờ `--no-ref-codes`)*.

---

## 4. Cơ Chế Auto-Fit Atempo Timing

### Vấn đề:
VieNeu-TTS là mô hình autoregressive sinh âm thanh tự nhiên theo ngữ cảnh ngữ âm, **không có tham số tốc độ trực tiếp** trong bước suy luận (inference). Tuy nhiên trong hoạt hình Stickman:
- Một shot diễn xuất kéo dài chính xác `4.5 giây`.
- Nếu giọng đọc dài `5.2 giây`, video sẽ bị trôi timeline hoặc cảnh sau bị đè/cắt âm thanh.
- Nếu rút ngắn cảnh video theo giọng đọc, nhịp dựng (pacing) và beat nhạc nền sẽ bị phá vỡ.

### Giải pháp kỹ thuật:
Script `vieneu-local.py` tích hợp bộ lọc **FFmpeg `atempo` (Pitch-Preserving Audio Time-Stretching)**:
1. Sau khi sinh âm thanh raw, đo thời lượng thực tế $T_{\text{raw}}$ bằng `ffprobe`.
2. Tính toán tỷ lệ co giãn cần thiết:
   $$\text{Ratio} = \frac{T_{\text{raw}}}{T_{\text{target}}}$$
3. Giới hạn tỷ lệ an toàn trong ngưỡng $[0.70x, 1.60x]$ để đảm bảo âm thanh tự nhiên nhất:
   - **Tăng tốc ($> 1.0$)**: Khi câu đọc quá dài so với slot cảnh.
   - **Kéo dài ($< 1.0$)**: Khi câu đọc quá ngắn cần lấp đầy nhịp cảnh.
   - **Giữ nguyên cao độ (Pitch-preserving)**: Không bị đổi tần số F0 (không gây hiệu ứng "chuột sóc" sóc chuột Chipmunk hay méo giọng ma quỷ).
4. Chuỗi bộ lọc tự động phân rã các bước nếu ratio vượt ngoài khoảng $[0.5, 2.0]$.

### Tùy chọn dòng lệnh:
- `--target-duration <SECONDS>`: Đặt thời lượng mục tiêu cần khớp.
- `--atempo <RATIO>`: Chỉ định trực tiếp tỷ lệ tốc độ cố định (ví dụ `1.15` cho tốc độ +15%).
- `--min-speed <FLOAT>`: Giới hạn tối thiểu tốc độ (mặc định: `0.70`).
- `--max-speed <FLOAT>`: Giới hạn tối đa tốc độ (mặc định: `1.60`).
- `--trim-silence`: Tự động cắt bỏ khoảng lặng thừa ở đầu và cuối câu đọc.

---

## 5. Hướng Dẫn Sử Dụng Dòng Lệnh Nhanh

### 1. Xem danh mục giọng có sẵn:
```bash
python3 skills/directing-stickman-videos/scripts/vieneu-local.py --list-voices
```

### 2. Thu âm lời thoại thường với giọng "Thiện Minh" (Người dẫn chuyện):
```bash
python3 skills/directing-stickman-videos/scripts/vieneu-local.py \
    --text "Ngày xửa ngày xưa, trong một trang giấy trắng, có một người que tên là Bob." \
    --voice "Thiện Minh" \
    --output narration.wav \
    --replace
```

### 3. Tự động ép vừa slot cảnh 3.8 giây (Auto-fit):
```bash
python3 skills/directing-stickman-videos/scripts/vieneu-local.py \
    --text-file shot_02_script.txt \
    --voice "Hải Đăng" \
    --target-duration 3.8 \
    --trim-silence \
    --output shot_02_fitted.wav \
    --replace
```

### 4. Kết quả JSON trả về:
```json
{
  "output": "/Users/xitrum/Documents/Dev/stickman/shot_02_fitted.wav",
  "voice": "Hải Đăng",
  "init_seconds": 12.8,
  "infer_seconds": 3.4,
  "raw_duration": 4.62,
  "target_duration": 3.8,
  "applied_atempo": 1.216,
  "atempo_adjusted": true,
  "duration": 3.798,
  "sample_rate": 44100,
  "channels": 1,
  "codec": "pcm_s16le"
}
```

---

## 6. Liên kết tham khảo
- [Vietnamese Autopilot Pipeline](file:///Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/vietnamese-autopilot.md)
- [Báo cáo cải tiến từ xStudio](file:///Users/xitrum/Documents/Dev/stickman/docs/bao-cao-cai-tien-tu-xstudio.md)
- [VieNeu Local Script](file:///Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/scripts/vieneu-local.py)
