# Báo cáo Cải tiến Stickman Video Director
### Phân tích đối chiếu với xStudio / iContent Studio

> **Ngày lập:** 2026-11-16  
> **Nguồn tham chiếu:** `/Users/xitrum/Documents/Dev/xStudio` (iContent Studio v0.8.1)  
> **Dự án đích:** `phongsun01/stickman-video-director`

---

## Tóm tắt điều hành

Qua so sánh kiến trúc và tính năng giữa **iContent Studio** (xStudio — một production studio AI hoàn chỉnh) và **Stickman Video Director** (một AI-skill cho agent/CLI), xác định được **18 nhóm cải tiến** khả thi. Các cải tiến được phân loại theo **độ ưu tiên** dựa trên tác động thực tế và mức độ phức tạp triển khai.

| Mức ưu tiên | Số nhóm | Tác động |
|---|---|---|
| 🔴 Cao (nên làm ngay) | 6 | Lấp lỗ hổng nghiêm trọng ảnh hưởng chất lượng output |
| 🟡 Trung bình (sprint tiếp theo) | 7 | Nâng cao trải nghiệm sản xuất và khả năng tự động hóa |
| 🟢 Thấp (backlog dài hạn) | 5 | Tính năng mở rộng, không ảnh hưởng workflow hiện tại |

---

## 🔴 NHÓM 1 — TTS / Voiceover Nâng cao

### Vấn đề hiện tại
Stickman chỉ có VieNeu local adapter cơ bản (`vieneu-local.py`) với một giọng mặc định "Hải Đăng". Không có cơ chế tự động điều chỉnh tốc độ khi TTS output dài hơn slot thời gian cho phép.

### Giải pháp từ xStudio

**1.1 Chiến lược đồng bộ hóa TTS ↔ Timeline**

xStudio dùng pipeline 4 bước khi TTS vượt quá thời lượng slot:
```
1. Phát ở tốc độ bình thường → đo độ dài thực tế
2. Nếu > slot × 1.35: gửi yêu cầu LLM rút gọn script
3. Nếu vẫn dài: tăng tham số `rate` của TTS engine
4. Phần còn lại: FFmpeg atempo (pitch-preserving), tối đa 1.6×
```

Stickman hiện phát ra cảnh báo stderr (`Warning: preview requested Xs but narration is Ys`) nhưng không tự xử lý. **Nên thêm:**
- Flag `--auto-trim` trong `vieneu-local.py` để tự tính tỷ lệ atempo
- Báo cáo `atempo_applied: 1.14` trong verification JSON

**1.2 Catalog đầy đủ 25 giọng VieNeu**

Hiện tại chỉ document "Hải Đăng" làm default. xStudio document đầy đủ:
- Nam: Thiện Minh, Hải Đăng, Quang Sơn
- Nữ: Trúc Ly, Mai Anh, Ngọc Huyền

**Nên tạo:** `references/vieneu-voice-catalog.md` liệt kê tất cả 25 giọng với audio demo path, pitch F0 median, usecase khuyến nghị (narrator/character/narration).

**1.3 Voice Cloning từ audio mẫu 3–8 giây**

xStudio hỗ trợ `--ref-audio` để clone giọng bất kỳ. VieNeu v3 Turbo đã có tính năng này nhưng `vieneu-local.py` chưa expose flag `--ref-audio`. Thêm vào:
```bash
python scripts/vieneu-local.py \
  --text-file script.txt \
  --output narration.wav \
  --ref-audio samples/character_voice.wav   # MỚI
```

**1.4 Từ điển phát âm**

xStudio có pronunciation dictionary: `TikTok → Tíc Tốc`, tên thương hiệu, từ Hán-Việt. Stickman nên có `references/pronunciation-vi.json` để VieNeu phát âm đúng thuật ngữ kỹ thuật/tên riêng mà không ảnh hưởng subtitle.

---

## 🔴 NHÓM 2 — Caption Splitter Tiếng Việt

### Vấn đề hiện tại
`groupWords()` trong `autopilot.mjs` chia caption theo word count tiếng Anh. Tiếng Việt là ngôn ngữ âm tiết — mỗi âm tiết là một "word" trong tokenizer, dẫn đến caption tiếng Việt bị chia sai ngữ nghĩa.

