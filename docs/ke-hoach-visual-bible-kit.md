# Kế Hoạch Triển Khai: Hệ Thống Visual Bible & Entity Registry Cho Stickman

> **Mã kế hoạch:** `PLAN-STICKMAN-VISUAL-BIBLE`  
> **Ngày lập:** 2026-11-16 (Cập nhật chuẩn hóa theo Visual Anchors đã duyệt)  
> **Nguồn gốc dữ liệu chuẩn:** [docs/kit-stickman/kit-stickman.json](file:///Users/xitrum/Documents/Dev/stickman/docs/kit-stickman/kit-stickman.json) & 12 ảnh tham chiếu A4 đã được kiểm duyệt  
> **Trạng thái:** Sẵn sàng triển khai (Ready for Implementation)

---

## 1. Bối Cảnh & Vấn Đề Cốt Lõi

Khi sáng tạo video Stickman hoạt hình qua AI (đặc biệt là Phase B / Muse Prompting, phong cách A4 Cozy Storytelling, hoặc các series dài tập như *Sống Đáng Tiền*, *Chú mèo học...*):
* **Hiện tượng trôi hình (Character & Scene Drift)**: AI không có bộ nhớ ngữ cảnh dài hạn giữa các prompt độc lập. Mỗi lần sinh một shot mới, nhân vật lại bị thay đổi tỷ lệ đầu/thân, đổi mắt, đổi kiểu tóc, nhầm màu áo, thay đổi độ tuổi; bối cảnh đường phố, quán xá bị biến dạng phong cách hoặc sai lệch đặc trưng văn hóa.
* **Gõ lại prompt thủ công theo trí nhớ**: Người viết kịch bản hoặc AI Agent dễ bịa đặt hoặc mô tả không nhất quán (tập 1 tả Bố mặc áo trắng, tập 2 lại tả áo tối màu; bối cảnh phố lúc thì nhà mái ngói, lúc thì nhà kính hiện đại).

Bộ tài nguyên tại [docs/kit-stickman](file:///Users/xitrum/Documents/Dev/stickman/docs/kit-stickman) đã chứng minh tính hiệu quả vượt trội khi khóa cứng 7 nhân vật, 10 bối cảnh và 2 đạo cụ cho series hiện tại. Kế hoạch này nhằm **tổng quát hóa toàn bộ mô hình Kit thành tính năng nền tảng (Native Visual Bible & Entity Registry)** áp dụng cho toàn bộ dự án Stickman, loại bỏ hoàn toàn các giả định ngoài lề và đảm bảo khớp chuẩn xác 100% với 12 file ảnh tham chiếu A4 đã duyệt.

---

## 2. Nguyên Tắc Thiết Kế Visual Bible Chuẩn Cho Stickman

Hệ thống Visual Bible của Stickman tuân thủ các nguyên tắc thiết kế thị giác dựa trên dữ liệu chuẩn từ [kit-stickman.json](file:///Users/xitrum/Documents/Dev/stickman/docs/kit-stickman/kit-stickman.json):

1. **Quy Tắc Tạo Hình Cốt Lõi (`figure_construction`)**:
   - **Đầu tròn tô màu trắng đặc (`white filled circular head`)**: Tuyệt đối không vẽ đầu tròn rỗng xuyên thấu.
   - **Gương mặt tối giản (`face features`)**: Hai chấm bầu dục đen nhỏ (`two small dark oval eyes`), lông mày nét đơn (`simple eyebrow strokes`), miệng cong ngắn (`short curved mouth`).
   - **Thân và tứ chi (`torso & limbs`)**: Thân trắng thon gọn (`slim white torso`) với nhân vật trẻ, thân người đậm đà hơi nặng cân (`slightly overweight white torso`) với người trung niên (Bố). Chân tay luôn là nét đơn màu tối/đen (`dark single-line limbs`).

2. **Dấu Ấn Nhận Diện Bất Biến (`marks`) & Trang Phục Cố Định (`outfit`)**:
   - **Bố (`CHAR_02_BO`)**: Tóc ngắn hoa râm hai bên thái dương và sau gáy (`short grey hair along the sides and back of the head`), hai nếp nhăn ngang ngắn trên trán (`two short horizontal forehead wrinkles above the eyebrows`), áo dài tay sẫm màu trơn, quần dài tối màu.
   - **An (`CHAR_01_AN`)**: Đầu tròn trắng không tóc (`no hair`), áo trắng cộc tay trơn (`plain white top`), quần dài tối màu (`long dark pants`).
   - **Lan (`CHAR_03_LAN`)**: Tóc dài màu đen buộc đuôi ngựa thấp (`long black hair in a low ponytail`), áo trắng trơn, váy chữ A ngang gối màu sẫm (`straight dark knee-length skirt`).
   - **Mẹ Lan (`CHAR_04_ME_LAN`)**: Búi tóc thấp có các sợi bạc (`low bun with grey strands`), áo dài tay sẫm màu, váy dài tối màu.
   - **Bin (`CHAR_05_BIN`)**: Chiều cao bằng 1/2 Bố (`about half Bố's height`), đầu tròn trắng không tóc, áo trắng trơn, quần dài tối màu.
   - **Mimi (`CHAR_06_MIMI`)**: Mèo trắng, 2 tai tam giác viền đen, mũi tam giác đen nhỏ, đệm chân tròn tối màu, không quần áo hay phụ kiện.
   - **Bibo (`CHAR_07_BIBO`)**: Nhỏ hơn Mimi rõ rệt, thân và đầu tròn màu xám nhạt (`soft grey`), 1 chỏm lông nhỏ trên đỉnh đầu, không quần áo phụ kiện.

3. **Thói Quen Vận Động Đặc Trưng (`habits`)**:
   - Nhân vật que nhận diện hành động qua tư thế: Bố chắp tay sau lưng khi đi dạo, nâng tách trà bằng hai tay; An đứng thẳng nhìn người đối thoại hoặc bối rối; Bin luôn chơi an toàn cạnh Bố.

4. **Giải Pháp Thực Thể Nhóm (`ENS - Ensemble Sheet`) Cho Quota $\le 3$ Refs/Clip**:
   - AI video model (Muse/Gemini) chỉ nhận tối đa 3 ảnh ref/clip. Khi một shot có 3-4 nhân vật (ví dụ: cả gia đình ngồi phòng khách, hoặc An và Bố bên bàn trà), việc dùng ảnh đơn lẻ sẽ làm cạn kiệt slot ref.
   - **Giải pháp**: Tạo thực thể `ENS` với 1 ảnh tham chiếu nhóm duy nhất (`refs/ens-an-bo-ban-tra.png`), chiếm đúng 1 slot ref, dành 2 slot còn lại cho bối cảnh (`LOC`) và đạo cụ (`PROP`).

5. **Bóc Tách Bối Cảnh 3 Lớp Tường Minh (`LOC`)**:
   - Bối cảnh được chia tường minh thành 3 lớp độ sâu:
     - `foreground` (tiền cảnh): bàn trà, ấm chén trơn, vỉa hè hẹp, xe máy đậu...
     - `middle_ground` (trung cảnh): sofa gỗ đệm hoa dâm bụt, nhà ống mái ngói, quầy gỗ cà phê...
     - `background` (hậu cảnh): rèm voan đón nắng, cây bàng/cây phượng, trời xanh dịu...

6. **Điều Cấm Đoán Bắt Buộc (`forbid`)**:
   - **Không chữ đọc được**: Tuyệt đối không vẽ chữ viết, biển hiệu có chữ, văn bản đọc được.
   - **Không nhãn hiệu**: Không logo, không thương hiệu thương mại.
   - **Biển số xe máy trắng trơn**: Biển số luôn là hình chữ nhật trắng trơn hoàn toàn không chữ và không số (`blank license plate with no numbers and no letters`).
   - **Nội thất tối giản**: Bảng menu quán cafe trống trơn, phòng khách không vẽ đồng hồ treo tường có số.

---

## 3. Kiến Trúc Schema JSON Chuẩn (`core-schema.json`)

Toàn bộ gói thực thể trong `assets/kits/<pack-name>/kit.json` sẽ tuân thủ cấu trúc chuẩn hóa sau:

```json
{
  "pack": "vietnamese-daily",
  "title": "Stickman Kit — Sống Đáng Tiền + Chú mèo học…",
  "version": "3.0",
  "style": "A4 Cozy Storytelling: flat 2D stick figures on detailed full-color cartoon backgrounds, gentle light, warm watercolor",
  "global_rules": {
    "figure_construction": "white filled circular head, two small dark oval eyes, simple eyebrow strokes, short curved mouth, slim white torso (slightly overweight for elderly), dark single-line limbs",
    "identity_rule": "Maintain immutable facial marks, hair features, and canonical outfits defined in each character entity",
    "drawing_rule": "flat 2D stick figures on warm watercolor backgrounds, gentle daylight, consistent line weights",
    "forbid": [
      "readable text, letters, or numbers in frames",
      "license plate numbers (must always be blank white plates)",
      "commercial logos or brand marks",
      "hollow or transparent circular heads",
      "cluttered modern digital gadgets unless explicitly specified"
    ]
  },
  "entities": [
    {
      "type": "CHAR",
      "id": "CHAR_01_AN",
      "name": "An",
      "role": "nam chính, 28 tuổi, nhân viên văn phòng",
      "look": "white filled circular head, no hair, two small dark oval eyes, simple eyebrow strokes, short curved mouth, slim white torso, dark single-line limbs",
      "body_color": { "default": "trắng đặc", "hex": "#FFFFFF", "variable": false },
      "marks": ["đầu tròn trắng đặc không tóc", "nét mặt chuẩn"],
      "outfit": "plain white top, long dark pants",
      "habits": ["đứng thẳng nhìn người đối thoại", "cử chỉ nhanh nhẹn dứt khoát"],
      "expressions": ["bình thường", "mỉm cười nhẹ", "trầm ngâm", "lo lắng"],
      "forbid": ["vẽ tóc", "áo có họa tiết", "đầu rỗng xuyên thấu"],
      "ref": "refs/an-tham-chieu-a4.png"
    },
    {
      "type": "CHAR",
      "id": "CHAR_02_BO",
      "name": "Bố",
      "role": "bố của An, 55 tuổi, thói quen uống trà",
      "look": "white filled circular head, short grey hair along the sides and back of the head, two short horizontal forehead wrinkles above the eyebrows, two small dark oval eyes, simple eyebrow strokes, short curved mouth, slightly overweight white torso, dark single-line limbs",
      "body_color": { "default": "trắng đặc", "hex": "#FFFFFF", "variable": false },
      "marks": [
        "short grey hair along the sides and back of the head",
        "two short horizontal forehead wrinkles above the eyebrows",
        "slightly overweight white torso"
      ],
      "outfit": "plain dark long-sleeved top, long dark pants",
      "habits": ["chắp hai tay sau lưng khi đi dạo", "chậm rãi nâng tách trà bằng hai tay"],
      "expressions": ["ôn tồn mỉm cười", "trầm ngâm suy tư", "nghiêm nghị", "xót xa lo lắng"],
      "forbid": ["thân hình gầy mảnh", "áo trắng cộc tay", "thiếu nếp nhăn trán"],
      "ref": "refs/bo-tham-chieu-a4.png"
    },
    {
      "type": "CHAR",
      "id": "CHAR_03_LAN",
      "name": "Lan",
      "role": "đồng nghiệp của An, 28 tuổi, nhân viên văn phòng",
      "look": "white filled circular head, long black hair in a low ponytail, two small dark oval eyes, simple eyebrow strokes, short curved mouth, slim white torso, dark single-line limbs",
      "body_color": { "default": "trắng đặc", "hex": "#FFFFFF", "variable": false },
      "marks": ["long black hair in a low ponytail"],
      "outfit": "plain white top, straight dark knee-length skirt",
      "habits": ["cầm tập tài liệu trước ngực", "ngồi thẳng lưng chỉnh chu"],
      "expressions": ["thân thiện mỉm cười", "chăm chú lắng nghe", "bất ngờ"],
      "forbid": ["tóc buông xõa", "váy ngắn trên gối"],
      "ref": "refs/lan-tham-chieu-a4.png"
    },
    {
      "type": "CHAR",
      "id": "CHAR_05_BIN",
      "name": "Bin",
      "role": "cháu nội của Bố, 4 tuổi, luôn chơi an toàn bên cạnh Bố",
      "look": "about half Bố's height, white filled circular head, no hair, two small dark oval eyes, simple eyebrow strokes, short curved mouth, slim white torso, dark single-line limbs",
      "body_color": { "default": "trắng đặc", "hex": "#FFFFFF", "variable": false },
      "marks": ["chiều cao bằng 1/2 Bố", "đầu tròn trắng nhỏ không tóc"],
      "outfit": "plain white top, dark trousers",
      "habits": ["chạy lon ton quanh Bố", "ngồi bệt chơi đồ chơi trên sàn"],
      "expressions": ["hồn nhiên vui vẻ", "tò mò ngước nhìn", "mếu máo"],
      "forbid": ["vẽ cao bằng người lớn", "quần áo sặc sỡ hoa văn"],
      "ref": "refs/bin-tham-chieu-a4.png"
    },
    {
      "type": "CHAR",
      "id": "CHAR_06_MIMI",
      "name": "Mimi",
      "role": "mèo trắng, nhân vật chính series Chú mèo học…",
      "look": "white filled circular head, two small triangular ears with dark outlines, two small dark oval eyes, a tiny dark triangular nose and a short curved mouth, slim white torso, dark single-line limbs, small dark rounded paws, no clothing or accessories",
      "body_color": { "default": "trắng đặc", "hex": "#FFFFFF", "variable": false },
      "marks": ["hai tai tam giác viền đen", "mũi tam giác đen nhỏ", "chân tròn tối màu"],
      "outfit": "không quần áo, không phụ kiện",
      "habits": ["nghiêng đầu tò mò", "dùng hai chân trước ôm đồ vật"],
      "expressions": ["ngây thơ", "thích thú", "ngạc nhiên"],
      "forbid": ["mặc quần áo", "đeo vòng cổ"],
      "ref": null
    },
    {
      "type": "ENS",
      "id": "ENS_01_AN_VA_BO",
      "name": "An và Bố bên bàn trà phòng khách",
      "layout": "Bố ngồi trên ghế bành gỗ bên trái, An ngồi ghế đối diện bên phải, ở giữa là bàn trà gỗ thấp với bộ ấm chén trơn",
      "use": "Sử dụng 1 ảnh tham chiếu duy nhất đại diện cho cả 2 nhân vật và góc bàn trà, tiết kiệm slot ref",
      "ref": "refs/ens-an-bo-ban-tra.png"
    },
    {
      "type": "LOC",
      "id": "LOC_01_PHO_VN",
      "name": "Đường phố Việt Nam gần nhà",
      "role": "bối cảnh đường phố mặc định buổi sáng",
      "foreground": "vỉa hè hẹp, xe máy đậu dọc với biển số trắng trơn, ghế nhựa quán cóc",
      "middle_ground": "nhà ống hẹp mái ngói, mặt tiền nhỏ không biển hiệu, xe đẩy hàng rong trơn",
      "background": "cây bàng và cây phượng vươn cao, ánh nắng dịu buổi sáng",
      "forbid": ["chữ đọc được trên biển hiệu", "biển số xe có số", "tòa nhà kính chọc trời"],
      "ref": "refs/pho-vn-sang-tham-chieu.png"
    },
    {
      "type": "LOC",
      "id": "LOC_03_PHONG_KHACH",
      "name": "Phòng khách nhà An",
      "role": "bối cảnh sinh hoạt gia đình, Bố ngồi uống trà",
      "foreground": "bàn trà gỗ thấp màu trầm, ấm trà trơn, tách trà trơn, giỏ trái cây, hoa sứ",
      "middle_ground": "sofa gỗ đệm hoa dâm bụt, ghế bành gỗ, tủ gỗ trơn",
      "background": "cửa sổ lớn đón nắng, rèm voan mỏng, cây xanh ngoài vườn, nắng dịu buổi sáng",
      "forbid": ["đồng hồ treo tường", "lịch có số đọc được", "tivi màn hình phẳng hiện đại"],
      "ref": "refs/phong-khach-tham-chieu.png"
    },
    {
      "type": "LOC",
      "id": "LOC_08_QUAN_CAFE",
      "name": "Quán cà phê vỉa hè",
      "role": "bối cảnh quán cà phê buổi sáng",
      "foreground": "bàn gỗ tròn nhỏ, tách cà phê trơn không logo, ghế nhựa nhiều màu",
      "middle_ground": "quầy gỗ mộc mạc, lọ thủy tinh trơn, bảng menu trống hoàn toàn không chữ, chậu cây treo",
      "background": "phố nhà ống mái ngói, bóng cây xanh mát, nắng sớm",
      "forbid": ["chữ hoặc giá tiền trên bảng menu", "logo thương hiệu cà phê"],
      "ref": "refs/quan-cafe-tham-chieu.png"
    },
    {
      "type": "PROP",
      "id": "PROP_01_XE_MAY",
      "name": "Xe máy đường phố",
      "shape": "plain motorbike, blank license plate with no numbers and no letters",
      "function": "phương tiện di chuyển chính của nhân vật trên đường phố và ngõ hẻm",
      "forbid": ["chữ số trên biển số xe", "tem xe hoặc logo hãng xe"],
      "ref": null
    },
    {
      "type": "PROP",
      "id": "PROP_02_CHAU_HOA_VANG",
      "name": "Chậu hoa vàng của Mimi",
      "shape": "small clay pot with one yellow flower, no writing, no label",
      "function": "đạo cụ gắn bó với series Chú mèo học…",
      "forbid": ["nhãn mác trên chậu", "họa tiết vẽ trên đất nung"],
      "ref": null
    }
  ],
  "meta": {
    "name": "Stickman Kit — Sống Đáng Tiền + Chú mèo học…",
    "version": 3,
    "updated": "2026-11-16",
    "max_refs_per_clip": 3,
    "ref_priority": ["CHAR", "ENS", "LOC", "PROP"]
  }
}
```

---

## 4. Cấu Trúc Thư Mục & Tổ Chức Multi-Pack

Hệ thống được tổ chức chuyên nghiệp bên trong skill Stickman:

```
skills/directing-stickman-videos/assets/kits/
├── core-schema.json               # JSON Schema định nghĩa tính hợp lệ của mọi kit.json
├── vietnamese-daily/              # Pack đời sống Việt Nam chuẩn hóa (từ kit-stickman hiện có)
│   ├── kit.json                   # Metadata đầy đủ theo schema mới
│   └── refs/                      # 12 ảnh tham chiếu PNG chuẩn A4 đã được kiểm duyệt
│       ├── an-tham-chieu-a4.png
│       ├── bo-tham-chieu-a4.png
│       ├── lan-tham-chieu-a4.png
│       ├── me-lan-tham-chieu-a4.png
│       ├── bin-tham-chieu-a4.png
│       ├── pho-vn-sang-tham-chieu.png
│       ├── phong-khach-tham-chieu.png
│       ├── cho-vn-tham-chieu.png
│       ├── hem-vn-tham-chieu.png
│       ├── quan-cafe-tham-chieu.png
│       ├── nga-tu-den-xanh-tham-chieu.png
│       └── nga-tu-buoi-toi-tham-chieu.png
└── custom/                        # Thư mục cho người dùng tạo universe/pack riêng
```

---

## 5. Thiết Kế Kỹ Thuật & Công Cụ Thực Thi

### 5.1 Engine Backend (`visual-bible-kit.py`)
Đặt tại `skills/directing-stickman-videos/scripts/visual-bible-kit.py`:
- `load_pack(pack_name_or_path)`: Tự động tìm pack trong `assets/kits/` hoặc đường dẫn tùy chỉnh.
- `cmd_bible(pack, entity_ids=None)`:
  - Xuất khối văn bản `Visual Bible Block`: Liệt kê các quy tắc toàn cục (`global_rules`), mô tả các nhân vật có mặt kèm `marks` và `habits`, mô tả bối cảnh 3 lớp (`foreground`, `middle_ground`, `background`), và danh sách điều cấm kỵ (`forbid`).
- `cmd_refs(pack, entity_ids)`:
  - Tự động phân tích các ID được yêu cầu. Nếu có thực thể `ENS` (Ensemble), ưu tiên dùng thay thế cho các `CHAR` thành viên.
  - Tự động áp dụng luật **Tối đa 3 ảnh ref/clip**:
    $$\text{Ưu tiên giữ ref} = \text{Nhân vật / Nhóm (CHAR/ENS)} \rightarrow \text{Bối cảnh (LOC)} \rightarrow \text{Đạo cụ (PROP)}$$
  - Nếu số lượng $> 3$, tự động thông báo drop đạo cụ trước, rồi đến địa điểm, **không bao giờ drop nhân vật**.
- `cmd_check(pack)`: Quét kiểm tra toàn bộ file ảnh tham chiếu, đối chiếu sự tồn tại thực tế trên đĩa và báo cáo các khoảng trống (gaps) cần tạo bổ sung.
- `cmd_list()`: Liệt kê bảng tra cứu các pack, số lượng nhân vật, bối cảnh sẵn có.

### 5.2 Tích Hợp CLI Autopilot (`autopilot.mjs kit`)
Mở rộng subcommand `kit` vào `skills/directing-stickman-videos/scripts/autopilot.mjs`:
```bash
# 1. Xem tất cả các pack thực thể và nhân vật:
node scripts/autopilot.mjs kit --list

# 2. Xuất Visual Bible Block cho kịch bản:
node scripts/autopilot.mjs kit bible --pack vietnamese-daily

# 3. Lấy đường dẫn ảnh ref tự động cho 1 cảnh (tự kiểm soát quota <= 3 ref):
node scripts/autopilot.mjs kit refs CHAR_01_AN CHAR_02_BO LOC_01_PHO_VN

# 4. Kiểm tra tính toàn vẹn của ảnh tham chiếu trong dự án:
node scripts/autopilot.mjs kit check project.json
```

---

## 6. Lộ Trình Triển Khai Chi Tiết (Work Breakdown Structure)

| Giai đoạn | Nội dung công việc | File đích |
| :--- | :--- | :--- |
| **P1. Xây dựng Core Schema** | Thiết kế `core-schema.json` hỗ trợ `global_rules`, `CHAR` (marks, habits, expressions, forbid), `ENS`, `LOC` (3 lớp), `PROP`. | `skills/directing-stickman-videos/assets/kits/core-schema.json` |
| **P2. Chuẩn hóa Pack Mẫu** | Di chuyển 12 ảnh PNG và chuẩn hóa `kit-stickman.json` theo schema mới vào `assets/kits/vietnamese-daily/`. | `skills/directing-stickman-videos/assets/kits/vietnamese-daily/kit.json` và `refs/` |
| **P3. Xây dựng Engine Core** | Xây dựng script Python `visual-bible-kit.py` với đầy đủ tính năng nạp pack, xuất Visual Bible, tính toán 3 ref thông minh (hỗ trợ ENS). | `skills/directing-stickman-videos/scripts/visual-bible-kit.py` |
| **P4. Tích hợp CLI Autopilot** | Bổ sung subcommand `kit` vào `autopilot.mjs` hỗ trợ các cờ `--list`, `bible`, `refs`, `check`, `--pack`. | `skills/directing-stickman-videos/scripts/autopilot.mjs` |
| **P5. Tài liệu & Test Suite** | Viết tài liệu hướng dẫn và bộ test kiểm thử tự động `tests/verify-visual-bible-kit.py`. | `references/visual-bible-kit.md` và `tests/verify-visual-bible-kit.py` |

---

## 7. Tiêu Chí Nghiệm Thu (Acceptance Criteria)

1. Lệnh `node scripts/autopilot.mjs kit --list` hiển thị đầy đủ danh sách nhân vật, bối cảnh từ pack `vietnamese-daily`.
2. Lệnh `node scripts/autopilot.mjs kit bible` xuất đúng format Visual Bible chuẩn của Stickman (A4 Cozy Storytelling), không trôi lệch tạo hình, không dính bất kỳ yếu tố camera/CCTV ngoại lai nào.
3. Lệnh `node scripts/autopilot.mjs kit refs` khi nhận quá 3 ID sẽ tự động cắt tỉa theo đúng thứ tự ưu tiên (bỏ prop trước, rồi đến place, không được bỏ character).
4. Kiểm thử tự động `tests/verify-visual-bible-kit.py` vượt qua 100%.
