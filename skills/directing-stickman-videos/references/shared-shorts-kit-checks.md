# Lớp kiểm tra chung mượn từ shorts-kit — dùng cho mọi kiểu B1–B5

> **Vị trí:** lớp dùng chung, đặt cạnh `autopilot-production-qa.md`. Nó KHÔNG sửa
> bất kỳ file của riêng kiểu nào (B1–B5 giữ nguyên contract visual, phụ đề, giọng,
> nhịp và SFX của mình) và KHÔNG thay thế `autopilot-production-qa.md` — đó vẫn là
> quality floor bắt buộc. File này chỉ thêm 3 thứ mượn từ shorts-kit, ở tầng chung.
> Chế độ A (Director) không kế thừa lớp này; chỉ phần ngưỡng phụ đề/âm thanh (§1.3)
> mới dùng ké được cho A, và phải ghi riêng, không gộp chung.
>
> **Nguồn mượn:** shorts-kit `howznguyen/shorts-kit`, MIT, v2.0.0, HEAD `828e120`.
> Bản chép local tại `references/shorts-kit/` trong skill này (xem
> `references/shorts-kit/SOURCES.md`); bản trial gốc ở `workspace/shorts-kit-trial/`:
> `shorts-kit/thresholds.json` (ngưỡng + luật lint), `shorts-kit/facts/` (schema fact
> ledger), `shorts-kit/shots/` (~170 shot card, trong đó `shorts-kit/shots/transition/`
> 15 thẻ). Verdict cũ vẫn giữ: KHÔNG chuyển pipeline B4 sang shorts-kit —
> chỉ mượn 3 thứ dưới đây. Mọi con số trong thresholds.json đều là "đo trên một kênh,
> phải đo lại cho kênh của mình", không phải chân lý — file đó tự ghi như vậy.

## §1. Luật lint + ngưỡng (thresholds.json)

### §1.1 Áp dụng được ngay, giống nhau cho cả 5 kiểu

| Luật (kit) | Ngưỡng | Ghi chú cho B1–B5 |
|---|---|---|
| Độ dài video | tối đa cứng 180s; mục tiêu mềm 60–90s | B4 mỗi tập 60–63s là vừa khít. Video dưới 60s thì dưới mục tiêu mềm — chỉ là cảnh báo mềm, không phải lỗi. |
| Câu dài nhất | tối đa 25 từ/câu | Đo được thì cắt câu bằng dấu chấm. Dấu phẩy / gạch ngang gần như không tạo khoảng lặng cho TTS VieNeu — chỉ dấu chấm mới tạo pause. |
| Mật độ beat | ~1 ý mới / 2,5s | Với B4, "ý" là beat truyện chứ không phải fact. Một cảnh 20s không có gì mới thì nên cắt. |
| Chữ trên khung hình | tối đa 50% số cảnh có chữ; kicker ≤25 ký tự; headline ≤6 từ | Dùng ngay cho cả 5 kiểu. |
| Âm thanh | -13 LUFS, true peak tối đa -1 dB (encode xong AAC vọt thêm 0,2–0,6 dB, nên normalize với trần -1,5 dB) | Đã sống qua ở trial cầu vồng: normalize đo -0,9 dB tưởng đạt, encode đo lại -0,7 dB. Xem §4: Tập 2 B4 đo -17,9 LUFS / -0,26 dBTP — B4 trầm lặng nên ngồi thấp hơn mục tiêu này là có chủ đích, không tự "sửa" cho bằng -13. |
| SFX | tối đa 5 hiệu ứng/video, mỗi cái gắn vào đúng từ xứng đáng | B4 đã làm đúng luật này (tiếng kéo lê, tiếng gõ). |
| Chống khuôn mẫu | cụm 4 từ lặp lại trong 3+ video = mould đang hình thành | Với B4 (30 tập) đây là luật đáng giá nhất: bắt câu cửa miệng lặp qua các tập trước khi khán giả chán. Chạy kiểm tra 4-gram mỗi tập mới so với các tập trước. |
| Kết thúc | outro hold 3–4s im lặng sau chữ cuối; không kết bằng lời kêu gọi đăng ký — kết bằng cú twist rồi một câu share | B4 kết bằng bóng tối (Tập 2: câu cuối hết ở 59,5s, video 60s) — khác luật này về hình thức nhưng cùng mục đích: để lại một nhịp. Ghi nhận khác biệt, không áp mù. |

