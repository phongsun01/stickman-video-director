# Biên Bản Đối Soát Bản Chuẩn & Ma Trận Xung Đột Ảnh — Chữ

> **Mã biên bản:** `AUDIT-STICKMAN-A4-2026-11-16`  
> **Ngày lập:** 2026-11-16  
> **Đối tượng thẩm định:** 12 file ảnh tham chiếu A4 tại `docs/kit-stickman/` và dữ liệu `kit-stickman.json`  
> **Người thực hiện:** Antigravity System Auditor

---

## 1. Bảng Khóa Mã Băm SHA-256 Của 12 Ảnh Tham Chiếu A4

Mọi file ảnh tham chiếu chuẩn A4 phải được kiểm tra tính toàn vẹn thông qua mã băm SHA-256 dưới đây:

| File ảnh tham chiếu | Kích thước | SHA-256 Hash |
| :--- | :--- | :--- |
| `an-tham-chieu-a4.png` | 2,203,290 bytes | `081c4bbf3f7e5a766de595320c2efe99bc5af64fdf01992bcc3585d4b22d7f12` |
| `bin-tham-chieu-a4.png` | 2,094,949 bytes | `b2a3bd254b9d936c405c180f826298c191b551389e971f5ff90cec8c57e97fd0` |
| `bo-tham-chieu-a4.png` | 1,935,457 bytes | `655784d81ebcf9b6611f35baafaf75618fd52d9ec396044a11f8dc122f5bc1aa` |
| `lan-tham-chieu-a4.png` | 2,234,558 bytes | `1398a9fe4eae0287426f53b79dadc5a378efb108a5d8d5776db08952af76719c` |
| `me-lan-tham-chieu-a4.png` | 1,710,674 bytes | `89f6fff4acf240abc2037e504d15ca1da17644df307ee67cfecaaab7473da6e2` |
| `cho-vn-tham-chieu.png` | 3,673,682 bytes | `5fb11a2a5cecaea7d8a598b20a1284f3eea7c0dc9b4e88797b055f11a5619f6f` |
| `hem-vn-tham-chieu.png` | 3,771,883 bytes | `31c2609a4e6e12d962d1b65fb20d2446af2ce34dae01260e4918bc68c0f83a81` |
| `nga-tu-buoi-toi-tham-chieu.png` | 3,607,964 bytes | `0cae4ee26fdb769445c666dddbb768abe2d2b7360ca0ddcaed26666138392851` |
| `nga-tu-den-xanh-tham-chieu.png` | 3,570,203 bytes | `e04de09a2624cb245854f57c3a36d244a3b8c868f324a7c927abf36e9d561af0` |
| `pho-vn-sang-tham-chieu.png` | 3,464,424 bytes | `f877939ea74bb820b68de1971f9e0223c628b529ee88436cb3d06e38add89437` |
| `phong-khach-tham-chieu.png` | 2,897,917 bytes | `644bb61e4ffb191925deedf7a72fe10fa6012928d340b0380b5743c6025a6c32` |
| `quan-cafe-tham-chieu.png` | 3,375,746 bytes | `79b61f15dbc0d953f8f8c7ac879d13a5f5ce3bebee1584efae9311a492f7d26a` |

---

## 2. Ma Trận Xung Đột Ban Đầu (Lịch Sử, Đã Được Quyết Định 2026-11-17 Thay Thế)

