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

## 2. Bản Chất & Nguyên Tắc Visual Bible

Hệ thống quản lý thực thể dựa trên nguyên tắc **Khóa cứng định danh (Canonical Frozen)** cho 3 nhóm thực thể:

1. **Nhân vật (`CHAR`)**:
   - `look`: Cấu trúc hình thể bất biến (đầu tròn, mắt bầu dục, thân que, tóc, nếp nhăn trán...).
   - `outfit`: Trang phục đặc trưng cố định.
   - `ref`: Đường dẫn tới bảng ảnh tham chiếu chuẩn A4 (chứa **3 dáng đứng + 4 sắc thái biểu cảm**).
2. **Địa điểm / Bối cảnh (`LOC`)**:
   - `look`: Mô tả chuẩn 3 lớp có chiều sâu:
     - *Foreground (Tiền cảnh)*: Vỉa hè, bàn trà, chậu cây, xe máy trơn.
     - *Middle ground (Trung cảnh)*: Nhà ống mái ngói, sofa gỗ, mặt tiền quán.
     - *Background (Hậu cảnh)*: Tán cây bàng/phượng, nắng sớm, trời mây dịu.
   - *Quy tắc an toàn thị giác*: Không có chữ đọc được, không có logo thương hiệu, biển số xe máy luôn là biển trắng trơn (chống hallucination của model video).
   - `ref`: Ảnh tham chiếu phối cảnh màu nước chuẩn.
3. **Đạo cụ (`PROP`)**:
   - `look`: Hình dáng, tỷ lệ, màu sắc của vật thể tương tác (chậu hoa vàng, ấm trà, xe máy...).

---

## 3. Kiến Trúc Tổng Quát: Multi-Pack Entity Registry

Thay vì một file `kit-stickman.json` đơn lẻ, hệ thống tổ chức theo cấu trúc các gói thực thể (Entity Packs):

```
skills/directing-stickman-videos/assets/kits/
├── core-schema.json               # Schema JSON chuẩn cho mọi thực thể (CHAR, LOC, PROP)
├── vietnamese-daily/              # Pack đời sống Việt Nam (An, Bố, Lan, phố, chợ, quán cafe...)
│   ├── kit.json                   # Metadata 7 CHAR, 10 LOC, 2 PROP
│   └── refs/*.png                 # 12 ảnh tham chiếu PNG chuẩn
├── tech-explainer/                # Pack công nghệ / giải thích logic B2 (Kỹ sư, lập trình viên, phòng server...)
│   ├── kit.json
│   └── refs/*.png
└── custom/                        # Thư mục cho người dùng tự tạo universe riêng
    └── my-series/
        ├── kit.json
        └── refs/
```

### Khai báo trong `project.json`:
Mỗi dự án video có thể liên kết trực tiếp tới một pack, và các shot chỉ cần gọi ID định danh:
```json
{
  "title": "Bí Quyết Quản Lý Thời Gian",
  "style": "A4",
  "kit": "vietnamese-daily",
  "shots": [
    {
      "id": "shot_01",
      "cast": ["CHAR_01_AN", "CHAR_02_BO"],
      "location": "LOC_03_PHONG_KHACH",
      "props": ["PROP_02_XE_MAY"],
      "action": "An ngồi trò chuyện cùng Bố bên bàn trà"
    }
  ]
}
```

---

## 4. Thiết Kế Kỹ Thuật & Công Cụ Thực Thi

### 4.1 Engine Backend (`visual-bible-kit.py`)
Đặt tại `skills/directing-stickman-videos/scripts/visual-bible-kit.py`:
- `load_pack(pack_name_or_path)`: Nạp schema và dữ liệu từ pack hệ thống hoặc custom pack.
- `cmd_bible(pack, entity_ids=None)`: Xuất khối văn bản Visual Bible Block để dán lên đầu prompt Phase B.
- `cmd_refs(pack, entity_ids)`: Tự động lọc ra tối đa **3 ảnh ref/clip** theo đúng thứ tự ưu tiên:
  $$\text{Thứ tự ưu tiên ref} = \text{Nhân vật (theo thứ tự kịch bản)} \rightarrow \text{Bối cảnh (Location)} \rightarrow \text{Đạo cụ (Prop)}$$
