# Autopilot tiếng Việt — quick-start (bản patch trên fork phongsun01)

> Chỉ áp dụng cho bản skill đã patch này (xem `PATCH-NOTES.md`).
> Không dùng Gemini ở bước nào. Quy trình duyệt sample → approve → render
> giữ nguyên như Autopilot gốc; xem thêm [narration language and timing](narration-language.md).

## 1. Chuẩn bị (làm 1 lần)

```bash
cd skills/directing-stickman-videos
npm ci
node scripts/autopilot.mjs doctor   # node, ffmpeg, ffprobe, canvas, sharp, fonts đều true
```

Cài VieNeu local (TTS tiếng Việt, chạy CPU, không cần key):

```bash
python3 -m venv ~/workspace/vieneu-venv
~/workspace/vieneu-venv/bin/pip install vieneu
```

Tải model v3 Turbo từ Hugging Face rồi materialize về một thư mục chung
(`cp -rL` từ HF cache vào `~/workspace/vieneu-models/`, gồm 2 thư mục con
`v3-turbo-onnx/` và `moss-codec-onnx/`). Bước này bắt buộc: `Vieneu()` gốc
tải model rải rác nhiều thư mục blob nên ONNX báo lỗi
"External data path escapes model directory".

Cài faster-whisper (làm timestamps phụ đề, thay cho openai-whisper vốn đòi
torch CUDA ~1 GB trên máy chỉ có CPU):

```bash
python3 -m venv ~/workspace/whisper-venv
~/workspace/whisper-venv/bin/pip install faster-whisper soundfile
```

## 2. Làm 1 video (mẫu đã kiểm chứng: "Áp lực của người trưởng thành")

```bash
node scripts/autopilot.mjs init /absolute/path/my-video --style B1
# Viết script tiếng Việt, duyệt script trước (50 từ ≈ 12 giây đọc tự nhiên;
# muốn ~20 giây thì viết ~80 từ, đừng kéo dài audio giả tạo)

# Lời dẫn bằng VieNeu local, giọng Hải Đăng (mặc định)
python3 scripts/vieneu-local.py --text-file script.txt \
  --output /absolute/path/my-video/narration.wav --voice "Hải Đăng"
# Script tự kiểm tra file bằng ffprobe và in thời lượng thật — dùng số này
# để viết shots, đừng ước lượng bằng số từ.

# Word timestamps tiếng Việt
python3 scripts/align_captions_fast.py /absolute/path/my-video/narration.wav \
  --output /absolute/path/my-video/words.json --language vi \
  --script script.txt
node scripts/autopilot.mjs captions /absolute/path/my-video/words.json \
  /absolute/path/my-video/captions.json --lead 0.15
# Kiểm tra lại text phụ đề bằng mắt: Whisper nghe sai thì sửa 1:1 theo
# script đã duyệt, giữ nguyên timestamps (flag --script làm sẵn việc này
# khi số từ khớp).

# Font: headline tiếng Việt KHÔNG dùng được font Caveat mặc định (thiếu dấu
# ệ ồ ữ ắ ơ ư ố ả). Runtime đã tự fallback sang NotoSans khi gặp dấu tiếng
# Việt và chưa chọn font; muốn chữ đậm thì set trong project.json:
#   "font": "assets/NotoSans-Bold.ttf"
# Kiểm tra trước khi render:
python3 scripts/check_font.py assets/fonts/Caveat.ttf \
  --project /absolute/path/my-video/project.json   # sẽ báo thiếu dấu
python3 scripts/check_font.py assets/fonts/NotoSans.ttf \
  --project /absolute/path/my-video/project.json   # phải pass

# Ảnh minh họa: tự tạo hoặc đưa ảnh PNG/JPEG local vào, không cần Gemini image.
# Viết project.json (shots phủ kín narration + lead/tail, không gap/overlap),
# rồi:
node scripts/autopilot.mjs validate /absolute/path/my-video/project.json --seconds 20
node scripts/autopilot.mjs preview /absolute/path/my-video/project.json --seconds 20
# Lưu ý: nếu narration chỉ dài 12 giây mà xin preview 20 giây, CLI sẽ cảnh
# báo và preview ra 12 giây — đó là đúng, không phải lỗi.
# Xem + nghe preview, duyệt rồi mới:
node scripts/autopilot.mjs approve /absolute/path/my-video/project.json --note "…"
node scripts/autopilot.mjs render /absolute/path/my-video/project.json
```

## 3. Các lỗi đã gặp và cách tránh

| Lỗi | Cách tránh |
|---|---|
| `Vieneu()` lỗi ONNX external-data path | Luôn dùng `scripts/vieneu-local.py` (hàm `load_vieneu()`), không gọi `Vieneu()` trần |
| `preview --replace PROJECT` báo sai đường dẫn | Đã sửa CLI: `--replace` và `--seconds` đặt trước hay sau PROJECT đều được |
| Headline tiếng Việt mất dấu | Runtime tự fallback NotoSans; hoặc set `project.font` là NotoSans-Bold |
| `align_captions.py` đòi torch CUDA | Dùng `align_captions_fast.py` (faster-whisper, CPU int8) |
| Preview ngắn hơn 20 giây | Bình thường: thời lượng = audio thật. Muốn dài hơn thì viết thêm script |
| Whisper nghe sai từ | Dùng `--script` để sửa text 1:1, giữ timestamps; kiểm tra lại bằng mắt |