Ví dụ hiện tại (sai):
```
"học sinh" "trường" → "học sinh trường"  ← cắt sai ranh giới ngữ pháp
```

### Giải pháp

**2.1 Vietnamese-aware `groupWords()`**

xStudio dùng thời gian ASR pause để phân đoạn — không phải word count. Nên thêm logic:
```js
// Trong autopilot-core.mjs
function groupWordsVi(words, maxSilence = 0.4) {
  // Split tại điểm pause > maxSilence hoặc dấu chấm/phẩy
  // Merge nhóm ngắn < 0.8s với nhóm kề
  // Giới hạn 7 âm tiết/dòng cho 9:16, 10 cho 16:9
}
```

**2.2 Thêm `narration_language` vào project.json**

Khi `narration_language: "vi"`, tự động:
- Dùng groupWordsVi() thay groupWords()
- Giảm words-per-line xuống 7–8 (Việt dài hơn Anh về pixel)
- Áp dụng NotoSans thay Caveat không cần flag

**2.3 Document chuẩn timing tiếng Việt**

Thêm vào `references/narration-language.md`:
```
Tiếng Việt: ~80 âm tiết ≈ 20s (Hải Đăng, natural rate)
            ~50 âm tiết ≈ 12–13s
Tiếng Anh:  ~50 words ≈ 20s
Lưu ý: Đừng dùng word count tiếng Anh cho script tiếng Việt
```

---

## 🔴 NHÓM 3 — EBU R128 Mastering Chính xác

### Vấn đề hiện tại
Stickman target `-16 to -14 LUFS` nhưng không có verification sau render. xStudio đạt chính xác **-14.0 LUFS** với True-Peak ≤ -1.5 dBTP qua biquad K-weighted filter + 4× sinc interpolation.

### Giải pháp

**3.1 Post-render loudness verification**

Thêm vào `autopilot.mjs render`:
```js
// Sau khi render xong, chạy ebur128 measurement
const lufs = await measureLoudness(outputPath); // via ffprobe
if (Math.abs(lufs.integrated - (-14)) > 0.5) {
  console.error(`Warning: output loudness ${lufs.integrated} LUFS (target: -14 LUFS)`);
}
```

**3.2 Smart Ducking BGM**

xStudio duck BGM **-14dB** trong 250ms fade khi TTS nói, recover khi silence. Stickman chỉ có `music.gain` tĩnh (0–0.2). Nên thêm field:
```json
"music": {
  "path": "bgm.mp3",
  "gain": 0.08,
  "ducking": {"target_gain": 0.01, "fade_ms": 250}
}
```

**3.3 Procedural SFX bổ sung**

xStudio có 11 loại procedural SFX (không cần file WAV). Stickman chỉ có 5 (`tap`, `paper`, `pop`, `chime`, `jingle`). Nên thêm:
- `whoosh` — transition sweep
- `riser` — tension build-up (B4 chuyên dùng)
- `impact` — climax hit
- `scratch` — vinyl scratch / glitch
- `pad` — ambient tone

---

## 🔴 NHÓM 4 — Post-render Quality Control

### Vấn đề hiện tại
Stickman không có automated QC sau khi render. Người dùng phải tự xem video để phát hiện freeze frame, khoảng lặng, lỗi audio.

### Giải pháp từ xStudio

**4.1 QC tự động sau `render`**

Thêm script `scripts/qc-verify.mjs` chạy FFmpeg filters:
```bash
# Black screen detection
ffprobe -f lavfi -i "movie=output.mp4,blackdetect[out0]"

# Freeze detection (> 2s)
ffprobe -vf freezedetect=n=0.003:d=2

# Silence detection (> 1s gaps)
ffprobe -af silencedetect=n=-50dB:d=1

# EBU R128 loudness
ffprobe -af ebur128=peak=true
```

**4.2 Verification report JSON**

Sau render, tạo `verification.json` cạnh MP4:
```json
{
  "output": "film.mp4",
  "duration_s": 62.3,
  "lufs": -13.8,
  "true_peak_dbtp": -1.2,
  "issues": [
    {"type": "freeze", "time_s": 23.4, "duration_s": 2.1},
    {"type": "silence", "time_s": 45.0, "duration_s": 1.3}
  ],
  "qa_passed": false
}
```

**4.3 Caption-face collision check (B5/B6)**

