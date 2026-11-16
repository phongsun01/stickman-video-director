# Kế Hoạch Triển Khai: Hệ Thống Visual Bible & Entity Registry Cho Stickman

> **Mã kế hoạch:** `PLAN-STICKMAN-VISUAL-BIBLE`  
> **Ngày lập:** 2026-11-16  
> **Nguồn cảm hứng & chuyển thể:** `Garden Kit` / `kit-stickman` & `Whiteboard Character Bible` (REA)  
> **Trạng thái:** Chờ phê duyệt triển khai (Draft for Implementation)

---

## 1. Bối Cảnh & Vấn Đề Cốt Lõi

Khi sáng tạo video Stickman hoạt hình qua AI (đặc biệt là Phase B / Muse Prompting, A4 Cozy Storytelling, hoặc các series dài tập như *Sống Đáng Tiền*, *Chú mèo học...*):
* **Hiện tượng trôi hình (Character & Scene Drift)**: AI không có bộ nhớ ngữ cảnh dài hạn giữa các prompt độc lập. Mỗi lần sinh một shot mới, nhân vật lại bị thay đổi tỷ lệ đầu/thân, đổi mắt, đổi kiểu tóc, nhầm màu áo, thay đổi độ tuổi; bối cảnh đường phố, quán xá bị biến dạng phong cách hoặc sai lệch đặc trưng văn hóa.
* **Gõ lại prompt thủ công theo trí nhớ**: Người viết kịch bản hoặc AI Agent dễ bịa đặt hoặc mô tả không nhất quán (tập 1 tả Bố mặc áo trắng, tập 2 lại tả áo tối màu; bối cảnh phố lúc thì nhà mái ngói, lúc thì nhà kính hiện đại).

