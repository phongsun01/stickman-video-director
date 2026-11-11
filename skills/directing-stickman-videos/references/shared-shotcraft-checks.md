# Lớp kiểm tra chung mượn từ video-shotcraft — luật nhịp + thiết kế âm thanh, dùng cho mọi kiểu B1–B5

> **Vị trí:** lớp dùng chung, đặt cạnh `autopilot-production-qa.md` và
> `shared-shorts-kit-checks.md`. Nó KHÔNG sửa bất kỳ file của riêng kiểu
> nào (B1–B5 giữ nguyên contract visual, phụ đề, giọng, nhịp và SFX của
> mình) và KHÔNG thay thế `autopilot-production-qa.md` — đó vẫn là
> quality floor bắt buộc — cũng KHÔNG thay thế `autopilot-sound-system.md`
> hay `b4-audio-direction.md` (B4). File này chỉ thêm 2 thứ mượn từ
> video-shotcraft, ở tầng chung: (1) luật nhịp, (2) thiết kế âm thanh.
> Chế độ A (Director) không kế thừa lớp này.
>
> **Nguồn mượn:** video-shotcraft, `Vincentwei1021/video-shotcraft`
> (bản Pandu review là fork `xitrum14/video-shotcraft`), Apache-2.0,
> main, commit duy nhất `1266a3e`, review ngày 2026-11-06. Bản chép
> local tại `references/shotcraft/` trong skill này (xem
> `references/shotcraft/SOURCES.md`); clone gốc ở `/tmp/video-shotcraft/`
> (bản sao tạm, có thể mất khi VM reset — bản trong `references/shotcraft/`
> mới là bản lưu). Chỉ chép rules/văn bản, **không chép code Remotion/TS/JS**,
> không chép demo, texture hay audio của repo đó.
>
> **Nguyên tắc mượn:** mọi con số của video-shotcraft đều là "đo trên phim
> quảng cáo sản phẩm của họ, phải đo lại cho phim của mình", không phải
> chân lý. Chỗ nào xung đột với contract B đã có thì contract B thắng,
> và xung đột được ghi rõ ở §1.4 / §2.5, không áp mù.

## §1. Luật nhịp (mượn từ `aesthetic-rules.md` R1–R4, Q5, P4 + `sequences/promo-energy-arc.md`)

### §1.1 Các luật — áp cho mọi kiểu B