Dùng `sharp` (đã có trong deps) để detect vùng caption có overlap với vùng mặt nhân vật trong B5/B6. Flag nếu caption che mặt presenter.

---

## 🔴 NHÓM 5 — Multi-speaker / Dialogue Support

### Vấn đề hiện tại
Stickman chỉ hỗ trợ 1 narrator duy nhất (hoặc Brian cho B4). Không có cơ chế tự động phân giọng khi có dialogue giữa nhiều nhân vật.

### Giải pháp từ xStudio

**5.1 Per-character TTS routing**

xStudio gán `voice_id` riêng cho từng nhân vật trong storyboard. Stickman nên hỗ trợ:
```json
"voice": {
  "path": "narration.wav",
  "characters": {
    "nhan_vat_a": {"vieneu_voice": "Trúc Ly", "path": "char_a.wav"},
    "nhan_vat_b": {"vieneu_voice": "Hải Đăng", "path": "char_b.wav"}
  }
}
```

**5.2 Dialogue shot type**

B4 đã có `dialogue` field nhưng chưa được leverage cho automated voice routing. Nên standardize across B1–B3:
```json
"shots": [{
  "start": 5.2, "end": 8.1,
  "speaker": "nhan_vat_a",
  "layers": [...]
}]
```

---

## 🔴 NHÓM 6 — Storyboard Narrative Structure Templates

### Vấn đề hiện tại
Stickman có `storyboard-template.md` nhưng không có cấu trúc narrative cụ thể để agent lựa chọn. xStudio có **8 proven narrative structures** giúp tăng tỷ lệ engagement.

### Giải pháp

**6.1 Story Flows trong `references/director-story-pacing.md`**

```
1. Problem-Agitate-Solution (PAS)
   Hook: đặt vấn đề (5s) → Khuếch đại nỗi đau (10s) → Giải pháp (20s) → CTA (5s)

2. Three Reasons Why
   Hook → Lý do 1 (10s) → Lý do 2 (10s) → Lý do 3 (10s) → Tổng kết + CTA

3. Myth Buster
   "Nhiều người nghĩ X..." → Thực tế là Y → Chứng minh → Insight

4. Before-After
   Trạng thái trước (5s) → Chuyển đổi (3s) → Trạng thái sau (10s) → Giải thích

5. Product Demo
   Problem → "Hãy để tôi chỉ cho bạn..." → Demo step-by-step → Kết quả

6. Fact Ledger (Hallucination Guard)
   Mỗi claim phải có source, fact không được lặp không có lý do
```

**6.2 Fact Ledger cho A-mode**

xStudio có cơ chế Fact Ledger chống hallucination. Stickman nên thêm:
```md
## Fact Ledger (bắt buộc cho video thông tin)
| Claim | Source | Lần đầu dùng | Các lần sau |
|-------|--------|-------------|------------|
```

---

## 🟡 NHÓM 7 — Face-aware Layer Region Suggestion (9:16)

### Vấn đề hiện tại
Stickman có B1/B2/B3 native portrait contract nhưng `portrait.regions` được author thủ công. Không có cơ chế tự động suggest vùng focal dựa trên layer positions.

### Giải pháp

Thêm script `scripts/suggest-portrait-regions.mjs`:
```bash
node scripts/suggest-portrait-regions.mjs project.json \
  --output portrait-suggestions.json
# Phân tích bounding box của layer quan trọng (pose, main image)
# Suggest focal_regions cho từng shot tự động
```

xStudio dùng YuNet face detection. Stickman dùng layer geometry analysis (phù hợp hơn với illustration).

---

## 🟡 NHÓM 8 — Kinetic Typography / Subtitle Styles

### Vấn đề hiện tại
Stickman chỉ có 1 kiểu caption tĩnh. xStudio có **6 preset styles** bao gồm Kinetic Typography và Karaoke word-highlight.

### Giải pháp

**8.1 `caption_style` field trong project.json**
```json
"caption_style": {
  "preset": "tiktok",
  "highlight_color": "#FFD700",
  "scale_bounce": 1.24
}
```

**8.2 Style gợi ý theo B-style**
- B1: `classic` (handwritten feel)
- B2: `cinema` (white box)
- B4: `tiktok` (word-highlight thriller)
- B6: Archivo Black bold, không decoration

---