- `cmd_check(pack)`: Quét kiểm tra toàn bộ file ảnh tham chiếu, báo cáo tỷ lệ sẵn sàng ($N/M$ refs) và cảnh báo các ref còn thiếu.
- `cmd_list()`: Liệt kê danh sách tất cả các pack và thực thể có sẵn trong hệ sinh thái.

### 4.2 Tích Hợp CLI Autopilot (`autopilot.mjs kit`)
Mở rộng subcommand `kit` vào `skills/directing-stickman-videos/scripts/autopilot.mjs`:
```bash
# 1. Xem tất cả các pack thực thể và nhân vật:
node scripts/autopilot.mjs kit --list

# 2. Xuất Visual Bible Block cho kịch bản:
node scripts/autopilot.mjs kit bible --pack vietnamese-daily

# 3. Lấy đường dẫn ảnh ref tự động cho 1 cảnh:
node scripts/autopilot.mjs kit refs CHAR_01_AN CHAR_03_LAN LOC_01_PHO_VN

# 4. Kiểm tra tính toàn vẹn của ảnh tham chiếu trong dự án:
node scripts/autopilot.mjs kit check project.json
```

### 4.3 Tích Hợp Vào Khâu Tạo Kịch Bản (`autopilot storyboard`)
Khi AI tạo kịch bản:
- Tự động nhận diện pack được chỉ định.
- Gợi ý nhân vật và địa điểm có sẵn trong kit thay vì tự tạo tên mới bừa bãi.
- Gắn kèm khối Visual Bible vào phần mô tả chi tiết của Storyboard.

---

## 5. Lộ Trình Triển Khai Chi Tiết (Work Breakdown Structure)

| Giai đoạn | Nội dung công việc | File đích |
| :--- | :--- | :--- |
| **P1. Di chuyển & Chuẩn hóa Pack Mẫu** | Đưa gói `kit-stickman` hiện có vào vị trí chuẩn `assets/kits/vietnamese-daily/` làm pack mẫu mặc định. | `skills/directing-stickman-videos/assets/kits/vietnamese-daily/` |
| **P2. Xây dựng Engine Core** | Xây dựng script Python đa năng quản lý pack, xuất Visual Bible, tính toán 3 ref/clip và kiểm tra integrity. | `skills/directing-stickman-videos/scripts/visual-bible-kit.py` |
| **P3. Tích hợp CLI Autopilot** | Bổ sung subcommand `kit` vào `autopilot.mjs` hỗ trợ các cờ `--list`, `bible`, `refs`, `check`. | `skills/directing-stickman-videos/scripts/autopilot.mjs` |
| **P4. Tài liệu Hướng dẫn** | Viết tài liệu hướng dẫn sử dụng và quy chuẩn tạo custom pack cho người dùng. | `skills/directing-stickman-videos/references/visual-bible-kit.md` |
| **P5. Bộ Test Kiểm thử Toàn diện** | Viết test kiểm tra load pack, xuất bible, giới hạn 3 ref, báo lỗi thiếu file. | `tests/verify-visual-bible-kit.py` |

---

## 6. Tiêu Chí Nghiệm Thu (Acceptance Criteria)

1. Lệnh `node scripts/autopilot.mjs kit --list` hiển thị đầy đủ danh sách nhân vật, bối cảnh từ pack `vietnamese-daily`.
2. Lệnh `node scripts/autopilot.mjs kit bible` xuất đúng format Visual Bible không lỗi chính tả hay trôi dữ liệu.
3. Lệnh `node scripts/autopilot.mjs kit refs` khi nhận quá 3 ID sẽ báo lỗi rõ ràng và yêu cầu bỏ bớt theo đúng thứ tự ưu tiên (bỏ prop trước, rồi đến place, không được bỏ character).
4. Kiểm thử tự động `tests/verify-visual-bible-kit.py` vượt qua 100%.