| Luật (shotcraft) | Nội dung | Ghi chú cho B1–B5 |
|---|---|---|
| R1 — Thông tin rơi xuống phải thở | Yếu tố mang thông tin (chữ lớn / số / toàn cảnh / wordmark) sau khi rơi vào vị trí phải đứng yên **≥1s** rồi mới cắt cảnh. Khoảng thở ưu tiên cho điểm cần nhớ (wordmark, reveal chính), không cho card nội dung thường. | B4: áp cho cú reveal cuối (màn hình đen, tiếng gõ cuối) và title mở đầu. Hold là **có chủ đích, ghi lý do**, không phải shot bị đứng hình. |
| R2 — Tốc độ đến từ gia tốc, không phải chạy nhanh đều | Chuyển động vào/ra phải phi tuyến (easing) + lệch pha không đều; chuyển động đều đọc như PPT rẻ tiền. Nhiều phần tử cùng vào thì **càng về sau càng nhanh** (gắn ẩn dụ vật lý nếu được, ví dụ phát bài), rồi **đứng yên 0,5s** mới cắt. | B4: tiếng kéo lê lần 2, bóng xuất hiện lại gần hơn — phải nhanh/dồn hơn lần 1, rồi dừng thở, không lặp y hệt lần 1 với cùng tốc độ. |
| R3 — Nhịp thà chậm chứ đừng nhanh | Mở đầu: cung hành động chính của chủ thể (tụ → tiến → lơ lửng → về vị trí) **≥3s**. Diễn tương tác (gõ, tìm, bấm) theo tốc độ người thật — khán giả phải theo kịp. Khi xếp timeline, **trừ trước ngân sách hold/rest** (R1 ≥30f, cuối cụm ≥15f) rồi mới xếp động tác, không xếp xong mới tìm chỗ thở. Lịch sử của họ: mọi feedback đều là "chậm lại", chưa từng có "chậm quá". | B4: cung hành động ≥3s áp cho reveal (bóng trên màn hình, bóng tiến lại gần). Không dùng zoom-only để kéo dài shot cho đủ giờ. |
| R4 — Chấn động toàn khung ≤3 lần/phim | Tác động lên toàn khung / tầng camera (scale cả khung, rung màn, flash, negative) tính là một "slam" lớn: **tối đa 3 lần/phim**, chỉ đặt ở hit mạnh nhất, hai lần cách nhau ≥16 nhịp (nếu có nhạc). Các nhịp còn lại chỉ động ở tầng phần tử. Kick/bump nào cũng đập toàn khung thì đọc thành "camera rung theo nhạc". | B4 **không có BGM** nên dịch ra: không flash/rung/scale toàn khung theo từng nhịp; một cú chấn toàn khung (nếu có, ví dụ màn hình tắt phụt) chỉ dùng ở payoff đã kiếm được, tối đa 3 lần/tập, và ghi rõ hit nào. |
| Q5 — Mở đầu chỉ một nhân vật chính | Mở đầu: một chủ thể, một cung hành động trọn vẹn (tụ → tiến → lơ lửng → về vị trí). Nhiều phần tử cùng múa không làm nên ấn tượng đầu. | B4 Tập 1/2/3 đều đã làm đúng kiểu này (một bóng / một thùng / một màn hình). Giữ. |
| P4 — Một thủ pháp chỉ làm nhân vật chính một lần/phim | Liệt kê chức năng/beat trước, mỗi beat map một shot; một thủ pháp (bay vào / xếp chồng / lật trang) chỉ làm chính **một lần/phim**; shot lặp thông tin thì cắt. | B4 (30 tập): áp **trong từng tập**, không áp xuyên tập — "bóng xuất hiện trên camera" là motif series, nhưng trong một tập không được dùng cùng một kiểu reveal hai lần với cùng một cách. Kiểm tra 4-gram của shorts-kit vẫn chạy riêng cho chống lặp lời. |

### §1.2 Khung năng lượng toàn phim (promo-energy-arc)

Sườn mặc định cho phim 30–60s, 4 đoạn: (1) mở đầu thương hiệu, năng lượng
thấp, wordmark hold ≥1s; (2) một nhân vật chính lập thân, năng lượng trung
bình, nhịp chậm nhất, cung hành động ≥3s; (3) leo chức năng/beat, năng lượng
trung-cao **xen kẽ** với chữ thở ở giữa (mỗi 1–2 beat chèn một chữ thở ~1,8s);
(4) kết thúc ở đỉnh cao nhất — mọi phần tử đã xuất hiện quay lại "chụp chung"
quanh wordmark, rồi hold ≥1s. Đây là sườn mặc định, không phải lệnh: lệch
có chủ đích thì ghi vào spec của tập đó.

Dịch sang B4 (tập 60s, thriller, không phải promo): (1) hook im lặng/thấp;
(2) một mối đe dọa / một vật chứng duy nhất; (3) leo căng thẳng xen kẽ khoảng
lặng (im lặng cũng là một nhịp thở, không phải lỗi); (4) đỉnh sợ rồi giữ bóng
tối. **Không copy tỉ lệ % của promo** (8–12% / 12–15% / 55–65% / 13–16% là
số đo trên phim mẫu của họ) — chỉ mượn thứ tự và nguyên tắc xen kẽ.

### §1.3 Mỗi kiểu chạm vào những luật nào

- **B1 Minimal Line Art:** R1/R3 là chính — chữ lớn cần thời gian đọc, cung
  hành động chậm; R2 áp cho cụm nét vẽ vào theo đợt.
- **B2 Colorful Hand-Drawn:** P4 là chính — nhiều nhân vật/đạo cụ dễ lặp thủ
  pháp; Q5 giữ mở đầu chỉ một nhân vật.