## 🟡 NHÓM 9 — Platform Export Packages

### Vấn đề hiện tại
Stickman chỉ export MP4 + SRT/VTT. xStudio tạo **multi-platform package** cho TikTok, Reels, Shorts, YouTube với thumbnail + description + hashtags tự động.

### Giải pháp

**9.1 `autopilot.mjs package` command**
```bash
node scripts/autopilot.mjs package film.mp4 \
  --title "Tiêu đề video" \
  --style b1 \
  --platforms tiktok,youtube,reels
# Output:
#   package/tiktok/video_9x16.mp4 + caption.txt + hashtags.txt
#   package/youtube/video_16x9.mp4 + description.txt
```

**9.2 Auto-generated description từ captions**

Dùng captions.json + storyboard để generate mô tả video + hashtag tự động bằng LLM, lưu vào `metadata.description` trong project.json sau `approve`.

---

## 🟡 NHÓM 10 — Thumbnail Generator

### Vấn đề hiện tại
Stickman có `thumbnail-publishing-kit.md` nhưng không có tool generate thumbnail tự động từ contact sheet.

### Giải pháp

```bash
node scripts/autopilot.mjs thumbnail project.json \
  --frame 00:00:03 \
  --text "Tiêu đề ngắn" \
  --preset bold    # bold | minimal | dark | split
# Output: thumbnail.jpg (< 2MB, 16:9 hoặc 1:1)
```

**4 preset thumbnails cơ bản** (port từ xStudio):
- Nền tối + text nổi vàng (B4)
- Nền sáng + text đen (B1/B2)
- Split 50/50 before/after
- Closeup shot + overlay text

---

## 🟡 NHÓM 11 — Tiếng Việt: Pronoun Lock & Hán-Việt

### Vấn đề hiện tại
Stickman không có cơ chế track pronoun tiếng Việt qua nhiều scene. xStudio pre-reads toàn bộ video để establish `anh/em/tôi/mình` conventions.

### Giải pháp

**11.1 Pronoun lock** trong `references/narration-language.md`:
```
Trước khi viết script, xác định:
- Người kể chuyện xưng: tôi / mình / ta
- Gọi người xem là: bạn / các bạn / mình
- Giữ nhất quán xuyên suốt video
- Lưu vào metadata.pronoun_profile trong project.json
```

**11.2 Từ điển Hán-Việt**

Thêm `references/han-viet-dictionary.md` cho A5 Historical Cartoon biết gọi nhân vật lịch sử đúng (ví dụ: Lý Thế Dân, Tần Thủy Hoàng).

---

## 🟡 NHÓM 12 — Progress Streaming

### Vấn đề hiện tại
Stickman là CLI thuần — không có progress indicator trong quá trình render. Với B4/B6 build lớn (60–70s), user không biết tiến trình.

### Giải pháp

**12.1 Progress output chuẩn**
```
[  0%] Loading project...
[ 15%] Rendering shot 1/8 (0.0s–3.5s)...
[ 85%] Encoding final MP4...
[100%] Done: film.mp4 (62.3s, -14.0 LUFS) ✅
```

**12.2 `--progress-json` flag**
```bash
node scripts/autopilot.mjs render project.json --progress-json
# STDOUT: {"phase":"render","shot":2,"total":8,"pct":25}
```

---

## 🟡 NHÓM 13 — Offline / Local LLM Support

### Vấn đề hiện tại
A-mode Director yêu cầu Gemini/Claude API. Không có offline option cho user không có API key hoặc ở vùng bị giới hạn.

### Giải pháp

**13.1 Ollama adapter**
```bash
AUTOPILOT_PROVIDER=ollama \
OLLAMA_MODEL=qwen3:4b \
node scripts/autopilot.mjs init my-video --style b2
```

Document trong `references/autopilot.md` → `selected-provider-execution` section. xStudio dùng Hy-MT2 1.8B (Tencent) + Qwen3 local — cùng ecosystem.

---

## 🟢 NHÓM 14 — Vocal Separation cho Source Audio

Thêm preprocessing script dùng **demucs** (hoặc tích hợp với iContent UVR):
```bash
python scripts/separate-vocal.py mixed_narration.wav \
  --output narration_clean.wav
```
Hữu ích khi user có recording sẵn có BGM lẫn vào.

---

