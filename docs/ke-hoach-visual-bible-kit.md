# Kế Hoạch Triển Khai: Hệ Thống Visual Bible, Shot Compiler & Continuity Kit Cho Stickman

> **Mã kế hoạch:** `PLAN-STICKMAN-VISUAL-BIBLE`
> **Phiên bản:** `2.3-REVISED`
> **Cập nhật:** 2026-11-17 — Đồng bộ dữ liệu mẫu, snapshot, state machine và bộ chọn ref.
> **Ngày lập:** 2026-11-16 (Đã cập nhật theo phản biện Bản 2: Đóng băng đặc tả, Hợp đồng dữ liệu Project 2-Shot & Phân lập kiểm tra tự động vs đối soát thị giác)
> **Nguồn gốc dữ liệu chuẩn:** [docs/kit-stickman/kit-stickman.json](/Users/xitrum/Documents/Dev/stickman/docs/kit-stickman/kit-stickman.json), 12 ảnh tham chiếu A4 và quy chuẩn thiết kế [skills/directing-stickman-videos/references/cozy-storytelling.md](/Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/cozy-storytelling.md)
> **Trạng thái:** Người dùng đã chốt tạo hình và duyệt góc nhìn ngày 2026-11-17; còn tạo/duyệt ảnh ENS và xác minh capability model thực tế trước production.

---

### Ghi nhận triển khai và sửa lỗi ngày 2026-11-17

Pack runtime hiện là 3.1.1. Đã sửa snapshot thực tế, kiểm tra hash/dependency, state machine `op/time_s`, gate production, ref/ENS/quota và ánh sáng; các ví dụ hiện hành nằm trong `skills/directing-stickman-videos/examples/`. Snapshot mẫu JSON trong plan là minh họa thiết kế lịch sử, không thay thế lockfile được tạo bởi `kit lock`.

CLI bổ sung `kit lock --project ... --pack ...`. `compile --output` ghi gói JSON gồm `prompt` và manifest ảnh riêng; không tự upload hay sinh video. Hướng dẫn vận hành: [visual-bible-kit.md](/Users/xitrum/Documents/Dev/stickman/skills/directing-stickman-videos/references/visual-bible-kit.md). Bộ test hiện hành: `skills/directing-stickman-videos/tests/test_visual_bible_kit.py` (38 test).

P6 còn pending: chưa có bằng chứng nghiệm thu ảnh/video benchmark qua model thực tế. Xem [báo cáo cập nhật](/Users/xitrum/Documents/Dev/stickman/tests/reports/visual-bible-benchmark-report.md). Cấu hình model giả lập không được xem là capability đã xác minh.

---

## 1. Bối Cảnh, Mục Tiêu & Vấn Đề Cốt Lõi

Khi sáng tạo video Stickman hoạt hình qua AI (Muse, Gemini, Wan, CogVideoX...) theo phong cách **A4 Cozy Storytelling** hoặc các series dài tập (*Sống Đáng Tiền*, *Chú mèo học…*), việc lưu trữ dữ liệu mô tả nhân vật chỉ là điều kiện cần. Điều kiện đủ để tạo nên một quy trình sản xuất ổn định là **khóa chặt bản chuẩn tạo hình, biên soạn prompt độc lập từng shot (Shot-Level Compiler), và bảo toàn tính liên tục không gian/đạo cụ (Continuity) được kiểm chứng qua kết quả thực tế**.

### 1.1 Những Lỗ Hổng Kỹ Thuật Đã Được Nhận Diện & Khắc Phục
1. **Tránh tự động coi dữ liệu chưa duyệt là chuẩn**:
   - Nếu trong schema mẫu vội vàng đóng dấu `approved` cho các biến thể đang có xung đột (như trường hợp áo Bố) hoặc tự ý chốt các thực thể nhóm `ENS` khi thành viên chưa hoàn tất đối soát, hệ thống sẽ lan truyền sai lệch sang khâu sinh hình.
   - **Quy tắc mới**: Production (`--mode prod`, cũng là mặc định khi không ghi mode) chỉ chấp nhận thực thể/variant/angle/lighting `approved`; mọi trạng thái khác bị từ chối. Chế độ nháp (`--draft`) có thể xuất để xem trước nhưng phải mang nhãn `[UNRESOLVED CONFLICT]` và không được xem là canonical.
2. **Hợp đồng dữ liệu đầu vào cho Compiler & Continuity**:
   - Không thể phó mặc cho script phân tích các câu văn mô tả tự do để đoán xem ai đang cầm gì. Timeline cần một cấu trúc sự kiện tường minh (`events`) với các động từ thao tác rõ ràng (`pickup`, `putdown`, `handover`) để linter tự động kiểm tra tính liên tục.
   - Phân biệt rạch ròi giữa **Định nghĩa loại đạo cụ (Prop Definition)** và **Thể hiện cụ thể trong cảnh (Prop Instances)**: Một mẫu tách trà có thể sinh ra `cup_01` (Bố cầm) và `cup_02` (trên bàn trước mặt An).
3. **Chuẩn hóa bố cục không gian & Loại bỏ rác hành động khỏi Bối cảnh (LOC)**:
   - Bố cục phòng khách phải được neo theo **Hệ tọa độ phòng / Tường tham chiếu** và **Góc nhìn máy quay tham chiếu**, tránh việc đổi góc máy làm đảo lộn tương quan trái/phải.
   - Bối cảnh cố định (`LOC`) tuyệt đối chỉ chứa kiến trúc, nội thất cố định và ánh sáng; loại bỏ hoàn toàn các mô tả hành động (như "tay nhân vật nâng tách") hoặc các chi tiết bịa đặt (như "gạch men sáng trơn").
4. **Cơ chế Khóa bản đã dùng (Project Lockfile)**:
   - Project phải có lockfile (`project.lock.json` hoặc khối `pack_lock`) ghim chặt mã băm SHA-256 thực tế, revision và variant cụ thể của từng ảnh ref đã dùng. Tránh việc sửa đổi kit hôm nay làm âm thầm đổi tạo hình của các tập phim cũ.
5. **Chính sách phân bổ Ref khi không thể đáp ứng quota**:
   - Thiết lập danh sách `required_refs` và `optional_refs`. Nếu `required_refs` vượt quota mà không có ENS hợp lệ, compiler phải **dừng và báo lỗi (Hard Stop)** thay vì tự ý cắt bỏ nhân vật quan trọng.
6. **Phân lập rõ ràng giữa Kiểm tra tự động vs Đối soát thị giác**:
   - Công cụ máy tính chỉ tự động kiểm tra: schema, tính hợp lệ của file, mã băm SHA-256, logic sự kiện continuity.
   - Việc xác nhận ảnh có đúng nếp nhăn, đúng tỷ lệ, đúng tóc hay không là **Đối soát thị giác (Visual Semantic Audit)** cần con người hoặc mô hình thị giác chuyên biệt đánh giá trước khi chuyển trạng thái sang `approved`.

---

## 2. Nguyên Tắc Thiết Kế Visual Bible & Quản Lý Thực Thể Chuẩn

### 2.1 Quy Tắc Tạo Hình Cốt Lõi (`figure_construction`) — Chuẩn A4 Cozy Storytelling
- **Đầu tròn tô trắng đặc (`white filled circular head`)**: Đường viền tối màu rõ nét, bên trong phủ màu trắng đặc (`solid white fill`). Tuyệt đối không vẽ đầu rỗng xuyên thấu hoặc đầu trong suốt.
- **Gương mặt tối giản (`face features`)**: Hai chấm bầu dục đen nhỏ (`two small dark oval eyes`), lông mày nét đơn ngắn (`simple eyebrow strokes`), miệng cong ngắn (`short curved mouth`). Biểu cảm chỉ làm biến đổi lông mày/miệng, không làm méo hình khối đầu.
- **Thân mình khép kín tô trắng đặc (`closed torso with solid white fill`)**:
  - Thân nhân vật A4 là khối khép kín có viền đen và tô trắng đặc bên trong (`closed tapered shape with solid white fill inside dark outline`).
  - Nhân vật trẻ/thanh niên (An, Lan): Thân thon gọn phẳng (`slim closed white torso`).
  - Người trung niên (Bố): Thân đậm đà hơn, hơi nặng cân (`slightly overweight closed white torso`).
