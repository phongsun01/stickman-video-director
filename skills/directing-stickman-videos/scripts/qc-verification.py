#!/usr/bin/env python3
"""Automated Post-Render Quality Control (QC) & Verification Engine.

Adopted from xStudio (iContent Studio v0.8.1) for Stickman Video Director.

Features:
1. Single-pass FFmpeg diagnostic decoding (scaled 320p for fast execution):
   - Black screen detection (`blackdetect`)
   - Video freeze detection (`freezedetect`)
   - Audio silence detection (`silencedetect`)
   - EBU R128 Integrated Loudness (LUFS) & True-Peak (dBFS) measurement
2. Caption & Character Collision Analysis:
   - Cross-references project.json shots and captions to detect if character
     models or presenter poses overlap with bottom caption safe zones.
3. Standardized scoring (0 - 100) with weighted penalties:
   - bad: -25 points
   - warn: -8 points
   - info: 0 points
   - qa_passed: true if score >= 80 and zero 'bad' findings.
4. Generates structured `verification.json`.

Usage:
    python3 scripts/qc-verification.py --video output/film.mp4
    python3 scripts/qc-verification.py --video output/film.mp4 --project project.json --output output/verification.json
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TARGET_LUFS = -14.0
BLACK_MIN_SEC = 0.4
FREEZE_MIN_SEC = 2.5
SILENCE_MIN_SEC = 1.5

PENALTY = {"bad": 25, "warn": 8, "info": 0, "ok": 0}


def find_ffmpeg():
    exe = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg" or "/usr/local/bin/ffmpeg"
    if not Path(exe).exists():
        raise SystemExit("FFmpeg binary not found on PATH")
    return str(exe)


def find_ffprobe():
    exe = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe" or "/usr/local/bin/ffprobe"
    if not Path(exe).exists():
        raise SystemExit("FFprobe binary not found on PATH")
    return str(exe)


def get_stream_info(filepath: Path) -> dict:
    ffprobe = find_ffprobe()
    cmd = [
        ffprobe, "-v", "error", "-print_format", "json",
        "-show_streams", "-show_format", str(filepath)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"FFprobe failed to inspect {filepath}: {res.stderr}")
    d = json.loads(res.stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    dur = float(d.get("format", {}).get("duration") or 0)
    return {
        "duration": round(dur, 2),
        "size_bytes": int(d.get("format", {}).get("size") or filepath.stat().st_size),
        "video": {
            "codec": v.get("codec_name"),
            "pix_fmt": v.get("pix_fmt"),
            "width": int(v.get("width") or 0),
            "height": int(v.get("height") or 0),
            "duration": round(float(v.get("duration") or dur), 2),
        } if v else None,
        "audio": {
            "codec": a.get("codec_name"),
            "channels": int(a.get("channels") or 0),
            "sample_rate": int(a.get("sample_rate") or 0),
            "duration": round(float(a.get("duration") or dur), 2),
        } if a else None,
    }


def parse_diagnostic_log(text: str, total_duration: float) -> dict:
    """Parses raw FFmpeg stderr output from blackdetect, freezedetect, silencedetect and ebur128."""
    num = r"(-?[0-9.]+(?:[eE][-+]?[0-9]+)?|-?inf|nan)"

    # 1. Black frames
    raw_black = [(float(a), float(b)) for a, b in re.findall(rf"black_start:{num} black_end:{num}", text)]

    # 2. Freeze frames
    raw_freeze = []
    for kind, val in re.findall(rf"(?:lavfi\.)?freezedetect\.freeze_(start|end):\s*{num}", text):
        if kind == "start":
            raw_freeze.append([float(val), None])
        elif raw_freeze and raw_freeze[-1][1] is None:
            raw_freeze[-1][1] = float(val)

    # 3. Silence periods
    raw_silence = []
    for kind, val in re.findall(rf"(?:lavfi\.)?silence_(start|end):\s*{num}", text):
        if kind == "start":
            raw_silence.append([max(0.0, float(val)), None])
        elif raw_silence and raw_silence[-1][1] is None:
            raw_silence[-1][1] = float(val)

    # Complete unclosed spans at EOF
    def finalize_spans(spans):
        out = []
        for a, b in spans:
            end_val = b if b is not None else total_duration
            if end_val > a:
                out.append({"start_s": round(a, 2), "end_s": round(end_val, 2), "duration_s": round(end_val - a, 2)})
        return out

    # 4. EBU R128 Loudness
    summary_idx = text.rfind("Summary:")
    block = text[summary_idx:] if summary_idx != -1 else text
    m_i = re.search(rf"I:\s*{num}\s*LUFS", block)
    m_lra = re.search(rf"LRA:\s*{num}\s*LU", block)
    m_tp = re.search(rf"Peak:\s*{num}\s*dBFS", block)

    def parse_float(m):
        if not m:
            return None
        val_s = m.group(1).lower()
        if "inf" in val_s or "nan" in val_s:
            return None
        try:
            return round(float(val_s), 2)
        except ValueError:
            return None

    return {
        "black_spans": finalize_spans(raw_black),
        "freeze_spans": finalize_spans(raw_freeze),
        "silence_spans": finalize_spans(raw_silence),
        "integrated_lufs": parse_float(m_i),
        "loudness_range_lra": parse_float(m_lra),
        "true_peak_dbfs": parse_float(m_tp),
    }


def run_ffmpeg_diagnostics(video_path: Path, total_duration: float) -> dict:
    ffmpeg = find_ffmpeg()
    # Fast 1-pass execution: scale to 320 width for rapid visual checks
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-nostats",
        "-loglevel", "info",
        "-i", str(video_path),
        "-vf", f"scale=320:-2,blackdetect=d={BLACK_MIN_SEC}:pix_th=0.10,freezedetect=n=-58dB:d={FREEZE_MIN_SEC}",
        "-af", f"silencedetect=n=-45dB:d={SILENCE_MIN_SEC},ebur128=peak=true:framelog=quiet",
        "-f", "null",
        "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    return parse_diagnostic_log(res.stderr, total_duration)


def check_caption_face_collision(project_data: dict) -> list[dict]:
    """Analyzes project shots, layers and captions to detect visual collisions with caption safe areas."""
    collisions = []
    if not project_data:
        return collisions

    height = project_data.get("height", 720)
    captions = project_data.get("captions", [])
    shots = project_data.get("shots", [])

    if not captions or not shots:
        return collisions

    # Safe bottom area where subtitles reside (typically bottom 20% of canvas)
    caption_zone_y = height * 0.80

    for shot_idx, shot in enumerate(shots):
        shot_start = shot.get("start", 0.0)
        shot_end = shot.get("end", 0.0)
        layers = shot.get("layers", [])

        # Check if any caption is active during this shot
        has_active_caption = any(
            not (c.get("end", 0) <= shot_start or c.get("start", 0) >= shot_end)
            for c in captions
        )
        if not has_active_caption:
            continue

        for layer in layers:
            l_type = layer.get("type", "")
            # Check visual character elements (pose, puppet, image, character)
            if l_type in ["pose", "puppet", "image", "character"]:
                ly = layer.get("y", 0)
                lh = layer.get("h", 0)
                # If layer extends into the bottom caption safe zone
                if (ly + lh * 0.85) > caption_zone_y:
                    collisions.append({
                        "shot": shot_idx + 1,
                        "time_s": shot_start,
                        "layer_id": layer.get("id", f"layer_{l_type}"),
                        "detail": f"Character element '{layer.get('id', l_type)}' overlaps bottom caption band (y={ly + lh:.0f} > {caption_zone_y:.0f})"
                    })
                    break

    return collisions


def evaluate_qc(stream: dict, diag: dict, project_data: dict = None) -> dict:
    """Evaluates metrics against broadcasting standards and computes final score."""
    findings = []
    total_dur = stream.get("duration", 0.0)

    # 1. Video & Audio presence
    if not stream.get("video"):
        findings.append({"id": "no_video", "level": "bad", "title": "Video stream missing", "detail": "Output has no decodable video stream"})
    elif stream["video"]["codec"] != "h264":
        findings.append({"id": "codec_warn", "level": "warn", "title": f"Video codec is {stream['video']['codec']}", "detail": "H.264 (yuv420p) is strongly recommended for social platforms"})

    if not stream.get("audio"):
        findings.append({"id": "no_audio", "level": "bad", "title": "Audio stream missing", "detail": "Output has no decodable audio stream"})

    # 2. Black screen spans
    black_spans = diag.get("black_spans", [])
    # Filter out normal brief head/tail fades (<= 0.8s)
    body_black = [s for s in black_spans if s["duration_s"] >= BLACK_MIN_SEC and not (s["start_s"] <= 0.5 and s["duration_s"] <= 0.8)]
    if body_black:
        longest = max(s["duration_s"] for s in body_black)
        lvl = "bad" if longest >= 2.0 else "warn"
        findings.append({
            "id": "black_screen",
            "level": lvl,
            "title": f"Black screen detected ({len(body_black)} segment(s), longest {longest}s)",
            "detail": "Unintended black frames disrupt video flow and engagement",
            "spans": body_black
        })

    # 3. Freeze frame spans
    freeze_spans = diag.get("freeze_spans", [])
    # Filter out normal brief opening/ending static holds (<= 1.0s)
    body_freeze = [s for s in freeze_spans if s["duration_s"] >= FREEZE_MIN_SEC and not (s["start_s"] <= 0.5 and s["duration_s"] <= 1.0)]
    if body_freeze:
        longest = max(s["duration_s"] for s in body_freeze)
        lvl = "bad" if longest >= 5.0 else ("warn" if longest >= 3.0 else "info")
        findings.append({
            "id": "freeze_frame",
            "level": lvl,
            "title": f"Video freeze detected ({len(body_freeze)} segment(s), longest {longest}s)",
            "detail": "Prolonged static images cause viewer drop-off in short-form content",
            "spans": body_freeze
        })

    # 4. Audio silence gaps
    silence_spans = diag.get("silence_spans", [])
    # Filter out brief pre-roll silence (<= 1.0s)
    body_silence = [s for s in silence_spans if s["duration_s"] >= SILENCE_MIN_SEC and not (s["start_s"] <= 0.5 and s["duration_s"] <= 1.0)]
    if body_silence:
        longest = max(s["duration_s"] for s in body_silence)
        lvl = "bad" if longest >= 4.0 else ("warn" if longest >= 2.0 else "info")
        findings.append({
            "id": "audio_silence",
            "level": lvl,
            "title": f"Audio silence gap ({len(body_silence)} segment(s), longest {longest}s)",
            "detail": "Auditory dead zones cause immediate scroll-away on TikTok/Shorts",
            "spans": body_silence
        })

    # 5. Loudness & True-Peak
    lufs = diag.get("integrated_lufs")
    tp = diag.get("true_peak_dbfs")
    if lufs is None:
        findings.append({"id": "loudness_null", "level": "warn", "title": "Could not measure LUFS loudness", "detail": "Audio track might be too short or corrupt"})
    else:
        diff = abs(lufs - TARGET_LUFS)
        if diff <= 2.0:
            pass  # Normal
        elif diff <= 4.0:
            findings.append({
                "id": "loudness_warn",
                "level": "warn",
                "title": f"Loudness is {lufs} LUFS (target: {TARGET_LUFS} LUFS)",
                "detail": f"Audio is slightly {'too loud' if lufs > TARGET_LUFS else 'too quiet'}; within 2 LUFS of -14 is optimal"
            })
        else:
            findings.append({
                "id": "loudness_bad",
                "level": "bad",
                "title": f"Loudness severely off ({lufs} LUFS)",
                "detail": "Platform loudness penalty will aggressively alter your video volume"
            })

    if tp is not None:
        if tp >= -0.1:
            findings.append({"id": "peak_clipped", "level": "bad", "title": f"Audio clipping detected (True-Peak: {tp} dBFS)", "detail": "Audio peaks above 0 dBFS cause digital distortion and raspiness"})
        elif tp > -1.0:
            findings.append({"id": "peak_warn", "level": "warn", "title": f"True-Peak near limit ({tp} dBFS)", "detail": "Recommended to keep true peak <= -1.5 dBFS to prevent lossy AAC codec distortion"})

    # 6. Caption-Face collisions
    collisions = check_caption_face_collision(project_data) if project_data else []
    if collisions:
        lvl = "warn" if len(collisions) >= 2 else "info"
        findings.append({
            "id": "caption_collision",
            "level": lvl,
            "title": f"Caption overlaps character elements in {len(collisions)} shot(s)",
            "detail": "Subtitles may obscure characters or actions in the bottom safe zone",
            "collisions": collisions
        })

    # Calculate overall Score (0 to 100)
    score = 100
    for f in findings:
        score -= PENALTY.get(f["level"], 0)
    score = max(0, score)

    has_bad = any(f["level"] == "bad" for f in findings)
    qa_passed = score >= 80 and not has_bad

    return {
        "qa_passed": qa_passed,
        "score": score,
        "standard": "EBU R128 / ITU-R BS.1770-4 / Mobile Safe Zones",
        "summary": {
            "findings_count": len(findings),
            "bad": sum(1 for f in findings if f["level"] == "bad"),
            "warn": sum(1 for f in findings if f["level"] == "warn"),
            "info": sum(1 for f in findings if f["level"] == "info"),
        },
        "findings": findings
    }


def perform_qc(video_path: Path, project_path: Path = None) -> dict:
    stream_info = get_stream_info(video_path)
    total_dur = stream_info.get("duration", 0.0)
    diag_metrics = run_ffmpeg_diagnostics(video_path, total_dur)

    project_data = None
    if project_path and project_path.is_file():
        try:
            with open(project_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)
        except Exception:
            pass

    evaluation = evaluate_qc(stream_info, diag_metrics, project_data)

    return {
        "file": str(video_path.resolve()),
        "duration_seconds": total_dur,
        "stream_info": stream_info,
        "audio_metrics": {
            "integrated_lufs": diag_metrics.get("integrated_lufs"),
            "loudness_range_lra": diag_metrics.get("loudness_range_lra"),
            "true_peak_dbfs": diag_metrics.get("true_peak_dbfs"),
            "target_lufs": TARGET_LUFS
        },
        "qc_evaluation": evaluation
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--video", required=True, help="Video file (MP4/WebM) to inspect")
    parser.add_argument("--project", help="Optional project.json to check caption collisions")
    parser.add_argument("--output", help="Optional output JSON path (defaults to verification.json next to video)")
    args = parser.parse_args()

    video_p = Path(args.video).expanduser().resolve()
    if not video_p.is_file():
        parser.error(f"Video file not found: {video_p}")

    project_p = Path(args.project).expanduser().resolve() if args.project else None
    out_p = Path(args.output).expanduser().resolve() if args.output else video_p.parent / "verification.json"

    report = perform_qc(video_p, project_p)

    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "verification_file": str(out_p),
        "qa_passed": report["qc_evaluation"]["qa_passed"],
        "score": report["qc_evaluation"]["score"],
        "findings": report["qc_evaluation"]["summary"],
        "lufs": report["audio_metrics"]["integrated_lufs"],
        "true_peak": report["audio_metrics"]["true_peak_dbfs"]
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