## 🟢 NHÓM 15 — Background Removal cho B5 Character Art

Port **u2netp** (4.5MB ONNX) từ xStudio:
```bash
python scripts/remove-bg.py character.jpg \
  --output character_transparent.png
```
Tích hợp vào B5 workflow documentation.

---

## 🟢 NHÓM 16 — 58 Video Style Catalog (CineCode)

xStudio có **58 cinematic styles** phân loại thành 9 nhóm. Stickman có thể mở rộng A-mode style catalog và port **5 HTML5 Canvas motion templates** ưu tiên:
1. Kinetic Typography
2. Glassmorphism (phù hợp B2)
3. Neon Glow (phù hợp B3)
4. Comic Book (phù hợp B1/B4)
5. Blueprint (phù hợp B2 tech)

---

## 🟢 NHÓM 17 — SQLite Project Registry

Lightweight project index tại `~/.stickman/projects.db`:
```bash
node scripts/autopilot.mjs list-projects ~/Videos/stickman/
# ID    | Style | Date       | Duration | Status
# vid01 | B1    | 2026-11-10 | 62.3s    | rendered ✅
# vid02 | B4    | 2026-11-15 | 68.1s    | preview only
```

---

## 🟢 NHÓM 18 — Windows Installer & Doctor Nâng cấp

**18.1 `install-windows.cmd`** style launcher:
```batch
:: Check Node.js, FFmpeg, install dependencies
:: Set up vieneu-venv và whisper-venv tự động
:: Verify all tools
echo Installation complete!
```

**18.2 `doctor` command mở rộng** (hiện chỉ check key presence):
```
✅ node v26.13.0
✅ ffmpeg 7.1 / ffprobe 7.1
✅ @napi-rs/canvas
⚠️  sharp: not found (B5 PNG review sẽ bị giới hạn)
✅ NotoSans.ttf (SHA verified)
✅ VieNeu TTS: vieneu-venv OK — 25 voices available
✅ faster-whisper: whisper-venv OK
❌ SFX Library: D:\Video creator\... not found
   → Set SFX_THU_VIEN_DIR env variable
```

---

## Lộ trình Triển khai Đề xuất

- [x] **Sprint 1: Cải tiến Âm thanh & Đồng bộ Tiếng Việt (ĐÃ HOÀN THÀNH TOÀN BỘ)**
  - [x] Cấu hình đường dẫn mặc định `sfx-thu-vien` cho macOS (`/Users/xitrum/Documents/Dev/library/sfx-thu-vien`)
  - [x] **Tính năng Auto SFX (`autopilot.mjs auto-sfx`):** Tự động phát hiện hành động kịch bản và chèn SFX căn onset
  - [x] **Bổ sung kho âm thanh Cinematic / UI từ `Motion-graphics-skill-stack-store/sound-effects` vào catalog:** Gộp 55 âm thanh Whooshes, Risers, Clicks, Data Collect, Pop, Gear vào chỉ mục tra cứu và Auto-score
  - [x] **VieNeu Voice Catalog & cơ chế auto-fit atempo timing:** Danh mục 12 giọng tiếng Việt (`references/vieneu-voice-catalog.md`), hỗ trợ Voice Cloning (`--ref-audio`) và tự động co giãn thời lượng fit slot cảnh bằng FFmpeg atempo pitch-preserving (`--target-duration`, 0.7x - 1.6x)
  - [x] **Bộ ngắt phụ đề tiếng Việt chuẩn ngữ pháp (`Vietnamese Caption Splitter`):** Tự động nhận diện từ nối/dấu câu/âm tiết tiếng Việt trong `groupWords()`
  - [x] **Đo kiểm và chuẩn hóa âm lượng EBU R128 (-14 LUFS) sau render & Smart Ducking BGM:** Tích hợp bộ đo EBU R128 ITU-R BS.1770-4 (`scripts/audio-master-lufs.py`), chuẩn hóa 2-pass -14 LUFS, Smart Ducking BGM (-14dB sidechaincompress) và tự động đo kiểm ghi báo cáo `report.audio_loudness` sau render (`references/audio-loudness-and-ducking.md`)