- **Tứ chi nét đơn (`dark single-line limbs`)**: Cả 2 tay và 2 chân là các đường nét đơn màu tối/đen với độ dày ổn định (`dark single-line strokes with constant medium weight`). Bàn tay là hình vòm/chấm tròn tối màu nhỏ, bàn chân là vạch ngắn tối màu.
- **Nguyên tắc tứ chi bất biến**: Luôn luôn đúng 2 tay và 2 chân; khi vận động, chi ở tư thế mới thay thế tư thế cũ, không để lại vệt bóng nhân bản chi.

### 2.2 Phân Tách Thiết Kế 3 Tầng: Bất Biến vs Cho Phép Thay Đổi

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. IDENTITY (Bất biến)                                          │
│    - Cấu trúc đầu tròn trắng, thân khép kín tô trắng            │
│    - Dấu nhận diện bất biến (marks): tóc, nếp nhăn trán, tỷ lệ  │
│    - Cấm đoán tuyệt đối (forbid): không vẽ tóc cho An, ...      │
├─────────────────────────────────────────────────────────────────┤
│ 2. APPROVED VARIANTS (Biến thể được duyệt)                       │
│    - Trang phục theo hoàn cảnh (outfit variant ID)              │
│    - Phiên bản tuổi tác (age variant ID)                        │
│    - Phải có status: "approved" mới được dùng trong prod        │
├─────────────────────────────────────────────────────────────────┤
│ 3. SHOT STATE (Trạng thái động theo cảnh)                       │
│    - Biểu cảm (expressions), hướng nhìn (gaze)                  │
│    - Tư thế (pose), tọa độ/vị trí không gian (position)         │
│    - Đồ vật đang cầm/tương tác (instances holding)              │
└─────────────────────────────────────────────────────────────────┘
```

- **Thói quen vận động (`habits`)**: Được xếp vào nhóm **gợi ý diễn xuất (acting cues)** cho kịch bản, **không phải hành động bắt buộc lặp lại trong mọi shot**.
- **Không tự ý thêm dấu nhận diện mới**: Thiết kế An đang đối soát được mô tả bằng tổ hợp (đầu tròn trắng đặc không tóc + thân trắng khép kín + mắt oval + lông mày đơn). Tuyệt đối không tùy tiện thêm phụ kiện ngoài luồng (như vòng tay trái).
- **Cô lập quy tắc đặc thù theo Pack**: Các quy tắc đổi màu thân hình hoặc lớp giám sát (CCTV/Scanlines của vũ trụ Tầng 0) phải được đóng gói cục bộ trong pack đó; tuyệt đối không để rò rỉ vào phong cách ấm áp của A4 Cozy Storytelling.

### 2.3 Quản Lý Bối Cảnh (LOC), Đạo Cụ (PROP) & Tách Biệt Instance
- **Hệ quy chiếu không gian của LOC**:
  - Xác định theo **Hệ tọa độ căn phòng (Room Reference Coordinates)** kết hợp **Góc nhìn máy quay tham chiếu (Reference View)**.
  - Ví dụ phòng khách: Từ góc nhìn máy quay tham chiếu chính diện (Front Wide), tủ gỗ nằm ở phía bên trái khung hình (sát tường Tây), cửa sổ đón nắng ở tường hậu cảnh (tường Bắc), sofa gỗ đặt ở trung tâm trước cửa sổ, bàn trà đặt trước sofa. Khi máy quay xoay góc, quan hệ topo này vẫn giữ nguyên.
  - Bối cảnh cố định chỉ chứa cấu trúc kiến trúc, ánh sáng và đồ đạc cố định. Không đưa hành động nhân vật hay các đồ vật di chuyển vào mô tả LOC.
- **Đối soát các bối cảnh ngoại cảnh biến thể**:
  - Các bối cảnh như ngã tư ban ngày (`LOC_09`) và ngã tư ban đêm (`LOC_10`) là hai góc nhìn/thời điểm tham chiếu riêng biệt đang trong diện đối soát cấu trúc không gian, chưa thể khẳng định chúng có cùng quan hệ topo 100% cho đến khi hoàn tất kiểm tra thị giác.
- **Tách biệt Prop Type vs Prop Instance**:
  - `PROP_03_TACH_TRA` định nghĩa kiểu dáng, màu sắc, kích thước chuẩn của tách trà men gốm.
  - Trong mỗi shot, các tách trà cụ thể được định danh thành các instance: `cup_01`, `cup_02`. Mỗi instance có chủ sở hữu (`owner`) và vị trí (`position`) độc lập.

### 2.4 Điều Kiện Sử Dụng & Ràng Buộc Thực Thể Nhóm (ENS - Ensemble)
- **Cấu trúc thực thể `ENS`**:
  - `members`: Danh sách ID các thành viên có mặt (`["CHAR_01_AN", "CHAR_02_BO"]`).
  - `member_revisions`: Map phiên bản duyệt của từng thành viên.
  - `member_variants`: Map variant cụ thể của từng thành viên (`{"CHAR_01_AN": "DEFAULT_DAILY", "CHAR_02_BO": "BO_WHITE_TORSO"}`).
  - `location_id`: ID địa điểm nếu ảnh ENS gắn liền với bối cảnh cụ thể (`LOC_03_PHONG_KHACH`).
  - `reference_role`: Vai trò tham chiếu (`identity` | `composition` | `first_frame`).
- **Quy tắc nghiệm thu ENS**:
  - `ENS` chỉ được mang trạng thái `approved` khi toàn bộ thành viên thành phần đều có `status: "approved"` ở đúng `revision` và `variant` tương ứng, đồng thời file ảnh tham chiếu ENS đã tồn tại thực tế và có mã băm SHA-256 xác thực. Nếu ảnh chưa được tạo ra, ENS bắt buộc phải để `status: "draft"` và `ref_hash: null`.
  - Ảnh ENS bố cục cụ thể (`composition`) chỉ được kích hoạt khi shot diễn ra đúng tại `location_id` quy định.
  - Ảnh ENS chiếm 1 slot ref hình ảnh, nhưng trong prompt văn bản, compiler **vẫn phải bung đầy đủ mô tả thiết kế độc lập của từng thành viên**.

### 2.5 Quyết Định Thiết Kế Đã Chốt Ngày 2026-11-17
Nguồn duyệt: người dùng trong chat này. Các quyết định sau thay thế những xung đột ghi ở các phiên bản kế hoạch trước; không yêu cầu duyệt lại khi triển khai đúng lựa chọn này.

| Thực thể / biến thể | Quyết định hiện hành | Trạng thái |
| :--- | :--- | :--- |
| Bố | Thân khép kín tô trắng theo ảnh hiện có; không áp áo dài tay sẫm vào bản mặc định. Chân nét đơn tối màu theo ảnh. | `approved` |
| An | Giữ chân nét đơn tối màu, không vẽ thêm ống quần; bỏ mô tả long dark pants khỏi anchor mặc định. | `approved` |
| Tách trà | Giữ mô tả cũ: tách trà trơn, không chữ/hoa văn; không tự thêm màu men beige, quai hay đĩa lót. | `approved` (text); chưa có ảnh riêng |
| Xe máy | Giữ nguyên anchor cũ: plain motorbike, blank license plate with no numbers and no letters. Không thêm vintage, bánh nan hoa hay kiểu gương bắt buộc. | `approved` (text); chưa có ảnh riêng |
| Phòng khách | Kế thừa ảnh chính diện; duyệt thêm góc cận bàn trà và biến thể buổi tối. Đổi góc/ánh sáng giữ nguyên kiến trúc, nội thất. | `approved` (thiết kế); góc/tình huống mới chưa có ảnh riêng |
| ENS An–Bố | Chưa có ảnh nhóm; chỉ tạo sau khi xác định cần bảng nhận diện hay bố cục cảnh cụ thể. | `draft` |
| Model đích | Chưa chọn provider/model/chế độ chạy; cấu hình ví dụ chỉ là giả lập. | Chưa xác minh capability |

Việc duyệt góc nhìn/ánh sáng là duyệt thiết kế, không chứng minh ảnh/video mới sinh đã đạt nghiệm thu. Ảnh ENS mới vẫn cần duyệt độc lập; không dùng trạng thái duyệt của hai nhân vật để tự duyệt ảnh nhóm.

---

## 3. Đặc Tả Hợp Đồng Dữ Liệu Pack (`kit.json`), Schema Rules & Cơ Chế Lockfile

### 3.1 Quy Tắc Hợp Lệ Theo Từng Loại Thực Thể (Schema Rules)
Quy tắc chung:
- Giữ nguyên 100% ID gốc khi migration. Ví dụ mục 3.2 chỉ là tập con để minh họa; migration thật phải giữ đủ 7 CHAR, 10 LOC và 2 PROP của kit gốc, rồi mới bổ sung thực thể mới.
- `status` chỉ nhận `draft | conflict | approved | deprecated`. Production chỉ chấp nhận `approved`; giá trị lạ bị lỗi schema. Trạng thái ghi trong ma trận phải khớp dữ liệu mẫu.
- Không tự nâng trạng thái khi migration. Mọi thay đổi thiết kế mới cần đối soát riêng; việc giữ ID không có nghĩa là đã duyệt nội dung mới.
- `ref` và `ref_hash` cùng null hoặc cùng có giá trị. `ref_hash` có giá trị phải là SHA-256 thực tế. `approved` ở cấp thực thể/variant cần thông tin duyệt (`approved_by`, `approved_date`); angle/lighting có thể kế thừa thông tin duyệt của thực thể khi có `approval_source` rõ ràng; ghi nhận nguồn duyệt kế thừa nếu có, không tạo chữ ký duyệt giả.
- Mỗi variant tham chiếu đúng ảnh của nó qua `ref` và `ref_hash`; không dùng ảnh default cho biến thể có thiết kế khác. Variant còn draft có thể chưa có ảnh.
- `identity` khóa cấu trúc hình học và nhận diện; màu bề mặt mặc định có thể được variant thay thế qua trường `surface_override` được duyệt. Compiler hợp nhất thành một mô tả duy nhất, không đồng thời yêu cầu thân trắng và áo sẫm ở cùng vùng. Không được override tóc, tỷ lệ hoặc cấu trúc chi bằng biến thể trang phục.

1. **`CHAR` (Nhân vật)**:
   - Bắt buộc: `id`, `type: "CHAR"`, `name`, `status`, `revision`, `identity` (head, torso, limbs, proportions, marks), `approved_variants`, `forbid`.
   - Nếu `status == "approved"`, bắt buộc phải có `ref` trỏ tới file ảnh tồn tại và `ref_hash` khớp mã SHA-256 thực tế.
2. **`LOC` (Địa điểm)**:
   - Bắt buộc: `id`, `type: "LOC"`, `name`, `status`, `revision`, `spatial_layout.fixed_relations`, `approved_angles`, `forbid`.
   - Bố cục `fixed_relations` phải tham chiếu hệ tọa độ phòng hoặc góc nhìn máy quay tham chiếu; không chứa hành động nhân vật.
3. **`PROP` (Đạo cụ)**:
   - Bắt buộc: `id`, `type: "PROP"`, `name`, `status`, `revision`, `shape`, `scale_relative`, `visible_faces`, `forbid`.
4. **`ENS` (Thực thể nhóm)**:
   - Bắt buộc: `id`, `type: "ENS"`, `name`, `status`, `revision`, `members`, `member_revisions`, `member_variants`, `reference_role`, `ref`.
   - `status` chỉ được là `"approved"` nếu tất cả `members` đều có `status: "approved"` với đúng `member_revisions` và `member_variants`.

### 3.2 Ví Dụ Pack Mẫu Có Khai Báo Các Điểm Chưa Chốt (`assets/kits/vietnamese-daily/kit.json`)

```json
{
  "pack": "vietnamese-daily",
  "title": "Stickman Kit — Sống Đáng Tiền + Chú mèo học…",
  "version": "3.1.0",
  "style": "A4 Cozy Storytelling: flat 2D stick figures on detailed full-color cartoon backgrounds, gentle light, warm watercolor",
  "global_rules": {
    "figure_construction": "white filled circular head, two small dark oval eyes, simple eyebrow strokes, short curved mouth, closed white torso with solid white fill inside dark outline (slim for youth, slightly overweight for middle-aged), dark single-line limbs with constant medium weight, small dark rounded paws/hands",
    "drawing_rule": "flat 2D stick figures on warm watercolor cartoon backgrounds, clear cartoon contours, gentle daylight, consistent line weights, no sketchbook borders, no 3D elements",
    "forbid": [
      "readable text, letters, or numbers in frames",
      "license plate numbers (must always be blank white plates)",
      "commercial logos or brand marks",
      "hollow or transparent circular heads",
      "cluttered modern digital gadgets unless explicitly specified",
      "crude hand drawings or rough paper overlays"
    ]
  },
  "entities": [
    {
      "type": "CHAR",
      "id": "CHAR_01_AN",
      "status": "approved",
      "revision": "rev-2026-11-17.1",
      "name": "An",
      "role": "nam chính, 28 tuổi, nhân viên văn phòng",
      "identity": {
        "head": "white filled circular head, no hair, two small dark oval eyes, simple eyebrow strokes, short curved mouth",
        "torso": "slim closed tapered torso with solid white fill inside dark outline",
        "limbs": "dark single-line limbs with constant medium weight, small dark rounded hands and short dark rounded feet",
        "proportions": "standard adult stickman height, head-to-body balanced",
        "marks": [
          "đầu tròn trắng đặc không tóc",
          "gương mặt tối giản chuẩn",
          "thân khép kín tô trắng"
        ]
      },
      "approved_variants": [
        {
          "variant_id": "DEFAULT_DAILY",
          "name": "Trang phục thường ngày",
          "outfit": "plain white closed torso, dark single-line legs; no trouser silhouettes",
          "status": "approved",
          "ref": "refs/an-tham-chieu-a4.png",
          "ref_hash": "081c4bbf3f7e5a766de595320c2efe99bc5af64fdf01992bcc3585d4b22d7f12",
          "approved_by": "Người dùng trong chat",
          "approved_date": "2026-11-17"
        }
      ],
      "habits": [
        "đứng thẳng nhìn người đối thoại",
        "cử chỉ nhanh nhẹn dứt khoát"
      ],
      "expressions": [
        "bình thường",
        "mỉm cười nhẹ",
        "trầm ngâm",
        "lo lắng"
      ],
      "forbid": [
        "vẽ tóc",
        "áo có họa tiết",
        "đầu rỗng xuyên thấu",
        "vòng đeo tay hoặc phụ kiện lạ"
      ],
      "ref": "refs/an-tham-chieu-a4.png",
      "ref_hash": "081c4bbf3f7e5a766de595320c2efe99bc5af64fdf01992bcc3585d4b22d7f12",
      "approved_by": "Người dùng trong chat",
      "approved_date": "2026-11-17"
    },
    {
      "type": "CHAR",
      "id": "CHAR_02_BO",
      "status": "approved",
      "revision": "rev-2026-11-17.1",
      "name": "Bố",
      "role": "bố của An, 55 tuổi, thói quen uống trà",
      "identity": {
        "head": "white filled circular head, short grey hair along the sides and back of the head, two short horizontal forehead wrinkles above the eyebrows, two small dark oval eyes, simple eyebrow strokes, short curved mouth",
        "torso": "slightly overweight closed torso with solid white fill inside dark outline",
        "limbs": "dark single-line limbs with constant medium weight",
        "proportions": "mature adult stickman height, slightly broader torso than An",
        "marks": [
          "short grey hair along the sides and back of the head",
          "two short horizontal forehead wrinkles above the eyebrows",
          "slightly overweight closed white torso"
        ]
      },
      "approved_variants": [
        {
          "variant_id": "BO_WHITE_TORSO",
          "name": "Thân trắng truyền thống (theo ảnh tham chiếu A4 hiện có)",
          "outfit": "plain white closed torso, dark single-line legs; no trouser silhouettes",
          "status": "approved",
          "ref": "refs/bo-tham-chieu-a4.png",
          "ref_hash": "655784d81ebcf9b6611f35baafaf75618fd52d9ec396044a11f8dc122f5bc1aa",
          "approved_by": "Người dùng trong chat",
          "approved_date": "2026-11-17"
        },
        {
          "variant_id": "BO_DARK_SHIRT",
          "name": "Áo dài tay sẫm màu (theo kịch bản tập 55-60)",
          "outfit": "plain dark long-sleeved top, long dark pants",
          "status": "draft",
          "ref": null,
          "ref_hash": null,
          "surface_override": {
            "torso": "plain dark long-sleeved top"
          }
        }
      ],
      "habits": [
        "chắp hai tay sau lưng khi đi dạo thong thả",
        "chậm rãi nâng tách trà bằng hai tay"
      ],
      "expressions": [
        "ôn tồn mỉm cười",
        "trầm ngâm suy tư",
        "nghiêm nghị",
        "xót xa lo lắng"
      ],
      "forbid": [
        "thân hình gầy mảnh",
        "thiếu nếp nhăn trán",
        "thiếu tóc hoa râm"
      ],
      "ref": "refs/bo-tham-chieu-a4.png",
      "ref_hash": "655784d81ebcf9b6611f35baafaf75618fd52d9ec396044a11f8dc122f5bc1aa",
      "approved_by": "Người dùng trong chat",
      "approved_date": "2026-11-17"
    },
    {
      "type": "ENS",
      "id": "ENS_01_AN_VA_BO",
      "status": "draft",
      "revision": "rev-2026-11-16.1",
      "notes": "Hai nhân vật đã chốt thiết kế ngày 2026-11-17; ảnh ENS chưa được tạo hoặc duyệt.",
      "name": "An và Bố bên bàn trà phòng khách",
      "members": [
        "CHAR_01_AN",
        "CHAR_02_BO"
      ],
      "member_revisions": {
        "CHAR_01_AN": "rev-2026-11-17.1",
        "CHAR_02_BO": "rev-2026-11-17.1"
      },
      "member_variants": {
        "CHAR_01_AN": "DEFAULT_DAILY",
        "CHAR_02_BO": "BO_WHITE_TORSO"
      },
      "location_id": "LOC_03_PHONG_KHACH",
      "reference_role": "composition",
      "layout": "Bố ngồi trên ghế bành gỗ bên trái, An ngồi đối diện bên phải, ở giữa là bàn trà gỗ thấp",
      "allowed_usage_condition": "Chỉ dùng khi cảnh diễn ra tại phòng khách bên bàn trà",
      "ref": null,
      "ref_hash": null
    },
    {
      "type": "LOC",
      "id": "LOC_03_PHONG_KHACH",
      "status": "approved",
      "revision": "rev-2026-11-17.1",
      "approved_by": "Người dùng trong chat",
      "approved_date": "2026-11-17",
      "name": "Phòng khách nhà An",
      "role": "bối cảnh sinh hoạt gia đình, Bố ngồi uống trà",
      "spatial_layout": {
        "fixed_relations": [
          "Từ góc nhìn máy quay chính diện (Front Wide View Anchor):",
          "- Tủ gỗ thấp đặt dọc theo bức tường phía bên trái (tường Tây)",
          "- Cửa sổ lớn đón nắng ở tường hậu cảnh (tường Bắc), rèm voan mỏng buông nhẹ",
          "- Ghế sofa gỗ đệm hoa dâm bụt đặt ở trung tâm phía trước cửa sổ lớn",
          "- Bàn trà gỗ thấp màu trầm đặt ở trung tâm ngay trước ghế sofa",
          "- Ghế bành gỗ đơn đặt bên trái bàn trà, vuông góc với ghế sofa"
        ],
        "coordinate_convention": "Bắc/Tây là nhãn nội bộ quy ước từ front_wide, không phải hướng địa lý đã đo.",
        "anchors": {
          "on_tea_table_center": {
            "support": "tea_table",
            "capacity": 1
          }
        }
      },
      "approved_angles": {
        "front_wide": {
          "foreground": "bàn trà gỗ thấp màu trầm",
          "middle_ground": "sofa gỗ đệm hoa dâm bụt, ghế bành gỗ, tủ gỗ thấp bên trái",
          "background": "cửa sổ lớn đón nắng, rèm voan mỏng, cây xanh ngoài vườn, nắng dịu buổi sáng",
          "status": "approved",
          "approval_source": "Người dùng duyệt thiết kế ngày 2026-11-17; đầu ra mới cần nghiệm thu riêng."
        },
        "table_close": {
          "foreground": "mặt bàn trà gỗ vân mộc",
          "middle_ground": "mép ghế bành gỗ bên trái",
          "background": "ánh sáng xiên từ cửa sổ hậu cảnh, mờ nhẹ dịu mắt",
          "status": "approved",
          "approval_source": "Người dùng duyệt thiết kế ngày 2026-11-17; đầu ra mới cần nghiệm thu riêng."
        }
      },
      "lighting_variants": {
        "morning": {
          "description": "ánh nắng dịu buổi sáng chiếu qua rèm voan tạo bóng đổ mềm mại",
          "status": "approved",
          "approval_source": "Người dùng duyệt thiết kế ngày 2026-11-17; đầu ra mới cần nghiệm thu riêng."
        },
        "evening": {
          "description": "ánh đèn vàng ấm áp từ đèn trần mộc mạc, ngoài cửa sổ là trời tối",
          "status": "approved",
          "approval_source": "Người dùng duyệt thiết kế ngày 2026-11-17; đầu ra mới cần nghiệm thu riêng."
        }
      },
      "forbid": [
        "đồng hồ treo tường có số",
        "lịch treo tường có chữ",
        "tivi màn hình phẳng hiện đại"
      ],
      "ref": "refs/phong-khach-tham-chieu.png",
      "ref_hash": "644bb61e4ffb191925deedf7a72fe10fa6012928d340b0380b5743c6025a6c32"
    },
    {
      "type": "PROP",
      "id": "PROP_02_XE_MAY",
      "status": "approved",
      "revision": "rev-2026-11-17.1",
      "name": "Xe máy đường phố",
      "shape": "plain motorbike, blank license plate with no numbers and no letters",
      "scale_relative": "Không bổ sung tỷ lệ thiết kế mới; đối chiếu kích thước với nhân vật khi dàn cảnh.",
      "visible_faces": {
        "all_views": "plain motorbike; any visible license plate is blank with no numbers and no letters"
      },
      "forbid": [
        "numbers or letters on license plate",
        "readable brand logos"
      ],
      "ref": null,
      "ref_hash": null,
      "approved_by": "Người dùng trong chat",
      "approved_date": "2026-11-17"
    },
    {
      "type": "PROP",
      "id": "PROP_03_TACH_TRA",
      "status": "approved",
      "revision": "rev-2026-11-17.1",
      "name": "Tách trà men gốm",
      "shape": "plain tea cup, no writing or decorative pattern",
      "scale_relative": "Kích thước tách trà phù hợp tay nhân vật; không bổ sung thiết kế mới.",
      "visible_faces": {
        "all_views": "plain tea cup; no newly prescribed glaze color, handle or saucer"
      },
      "forbid": [
        "readable writing",
        "decorative pattern"
      ],
      "ref": null,
      "ref_hash": null,
      "approved_by": "Người dùng trong chat",
      "approved_date": "2026-11-17"
    }
  ],
  "meta": {
    "name": "Stickman Kit — Sống Đáng Tiền + Chú mèo học…",
    "version": "3.1.0",
    "updated": "2026-11-16",
    "provider_limits": {
      "example-provider": {
        "example-model": {
          "reference_images": {
            "max_refs": 3,
            "supported_roles": [
              "identity",
              "composition"
            ]
          }
        }
      }
    },
    "provider_limits_note": "Cấu hình giả lập cho ví dụ; production phải dùng capability profile đã xác minh cho đúng provider/model/mode. Không suy ra giới hạn từ tên hãng."
  }
}
```

Đây là dữ liệu minh họa hợp đồng, chưa phải pack production. Các thiết kế được người dùng duyệt ngày 2026-11-17 đã cập nhật trạng thái; variant BO_DARK_SHIRT và ảnh ENS vẫn draft. `approved_angles` là tên trường danh mục; mỗi góc có `status` riêng, không mặc nhiên được duyệt vì nằm trong danh mục này.

### 3.3 Cơ Chế Khóa Bản Chuẩn Cho Dự Án (`project.lock.json`)
Để việc cập nhật `kit.json` trong tương lai không làm thay đổi âm thầm tạo hình của các tập phim cũ, mỗi dự án (`project.json`) có snapshot bất biến và lockfile:
- Lưu toàn bộ pack vào `snapshots/vietnamese-daily/kit.json`, sao chép các ảnh được dùng vào `snapshots/vietnamese-daily/refs/`. Đường dẫn ref giải quyết từ thư mục snapshot, không từ kit đang hoạt động.
- Compiler đọc thiết kế, global rules, variant, angle, lighting và ảnh từ snapshot; không tra phiên bản mới nhất. Thiếu snapshot, sai hash hoặc thiếu dependency thì dừng, kể cả khi revision ghi trong kit hiện tại vẫn giống.
- `kit_snapshot_sha256` băm JSON chuẩn hóa bằng Python `json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")`. Ảnh dùng hash byte gốc. Revision đã phát hành bất biến; cập nhật cần revision mới và thao tác relock tường minh.
- Lock phải bao phủ toàn bộ dependency các shot sử dụng, kể cả nhân vật, variant, ENS, LOC và PROP không có ảnh. Khóa angle/lighting trong project và nội dung tương ứng trong snapshot.
- Ví dụ dưới là **lock draft** cho đúng project hai shot ở mục 4; chưa được duyệt sản xuất. Hash snapshot tính từ pack minh họa mục 3.2. Các file snapshot sẽ được tạo ở P2, chưa được tuyên bố tồn tại chỉ vì có ví dụ này:

```json
{
  "project_id": "EPISODE_56_SONG_DANG_TIEN",
  "status": "draft",
  "locked_at": "2026-11-17T00:00:00Z",
  "kit_pack": "vietnamese-daily",
  "kit_pack_version": "3.1.0",
  "kit_snapshot": "snapshots/vietnamese-daily/kit.json",
  "kit_snapshot_sha256": "15ef726d1c28a02b58bf94040aa93a9c15e4d3c5001e0e1c86abb0a8e9c82f7d",
  "locked_entities": {
    "CHAR_02_BO": {
      "revision": "rev-2026-11-17.1",
      "ref_hash": "655784d81ebcf9b6611f35baafaf75618fd52d9ec396044a11f8dc122f5bc1aa",
      "variant": "BO_WHITE_TORSO"
    },
    "LOC_03_PHONG_KHACH": {
      "revision": "rev-2026-11-17.1",
      "ref_hash": "644bb61e4ffb191925deedf7a72fe10fa6012928d340b0380b5743c6025a6c32"
    },
    "PROP_03_TACH_TRA": {
      "revision": "rev-2026-11-17.1",
      "ref_hash": null
    }
  }
}
```

---

## 4. Hợp Đồng Dữ Liệu Đầu Vào Project & Biên Soạn Prompt Theo Shot (Shot Compiler Engine)

