# Nguồn mượn từ shorts-kit — provenance

- Nguồn: `howznguyen/shorts-kit`, MIT, v2.0.0, HEAD `828e120`
  (bản trial đã clone tại `workspace/shorts-kit-trial/`, ngày 2026-11-11).
- Chỉ chép **luật và số, không chép code**: `thresholds.json` (ngưỡng + luật lint),
  `facts/` (schema sổ fact — README gốc + 2 file template rỗng, KHÔNG chép
  `facts.json`/`sources.json` của trial vì trong đó đã có fact cầu vồng f-0005–f-0010),
  `shots/` (toàn bộ thẻ shot dạng .md, trong đó `shots/transition/` 15 thẻ).
- Không chép: mọi code Remotion/TS/JS, `src/demo/`, `scripts/lint.ts`, `docs/soul/`
  (trừ thresholds.json). Các thẻ shot có nhắc tới file demo trong `src/demo/` —
  đó là code tham khảo của kit gốc, không có trong bản chép này; đọc thẻ là đủ
  để dùng, cần code mẫu thì mở ở bản trial.
- Mọi con số trong `thresholds.json` đều là "đo trên một kênh, phải đo lại cho
  kênh của mình" — xem `../shared-shorts-kit-checks.md` §1.2 (đo lại cho tiếng Việt).
- Verdict giữ nguyên: KHÔNG chuyển pipeline B4 / whiteboard sang shorts-kit —
  chỉ mượn 3 thứ này.