- **B3 Retro TV:** R4 là chính — hiệu ứng TV (nhiễu, flash) rất dễ lạm thành
  chấn toàn khung; đếm slam trước khi giao.
- **B4 Survival Thriller:** R1 (hold cuối), R2 (lần 2 dồn hơn lần 1), R3
  (reveal ≥3s), R4 (không chấn toàn khung theo nhịp), khung năng lượng §1.2
  dịch sang thriller. Xem §1.5 cho ví dụ Tập 3.
- **B5 Character Explainer:** P4 + Q5 — một nhân vật giải thích, một thủ pháp
  minh họa chỉ làm chính một lần; R1 cho định nghĩa/kết luận cần nhớ.

### §1.4 Xung đột đã biết — contract B thắng

- **B4 deliberate-hold vs quota 2,5s:** `autopilot-production-qa.md` đã có
  ngoại lệ deliberate-hold cho B4 (pose đẹp được phép đứng yên, không bắt
  cử động để đủ quota). R1/R3 **không mâu thuẫn** với ngoại lệ này: hold
  trong R1/R3 là hold **có ghi lý do kể chuyện** (reveal, đọc, thở), đúng
  bản chất của deliberate-hold. Hold không lý do, hold để lấp giờ, vẫn fail
  như cũ.
- **Giới hạn shot kể chuyện 3,0s của B4** (`b4-opening-direction.md`): vẫn
  giữ — đổi góc nhìn/trạng thái có ý nghĩa trước 3,0s. R3 (cung ≥3s) không
  có nghĩa là một shot được đứng yên 3s: cung hành động diễn ra **trong**
  3s đó (tụ → tiến → về vị trí), không phải freeze 3s.
- **B1–B3 quota 2,5s inactivity:** vẫn giữ nguyên; R1 hold ≥1s nằm trong
  quota này (hold 1s < 2,5s), không phải ngoại lệ mới.

### §1.5 Ví dụ áp cho B4 Tập 3 (phòng camera) — kiểm tra ở bản full, không sửa kịch bản đã duyệt

Kịch bản Tập 3 đã duyệt (261 từ, ~62s; preview ~20s đã xong 2026-11-11):
bóng cao đứng yên trên camera #7, biến mất, xuất hiện lại gần hơn trên
camera hành lang, rồi ở màn hình cuối ngoài cửa phòng camera nó với tay
tới ống kính, màn hình đen, một tiếng gõ nhẹ — "bạn có ở trong đó không."

- R3: mỗi lần xuất hiện của bóng là một cung ≥3s (đứng yên → nhận ra →
  biến mất), không cắt vụt 1s cho "nhanh".
- R2: lần xuất hiện thứ hai phải dồn/nhanh hơn lần đầu (gần hơn = nguy
  hiểm hơn), rồi đứng yên 0,5s trước khi cắt sang màn hình cuối.
- R1: màn hình đen cuối giữ ≥1s sau tiếng gõ — đó là điểm cần nhớ, không
  cắt ngay sang outro.
- R4: màn hình tắt phụt tính là một chấn toàn khung (nếu làm flash/scale);
  cả tập tối đa 3 lần kiểu này, và chỉ ở payoff.
- P4: trong tập này, kiểu reveal "bóng trên màn hình" chỉ làm chính một
  lần theo một cách — các lần sau phải đổi cách (biến mất / gần hơn / với
  tay tới ống kính), không lặp y hệt shot camera #7 ba lần.

## §2. Thiết kế âm thanh (mượn từ `sound-design.md` S1–S5 + `music-beat-sync.md` + `sfx-sourcing.md`)

### §2.1 Các luật — áp cho mọi kiểu B