| ID Thực thể | Tên | Trạng thái | Điểm xung đột đối soát | Quyết định kỹ thuật |
| :--- | :--- | :--- | :--- | :--- |
| `CHAR_01_AN` | An | `pending_clarification` | JSON ghi `long dark pants` nhưng ảnh tham chiếu A4 thể hiện chân là các vạch nét đơn tối màu (`dark single-line limbs`), không vẽ rõ ống quần. Không có vòng tay trái. | Tạm coi là thống nhất ở mức biểu hiện que tối màu; loại bỏ mọi ý tưởng thêm vòng tay trái. Cần đối soát thêm khi tạo dáng cận cảnh. |
| `CHAR_02_BO` | Bố | `conflict` | JSON cũ ghi "plain dark long-sleeved top" (áo dài tay sẫm màu), trong khi ảnh `bo-tham-chieu-a4.png` thể hiện thân khép kín tô trắng đặc (`closed white torso`). | **Chặn ở chế độ sản xuất (`--mode prod`)**. Cần phê duyệt thiết kế: hoặc cập nhật ảnh áo tối màu, hoặc chốt variant thân trắng làm chuẩn. |
| `CHAR_03_LAN` | Lan | `approved` | Tóc buộc đuôi ngựa thấp, áo trắng, váy chữ A ngang gối màu sẫm. Khớp hoàn toàn. | Phê duyệt bản chuẩn. |
| `CHAR_04_ME_LAN` | Mẹ Lan | `approved` | Búi tóc thấp có sợi bạc, áo tối màu, váy dài tối màu. Khớp hoàn toàn. | Phê duyệt bản chuẩn. |
| `CHAR_05_BIN` | Bin | `approved` | Chiều cao bằng 1/2 Bố, đầu tròn trắng không tóc. Khớp hoàn toàn. | Phê duyệt bản chuẩn. |
| `CHAR_06_MIMI` | Mimi | `draft` | Chưa có ảnh tham chiếu trên đĩa (`ref: null`). | Để trạng thái `draft`. |
| `CHAR_07_BIBO` | Bibo | `draft` | Chưa có ảnh tham chiếu trên đĩa (`ref: null`). | Để trạng thái `draft`. |
| `LOC_01_PHO_VN` | Phố sáng | `approved` | Nhà ống mái ngói, xe máy đậu dọc biển số trắng trơn, không chữ đọc được. | Phê duyệt bản chuẩn. |
| `LOC_03_PHONG_KHACH` | Phòng khách | `approved` | Góc nhìn chính diện: tủ gỗ thấp ở bên trái (tường Tây), cửa sổ đón nắng ở hậu cảnh (tường Bắc), sofa ở giữa, bàn trà trước sofa. | Sửa lại spatial layout cho tủ gỗ ở bên trái (không phải bên phải). Loại bỏ rác "gạch men sáng trơn" và hành động nhân vật khỏi LOC. |
| `LOC_06_CHO` | Chợ VN | `approved` | Sạp rau quả, rổ tre, mái che vải trơn, không chữ. | Phê duyệt bản chuẩn. |
| `LOC_07_HEM` | Hẻm nhỏ | `approved` | Hẻm lát đá, chậu cây, xe máy, dây phơi trơn. | Phê duyệt bản chuẩn. |
| `LOC_08_QUAN_CAFE` | Quán cà phê | `approved` | Bàn gỗ tròn, ghế nhựa, quầy gỗ, bảng menu trống trơn. | Phê duyệt bản chuẩn. |
| `LOC_09_NGA_TU_NGAY` | Ngã tư ngày | `approved` | Cột đèn xanh, xe máy biển trắng trơn, nhà ống xen nhà kính. | Phê duyệt bản chuẩn. Cần lưu ý cột đèn sáng cả vàng lẫn xanh trong ảnh ref; prompt cần ghi rõ chỉ sáng 1 bóng. |
| `LOC_10_NGA_TU_TOI` | Ngã tư tối | `approved` | Đèn đỏ, đèn đường vàng, trời hoàng hôn. | Hai bối cảnh ngã tư ngày/đêm là hai góc nhìn tham chiếu riêng biệt đang trong diện đối soát cấu trúc không gian. |
| `PROP_01_CHAU_HOA_VANG`| Chậu hoa | `draft` | Chưa có ảnh ref. | Để trạng thái `draft`. |
| `PROP_02_XE_MAY` | Xe máy | `approved` (text) | Biển số trắng trơn hoàn toàn không chữ và số. Chưa có ảnh ref. | Giữ ID `PROP_02_XE_MAY`; `ref: null`, `ref_hash: null`. |
| `PROP_03_TACH_TRA` | Tách trà men | `approved` (text) | Tách trà men gốm không quai, không hoa văn. | Tách riêng thành PROP độc lập để theo dõi instance (`cup_01`, `cup_02`). |
| `ENS_01_AN_VA_BO` | An và Bố | `draft` | Chưa có file ảnh nhóm trên đĩa; phụ thuộc vào Bố đang `conflict`. | Để trạng thái `draft`, `ref: null`, `ref_hash: null`. Chặn ở production. |

## 3. Quyết định hiện hành ngày 2026-11-17

Người dùng đã chốt Bố thân trắng và An chân nét đơn; hai thiết kế mặc định là approved. Giữ nguyên mô tả cũ của tách trà trơn và xe máy trơn/biển trắng; không tự thêm men beige hoặc dáng vintage. Góc cận bàn trà và phòng khách buổi tối được duyệt về thiết kế. ENS chưa có ảnh nên vẫn draft. Ma trận mục 2 giữ làm lịch sử, không được dùng để mở lại các quyết định đã chốt.

Pack 3.1.1 và snapshot dự án chứa những quyết định này. Các hash ảnh mục 1 giữ nguyên. Kết quả ảnh/video mới vẫn cần đánh giá thị giác riêng; kiểm thử compiler không thay thế nghiệm thu sản phẩm sinh ra.