- [ ] **Sprint 2: Đảm bảo Chất lượng & Kịch bản Chuyên sâu**
  - [x] **Xuất báo cáo QC sau render (`verification.json`):** Tự động quét đứng hình (`freeze`), đoạn câm (`silence`), độ to (`loudness`), va chạm phụ đề (`caption-collision`), tính điểm chất lượng QA Score 0-100 (`references/post-render-qc.md`)
  - [ ] Hỗ trợ Multi-speaker / Dialogue TTS routing theo từng nhân vật
  - [x] **Tích hợp 6 Narrative Story Flows vào template kịch bản:** PAS, Three Reasons Why, Myth Buster, Before-After-Bridge, Hero's Journey, Curiosity Gap (`references/narrative-story-flows.md`), hỗ trợ sinh khung tự động `autopilot.mjs storyboard --flow <key>` (`scripts/story-flow-scaffold.py`)

- [ ] **Sprint 3: Nâng cấp Trực quan & Đóng gói Phân phối**
  - [ ] Tích hợp 20 Motion Graphics Templates (làm layer overlay / background động)
  - [ ] Kinetic Typography (chữ nảy TikTok / Karaoke style)
  - [ ] Công cụ đóng gói đa nền tảng (`autopilot.mjs package` cho TikTok, Reels, Shorts, YouTube)
  - [ ] Trình tạo Thumbnail tự động theo preset từ Contact Sheet
  - [ ] Hiển thị tiến trình render chi tiết (Progress streaming / JSON)

- [ ] **Backlog dài hạn:**
  - [ ] Tách giọng / nhạc nền (Vocal Separation UVR-MDX)
  - [ ] Tách nền nhân vật B5 tự động (u2netp)
  - [ ] Sổ bộ lưu trữ dự án cục bộ (SQLite Project Registry)
  - [ ] Trình cài đặt tự động 1-click cho Windows / macOS

---

## Ma trận ưu tiên theo Impact × Effort

| | Effort Thấp | Effort Cao |
|---|---|---|
| **Impact Cao** | 🔴 Story Flow templates (docs) · 🔴 VieNeu catalog · 🔴 EBU R128 check · 🟡 Progress streaming | 🔴 Vietnamese caption splitter · 🔴 Multi-speaker TTS · 🟡 Kinetic Typography |
| **Impact Thấp** | 🟡 Pronoun lock docs · 🟡 Pronunciation dict | 🟢 SQLite registry · 🟢 Background removal · 🟢 Motion templates |

---

---

## 🎯 PHẦN ĐẶC BIỆT: TÍCH HỢP TRỰC TIẾP 2 BỘ THƯ VIỆN TẠI `/Users/xitrum/Documents/Dev/library`

Thực tế kiểm tra cho thấy cả 2 bộ tài nguyên này chính là các tài nguyên cốt lõi mà xStudio từng khai thác trên Windows (`D:\Video creator\Hoang Lma\...`). Hiện tại chúng đã nằm sẵn trên máy tại `/Users/xitrum/Documents/Dev/library`. Dưới đây là phương án kỹ thuật chi tiết để Stickman tích hợp và tận dụng tối đa:

### 1. Tận dụng `sfx-thu-vien` (/Users/xitrum/Documents/Dev/library/sfx-thu-vien)

Bộ này gồm **585 file** (439 SFX chia 50 danh mục + 146 track BGM), có sẵn metadata `catalog.json`, `do_to.json` (độ to LUFS + onset va chạm chuẩn ms) và `su_kien.json`.

#### 1.1 Cấu hình đường dẫn mặc định & fallback cross-platform
Hiện tại các script của Stickman mặc định tìm ở Windows `D:\...`. Cần chuẩn hóa cấu hình ưu tiên tìm tại local Mac:
* **Ưu tiên 1:** Biến môi trường `SFX_THU_VIEN_DIR`.
* **Ưu tiên 2:** `/Users/xitrum/Documents/Dev/library/sfx-thu-vien`.
* **Ưu tiên 3:** Fallback Windows / Linux paths cũ.

Cập nhật trong `scripts/sfx-catalog-local.py` & `scripts/autopilot-core.mjs`:
```python
DEFAULT_PATHS = [
    Path("/Users/xitrum/Documents/Dev/library/sfx-thu-vien"),
    Path.home() / "Documents/Dev/library/sfx-thu-vien",
    Path("D:/Video creator/Hoang Lma/sfx-thu-vien")
]
```