| Luật (shotcraft) | Nội dung | Ghi chú cho B1–B5 |
|---|---|---|
| S1 — Chọn âm theo "loại phim", không theo "sự kiện" | Bảng từ SFX theo thể loại: whoosh (vận động máy), impact (rơi/đập), riser (dồn), sparkle (sáng), transition (chuyển cảnh). **Cấm âm sắc game** (pluck/bloop synth, nhảy cartoon, thang game-over) — cấm **âm sắc**, không cấm **động tác**: hình có cú click thật thì vẫn dùng tiếng click thật của vật đó. | B4: bảng từ của B4 là foley thật (gõ, kéo lê, máy phát rì rì, chốt cửa, tiếng bước) theo `autopilot-sound-system.md` + `b4-audio-direction.md`, KHÔNG phải bảng từ promo (tech-house + whoosh/impact liên tục). Không mang BGM tech-house của họ vào phim suspense im lặng. |
| S2 — SFX quản lý bằng bảng ghim frame | Một bảng trung tâm `{from, src, volume}[]`, mỗi dòng ghi chú động tác tương ứng; `from` suy ra từ `SHOTS` / beat, không ghi số frame tuyệt đối rải rác. Cùng loại cue lặp lại thì chống "máy bắn": **đổi 2 mẫu luân phiên + âm lượng giảm dần theo dãy + khoảng cách theo đường cong động tác mà ngắn lại**; dày quá không nghe rõ từng cái thì thu lại thành swoosh. | B4 Tập 2 đã làm đúng tinh thần này (tiếng kéo lê 2 lần, lần 2 gần/to hơn). Từ nay ghi thành bảng, không để trong đầu. |
| S3 — Âm thanh làm sau khi hình đã khóa | BGM/SFX xếp sau khi cấu trúc hình cơ bản đã khóa; **bất cứ lần nào đổi độ dài/thứ tự shot thì làm lại toàn bộ bảng SFX** — lệch âm-hình là mục kiểm tra bắt buộc trước giao. | Áp thẳng cho B4: Tập 3 bản full (~70s, xem §2.5) mà đổi shot thì bảng SFX của preview không được mang nguyên sang. |
| S4 — Foley thật ưu tiên hơn âm trang trí | Hình có động tác nào thì dùng tiếng thật của động tác đó (gõ bàn phím dùng tiếng phím, rơi từng món dùng từng tiếng pop); mẫu dài cắt đúng độ dài động tác (dùng `durationInFrames` cho mẫu >5s); mẫu nhẹ peak <-12dB thì đổi mẫu hoặc tiền xử lý trước, gain >1 chỉ khi đã kiểm trên bản render thật. | B4: "lời nói có tiếng kính vỡ" không thay được tiếng kính vỡ thật; tiếng kéo lê phải là tiếng kéo lê, không phải swoosh chung chung. |
| S5 — Bù hai độ trễ (đo, không đoán) | Công thức: `from = khung peak đích − trễ peak của file − trễ output`. (a) **Trễ output:** toàn bộ track audio của file xuất ra bị trễ cố định do chuỗi encode (AAC encoder priming, 48kHz điển hình 2048 samples ≈ **1,28 frame @30fps** trong pipeline Remotion 4.x + AAC 48kHz của họ — **KHÔNG copy hằng số này mù**; xem §2.4). (b) **Trễ peak của từng file:** peak năng lượng không nằm ở đầu file (mẫu dồn dần, hơi thở đầu), đo từng file (ví dụ của họ: brush-write 2f, paper-slide 10f, ink-char 24f). | Đây là luật mới nhất cho B4: tiếng gõ cuối Tập 3 phải rơi đúng khung tay chạm ống kính / màn hình đen, không được trễ 2–3 frame mà nghe như "đánh trượt". |

### §2.2 Chọn nguồn SFX (mượn từ `sfx-sourcing.md`)

- Ghi nhu cầu thành: shot/động tác, nguồn âm/vật liệu, độ dài đích, attack/tail,
  âm sắc, license yêu cầu. Tìm theo **nguồn âm** (ví dụ `dry paper slide`,
  `mechanical switch click`), không tìm từ chung chung (`click`, `impact`).
- Mặc định **CC0**; chấp nhận ghi công (attribution) thì mới dùng CC BY; loại BY-NC / Sampling+ /
  license không rõ. Tải về phải đọc lại trang chi tiết để chốt license thật,
  không lấy kết quả search làm bằng chứng license.