### 4.1 Hợp Đồng Dữ Liệu Đầu Vào: Dự Án Mẫu Hai Shot Liên Tiếp (`project.json`)
Dưới đây là hợp đồng chuẩn của một kịch bản gồm 2 shot tiếp nối liên tục: Shot 1 (Bố nhấc tách trà khỏi bàn) và Shot 2 (Cận cảnh Bố cầm tách trà uống, không reset vị trí tách về mặt bàn).

```json
{
  "project_id": "EPISODE_56_SONG_DANG_TIEN",
  "pack_ref": "vietnamese-daily@3.1.0",
  "timeline": [
    {
      "shot_id": "S01",
      "continuity_from": null,
      "cut_type": "scene_establish",
      "location": {
        "id": "LOC_03_PHONG_KHACH",
        "angle": "front_wide",
        "lighting": "morning"
      },
      "characters": [
        {
          "id": "CHAR_02_BO",
          "variant": "BO_WHITE_TORSO"
        }
      ],
      "prop_instances": [
        {
          "instance_id": "cup_01",
          "type_id": "PROP_03_TACH_TRA"
        }
      ],
      "initial_state": {
        "CHAR_02_BO": {
          "pose": "seated",
          "gaze": "looking downward at cup_01 on the tea table",
          "holding": null,
          "seat": "left_armchair",
          "hands": {
            "left": null,
            "right": null
          }
        },
        "cup_01": {
          "placed_at": "on_tea_table_center",
          "held_by": null,
          "fill_fraction": 1.0
        }
      },
      "events": [
        {
          "time_s": 1.0,
          "op": "pickup",
          "actor": "CHAR_02_BO",
          "target": "cup_01",
          "from": "on_tea_table_center",
          "hands": [
            "left",
            "right"
          ],
          "acting": "reach slowly, cup with both hands, then lift toward chest"
        }
      ],
      "narrative_action": "Bố ngồi trên ghế bành gỗ bên trái, từ từ vươn hai tay ôm lấy tách trà cup_01 trên bàn, rồi chậm rãi nâng tách lên trước ngực. Vị trí trên mặt bàn trở nên trống.",
      "expected_final_state": {
        "CHAR_02_BO": {
          "pose": "seated",
          "holding": "cup_01",
          "seat": "left_armchair",
          "hands": {
            "left": "cup_01",
            "right": "cup_01"
          }
        },
        "cup_01": {
          "placed_at": null,
          "held_by": "CHAR_02_BO",
          "fill_fraction": 1.0
        }
      },
      "required_refs": [
        "CHAR_02_BO",
        "LOC_03_PHONG_KHACH"
      ],
      "optional_refs": [],
      "duration_s": 4,
      "camera": {
        "framing": "medium",
        "movement": "static"
      }
    },
    {
      "shot_id": "S02",
      "continuity_from": "S01",
      "cut_type": "continuous",
      "location": {
        "id": "LOC_03_PHONG_KHACH",
        "angle": "table_close",
        "lighting": "morning"
      },
      "characters": [
        {
          "id": "CHAR_02_BO",
          "variant": "BO_WHITE_TORSO"
        }
      ],
      "prop_instances": [
        {
          "instance_id": "cup_01",
          "type_id": "PROP_03_TACH_TRA"
        }
      ],
      "initial_state": {
        "CHAR_02_BO": {
          "pose": "seated",
          "gaze": "contemplative, looking slightly forward",
          "holding": "cup_01",
          "seat": "left_armchair",
          "hands": {
            "left": "cup_01",
            "right": "cup_01"
          }
        },
        "cup_01": {
          "placed_at": null,
          "held_by": "CHAR_02_BO",
          "fill_fraction": 1.0
        }
      },
      "events": [
        {
          "time_s": 1.0,
          "op": "consume",
          "actor": "CHAR_02_BO",
          "target": "cup_01",
          "amount_fraction": 0.1,
          "acting": "bring cup to lips, take one small sip, return near chest"
        }
      ],
      "narrative_action": "Cận cảnh Bố hai tay nâng tách trà cup_01 sát miệng nhấp một ngụm nhỏ, ánh mắt suy tư trầm ngâm. Vị trí cũ của cup_01 trên bàn trống, không có bản sao tách trà nào khác.",
      "expected_final_state": {
        "CHAR_02_BO": {
          "pose": "seated",
          "holding": "cup_01",
          "seat": "left_armchair",
          "hands": {
            "left": "cup_01",
            "right": "cup_01"
          }
        },
        "cup_01": {
          "placed_at": null,
          "held_by": "CHAR_02_BO",
          "fill_fraction": 0.9
        }
      },
      "required_refs": [
        "CHAR_02_BO"
      ],
      "optional_refs": [
        "LOC_03_PHONG_KHACH"
      ],
      "duration_s": 4,
      "camera": {
        "framing": "close",
        "movement": "static"
      }
    }
  ],
  "lockfile": "project.lock.json",
  "target": {
    "provider": "example-provider",
    "model": "example-model",
    "mode": "reference_images"
  }
}
```