#### 1.2 Tự động chấm điểm và chèn SFX (Auto SFX Scoring)
Thay vì bắt user/agent phải tự tìm file audio thủ công bằng CLI rồi paste vào `project.json`:
* Tạo lệnh `node scripts/autopilot.mjs auto-sfx project.json`:
  1. Đọc danh sách `shots` và `captions` trong `project.json`.
  2. Dựa vào từ khóa hành động trong shot (vd: "đấm", "bước đi", "mở cửa", "bất ngờ", "ting") đối chiếu với `data/su_kien.json` của `sfx-thu-vien`.
  3. Tự động tính toán thời điểm bắt đầu: `sfx_time = action_time - (onset_ms / 1000)`.
  4. Ghi trực tiếp danh sách `sfx: [...]` vào `project.json` với gain chuẩn theo `do_to.json`.

---

### 2. Tận dụng `Motion-graphics-skill-stack-store` (/Users/xitrum/Documents/Dev/library/Motion-graphics-skill-stack-store)

Bộ này cung cấp engine đồ họa chuyển động mạnh mẽ của Claude Code Skill v3.5.2 với **20 reference motion styles** và gói SFX bổ trợ (Whooshes, Risers, Clicks, Data Collect...).

#### 2.1 Bổ sung gói SFX Cinematic/UI vào bộ máy âm thanh Stickman
Thư mục `sound-effects` của bộ này chứa các âm thanh hiện đại phương Tây mà `sfx-thu-vien` còn thiếu:
* `Whooshes/`: Smooth, fast, cinematic whoosh (cho các chuyển cảnh zoom/pan nhanh).
* `Risers/`: Âm thanh căng thẳng dồn dập (cực kỳ thích hợp cho phong cách **B4 Survival Thriller**).
* `Data Collect/` & `Clicks/`: Hiệu ứng HUD, số liệu nhảy (cho phong cách **B2 Minimalist Tech** / Explainer).
* **Cách tích hợp:** Cho `sfx-catalog-local.py` quét thêm thư mục `/Users/xitrum/Documents/Dev/library/Motion-graphics-skill-stack-store/sound-effects` để gộp vào chỉ mục chung.

#### 2.2 Tích hợp 20 Phong cách Motion Graphics làm Overlay/Background cho Stickman
Trong thư mục `20-reference-motion-styles` chứa các source code HTML5 Canvas/Playwright hoàn chỉnh:
* **Kinetic Typography:** Tạo chữ chạy nảy theo nhịp nói (TikTok/Reels style) thay vì phụ đề tĩnh.
* **Comic Book & Retro VHS:** Làm background hoặc overlay hạt nhiễu, khung truyện tranh cho **B1** và **B3 Retro TV**.
* **Neon Glow & Blueprint:** Làm visual backdrop kỹ thuật cho các video giải thích công nghệ/logic.
* **Cách tích hợp:**
  1. Tạo cầu nối `scripts/render-motion-overlay.mjs` gọi Playwright/Puppeteer render các template này thành video transparent WebM/MOV (alpha channel).
  2. Bổ sung loại layer mới vào `project.json`:
     ```json
     {
       "type": "motion_overlay",
       "template": "kinetic-type", // hoặc "retro-vhs", "blueprint"
       "params": { "accent_color": "#00ffcc" }
     }
     ```
  3. Engine compositing của Stickman (`autopilot-render.mjs`) sẽ hòa trộn (blend/composite) layer motion này trực tiếp lên video stickman trong lúc render FFmpeg.

---

## Ghi chú

Tất cả cải tiến đề xuất dựa trên code và documentation thực tế của xStudio (iContent Studio v0.8.1). Các feature không khả thi do kiến trúc khác nhau (web UI, Windows Job Objects, Ed25519 license) đã được loại bỏ. Chỉ giữ lại các cải tiến thuần **CLI/script/documentation** phù hợp với kiến trúc agent-first của stickman-video-director.

---

*Báo cáo tạo bởi Antigravity Agent — 2026-11-16 18:50 +07:00*  
*Đọc tiếp: [tong-quan-tinh-nang-cho-nguoi-dung.md](tong-quan-tinh-nang-cho-nguoi-dung.md) | [ke-hoach-tich-hop-sfx-va-motion.md](ke-hoach-tich-hop-sfx-va-motion.md)*