- Mỗi file tải về giữ **manifest**: nguồn URL, tác giả, license URL/phiên bản,
  đánh dấu preview hay file gốc, thời gian tải, SHA-256, phân tích thực đo
  (format, sample rate, độ dài, sample peak, RMS, peak 10ms) và `changes`
  nếu đã xử lý. Manifest này **ghi thêm vào** sound/rights manifest đã có
  trong `autopilot-sound-system.md` (ghi path/fingerprint/provenance/license),
  không thay thế nó. Không được ghi file preview MP3 thành "file gốc không nén".
- Không tải cả thư viện, chỉ lấy đúng cue cần; không dùng HTML trang lỗi giả
  làm audio; một lần chỉ một tiến trình `get` trên cùng một thư mục đích.
- Nguồn Freesound là nguồn **bổ sung**, không thay thế cửa rights gate đã có
  trong `autopilot-sound-system.md` (Pixabay/Uppbeat/Ghosthack vẫn giữ nguyên
  quy tắc kiểm tra từng asset của chúng).

### §2.3 Beat-sync — CHỈ khi đã chọn BGM

Chỉ áp dụng khi user đã chọn BGM **và** phim là phim có nhịp mạnh. B4 hiện
**không có BGM** — không được thêm BGM chỉ để áp mục này.

- **Nhạc trước, phân tích trước, storyboard sau:** đo lưới nhịp bằng
  least-squares fit trên chuỗi beat (không tin con số tempo của beat tracker
  — ví dụ của họ: báo 129,2 vs thật 131,97 BPM), residual ≤±15ms mới tin;
  kiểm tra nhầm 0,5x/1x/2x bằng độ phủ kick; track phức tạp thì tách drum
  stem trước (HPSS / Demucs).
- Timeline viết bằng **số nhịp** (`beatF(n)`), không viết số frame tuyệt đối;
  đổi nhạc thì chỉ đổi 2 hằng số (t0, T) là cả phim xếp lại. Cut/quan trọng
 ghim đúng nhịp; trọng âm lẻ thì ghim đúng transient thật, không nội suy lưới.
- **Kiểm tra sau render:** trích audio từ file MP4 đã xuất, đo lại lưới,
  đối chiếu từng cut — sai số **≤3 frame** mới đạt (ngưỡng cảm nhận), lý
  tưởng ≤1,5f. Sai hệ thống cùng chiều thì kiểm tra trễ output (§2.4), không sửa
  từng điểm.
- Đổi BGM thì làm lại phân tích; không xóa/sửa lời dẫn để vừa nhạc.

### §2.4 Đo trễ output cho pipeline của mình — không copy hằng số 1,28f

Hằng số 1,28f của video-shotcraft đo trên **pipeline của họ** (Remotion 4.x
+ AAC 48kHz mp4, 2026-08-23, 2 probe click/impact). Pipeline stickman dùng
ffmpeg encode khác, nên:

1. Render xong một bản, trích audio: `ffmpeg -i out/film.mp4 -vn -acodec pcm_s16le /tmp/render-audio.wav`.
2. Lấy 2–3 SFX sắc (ví dụ tiếng gõ) làm probe, cross-correlate file gốc với
   audio đã xuất; vị trí peak trừ đi frame thiết kế = trễ output. Chỉ tin
   khi các probe cho cùng một số (residual nhất quán).
3. Ghi lại kèm **4 yếu tố pipeline** (renderer/version + codec + sample
   rate + container) và ngày đo. Đổi bất cứ yếu tố nào thì đo lại.
4. Tách sổ sách: hằng số phân tích nhạc gốc (t0/BPM) không bao giờ trộn trễ
   output vào; trễ output là một hằng số riêng trong công thức `from`.
5. Trễ peak từng file đo bằng energy envelope, ghi vào manifest của file đó
   (§2.2), không dùng peak toàn file cho mọi cue.

### §2.5 Xung đột đã biết — contract B / B4 thắng