Bộ tài nguyên tại [docs/kit-stickman](file:///Users/xitrum/Documents/Dev/stickman/docs/kit-stickman) đã chứng minh tính hiệu quả vượt trội khi áp dụng cho một series cụ thể. Kế hoạch này nhằm **tổng quát hóa toàn bộ mô hình Kit thành tính năng nền tảng (Native Visual Bible & Entity Registry)** áp dụng cho toàn bộ dự án Stickman.

---

## 2. Bản Chất & Nguyên Tắc Visual Bible (Học Hỏi Từ `kit-tang-0-draft.json`)

Kế thừa các đột phá thực chiến từ bản phác thảo `kit-tang-0-draft.json`, hệ thống Visual Bible cho Stickman thiết lập các nguyên tắc nhận diện nghiêm ngặt:

1. **Quy tắc Nhận diện Bằng Dấu Ấn (`identity_rule` & `marks`)**:
   - **Không dựa thuần túy vào màu thân**: Trong hoạt hình, màu thân có thể đổi theo trạng thái, ánh sáng hoặc cốt truyện (ví dụ: bị nhiễm độc, bóng tối, camera hồng ngoại).
   - **Nhận diện bằng dấu ấn cố định (`marks`)**: Mỗi nhân vật phải có một dấu ấn vật lý bất biến (ví dụ: *vạch song song ở cổ tay, túi dụng cụ bên hông, miếng vá ở đầu gối, khăn tam giác có nút thắt, vòng tròn rỗng trên ngực*). Dấu ấn này **không bao giờ thay đổi** dù màu thân có biến thiên.
2. **Quy tắc Thói quen Cử chỉ (`habits`)**:
   - Người que có đường nét tối giản, do đó **thói quen vận động (body language habit)** là chìa khóa để khán giả nhận ra nhân vật từ xa (ví dụ: *dừng lại nghiêng đầu nghe ngóng, tay chạm nút thắt khăn, tay đặt lên ngực, dáng đứng hơi cúi*).
3. **Giải pháp Đột phá: Thực thể Nhóm (`ENS - Ensemble`)**:
   - **Bài toán**: Model video AI (Muse/Gemini) giới hạn tối đa **3 ảnh tham chiếu/clip**. Nếu một cảnh có 4–5 nhân vật cùng xuất hiện, việc đính kèm từng ảnh lẻ là bất khả thi.
   - **Giải pháp**: Tạo thực thể **`ENS` (Ensemble Sheet)** — 1 ảnh tham chiếu duy nhất vẽ sẵn toàn bộ đội hình nhóm (ví dụ: *Hàng 5 người nằm ngang, nhóm bạn ngồi quanh bàn cafe*). Chỉ tiêu tốn đúng **1 slot ref**, dành 2 slot còn lại cho bối cảnh (`LOC`) và đạo cụ (`PROP`).
4. **Bóc tách Bối cảnh 3 Lớp Tường Minh (`LOC`)**:
   - Bắt buộc chia rõ 3 trường: `foreground` (tiền cảnh), `middle_ground` (trung cảnh), `background` (hậu cảnh).
5. **Cơ chế Cấm Đoán (Negative Constraints - `forbid`)**:
   - Định nghĩa danh sách cấm kỵ ở cả cấp toàn cục (`global_rules.forbid`) và từng thực thể (`entity.forbid`) để triệt tiêu hiện tượng AI tự ý vẽ thêm chữ nhỏ, biển số xe, đổi bên hông của túi, hoặc vi phạm tính liên tục của shot.

---

## 3. Kiến Trúc Schema JSON Chuẩn (`core-schema.json`)

Toàn bộ gói thực thể trong `assets/kits/<pack-name>/kit.json` sẽ tuân thủ cấu trúc chuẩn hóa sau:

```json
{
  "pack": "vietnamese-daily",
  "title": "Đời Sống Việt Nam — Sống Đáng Tiền",
  "version": "1.0",
  "style": "A4",
  "global_rules": {
    "figure_construction": "Hình que 2D: đầu tròn trắng, thân và tứ chi nét đơn đen. Giữ đồng nhất tỉ lệ đầu/thân và độ dày nét cọ xuyên suốt toàn bộ kịch bản.",
    "identity_rule": "Nhận diện nhân vật bằng dấu ấn vật lý và phụ kiện cố định (marks/outfit), không phụ thuộc vào màu nền.",
    "frame_layers": {
      "TT": "Khung hình thông thường: nét vẽ màu nước ấm áp, ánh sáng tự nhiên dịu mắt.",
      "MH": "Khung hình qua màn hình/CCTV: có viền mỏng, chấm REC đỏ, sọc quét scanlines; không chứa chữ nhỏ."
    },
    "forbid": [
      "chữ nhỏ hoặc văn bản đọc được trong khung hình",
      "biển số xe có chữ số (luôn vẽ biển trắng trơn)",
      "thay đổi vị trí dấu nhận diện giữa các shot",
      "logo thương hiệu thực tế"
    ]
  },
  "entities": [
    {
      "type": "CHAR",
      "id": "CHAR_01_AN",
      "name": "An",
      "role": "Nam chính 28 tuổi, nhân viên văn phòng",
      "look": "Đầu tròn trắng, mắt bầu dục đen, thân que thanh mảnh, cử chỉ dứt khoát nhanh nhẹn.",
      "body_color": { "default": "trắng", "hex": "#FFFFFF", "variable": false },
      "marks": ["Vòng đeo tay dây dù đen ở cổ tay trái."],
      "outfit": "Áo thun trắng trơn cộc tay, quần âu tối màu.",
      "habits": ["đưa tay gãi sau gáy khi bối rối", "đứng thẳng nhìn thẳng vào người đối thoại"],
      "expressions": ["bình thường", "nghiêm túc tập trung", "bất ngờ mắt mở to", "mỉm cười nhẹ"],
      "forbid": ["mặc áo có họa tiết", "đổi vòng tay sang cổ tay phải"],
      "ref": "refs/an-tham-chieu-a4.png"
    },
    {
      "type": "CHAR",
      "id": "CHAR_02_BO",
      "name": "Bố",
      "role": "Bố của An, 55 tuổi",
      "look": "Đầu tròn trắng, tóc hoa râm hai bên thái dương và sau gáy, hai nếp nhăn ngang trán, thân người đậm đà hơi nặng cân.",
      "body_color": { "default": "trắng", "hex": "#FFFFFF", "variable": false },
      "marks": ["Hai nếp nhăn ngang trán rõ nét", "Tóc bạc hoa râm hai bên thái dương"],
      "outfit": "Áo dài tay màu sẫm trơn, quần dài tối màu.",
      "habits": ["hai tay chắp sau lưng khi đi dạo", "chậm rãi nâng tách trà bằng hai tay"],
      "expressions": ["trầm ngâm suy tư", "ôn tồn mỉm cười", "nghiêm nghị", "lo lắng"],
      "forbid": ["vẽ thân hình gầy thanh mảnh", "mặc áo ngắn tay"],
      "ref": "refs/bo-tham-chieu-a4.png"
    },
    {
      "type": "ENS",
      "id": "ENS_01_AN_VA_BO",
      "name": "An và Bố bên bàn trà",
      "layout": "Bố ngồi ghế bành gỗ bên trái, An ngồi ghế đối diện bên phải, ở giữa là bàn trà gỗ thấp có ấm tách.",
      "use": "Sử dụng 1 ảnh tham chiếu duy nhất thay cho cả 2 nhân vật và bối cảnh bàn trà, tiết kiệm quota 3 ref/clip.",
      "ref": "refs/ens-an-bo-ban-tra.png"
    },
    {
      "type": "LOC",
      "id": "LOC_01_PHONG_KHACH",
      "name": "Phòng khách nhà An",
      "foreground": "Bàn trà gỗ thấp màu cánh gián, bộ ấm chén sứ trơn không hoa văn, giỏ trái cây.",
      "middle_ground": "Bộ ghế sofa gỗ đệm hoa, tủ chè gỗ trơn, chậu cây trầu bà.",
      "background": "Cửa sổ kính lớn nhìn ra sân, rèm voan mỏng đón nắng sớm dịu nhẹ, tường vàng nhạt.",
      "forbid": ["đồng hồ treo tường", "tranh ảnh có chữ đọc được", "đồ điện tử hiện đại cầu kỳ"],
      "ref": "refs/phong-khach-tham-chieu.png"
    },
    {
      "type": "PROP",
      "id": "PROP_01_XE_MAY",
      "name": "Xe máy số phổ thông",
      "shape": "Xe máy số kiểu dáng phổ thông, thân yếm gọn gàng, biển số màu trắng trơn hoàn toàn.",
      "function": "Phương tiện di chuyển chính của An trên đường phố, chợ và ngõ hẻm.",
      "forbid": ["chữ số trên biển số xe", "tem xe hoặc logo hãng xe rõ nét"],
      "ref": "refs/xe-may-tham-chieu.png"
    }
  ],
  "meta": {
    "name": "Vietnamese Daily Life Kit",
    "version": "1.0",
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
├── vietnamese-daily/              # Pack đời sống Việt Nam (chuyển đổi từ kit-stickman hiện có)
│   ├── kit.json                   # Metadata đầy đủ theo schema mới
│   └── refs/                      # 12 ảnh tham chiếu PNG chuẩn A4
│       ├── an-tham-chieu-a4.png
│       ├── bo-tham-chieu-a4.png
│       ├── lan-tham-chieu-a4.png
│       ├── pho-vn-sang-tham-chieu.png
│       └── ...
├── tang-0/                        # Pack viễn tưởng / bí ẩn Tầng 0 (chuyển đổi từ kit-tang-0-draft.json)
│   ├── kit.json
│   └── refs/
└── custom/                        # Thư mục cho người dùng tạo universe riêng
```

---

## 5. Thiết Kế Kỹ Thuật & Công Cụ Thực Thi

### 5.1 Engine Backend (`visual-bible-kit.py`)
Đặt tại `skills/directing-stickman-videos/scripts/visual-bible-kit.py`:
- `load_pack(pack_name_or_path)`: Tự động tìm pack trong `assets/kits/` hoặc đường dẫn tùy chỉnh.
- `cmd_bible(pack, entity_ids=None)`:
  - Xuất khối văn bản `Visual Bible Block`: Liệt kê các quy tắc toàn cục (`global_rules`), mô tả các nhân vật có mặt kèm `marks` và `habits`, mô tả bối cảnh 3 lớp, và danh sách điều cấm kỵ (`forbid`).
- `cmd_refs(pack, entity_ids)`:
  - Tự động phân tích các ID được yêu cầu. Nếu có thực thể `ENS` (Ensemble), ưu tiên dùng thay thế cho các `CHAR` thành viên.
  - Tự động áp dụng luật **Tối đa 3 ảnh ref/clip**:
    $$\text{Ưu tiên giữ ref} = \text{Nhân vật / Nhóm (CHAR/ENS)} \rightarrow \text{Bối cảnh (LOC)} \rightarrow \text{Đạo cụ (PROP)}$$
  - Nếu số lượng $> 3$, tự động thông báo drop đạo cụ trước, rồi đến địa điểm, **không bao giờ drop nhân vật**.
- `cmd_check(pack)`: Quét kiểm tra toàn bộ file ảnh tham chiếu, đối chiếu tồn tại trên đĩa và báo cáo các khoảng trống (gaps) cần tạo bổ sung.
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
| **P1. Xây dựng Core Schema** | Thiết kế `core-schema.json` hỗ trợ `global_rules`, `CHAR` (marks, habits, expressions), `ENS`, `LOC` (3 lớp), `PROP`. | `skills/directing-stickman-videos/assets/kits/core-schema.json` |
| **P2. Chuẩn hóa Pack Mẫu** | Nâng cấp `kit-stickman.json` hiện có và nạp `tang-0` theo schema mới vào `assets/kits/`. | `skills/directing-stickman-videos/assets/kits/vietnamese-daily/kit.json` và `assets/kits/tang-0/kit.json` |
| **P3. Xây dựng Engine Core** | Xây dựng script Python `visual-bible-kit.py` với đầy đủ tính năng nạp pack, xuất Visual Bible, tính toán 3 ref thông minh (hỗ trợ ENS). | `skills/directing-stickman-videos/scripts/visual-bible-kit.py` |
| **P4. Tích hợp CLI Autopilot** | Bổ sung subcommand `kit` vào `autopilot.mjs` hỗ trợ các cờ `--list`, `bible`, `refs`, `check`, `--pack`. | `skills/directing-stickman-videos/scripts/autopilot.mjs` |
| **P5. Tài liệu & Test Suite** | Viết tài liệu hướng dẫn và bộ test kiểm thử tự động `tests/verify-visual-bible-kit.py`. | `references/visual-bible-kit.md` và `tests/verify-visual-bible-kit.py` |

---

## 6. Tiêu Chí Nghiệm Thu (Acceptance Criteria)

1. Lệnh `node scripts/autopilot.mjs kit --list` hiển thị đầy đủ danh sách nhân vật, bối cảnh từ pack `vietnamese-daily`.
2. Lệnh `node scripts/autopilot.mjs kit bible` xuất đúng format Visual Bible không lỗi chính tả hay trôi dữ liệu.
3. Lệnh `node scripts/autopilot.mjs kit refs` khi nhận quá 3 ID sẽ báo lỗi rõ ràng và yêu cầu bỏ bớt theo đúng thứ tự ưu tiên (bỏ prop trước, rồi đến place, không được bỏ character).
4. Kiểm thử tự động `tests/verify-visual-bible-kit.py` vượt qua 100%.