### 4.1a Quy Tắc Thực Thi Sự Kiện & Continuity
Hợp đồng event MVP (mọi op đều cần `time_s`, `op`, `actor`, `target`):

| Op | Trường bổ sung bắt buộc | Ý nghĩa |
| :--- | :--- | :--- |
| `pickup` | `from`, `hands` | Nhấc từ anchor, các tay là tập con không rỗng của left/right |
| `putdown` | `to` | Đặt vật đang giữ vào anchor đích |
| `handover` | `recipient`, `recipient_hands` | Trao cho actor khác, giải phóng toàn bộ tay người trao đang giữ vật |
| `consume` | `amount_fraction` | Giảm mức chất chứa theo tỷ lệ dung tích tối đa |

`acting` là trường diễn xuất tùy chọn. Actor/recipient phải là CHAR đã khai báo; target phải là instance đã định nghĩa; from/to phải thuộc anchors của LOC. State bắt buộc có pose/seat/holding/hands cho CHAR và placed_at/held_by cho instance; fill_fraction bắt buộc với instance được consume và nằm trong [0, 1].
- Danh mục `op` MVP chỉ gồm `pickup`, `putdown`, `handover`, `consume`. Op không biết phải báo lỗi; `acting` và `narrative_action` chỉ mô tả diễn xuất, không tự sửa trạng thái. `time_s` là số trong `[0, duration_s]`, tăng dần; MVP từ chối sự kiện trùng thời điểm để tránh thứ tự mơ hồ.
- `pickup`: kiểm tra vật đúng `from`, chưa được giữ, các tay liệt kê đang rảnh; xóa `placed_at`, gán `held_by`, `holding` và từng tay liên quan. `putdown`: kiểm tra actor đang giữ vật, anchor đích tồn tại và còn chỗ; giải phóng tay và đặt vật tại `to`. `handover`: kiểm tra người trao đang giữ vật, tay người nhận còn rảnh; cập nhật đồng thời hai người và vật. `consume`: kiểm tra actor đang giữ vật, `amount_fraction > 0` và không vượt mức còn lại; trừ lượng đã dùng. Một ngụm ví dụ giảm từ 1.0 xuống 0.9, không mặc định thành nửa tách.
- Linter tính `computed_final_state` từ `initial_state + events`, rồi so các trường trạng thái bắt buộc với `expected_final_state`. Không tin trạng thái cuối do tác giả tự khai báo nếu sự kiện không tạo ra nó. MVP mỗi actor giữ tối đa một instance; cho phép cùng instance nằm trong cả hai tay.
- Trường continuity máy kiểm tra: `holding`, `hands`, `seat`, `pose` chuẩn hóa, `held_by`, `placed_at`, `fill_fraction`. `gaze`, khung hình camera và diễn xuất không tham gia so sánh bằng chuỗi; close-up không tự làm đổi trạng thái vật lý.
- `continuous`: trạng thái vật lý đầu shot phải khớp trạng thái cuối đã tính của `continuity_from`, không so toàn bộ JSON hoặc câu mô tả tư thế. `time_jump/location_cut` phải khai báo `state_changes` gồm giá trị trước/sau và lý do cho mọi thay đổi vật lý; đổi địa điểm không tự cho phép vật biến mất hoặc đổi người giữ.
- `instance_id` có định nghĩa bất biến trong project: lặp ID qua shot là cùng vật, không tạo vật mới; đổi `type_id` bị lỗi. Vật ngoài khung vẫn tồn tại trong state ledger và không bắt buộc xuất trong prompt. Mỗi instance chỉ có một nơi đặt hoặc một người giữ; `holding`, `hands`, `held_by` phải nhất quán hai chiều. Hai instance ở cùng vị trí chỉ lỗi nếu anchor khai báo capacity không đủ; cùng ở trên bàn chưa phải lỗi nhân bản.
- `continuity_from` phải trỏ shot trước đó trong timeline, không tạo vòng; project mẫu vẫn là draft vì target example-provider là cấu hình giả lập, chưa xác minh capability thực tế. Production dùng fixture đã duyệt riêng để kiểm tra happy path, không sửa trạng thái mẫu để lách gate.