### §1.2 Phải đo lại cho tiếng Việt — KHÔNG áp mù số tiếng Anh

| Luật (kit, đo trên tiếng Anh) | Ngưỡng gốc | Đo thật trên B4 (2026-11-11) | Kết luận |
|---|---|---|---|
| Trung vị từ/câu | 16 từ (trung vị 1.266 câu, 6 kênh tiếng Anh) | Tập 1: 7 từ (31 câu, 262 từ) · Tập 2: 11 từ (21 câu, 258 từ) | Tiếng Việt câu ngắn là tự nhiên. **Không dùng 16 làm chuẩn fail.** Baseline tạm cho B4 tiếng Việt: trung vị 7–11. Đo lại sau Tập 3–4. |
| Câu ngắn ≤7 từ | tối đa 13% | Tập 1: 51,6% · Tập 2: 38,1% | Vượt xa ngưỡng Anh — nhưng đó chính là phong cách B4 (câu ngắn, dồn dập). Không fail. |
| Câu rất ngắn ≤4 từ | tối đa 4% | Tập 1: 32,3% · Tập 2: 14,3% | Như trên. |
| Câu dài nhất | tối đa 25 từ | Tập 2 có 1 câu 27 từ ("Một tiếng kéo lê, chậm rãi, từ phía cửa cuốn cuối kho — hay vọng xuống từ ống thông khí trên trần, bạn không phân biệt nổi.") | Câu này chứa dấu gạch ngang (bannedMark của kit) — với B4 đó là nhịp kịch tính có chủ đích. Ghi nhận, không bắt sửa; chỉ cắt nếu nghe đọc bị đuối hơi. |

### §1.3 Mỗi kiểu chạm vào những ngưỡng khác nhau

- **B1 Minimal Line Art:** chữ cảnh lớn làm điểm nhấn → headline ≤6 từ, kicker ≤25 ký tự; giữ hình 5s để đọc (readingHoldSeconds).
- **B2 Colorful Hand-Drawn:** phụ đề cụm ngắn theo nghĩa + cấm câu mở đầu bằng đại từ ("nó", "cái này") ở đầu cảnh; luật cấm gán nhãn tâm lý / claim y tế không có nguồn — B2 cần nhất vì chủ đề hay đụng tâm lý.
- **B3 Retro TV:** vùng an toàn (trên 212px, dưới 1726px, cột nút phải từ x=927) + kiểm tra độ đọc trên frame đã encode — artwork xếp lớp + lớp TV phủ lên làm chữ dễ chìm.
- **B4 Survival Thriller:** chống lặp cụm từ qua 30 tập + mật độ beat 2,5s. Lưu ý: luật "hình chính không đứng yên quá 2,5s" đã có ngoại lệ deliberate-hold riêng cho B4 — thresholds không được áp mù vào B4.
- **B5 Character Explainer:** kiểu duy nhất được phụ đề 3 dòng (B1–B4 chỉ 1 dòng) — ngưỡng "phụ đề ngôn ngữ thứ hai tối đa 2 dòng" không áp nguyên cho B5, phải ghi ngoại lệ riêng. Luật chống khuôn mẫu bắt đúng chỗ ngứa của B5: câu cửa miệng của người dẫn lặp qua nhiều video thành mould rất nhanh.
- **Xung đột đã biết — phụ đề 2–4 từ/cụm:** thresholds.json quy định caption 2–4 từ/cụm, nhưng B4 (và mọi kiểu B) dùng **phụ đề ngữ nghĩa** theo `autopilot-production-qa.md` — giữ nguyên cụm nghĩa, không cắt máy. Đo thật Tập 2: 44 cue, 3–9 từ/cue, 36/44 cue trên 4 từ. Đây là **xung đột có chủ đích**: giữ luật ngữ nghĩa của skill, bỏ ngưỡng 2–4 từ của kit; kiểm tra bằng độ đọc trên frame thật thay vì đếm từ.

