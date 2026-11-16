#!/usr/bin/env python3
"""EBU R128 (-14 LUFS) Loudness Measurement, 2-Pass Normalization & Smart Ducking.

Adopted from xStudio / iContent Studio audio engineering practices for Stickman Video Director.

Features:
1. Measure Integrated Loudness (LUFS), Loudness Range (LRA), and True-Peak (dBFS)
   via FFmpeg's ITU-R BS.1770-4 / EBU R128 filter.
2. Two-pass Loudness Normalization targeting -14.0 LUFS and -1.5 dBFS True-Peak
   (the industry standard for YouTube, TikTok, Facebook Reels, and Spotify).
3. Smart Audio Ducking: Automatically compress/attenuate background music (BGM)
   by -14 dB whenever dialogue or voice-over is present using FFmpeg sidechaincompress.

Usage:
    # Measure audio loudness:
    python3 scripts/audio-master-lufs.py --measure video.mp4

    # Normalize audio/video to -14 LUFS:
    python3 scripts/audio-master-lufs.py --normalize input.wav --output normalized.wav

    # Smart ducking (Voice + BGM -> Master):
    python3 scripts/audio-master-lufs.py --duck --voice voice.wav --bgm bgm.mp3 \
        --output master.wav --duck-db -14.0 --normalize
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
TARGET_TRUE_PEAK = -1.5
TARGET_LRA = 11.0


def find_ffmpeg():
    ffmpeg = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg" or "/usr/local/bin/ffmpeg"
    if not Path(ffmpeg).exists():
        raise SystemExit("FFmpeg binary not found on system PATH")
    return str(ffmpeg)


def parse_ebur128_summary(stderr_text: str) -> dict:
    """Parse FFmpeg ebur128 output block into structured values."""
    # ebur128 outputs summary block at the end:
    #   Integrated loudness:
    #     I:         -23.4 LUFS
    #     Threshold: -33.8 LUFS
    #   Loudness range:
    #     LRA:         5.6 LU
    #   True peak:
    #     Peak:       -2.1 dBFS
    num = r"(-?[0-9.]+(?:[eE][-+]?[0-9]+)?|-?inf|nan)"

    summary_idx = stderr_text.rfind("Summary:")
    block = stderr_text[summary_idx:] if summary_idx != -1 else stderr_text

    m_i = re.search(rf"I:\s*{num}\s*LUFS", block)
    m_thresh = re.search(rf"Threshold:\s*{num}\s*LUFS", block)
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

    i_val = parse_float(m_i)
    thresh_val = parse_float(m_thresh)
    lra_val = parse_float(m_lra)
    tp_val = parse_float(m_tp)

    status = "needs_review"
    if i_val is not None and tp_val is not None:
        if -16.0 <= i_val <= -12.0 and tp_val <= -1.0:
            status = "pass"
        elif i_val < -16.0:
            status = "too_quiet"
        elif i_val > -12.0:
            status = "too_loud"
        elif tp_val > -1.0:
            status = "peak_exceeded"

    return {
        "integrated_lufs": i_val,
        "loudness_range_lra": lra_val,
        "true_peak_dbfs": tp_val,
        "threshold_lufs": thresh_val,
        "target_lufs": TARGET_LUFS,
        "target_true_peak": TARGET_TRUE_PEAK,
        "standard": "ITU-R BS.1770-4 / EBU R128",
        "status": status
    }


def measure_loudness(filepath: Path) -> dict:
    """Measure EBU R128 loudness metrics of an audio or video file."""
    ffmpeg = find_ffmpeg()
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-nostats",
        "-i", str(filepath),
        "-af", "ebur128=peak=true:framelog=quiet",
        "-f", "null",
        "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    metrics = parse_ebur128_summary(res.stderr)
    metrics["file"] = str(filepath.resolve())
    return metrics


def normalize_audio(
    input_path: Path,
    output_path: Path,
    target_lufs: float = TARGET_LUFS,
    true_peak: float = TARGET_TRUE_PEAK,
    lra: float = TARGET_LRA
) -> dict:
    """Perform 2-pass EBU R128 Loudness Normalization using FFmpeg loudnorm filter."""
    ffmpeg = find_ffmpeg()

    # Pass 1: Measure
    pass1_cmd = [
        ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-nostats",
        "-i", str(input_path),
        "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:print_format=json",
        "-f", "null",
        "-"
    ]
    p1 = subprocess.run(pass1_cmd, capture_output=True, text=True, errors="replace")
    
    # Extract JSON blob from pass 1 output
    json_match = re.search(r"\{[\s\S]*\}", p1.stderr)
    if not json_match:
        # Fallback to single-pass if JSON not parsed
        p2_filter = f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}"
    else:
        try:
            measured = json.loads(json_match.group(0))
            p2_filter = (
                f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:"
                f"measured_I={measured.get('input_i', -24)}:"
                f"measured_TP={measured.get('input_tp', -2)}:"
                f"measured_LRA={measured.get('input_lra', 7)}:"
                f"measured_thresh={measured.get('input_thresh', -34)}:"
                f"offset={measured.get('target_offset', 0)}:linear=true"
            )
        except Exception:
            p2_filter = f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_out = output_path.with_name(f"{output_path.stem}.norm_tmp{output_path.suffix}")

    is_video = input_path.suffix.lower() in [".mp4", ".mov", ".mkv", ".webm"]
    if is_video:
        pass2_cmd = [
            ffmpeg, "-y",
            "-i", str(input_path),
            "-af", p2_filter,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            str(temp_out)
        ]
    else:
        pass2_cmd = [
            ffmpeg, "-y",
            "-i", str(input_path),
            "-af", p2_filter,
            "-ar", "48000",
            str(temp_out)
        ]

    subprocess.run(pass2_cmd, capture_output=True, check=True)
    if temp_out.exists():
        os.replace(temp_out, output_path)

    # Verify final result
    return measure_loudness(output_path)


def smart_ducking(
    voice_path: Path,
    bgm_path: Path,
    output_path: Path,
    duck_db: float = -14.0,
    fade_ms: int = 250,
    normalize: bool = True
) -> dict:
    """Ducks background music whenever voice is active using FFmpeg sidechaincompress.
    
    Optionally normalizes the resulting master to target_lufs (-14.0 LUFS).
    """
    ffmpeg = find_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_mix = output_path.with_name(f"{output_path.stem}.duck_tmp.wav")

    # Ratio calculation: -14dB maps to ratio ~6.0
    ratio = max(2.0, min(12.0, abs(duck_db) / 2.3))

    filtergraph = (
        f"[0:a]asplit=2[v_orig][v_sc];"
        f"[1:a][v_sc]sidechaincompress=threshold=0.04:ratio={ratio:.1f}:"
        f"attack={fade_ms}:release={fade_ms * 2}[bgm_ducked];"
        f"[v_orig][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2,volume=1.0[aout]"
    )

    cmd = [
        ffmpeg, "-y",
        "-i", str(voice_path),
        "-i", str(bgm_path),
        "-filter_complex", filtergraph,
        "-map", "[aout]",
        "-c:a", "pcm_s16le",
        "-ar", "48000",
        str(temp_mix)
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        # Fallback to volume attenuation if sidechaincompress fails
        fallback_cmd = [
            ffmpeg, "-y",
            "-i", str(voice_path),
            "-i", str(bgm_path),
            "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.2[b];[v][b]amix=inputs=2:duration=first[aout]",
            "-map", "[aout]",
            "-ar", "48000",
            str(temp_mix)
        ]
        subprocess.run(fallback_cmd, check=True)

    if normalize:
        final_metrics = normalize_audio(temp_mix, output_path)
        if temp_mix.exists():
            temp_mix.unlink()
        return final_metrics
    else:
        os.replace(temp_mix, output_path)
        return measure_loudness(output_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--measure", help="Measure EBU R128 loudness metrics of a file")
    action_group.add_argument("--normalize", action="store_true", help="Normalize audio to -14 LUFS")
    action_group.add_argument("--duck", action="store_true", help="Perform smart ducking on Voice and BGM")

    parser.add_argument("--input", help="Input audio or video file for --normalize")
    parser.add_argument("--voice", help="Voice audio track for --duck")
    parser.add_argument("--bgm", help="Background music audio track for --duck")
    parser.add_argument("--output", help="Output file path for --normalize or --duck")
    parser.add_argument("--target-lufs", type=float, default=TARGET_LUFS,
                        help=f"Target Integrated Loudness (default: {TARGET_LUFS} LUFS)")
    parser.add_argument("--true-peak", type=float, default=TARGET_TRUE_PEAK,
                        help=f"Maximum True-Peak limit (default: {TARGET_TRUE_PEAK} dBFS)")
    parser.add_argument("--duck-db", type=float, default=-14.0,
                        help="Ducking attenuation in dB (default: -14.0 dB)")
    parser.add_argument("--fade-ms", type=int, default=250,
                        help="Attack and release fade duration in ms (default: 250ms)")
    parser.add_argument("--skip-normalize", action="store_true",
                        help="Skip loudness normalization after ducking")

    args = parser.parse_args()

    if args.measure:
        path = Path(args.measure).expanduser()
        if not path.is_file():
            parser.error(f"Input file not found: {path}")
        metrics = measure_loudness(path)
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
        return

    if args.normalize:
        if not args.input or not args.output:
            parser.error("--normalize requires both --input and --output")
        inp = Path(args.input).expanduser()
        out = Path(args.output).expanduser()
        if not inp.is_file():
            parser.error(f"Input file not found: {inp}")
        result = normalize_audio(inp, out, target_lufs=args.target_lufs, true_peak=args.true_peak)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.duck:
        if not args.voice or not args.bgm or not args.output:
            parser.error("--duck requires --voice, --bgm, and --output")
        v_p = Path(args.voice).expanduser()
        b_p = Path(args.bgm).expanduser()
        o_p = Path(args.output).expanduser()
        if not v_p.is_file():
            parser.error(f"Voice file not found: {v_p}")
        if not b_p.is_file():
            parser.error(f"BGM file not found: {b_p}")
        result = smart_ducking(
            v_p, b_p, o_p,
            duck_db=args.duck_db,
            fade_ms=args.fade_ms,
            normalize=not args.skip_normalize
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
