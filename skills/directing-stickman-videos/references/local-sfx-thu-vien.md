# Hướng Dẫn Sử Dụng Kho SFX Cục Bộ (sfx-thu-vien) Cho Stickman Video Director

> **Tài liệu tham chiếu:** `references/local-sfx-thu-vien.md`  
> **Nguồn kho âm thanh:** `sfx-thu-vien` (585 tracks: 439 SFX trong 50 nhóm + 146 BGM)  
> **Bộ công cụ hỗ trợ:** `skills/directing-stickman-videos/scripts/sfx-catalog-local.py`  

---

## 1. TỔNG QUAN KHO ÂM THANH

Kho `sfx-thu-vien` chứa các hiệu ứng âm thanh đã được đo lường chính xác:
- **`dur`**: Thời lượng track (giây).
- **`onset`**: Độ trễ từ đầu file đến điểm va chạm thực tế (tính bằng mili-giây / giây). Giúp căn đúng frame va chạm của Stickman.
- **`peak_db` / `rms_db`**: Độ to và đỉnh biên độ, phục vụ cân bằng âm lượng tự động.

---

## 2. BẢNG ÁNH XẠ NHÓM SFX CHO CÁC SUB-STYLES STICKMAN

| Sub-Style | Mục tiêu thẩm mỹ | Nhóm SFX ưu tiên từ `sfx-thu-vien` | Ví dụ gợi ý |
|---|---|---|---|
| **B1: Classic Stickman** | Phác thảo sổ tay, vẽ bút chì, mộc mạc | `Giấy - xé`, `Bút viết`, `Click - giao diện`, `Pop - nảy`, `Vút - chuyển cảnh` | `102_Paper tear`, `085_Pencil scribble`, `044_Pop sound` |
| **B2: Minimalist Tech** | Tối giản, hiện đại, icon, công nghệ phẳng | `Gõ phím`, `Click - giao diện`, `Glitch`, `Điện thoại`, `Chuông - ding` | `050_Mechanical keyboard typing`, `032_Soft UI click`, `018_Modern ding` |
| **B3: Explainer / Edu** | Giáo dục, trực quan, giải thích khái niệm | `Chuông - ding`, `Lấp lánh - phép thuật`, `Tiền - thưởng`, `Chiến thắng - fanfare`, `Vút - chuyển cảnh` | `121_Ding correct`, `090_Magic sparkle sparkle`, `155_Cash register kaching` |
| **B4: Dark / Psychology** | U ám, tâm lý, rùng rợn, kịch tính | `Nhịp tim`, `Đồng hồ tích tắc`, `Nền u ám - drone`, `Cinematic - boom`, `Bass drop`, `Sấm`, `Gió - bão`, `Rung chuyển - rumble` | `070_Heartbeat fast loop`, `062_Ticking clock intense`, `010_Sub rumble heavy`, `324_studio-bass-drop-3` |
| **B5: Viral Meme / Comedy** | Hài bựa, bất ngờ, tương tác cao, meme | `Đấm - đánh`, `Hài - phản ứng`, `Buzzer - sai`, `Xì hơi`, `Tiếng cười`, `Kính vỡ`, `Huýt sáo` | `283_Doss Hitting punch`, `193_Slap sound`, `180_Wrong buzzer`, `243_Fart short` |

---

## 3. NGUYÊN TẮC PHỐI ÂM 3 LỚP (3-LAYER AUDIO STACK)

Để video đạt chuẩn YouTube (-14 LUFS, không chát chúa, rõ giọng):

```
+-------------------------------------------------------------+
| LỚP 1: NARRATION (GIỌNG ĐỌC AI)                             |
| Target: -14 LUFS / True Peak -1.0 dBTP / Gain: 0 dB (Anchor)|
+-------------------------------------------------------------+
| LỚP 2: SFX (HIỆU ỨNG ĐIỂM NHẤN CĂN THEO ONSET)             |
| Target: -6 dBFS đến -3 dBFS / Delay offset: Frame - Onset   |
+-------------------------------------------------------------+
| LỚP 3: BGM (NHẠC NỀN 146 TRACKS)                            |
| Có voice: -26 dBFS (Ducking -12 dB)                         |
| Đoạn nghỉ/chuyển cảnh: -18 dBFS                             |
+-------------------------------------------------------------+
```

### Quy tắc căn `onset` chính xác
Mỗi file SFX thường có một khoảng im lặng vài chục mili-giây trước khi âm thanh va chạm phát ra.  
**Công thức căn frame:**
$$\text{Start Time của file SFX} = \text{Thời điểm va chạm trong video} - \text{Onset}$$

*Ví dụ:* Stickman vung tay đấm trúng mặt đối thủ ở giây thứ `02.500` (2500ms).  
File `283_Doss Hitting punch` có `onset = 32ms`.  
-> Thời điểm phát file âm thanh = $2500\text{ms} - 32\text{ms} = 2468\text{ms}$ (`02.468s`).  
Khi đó tiếng va chạm nổ ra **ngay đúng frame** nắm đấm chạm mặt!

---

## 4. CÁCH DÙNG CLI TRA CỨU NHANH

Trong terminal hoặc khi viết script tự động:

```bash
# 1. Tìm âm thanh cho một hành động kịch bản:
py skills/directing-stickman-videos/scripts/sfx-catalog-local.py suggest --action "stickman mở cửa bước vào phòng tối" --mood "hồi hộp" --style b4

# 2. Tìm kiếm tự do:
py skills/directing-stickman-videos/scripts/sfx-catalog-local.py search "heartbeat"

# 3. Xuất thông số dạng JSON để nối vào pipeline render:
py skills/directing-stickman-videos/scripts/sfx-catalog-local.py inspect "283_Doss" --json
```