## §2. Sổ fact / continuity ledger (mượn schema facts.json)

### §2.1 Schema — giữ nguyên từ shorts-kit, đổi nội dung theo kiểu

Một record: `id` (không đổi sau khi kịch bản đã trích dẫn), `claim` (một câu tự đứng
được), `value` (con số kèm đơn vị, nếu có), `status` (`verified` / `contested` /
`unverified`), `sources` (chỉ id nguồn, không nhét URL vào câu), `caveat` (bắt buộc
nếu `contested`), `checkedAt` (ngày mở nguồn đọc lần cuối), `usedIn` (video + scene
nào dùng). Hai quy tắc hay nhất của sổ này:

1. Khẳng định sai mà nhiều người tin thì **giữ lại, không xóa** — ghi thành fact
   `myth: true` kèm lời sửa đúng thành một fact `verified` riêng (bản thân "cái sai
   phổ biến" đã là một video). Với B4: ý tưởng đã loại ghi dạng `cutReason`
   (ví dụ "đi tìm nước" — myth, vì siêu thị đầy nước đóng chai).
2. Mỗi dòng lời dẫn phải trích đúng id fact — không có chuyện "nhớ mang máng rồi nói".
   Fact `unverified` thì lint báo lỗi, không được nói ra.

Sổ fact của kit là **nửa bằng chứng**; shot ledger của Autopilot
(`autopilot-production-qa.md`: câu nói, thời gian từng từ, ý cần truyền, chủ thể,
chữ cảnh, sự kiện, nguồn/bằng chứng, phụ đề, SFX, nối sang shot sau) là **nửa sản
xuất**. Hai cái ghép lại mới đủ — fact ledger không thay thế shot ledger.

### §2.2 Mỗi kiểu giữ một loại fact khác nhau

- **B1:** các khẳng định đang giải thích (mô hình tư duy, logic) — hợp với ledger nhất, gần như y hệt video cầu vồng.
- **B2:** claim tâm lý/thói quen — cần trường `evidence` nhất: claim chỉ dựa trên một nghiên cứu đơn lẻ thì không được nói "ai cũng vậy", "con người vốn thế".
- **B3:** claim về hành vi (ví dụ chó làm thế này vì sao) — ledger ngăn bịa lý do hành vi không có nguồn.
- **B4:** luật liên tục của series — xem §2.3 (bible v2.3 viết lại thành record).
- **B5:** claim trong chủ đề người dẫn đang giải thích, cộng hồ sơ duyệt avatar (đầu nào đã duyệt, giọng nào đã duyệt).

### §2.3 Hạt giống: sổ liên tục B4 từ bible v2.3 (đã verified, dùng cho mọi tập sau)

Nguồn: `workspace/your_files/sieu-thi-khong-gian-tham-chieu.md` v2.3 (2026-11-11).
Trạng thái mặc định `verified`; khi Pandu đổi luật thì sửa bản này trước, rồi mới
viết kịch bản (quy tắc vàng của bible).

| id | claim | usedIn |
|---|---|---|
| `b4-c01` | Máy phát dự phòng ở sân bốc hàng chỉ chạy tủ lạnh/tủ đông (+ kho lạnh) + camera an ninh; đèn trần tắt. | Tập 1, Tập 2 |
| `b4-c02` | "Không còn đường ra" nghĩa là không có lối thoát AN TOÀN: cửa kính và cửa cuốn đều mở được về mặt vật lý, nhưng ra ngoài là chết. | Tập 1, Tập 2 |
| `b4-c03` | Mối đe dọa đã ở trong siêu thị từ trước khi cửa bị khóa ("bạn khóa mình ở trong, cùng với nó"). | Tập 1, Tập 2 |
| `b4-c04` | Sân bốc hàng có rào sắt bao quanh, cổng sắt (cổng xe tải) khóa xích; mở cửa cuốn ra cũng chỉ tới sân có rào. | Tập 2 |
| `b4-c05` | Cửa cuốn có khe hở dưới chân — điểm yếu thứ hai; thứ bên ngoài có thể luồn qua hoặc đẩy cửa lõm vào. | Tập 2 |
| `b4-c06` | Ống thông khí trên trần 40×40cm, đã tắt từ khi mất điện, tối và lặng, thành đường truyền âm; người không chui lọt. | Tập 2 |
| `b4-c07` | Không có sương mù; không có hầm / bãi xe tầng hầm (1 tầng, bãi xe ngoài trời). | Tập 1, Tập 2 |
| `b4-c08` | Nước uống dồi dào (Lối 2 đầy nước đóng chai) — không bao giờ có tình tiết "đi tìm nước". | — (myth, `cutReason`: siêu thị đầy nước đóng chai) |
| `b4-c09` | Camera có chế độ hồng ngoại ban đêm; camera #14 (góc thấp cửa cuốn) là camera chết / nhiễu. | Tập 1, Tập 2 |
| `b4-c10` | Mối đe dọa chỉ là bóng/silhouette + tiếng động, không bao giờ lộ mặt rõ. | Tập 1, Tập 2 |
| `b4-c11` | Đồ ăn đủ ~3 tuần nếu ăn dè. | Tập 1 |
| `b4-c12` | Thời lượng dầu máy phát chưa chốt (mục 9 bible). | — (`unverified`, không được đưa vào lời dẫn cho tới khi chốt) |

## §3. Shot card — từ điển transition dùng chung

Nguồn: `shorts-kit/shots/transition/` (15 thẻ) + `shorts-kit/shots/sizes.md`. Mỗi thẻ có: tên,
tóm tắt, dùng ở đâu, dài bao nhiêu frame, Intent, Style choice, Parameters (kèm cảm
giác chỉnh), Known traps, Reference implementation trong `src/demo/` (tham khảo,
không build). **Cảnh báo chung của chính các thẻ:** mọi thông số đều chỉnh trên tư
liệu dựng tay/placeholder — lần dùng thật đầu tiên phải kiểm lại; khi thông số
trong thẻ xung đột với kinh nghiệm thực tế thì kinh nghiệm thực tế thắng.

### §3.1 Kỷ luật chung (áp cho mọi kiểu)

- **Một mối nối = một kiểu transition, không chồng hai hiệu ứng lên nhau.**
- **Chọn kiểu ngay từ lúc lập storyboard**, không phải lúc dựng — thêm transition sau sẽ xô lệch frame cả dây chuyền. Ghi transition vào storyboard: mỗi mối nối ghi một kiểu.
- Với B4: transition lấy frame từ ngân sách của chính hai shot kề nó, không được cộng thêm (mỗi shot truyện ≤3s).

### §3.2 Kiểu nào hợp kiểu nào

| Kiểu B | Transition hợp | Không dùng / cẩn thận |
|---|---|---|
| **B1** | flash-cut, hidden-cut (kín đáo, đúng giấy trắng yên tĩnh) | Whip-pan lia nhanh đánh nhau với thẩm mỹ B1. |
| **B2** | portal-wipe kiểu C (chui qua một vật để vào thế giới chi tiết), letterform-travel làm tiêu đề chương (chữ "PHẦN 5" khổng lồ, camera chui qua nét chữ) | — |
| **B3** | blinds-slice (12 lá chớp 3D lật như chuyển kênh TV — đúng ngữ nghĩa truyền hình) | Không chồng hiệu ứng TV lên trên transition. |
| **B4** | hidden-cut (che điểm cắt), whip-pan cho đoạn dồn dập (tiếng kéo lê → thùng bị xê dịch), crash-zoom-punch cho cú giật mình, tension-camera | Page-turn không hợp B4 (trong siêu thị không có trang sách). |
| **B5** | crash-zoom-punch và portal-wipe cho hài vật lý ở sân khấu bên trái | Chỉ được đụng vào sân khấu bên trái — người dẫn góc phải đứng yên. Whip-pan toàn khung hình làm rung cả người dẫn, không dùng. |

### §3.3 Các họ transition chính (tóm tắt từ thẻ gốc)

- **Handover — `shot-transitions.md`:** A push-in + chớp trắng che điểm cắt; B whip-pan phanh gấp (lia nhanh, đổi cảnh trên frame mờ — đỉnh tốc độ ≥300px/frame thì mờ mới đủ che, đuôi dài 48 frame để mắt kịp bắt cảnh mới); C mask-wipe qua cửa sổ (một element thật phóng to thành cửa sổ toàn màn hình). Chọn: cùng năng lượng → flash-cut; vào cảnh "cần đọc kĩ" → whip-pan; từ tổng quan vào chi tiết → kiểu cửa sổ.
- **Travel — `transition-travel.md`:** chữ tiêu đề chương khổng lồ làm cửa sổ, camera chui qua nét chữ để đổi cảnh. Chỉ dùng khi hậu cảnh "nằm sẵn" trong tiền cảnh (nhìn thấy qua lỗ chữ); hai cảnh chỉ nối tiếp nhau thì dùng handover.
- **Volume / page-turn — `page-turn-transitions.md`:** barn-door-split — trang cũ tách đôi như hai cánh cửa trượt ra hai bên, trang mới hiện từ dưới. Một kiểu duy nhất, ~150 frame (~5s), **chỉ dùng cho chuyển chương lớn, tối đa 2 lần/phim**. Thông số mẫu: hairline sáng ở đường giữa 20–30 frame trước khi tách; hai cánh trượt ∓1000px trong 24 frame; trang mới scale 1,08→1; mép cắt sáng 10px; sau khi ổn định giữ ≥30 frame rồi mới đẩy máy chậm 1,5–2%. Thẻ tự ghi rõ: **đây không phải cuộn giấy 3D thật** — cùng họ với demo page-turn rẻ 2,6s đã có, không hơn về độ thật, nhưng hơn ở bảng thông số và luật dùng/không dùng.
- **Geometric wipe — `wipe-transitions.md`:** blinds-slice — 12 lá chớp 3D lật theo sóng. Tối đa 2 lần/phim, không dùng hai lần liên tiếp; ranh giới wipe bắt buộc có đường sáng — wipe không đường sáng đọc như hiệu ứng PowerPoint.
- **Khác, đáng mượn thêm:** `sizes.md` (WS/MS/CU/ECU, góc eye/high/low/top/tilt — sửa bệnh "cả video một cỡ cảnh"); nhóm sfx (tối đa 5 hiệu ứng/video).

## §4. Chạy thử lần đầu — checklist này lên B4 Tập 2 (đã dựng xong 2026-11-11)

Chạy ngày 2026-11-11 trên: kịch bản v2 đã duyệt (`workspace/stickman-b4-sieu-thi-ngay2/script-draft-v2.md`,
258 từ), file full `workspace/your_files/sieu-thi-ngay-2-60s.mp4` (60,000s, 35 shot, 44 cue)
+ `.srt`, và kịch bản Tập 1 đã duyệt (`workspace/stickman-b4-sieu-thi/script-approved-60s.md`, 262 từ).

| Kiểm tra | Kết quả đo thật | Kết luận |
|---|---|---|
| Độ dài | 60,0s — trong mục tiêu mềm 60–90s | PASS |
| Câu dài nhất | 27 từ (1 câu, xem §1.2) — trên ngưỡng 25 | Ghi nhận, không sửa (nhịp kịch tính có chủ đích) |
| Trung vị câu | 11 từ (Tập 1: 7) — dưới 16 của kit | Không fail — baseline tiếng Việt, xem §1.2 |
| Câu ngắn ≤7 từ / ≤4 từ | 38,1% / 14,3% (Tập 1: 51,6% / 32,3%) | Không fail — phong cách B4, xem §1.2 |
| Cụm 4 từ lặp vs Tập 1 | 0 cụm chung | PASS — chưa có mould (luật chỉ báo khi lặp ở 3+ video; mới có 2 tập) |
| Phụ đề | 44 cue, 3–9 từ/cue; 36/44 cue trên 4 từ | Xung đột có chủ đích với ngưỡng 2–4 từ của kit — giữ phụ đề ngữ nghĩa của skill (§1.3) |
| SFX | 3 file SFX (hum máy phát + 2 tiếng kéo lê), dưới tối đa 5 | PASS |
| Âm thanh (ffmpeg loudnorm trên file đã giao) | -17,93 LUFS integrated, true peak -0,26 dBTP | Khác mục tiêu kit (-13 LUFS / -1 dBTP): B4 trầm lặng nên ngồi thấp hơn là có chủ đích; true peak trên -1 dBTP thì nên xem lại ở tập sau trước khi đăng — không tự normalize lại file đã duyệt khi chưa hỏi Pandu |
| Outro hold | câu cuối hết 59,5s, video 60,0s → hold 0,5s (kit muốn 3–4s) | Khác biệt có chủ đích (kết bằng bóng tối) — ghi nhận |
| Liên tục vs bible v2.3 | khớp: máy phát ở sân bốc hàng, ống xả qua tường, khe hở cửa cuốn, ống gió trần, không sương mù, không tìm nước, không tiếng gõ | PASS — đây chính là loại lỗi ledger sinh ra để bắt (hai plot hole Tập 1 đã tự bắt được: tìm nước, CCTV sáng đèn lúc mất điện) |
| Transition | hidden-cut + whip-pan nhẹ (theo kỷ luật §3.1) | PASS theo storyboard Tập 2 |

**Việc còn lại sau lần chạy thử này:** đo lại baseline tiếng Việt (trung vị câu, tỉ lệ câu ngắn)
sau Tập 3–4 rồi mới chốt số riêng cho B4; xem lại true peak trước khi đăng Tập 2 (đo -0,26 dBTP,
trên trần -1 dBTP của kit); khi viết Tập 3, chạy kiểm tra 4-gram so với Tập 1+2 trước khi duyệt
kịch bản — tới tập 3 là lúc luật mould bắt đầu có răng.

## §5. Cách chạy checklist cho tập/video mới

1. Lấy kịch bản đã duyệt + file `.srt` + file mp4 đã render.
2. Đếm: số câu, từ/câu (trung vị, dài nhất), tỉ lệ câu ≤7 từ / ≤4 từ — so với
   **baseline tiếng Việt §1.2**, không so với số tiếng Anh của kit.
3. Chạy 4-gram so với mọi tập/video trước cùng series — báo khi một cụm xuất hiện
   ở video thứ 3 trở đi.
4. Đếm SFX trong mix; đo loudness/true peak bằng `ffmpeg -af loudnorm` trên file đã giao.
5. Đối chiếu từng beat với sổ liên tục §2 (B4) hoặc fact ledger của kiểu đó; beat nào
   không có record `verified` thì đánh dấu, không tự bịa.
6. Ghi transition của từng mối nối vào storyboard trước khi dựng (§3.1).