### 4.2 Cú Pháp Thực Thi & Chế Độ Biên Soạn
```bash
# 1. Biên soạn chế độ sản xuất (nghiêm ngặt - từ chối nếu có conflict hoặc draft):
node scripts/autopilot.mjs kit compile --project project.json --shot S01 --mode prod

# 2. Biên soạn chế độ nháp đối soát (cho phép kiểm tra thực thể conflict, kèm cờ cảnh báo):
node scripts/autopilot.mjs kit compile --project project.json --shot S01 --draft

# 3. Kiểm tra tính liên tục (Continuity Linter) giữa các shot trong timeline:
node scripts/autopilot.mjs kit lint --project project.json
```

### 4.3 Đầu Ra Prompt Hoàn Chỉnh Của Compiler (Minh Họa Shot S01 & S02)
Hai prompt dưới là bản preview với target giả lập; các thiết kế đang dùng đã được duyệt ngày 2026-11-17. Compiler phải liệt kê **đầy đủ** dependency chưa duyệt trong diagnostics và gắn cảnh báo vào mỗi prompt độc lập; cảnh báo của S01 không thay thế cảnh báo S02. Chế độ draft chỉ nới gate duyệt, không bỏ qua schema, hash, continuity hoặc quota. Bố thân trắng là lựa chọn chính thức; tách giữ mô tả trơn cũ, không thêm màu men mới.

#### Đầu Ra Shot S01 (Preview với model giả lập)
```text
[DRAFT PREVIEW: example-provider is a test capability profile; production target has not been verified.]

[STYLE & FIGURE CONSTRUCTION]
A4 Cozy Storytelling: 2D flat minimalist cartoon stick figures on warm watercolor background, gentle natural light, clean contours. White filled circular head with solid white fill, two small dark oval eyes, simple eyebrow strokes, short curved mouth. Closed white torso with solid white fill inside dark outline. Limbs are dark single-line strokes of constant medium weight. Exactly two arms and two legs, no limb ghosting. No readable text, no numbers, no brand logos.

[STATIC DESIGN ANCHORS]
- CHAR_02_BO (Variant: BO_WHITE_TORSO): Mature stickman, white filled circular head, short grey hair along sides and back of head, two short horizontal forehead wrinkles above eyebrows, slightly overweight closed torso with solid white fill inside dark outline, dark single-line arms and legs, no trouser silhouettes.
- LOC_03_PHONG_KHACH (Angle: front_wide, Lighting: morning): Living room tea corner. From front view anchor: low dark wooden cabinet on the far left, sheer white curtain covering large background window with morning daylight, wooden sofa with red hibiscus cushions in center, low wooden tea table in front of sofa, wooden armchair on the left.
- PROP_03_TACH_TRA (Instance: cup_01): Plain tea cup with no writing or decorative pattern; preserve the existing approved simple design.

[FIRST FRAME & PLACEMENT]
Bố is sitting in the wooden armchair on the left, looking downward at cup_01 which rests quietly on the center of the wooden tea table. Both of Bố's dark single-line hands rest on his knees.

[TIMED TRANSFERS & ACTION]
At 01.0s, Bố slowly extends both single-line arms toward the table, cupping cup_01 with both rounded hands. He then lifts cup_01 smoothly off the table toward his chest, completing the pickup before the shot ends. The center of the table where cup_01 rested is now clearly empty.

[FINAL STATE / CONTINUITY HANDOFF]
Bố holds cup_01 with both hands near his chest. The former resting spot of cup_01 remains empty; other approved set dressing is unaffected. Handoff cup_01 as held by CHAR_02_BO into subsequent shot.

[REFERENCE MANIFEST]
- Ref 1 (identity): refs/bo-tham-chieu-a4.png (Role: Lock Bố's facial wrinkles, grey hair, overweight white torso)
- Ref 2 (composition): refs/phong-khach-tham-chieu.png (Role: Lock living room furniture layout)
Quota used: 2/3 (example capability profile). Pruned refs: None.
```

#### Đầu Ra Shot S02 (Draft, tiếp nối liên tục từ S01)
```text
[DRAFT PREVIEW: example-provider is a test capability profile; production target has not been verified.]
[STYLE & FIGURE CONSTRUCTION]
A4 Cozy Storytelling: 2D flat minimalist cartoon stick figures on warm watercolor background, gentle natural light, clean contours. White filled circular head with solid white fill, two small dark oval eyes, simple eyebrow strokes, short curved mouth. Closed white torso with solid white fill inside dark outline. Limbs are dark single-line strokes of constant medium weight. Exactly two arms and two legs, no limb ghosting. No readable text, no numbers, no brand logos.

[STATIC DESIGN ANCHORS]
- CHAR_02_BO (Variant: BO_WHITE_TORSO): Mature stickman, white filled circular head, short grey hair along sides and back of head, two short horizontal forehead wrinkles above eyebrows, slightly overweight closed torso with solid white fill inside dark outline, dark single-line arms and legs, no trouser silhouettes.
- LOC_03_PHONG_KHACH (Angle: table_close, Lighting: morning): Close-up of wooden tea table corner, soft daylight filtering through sheer curtain in soft-focus background.
- PROP_03_TACH_TRA (Instance: cup_01): Plain tea cup with no writing or decorative pattern; preserve the existing approved simple design.

[FIRST FRAME & PLACEMENT]
Continuous cut from S01. Bố is sitting upright, already holding cup_01 with both hands near his chest. The former resting spot of cup_01 is empty; there is no duplicate of cup_01 on the table.

[TIMED TRANSFERS & ACTION]
At 01.0s, Bố brings cup_01 to his lips, slowly taking a small gentle sip. His eyes look forward thoughtfully. The camera maintains a stable close shot on Bố.

[FINAL STATE / CONTINUITY HANDOFF]
Bố holds cup_01 near his chest, liquid level at 90% of capacity after one small sip.

[REFERENCE MANIFEST]
- Ref 1 (identity): refs/bo-tham-chieu-a4.png (Role: Lock Bố's close-up facial features)
- Ref 2 (composition): refs/phong-khach-tham-chieu.png (Role: Furniture identity only; use the authored close framing, omit movable set dressing unless declared)
Quota used: 2/3 (example capability profile). Pruned refs: None.
```