- **Loudness:** `autopilot-sound-system.md` đã chốt điểm làm việc cho web
  video **−16 đến −14 LUFS, trần −1 đến −2 dBTP** (không phải luật YouTube).
  `shared-shorts-kit-checks.md` §1.1 ghi −13 LUFS / trần −1 dBTP cho short
  kiến thức. B4 trầm lặng nên ngồi thấp hơn là **có chủ đích** — Tập 2 đo
  **−17,93 LUFS / true peak −0,26 dBTP** (vượt trần −1 dBTP 0,74 dB;
  Pandu đã chốt "Đăng như hiện tại" 2026-11-11). **Từ Tập 3: giữ true peak
  dưới −1 dBTP ngay lúc mix** (Tập 3 preview đo −22,06 LUFS / −3,41 dBTP,
  đạt trần nhờ narration đã hạ −3 dB — bản full phải dùng file narration
  đã hạ đó, `narration-att.wav`). Không "sửa" loudness B4 cho bằng −13 LUFS.
- **BGM:** S1 của shotcraft gắn với BGM tech-house mạnh; B4 không dùng BGM.
  Không áp S1 theo nghĩa "phải có nhạc nền mạnh".
- **Tập 3 dài ~70,2s:** vượt trần preview 65s của skill và gate approve/render
  >60s (bản preview-as-final của Tập 1/2 không dùng được cho Tập 3). Đây là
  vấn đề độ dài/timeline, **không phải** luật nhịp hay âm thanh — không dùng
  luật ở đây để cắt bớt 30 từ hay nâng trần thay cho quyết định của Pandu.
  **Đã chốt 2026-11-11 14:43:** Pandu chọn (a) giữ bản ~70s, nâng trần
  preview lên 71s (trần 65s→71s; gate approve/render >60s giữ nguyên, bản
  full vẫn giao dạng preview-render như Tập 1/2). Preview ~20s đã xong;
  bản full ~70s đang dựng ở chat Stickman.
- **Âm thanh mở đầu B4:** `b4-audio-direction.md` đã có first-frame audio
  gate + `b4-opening-audio-check.mjs` (onset 100ms, −36 dBFS mid-band).
  S5 bù trễ **cộng thêm** vào đó (tiếng đầu tiên cũng phải đúng frame),
  không thay thế ngưỡng onset của B4.

## §3. Per-style touchpoints (một dòng mỗi kiểu — chi tiết vẫn ở contract riêng)

- **B1:** R1 cho chữ đọc, S4 cho tiếng viết/vẽ tay (brush/paper) — đo trễ
  peak của tiếng bút (họ đo brush-write 2f).
- **B2:** P4 chống lặp thủ pháp màu, S1: âm sắc vui nhưng không dùng âm game.
- **B3:** R4 đếm slam (nhiễu/flash TV), Q11 chữ ≥56px phụ đề / ≥32px phụ
  (đo trên frame thật, xem `aesthetic-rules.md` Q11 trong `references/shotcraft/`).
- **B4:** xem §1.5 + §2.5.
- **B5:** P4 + R1 cho định nghĩa/kết luận; S2 bảng ghim frame cho từng cử chỉ
  minh họa của avatar.

## §4. Cái KHÔNG mượn

- Capture trang web thật bằng Puppeteer (không hợp stickman vẽ tay).
- Template Ink Press / Workbench / xuất JianYing của video-shotcraft (khung
  Remotion của họ; B đã có runtime riêng).
- Beat-sync bằng librosa làm bắt buộc (chỉ khi có BGM, §2.3).
- BGM tech-house / bảng từ promo làm mặc định cho mọi kiểu.
- Chuyển hẳn pipeline sang Remotion của họ — chỉ mượn luật, không mượn khung.

## §5. Kiểm chứng (deferred — như shorts-kit)

Chưa kiểm chứng trên phim thật. Lần chạy checklist đầu tiên là **bản full
Tập 3 B4** (không phải preview ~20s đã xong): chạy §1 (R1/R2/R3/R4/P4) và
§2 (bảng SFX, S5 đo trễ output + trễ peak tiếng gõ cuối, true peak <−1 dBTP
trong lúc mix) trên bản full, ghi kết quả frame-số vào project. Nếu luật nào
sai trên phim thật (ví dụ trễ output đo được khác xa 1,28f, hay R2 làm hỏng
nhịp suspense), sửa file này và ghi rõ, không áp mù sang Tập 4.