---

## 5. Thiết Kế Kỹ Thuật & Phân Lập Linter Tự Động vs Đối Soát Thị Giác

### 5.0 Chính Sách Chọn Ref Và Payload
- Project bắt buộc chọn `target.provider/model/mode`; không có capability profile đã xác minh thì production dừng. Profile giả lập trong ví dụ chỉ dành cho test deterministic, không đại diện giới hạn dịch vụ thật.
- Trước quota, kiểm tra ref tồn tại, trạng thái, hash và vai trò được model hỗ trợ. Không có ảnh của required ref là lỗi ngay cả khi còn slot. Tính quota trên file đính kèm duy nhất sau deduplicate và ENS coverage, không đếm số ID thô.

**Quy tắc ENS thay thế CHAR ref (ENS-covers-CHAR):**
> Nếu tồn tại một ENS `approved` phủ **đúng toàn bộ** tập nhân vật S xuất hiện trong shot (cùng revision và variant), ENS đó chiếm 1 slot và **loại bỏ toàn bộ CHAR ref của S**. Không dùng cả ENS lẫn CHAR ref của thành viên trong cùng slot set — đây là xung đột ưu tiên. CHAR ref chỉ giữ lại khi không có ENS phủ đủ hoặc ENS không thoả điều kiện revision/variant/location.

**Quy tắc giữ slot LOC tối thiểu:**
> **Luôn dành ít nhất 1 slot cho ảnh LOC** nếu shot có địa điểm có ảnh `approved`. Thứ tự phân bổ:
> 1. ENS (nếu hợp lệ, thay toàn bộ CHAR được phủ) — hoặc CHAR required theo số nhân vật thực trong shot.
> 2. Dành 1 slot cho LOC required trước khi lấy thêm CHAR/PROP optional.
> 3. Các optional refs điền vào slot còn thừa theo thứ tự khai báo.
>
> **Trường hợp đặc biệt — ≥ 3 nhân vật mà không có ENS hợp lệ:**
> Nếu shot yêu cầu ≥ 3 nhân vật trong `required_refs` và không có ENS hợp lệ phủ đủ, compiler **không được tự bỏ LOC để giải phóng slot cho CHAR**. Thay vào đó, compiler dừng và phát cảnh báo cứng:
> ```
> WARN [quota]: Shot SXX có N nhân vật required nhưng không có ENS hợp lệ.
>   → Giải pháp: (a) Tạo và duyệt ENS cho nhóm này,
>                (b) tách shot thành các cảnh nhỏ hơn 3 nhân vật,
>                (c) xác nhận tường minh thiếu LOC ref qua flag --allow-no-loc.
> ```
> Chỉ tiếp tục biên soạn nếu có `--allow-no-loc` tường minh; manifest phải ghi rõ LOC bị bỏ và lý do.

- ENS chỉ thay các thành viên trùng đúng revision/variant; `members` không được kéo người ngoài cast vào ảnh. Composition/first_frame còn phải khớp địa điểm, góc, lighting và trạng thái bố cục phù hợp. ENS identity không có location_id không bị loại chỉ vì shot đổi địa điểm. Không có ENS hợp lệ và required refs vượt quota thì dừng.
- Giữ optional refs theo thứ tự khai báo trong project, lấy hết nếu còn slot; nếu bỏ phải ghi ID và lý do vào manifest. Ví dụ S02 có 2/3 slot nên giữ cả ảnh phòng khách.
- Manifest máy đọc được tách khỏi chuỗi prompt gửi model: `attachments` ghi đường dẫn snapshot, SHA-256, vai trò, thực thể được phủ và lý do lựa chọn; `pruned_refs` ghi lý do bỏ. Phần manifest trong ví dụ là báo cáo cho người đọc, không phải bằng chứng đã upload ảnh. Adapter phải kiểm tra và gửi ảnh thực tế theo khả năng API; khi chỉ xuất prompt thủ công, báo rõ ảnh cần đính kèm.
- Ảnh LOC có đồ vật di chuyển sẵn (như ấm và nhiều tách) chỉ khóa kiến trúc/nội thất. Trạng thái instance quyết định vật nào hiện diện; không diễn giải “chỗ cup_01 trống” thành “xóa toàn bộ đồ trên bàn”. Đối soát đầu ra riêng để phát hiện xung đột giữa ảnh nền và state.

### 5.1 Phân Lập Hai Cấp Độ Kiểm Tra (Verification Separation)

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. DETERMINISTIC AUTOMATED LINTER (Máy tính tự kiểm tra)                │
│    - JSON Schema validation & required fields check                    │
│    - File existence & SHA-256 hash exact match check                   │
│    - ID uniqueness & cross-reference integrity                         │
│    - Conflict detection: Chặn compile ở mode prod nếu mang status      │
│      'conflict' hoặc 'draft'                                           │
│    - Continuity Linter: Phân tích mảng events có cấu trúc              │
│      (báo lỗi nếu nhấc vật khi tay bận, hoặc nhấc vật không ở vị trí)  │
│    - Quota: kiểm tra attachment required sau ENS và deduplicate      │
├────────────────────────────────────────────────────────────────────────┤
│ 2. VISUAL SEMANTIC AUDIT (Con người hoặc Vision Model đối soát)        │
│    - Đối chiếu ảnh PNG thực tế xem có đúng tóc, nếp nhăn, thân trắng   │
│    - Đánh giá sản phẩm sinh ra từ 6 shot Benchmark Test Sequence       │
│    - Ký duyệt (sign-off) chuyển trạng thái từ draft/conflict sang      │
│      approved kèm thông tin approved_by và approved_date               │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Kiến Trúc Engine Python (`skills/directing-stickman-videos/scripts/visual-bible-kit.py`)
- `load_pack(pack_path)`: Kiểm tra hợp lệ `kit.json` và mã băm SHA-256 của các file ảnh tham chiếu.
- `lint_project(project_path)`:
  - Đọc timeline sự kiện có cấu trúc (`events`).
  - Duyệt trạng thái của từng instance qua các shot liên tiếp (`continuity_from`).
  - Nếu `cut_type == "continuous"`: So các trường vật lý đã chuẩn hóa trong `initial_state` với `computed_final_state` của shot nguồn; quy tắc cụ thể tại 4.1a.
  - Nếu `cut_type in ["time_jump", "location_cut"]`: Cho phép thay đổi vị trí của các instance nhưng bắt buộc phải có khai báo tường minh.
- `compile_shot(project_path, shot_id, mode="prod")`:
  - Đọc và kiểm tra snapshot/lock trước khi chọn dữ liệu; production đòi lock đã duyệt. Chạy lint project trước khi xuất prompt; không xuất bản production cho project còn lỗi continuity ở shot khác.
  - Kiểm tra trạng thái của các thực thể tham gia. Nếu `mode == "prod"` và bất kỳ dependency thực thể/variant/angle/lighting nào không phải `approved` $\rightarrow$ Ném ngoại lệ `ValidationError` chặn build.
  - Phân bổ ref: Resolve ref/ENS theo mục 5.0, sau đó so số attachment bắt buộc duy nhất với quota target. Nếu vượt quá $\rightarrow$ Ném lỗi `QuotaExceededError`. Tự động cắt tỉa `optional_refs` nếu cần và ghi nhận vào manifest.
  - Lắp ráp 6 khối prompt văn bản hoàn chỉnh.

---

## 6. Lộ Trình Triển Khai Chi Tiết (Work Breakdown Structure)

> [!IMPORTANT]
> **Nguyên Tắc Điều Hành**: Chốt hoàn tất mục 1 đến mục 4 (Hợp đồng dữ liệu, ma trận đối soát và project mẫu) trước khi viết engine code để tránh sửa đổi kiến trúc khi đang lập trình.

| Giai đoạn | Nhiệm vụ trọng tâm | Sản phẩm đầu ra (Deliverables) |
| :--- | :--- | :--- |
| **P1. Chốt Bản Chuẩn & Ma Trận Đối Soát** | - Ghi quyết định người dùng ngày 2026-11-17 (Bố thân trắng, An chân nét đơn) vào dữ liệu migration; không hỏi duyệt lại.<br>- Tính toán và khóa mã băm SHA-256 cho 12 file ảnh A4.<br>- Đồng bộ anchor với quyết định đã duyệt; đối soát các thực thể khác trước khi migration. | `docs/kit-stickman/audit-matrix-2026-11-16.md`<br>Bảng SHA-256 chính thức. |
| **P2. Hoàn Thiện Schema & Migration Kit Mẫu** | - Đóng gói `core-schema.json` và `project-schema.json` với enum trạng thái, event op và quy tắc theo type; viết semantic validator riêng cho tham chiếu chéo, file/hash và timeline.<br>- Di chuyển dữ liệu sang `assets/kits/vietnamese-daily/kit.json`.<br>- Bảo toàn 100% ID gốc; chuyển đường dẫn tương đối portable.<br>- Tạo snapshot JSON/ảnh bất biến và lockfile bao phủ dependency; kiểm tra hash trước mỗi compile. | `assets/kits/core-schema.json`<br>`assets/kits/vietnamese-daily/kit.json`<br>`project.lock.json` |
| **P3. Xây Dựng Engine Compiler & Continuity Linter** | - Viết module `compile_shot` và `lint_project` trong Python.<br>- Xử lý sự kiện có cấu trúc (`pickup`, `putdown`, `handover`, `consume`).<br>- Triển khai cơ chế kiểm tra `mode="prod"` vs `mode="draft"`. | `scripts/visual-bible-kit.py` |
| **P4. Bộ Chọn Ref & Ràng Buộc Quota Theo Model** | - Đọc cấu hình ma trận `provider_limits`.<br>- Phân định xử lý `required_refs` (hard stop khi vượt) và `optional_refs` (tự tỉa).<br>- Ràng buộc kích hoạt ENS theo `member_variants` và `location_id`. | Module `resolve_refs` trong `visual-bible-kit.py` |
| **P5. Tích Hợp CLI Autopilot** | - Cập nhật CLI `autopilot.mjs kit` với các subcommand: `list`, `audit`, `compile`, `lint`, `check`.<br>- Xây dựng bộ test tự động `tests/verify-visual-bible-kit.py`. | `scripts/autopilot.mjs`<br>`tests/verify-visual-bible-kit.py` |
| **P6. Thử Nghiệm Chuỗi Hình Thực Tế (Benchmark Suite)** | - Chạy thử nghiệm chuỗi 6 shot thực tế qua AI model.<br>- Lập báo cáo đánh giá thị giác độc lập `Visual Consistency Assessment Report`. | `tests/reports/visual-bible-benchmark-report.md` |

---

## 7. Tiêu Chí Nghiệm Thu Hai Nhóm (Acceptance Criteria)

### 7.1 Nhóm 1: Kiểm Tra Dữ Liệu Tự Động (Automated Linter Pass)
1. **Khóa bản chuẩn**: Mọi file ảnh tham chiếu khai báo phải có mã SHA-256 khớp tuyệt đối với `ref_hash` — bất kỳ file nào không khớp là lỗi build.
2. **Chặn lỗi sản xuất**: Lệnh `kit compile --mode prod` từ chối biên soạn mọi shot có thực thể hoặc variant mang trạng thái `conflict` hoặc `draft`.
3. **Continuity Linter**:
   - Bắt được lỗi nếu Shot $N+1$ (continuous cut) khai báo đồ vật xuất hiện trở lại trên bàn trong khi Shot $N$ đã ghi nhận nhân vật nhấc đi.
   - Bắt được lỗi một instance xuất hiện ở nhiều nơi, quan hệ tay/người giữ mâu thuẫn hoặc vượt capacity anchor; không coi hai tách khác nhau cùng trên bàn là lỗi.
4. **Snapshot và tái lập**: Sửa kit đang hoạt động không làm đổi prompt dự án đã lock; sửa snapshot hoặc ảnh snapshot phải gây lỗi hash. Thiếu dependency Bố/variant hoặc lock chỉ chứa hash ảnh mà thiếu snapshot thiết kế phải thất bại.
5. **State machine**: Tính trạng thái cuối từ events; từ chối unknown op, thời gian sai, nhấc vật sai vị trí, tay bận và expected_final_state không khớp. Hai shot mẫu pass logic continuity ở draft nhưng fail production vì target còn giả lập; fixture conflict/draft riêng phải chứng minh gate duyệt vẫn hoạt động.
6. **Quota Hard Stop**: Báo lỗi và dừng biên dịch nếu số attachment required sau ENS/deduplicate vượt quota target; thiếu file required cũng thất bại. S02 phải giữ optional LOC khi còn slot.
7. **Độc lập và sạch sẽ**: Prompt xuất ra không chứa các mô tả rác của thực thể không có mặt trong shot.

### 7.2 Nhóm 2: Đánh Giá Kết Quả Thị Giác Thực Tế (Visual Consistency Verification)
Được đánh giá thông qua chuỗi 6 shot chuẩn (**Benchmark Test Sequence**):

```
[S01: Toàn thân] ──> [S02: Cận mặt] ──> [S03: Nghiêng/Đổi góc]
       │
       ▼
[S04: Tương tác đồ vật & Di chuyển] ──> [S05: Nhóm ENS] ──> [S06: Quay lại địa điểm cũ]
```

- **S01 (Toàn thân)**: Đúng tỷ lệ đầu/thân, thân khép kín tô trắng, chi nét đơn, Bố hơi đậm người hơn An.
- **S02 (Cận mặt)**: Nếp nhăn trán và tóc hoa râm của Bố giữ nguyên phong cách tối giản hoạt hình, không biến thành nét 3D.
- **S03 (Đổi góc nhìn)**: Xoay góc máy không làm biến dạng hình khối đầu, không mọc thêm chi thứ ba.
- **S04 (Tương tác đồ vật & Handoff)**: Nhân vật cầm đúng tách trà; vị trí cũ trên bàn hoàn toàn trống; shot tiếp nối không tự hồi sinh tách trà trên bàn.
- **S05 (Cảnh nhóm ENS)**: Đúng 2 nhân vật, đúng vị trí ghế sofa và ghế bành, không tráo đổi đặc điểm nhận diện.
- **S06 (Quay lại địa điểm cũ)**: Cấu trúc không gian phòng khách giữ đúng quan hệ topo (tủ gỗ bên trái, cửa sổ sau sofa, bàn trà ở giữa).

**Phép thử tính nhất quán (Consistency Stress Test):** Ngoài chuỗi 6 shot trên, sinh thêm N ≥ 3 lần lặp cho cùng một nhân vật ở cùng loại shot (ví dụ: S01 toàn thân × 3 lần với seed khác nhau), rồi chấm từng kết quả theo checklist dưới đây. Kết quả được ghi vào báo cáo benchmark; không có "khớp" hay "không khớp" tuyệt đối — chỉ có số mục đạt / tổng mục trên từng lần sinh.

| Hạng mục checklist | Mô tả |
|:---|:---|
| Dấu nhận diện | Đúng màu tóc, nếp nhăn, hình đầu tròn không méo |
| Tỉ lệ cơ thể | Đầu/thân đúng tỉ lệ; không thêm bớt chi |
| Cấu trúc thân | Thân khép kín tô trắng (Bố), chi nét đơn — không phải nét đơn thân |
| Trang phục / variant | Đúng variant đã compile (BO_WHITE_TORSO, DEFAULT_DAILY, …) |
| Không có rác ngoài cast | Không xuất hiện nhân vật, đồ vật ngoài khai báo trong shot |
| Topo địa điểm | Vị trí tương đối đồ vật, cửa, cửa sổ nhất quán với LOC anchor |

Mỗi lần sinh được ghi điểm (số mục đạt / 6). Nếu điểm trung bình < 5/6 trên N lần hoặc bất kỳ lần nào < 4/6 thì prompt anchor của nhân vật cần được tăng cường trước khi kit được phê duyệt sản xuất.

> [!NOTE]
> Báo cáo kiểm thử tự động (`Automated Linter Pass`) và Báo cáo đánh giá thị giác (`Visual Consistency Assessment Report`) là hai tài liệu tách biệt hoàn toàn. Phiên bản kit chỉ được cấp chứng chỉ phát hành sản xuất khi cả hai báo cáo đều không còn điểm chưa đạt.
