#!/usr/bin/env python3
"""VieNeu local TTS adapter for Autopilot (no Gemini, no cloud).

PATCH (fork 2026-11-09): the Autopilot renderer only needs a local
`narration.wav`; the bundled Gemini speech adapter is one way to make it,
not a requirement. This script makes that file with VieNeu-TTS v3 Turbo
running locally (CPU/ONNX, Apache-2.0), e.g. Vietnamese narration with the
"Hải Đăng" voice. Verified 2026-11-09 on a CPU-only VM (vieneu 3.8.3,
onnxruntime 1.31.1): init ~13s + ~11s inference for 5.7s of audio.

UPDATED (2026-11-16):
- Voice Cloning: Support `--ref-audio <PATH>` (3-8s audio sample).
- Auto-fit atempo timing: Support `--target-duration <SECONDS>`, automatically
  speeding up or slowing down audio via pitch-preserving FFmpeg atempo (0.7x - 1.6x)
  to precisely fit scene timeline slots without pitch distortion.
- Manual atempo: Support `--atempo <RATIO>` and `--trim-silence`.
- Built-in Voice Catalog with detailed metadata (gender, region, style, stickman roles).

Usage (run with the VieNeu venv python, or let the script re-exec into it):
    python3 scripts/vieneu-local.py --text "Xin chào." --output narration.wav
    python3 scripts/vieneu-local.py --text-file script.txt --output narration.wav \\
        --voice "Hải Đăng"
    python3 scripts/vieneu-local.py --text-file script.txt --output narration.wav \\
        --target-duration 4.5
    python3 scripts/vieneu-local.py --text "Clone test" --output narration.wav \\
        --ref-audio samples/my-voice.wav
    python3 scripts/vieneu-local.py --list-voices

Configuration (environment, all optional):
    VIENEU_VENV        Python venv with vieneu installed (default ~/workspace/vieneu-venv)
    VIENEU_MODELS_DIR  Materialized model directory (default ~/workspace/vieneu-models)
    VIENEU_VOICE       Default voice (default "Hải Đăng")
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_VOICE = "Hải Đăng"
_CODEC_REPO = "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX"

# Built-in Catalog for VieNeu Vietnamese Voices
PRESET_VOICE_CATALOG = [
    {
        "id": "Thiện Minh",
        "gender": "male",
        "region": "Bắc",
        "style": "Trầm ấm, truyền cảm, phong thái thuyết minh",
        "stickman_roles": ["Người dẫn chuyện (Narrator)", "Nhân vật nghiêm túc", "Thầy giáo", "Chuyên gia"]
    },
    {
        "id": "Trúc Ly",
        "gender": "female",
        "region": "Bắc",
        "style": "Tự nhiên, trong trẻo, phong cách hiện đại",
        "stickman_roles": ["Nữ chính", "Người dẫn dắt hiện đại", "Bạn đồng hành thông minh"]
    },
    {
        "id": "Hải Đăng",
        "gender": "male",
        "region": "Bắc",
        "style": "Sôi nổi, dứt khoát, trẻ trung, tự tin",
        "stickman_roles": ["Nhân vật chính Stickman", "Đối đáp nhanh", "Bình luận vui vẻ", "Meme/Hài hước"]
    },
    {
        "id": "Mai Anh",
        "gender": "female",
        "region": "Bắc",
        "style": "Dịu dàng, nhẹ nhàng, ấm áp, tâm tình",
        "stickman_roles": ["Nhân vật nữ dịu dàng", "Tâm sự", "Cảnh hồi tưởng", "Lời khuyên"]
    },
    {
        "id": "Quang Sơn",
        "gender": "male",
        "region": "Nam",
        "style": "Điềm đạm, rõ ràng, phong thái nam bộ",
        "stickman_roles": ["Người dẫn chuyện giọng Nam", "Nhân vật nam chững chạc", "Thương nhân/Kỹ sư"]
    },
    {
        "id": "Ngọc Huyền",
        "gender": "female",
        "region": "Nam",
        "style": "Năng động, tươi vui, biểu cảm cao",
        "stickman_roles": ["Nhân vật nữ tinh nghịch", "Phản ứng bất ngờ", "Shorts/Reels viral"]
    },
    {
        "id": "Quỳnh Giang",
        "gender": "female",
        "region": "Bắc",
        "style": "Trầm tĩnh, học thuật, tài liệu khoa học",
        "stickman_roles": ["Giải thích kiến thức", "Voiceover tài liệu", "Phân tích số liệu"]
    },
    {
        "id": "Minh Quang",
        "gender": "male",
        "region": "Bắc",
        "style": "Trầm vang, chững chạc, quyền uy",
        "stickman_roles": ["Trùm phản diện (Boss)", "Giám đốc", "Giọng nói quyền lực"]
    },
    {
        "id": "Bảo Ngọc",
        "gender": "female",
        "region": "Nam",
        "style": "Trẻ con, nhí nhảnh, hoạt hình",
        "stickman_roles": ["Nhân vật em bé", "Stickman ngây thơ", "Tình huống hài hước"]
    },
    {
        "id": "Đức Huy",
        "gender": "male",
        "region": "Nam",
        "style": "Hài hước, dí dỏm, đường phố",
        "stickman_roles": ["Nhân vật ngớ ngẩn (Silly Stickman)", "Tấu hài", "Reaction"]
    },
    {
        "id": "Thanh Hương",
        "gender": "female",
        "region": "Bắc",
        "style": "Chuẩn mực, nghiêm túc, phong cách biên tập viên thời sự",
        "stickman_roles": ["Bản tin Stickman News", "Báo cáo tình hình", "Thông báo khẩn"]
    },
    {
        "id": "Tiến Cường",
        "gender": "male",
        "region": "Bắc",
        "style": "Hào hùng, kịch tính, đầy năng lượng",
        "stickman_roles": ["Cảnh hành động", "Lời hiệu triệu", "Cao trào kịch tính"]
    }
]


def _ensure_vieneu():
    """Import vieneu, re-execing into VIENEU_VENV python if needed."""
    try:
        import vieneu  # noqa: F401
        return
    except ImportError:
        pass
    venv = Path(os.environ.get(
        "VIENEU_VENV", "~/workspace/vieneu-venv")).expanduser()
    venv_python = venv / "bin" / "python"
    # NOTE: do not realpath() the venv python here — it is a symlink to the
    # base interpreter, so realpath would equal sys.executable and the
    # re-exec would never trigger. Compare the unresolved venv path instead.
    if venv_python.is_file() and sys.executable != str(venv_python):
        os.execv(str(venv_python),
                 [str(venv_python), os.path.abspath(__file__), *sys.argv[1:]])
    raise SystemExit(
        "vieneu is not installed for this Python. Install it with "
        "`pip install vieneu` or set VIENEU_VENV to a venv that has it "
        "(e.g. ~/workspace/vieneu-venv).")


def load_vieneu(models_dir, precision="fp32", **kwargs):
    """Return a ready Vieneu() instance (v3 Turbo, ONNX/CPU)."""
    from vieneu._v3_turbo_engine import onnx_runtime_lite as ort_lite
    graph_dir = Path(models_dir) / "v3-turbo-onnx"
    codec_dir = Path(models_dir) / "moss-codec-onnx"
    for d, label in ((graph_dir, "model graphs"), (codec_dir, "codec")):
        if not d.is_dir():
            raise SystemExit(
                f"VieNeu {label} directory not found: {d}\n"
                "Materialize the model first (cp -rL the HF cache files "
                "into one directory) or set VIENEU_MODELS_DIR.")
    orig_fetch = ort_lite.OnnxV3LiteEngine._fetch

    @staticmethod
    def _patched_fetch(repo, files, subfolder=None):
        if repo == _CODEC_REPO:
            return codec_dir
        return orig_fetch(repo, files, subfolder)

    ort_lite.OnnxV3LiteEngine._fetch = _patched_fetch
    from vieneu import Vieneu
    try:
        return Vieneu(onnx_dir=str(graph_dir), precision=precision, **kwargs)
    finally:
        ort_lite.OnnxV3LiteEngine._fetch = orig_fetch


def verify_with_ffprobe(path):
    """Verify audio file properties using ffprobe."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams",
             "-of", "json", str(path)],
            capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {"ffprobe": "unavailable; output not verified"}
    info = json.loads(out.stdout)
    audio = next((s for s in info.get("streams", [])
                  if s.get("codec_type") == "audio"), {})
    return {
        "duration": float(info.get("format", {}).get("duration", 0)),
        "sample_rate": int(audio.get("sample_rate", 0)),
        "channels": int(audio.get("channels", 0)),
        "codec": audio.get("codec_name"),
    }


def apply_atempo(input_path: Path, output_path: Path, tempo: float, trim_silence: bool = False):
    """Apply FFmpeg pitch-preserving speed adjustment (atempo filter).
    
    FFmpeg's atempo accepts values between 0.5 and 2.0.
    For ratios outside this range, multiple atempo filters are chained together.
    """
    filters = []
    if trim_silence:
        filters.append(
            "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
            "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.06,areverse"
        )

    rem = tempo
    while rem > 2.0:
        filters.append("atempo=2.0")
        rem /= 2.0
    while rem < 0.5:
        filters.append("atempo=0.5")
        rem /= 0.5
    if abs(rem - 1.0) > 0.005 or not filters:
        filters.append(f"atempo={rem:.4f}")

    filter_str = ",".join(filters)
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-filter:a", filter_str,
        "-ar", "44100",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
        raise RuntimeError(f"FFmpeg atempo failed: {err_msg}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text to synthesize")
    group.add_argument("--text-file", help="File with the exact approved text")
    group.add_argument("--list-voices", action="store_true",
                       help="List preset voices and exit")
    parser.add_argument("--output", help="Output WAV file (required unless --list-voices)")
    parser.add_argument("--replace", action="store_true",
                        help="Replace an existing output WAV after successful synthesis")
    parser.add_argument("--voice", default=os.environ.get("VIENEU_VOICE", DEFAULT_VOICE),
                        help=f'Voice ID (default: "{DEFAULT_VOICE}")')
    parser.add_argument("--ref-audio",
                        help="Reference audio file (3-8s) for zero-shot voice cloning")
    parser.add_argument("--no-ref-codes", action="store_true",
                        help="Only extract timbre from ref-audio (useful for cross-lingual reference)")
    parser.add_argument("--target-duration", type=float, default=0.0,
                        help="Target duration in seconds; automatically adjusts speed via atempo")
    parser.add_argument("--atempo", type=float, default=0.0,
                        help="Explicit pitch-preserving tempo multiplier (e.g. 1.15 for +15%% speed)")
    parser.add_argument("--min-speed", type=float, default=0.70,
                        help="Minimum allowed tempo ratio when auto-fitting (default 0.70)")
    parser.add_argument("--max-speed", type=float, default=1.60,
                        help="Maximum allowed tempo ratio when auto-fitting (default 1.60)")
    parser.add_argument("--trim-silence", action="store_true",
                        help="Trim starting and trailing silence using FFmpeg silenceremove")
    parser.add_argument("--precision", default="fp32",
                        help="ONNX precision, fp32 (default) or int8 (faster)")
    parser.add_argument("--models-dir",
                        default=os.environ.get("VIENEU_MODELS_DIR",
                                               "~/workspace/vieneu-models"),
                        help="Materialized VieNeu model directory")
    args = parser.parse_args()

    if args.list_voices:
        # Check if vieneu is importable and has custom runtime list
        runtime_voices = None
        try:
            import vieneu
            if hasattr(vieneu, "list_preset_voices"):
                runtime_voices = vieneu.list_preset_voices()
        except Exception:
            pass

        out_data = {
            "catalog": PRESET_VOICE_CATALOG,
            "runtime_voices": runtime_voices,
            "default_voice": DEFAULT_VOICE,
            "cloning_supported": True,
            "auto_fit_atempo_supported": True
        }
        print(json.dumps(out_data, ensure_ascii=False, indent=2))
        return

    if not args.output:
        parser.error("--output is required (unless --list-voices)")
    output = Path(args.output).expanduser()
    if output.exists() and not args.replace:
        parser.error(f"Output already exists: {output}; choose another path or pass --replace")

    _ensure_vieneu()
    models_dir = Path(args.models_dir).expanduser()
    t0 = time.time()
    tts = load_vieneu(models_dir, precision=args.precision)
    init_s = time.time() - t0
    print(f"VieNeu ready in {init_s:.1f}s (backend={getattr(tts, 'backend', '?')})",
          flush=True)

    text = args.text if args.text is not None else Path(
        args.text_file).read_text(encoding="utf-8").strip()
    if not text:
        parser.error("Text is empty")

    infer_kw = {}
    if args.ref_audio:
        ref_path = Path(args.ref_audio).expanduser().resolve()
        if not ref_path.is_file():
            parser.error(f"Reference audio not found: {ref_path}")
        infer_kw["ref_audio"] = str(ref_path)
        infer_kw["use_ref_codes"] = not args.no_ref_codes
    else:
        infer_kw["voice"] = args.voice

    t1 = time.time()
    audio = tts.infer(text, **infer_kw)
    infer_s = time.time() - t1

    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_name(output.stem + ".pending" + output.suffix)
    if temp_output.exists():
        raise SystemExit(f"Temporary output exists; inspect it before retrying: {temp_output}")

    try:
        tts.save(audio, str(temp_output))
        if not temp_output.is_file() or temp_output.stat().st_size == 0:
            raise SystemExit("VieNeu did not produce a non-empty WAV")

        # Measure raw duration
        raw_probe = verify_with_ffprobe(temp_output)
        raw_duration = raw_probe.get("duration", 0.0)

        applied_atempo = 1.0
        do_atempo = False

        if args.atempo > 0:
            applied_atempo = args.atempo
            do_atempo = abs(applied_atempo - 1.0) > 0.005
        elif args.target_duration > 0 and raw_duration > 0:
            calculated_ratio = raw_duration / args.target_duration
            # Clamp ratio within safe speed boundaries
            applied_atempo = max(args.min_speed, min(args.max_speed, calculated_ratio))
            do_atempo = abs(applied_atempo - 1.0) > 0.01

        if do_atempo or args.trim_silence:
            fitted_temp = output.with_name(output.stem + ".fitted" + output.suffix)
            try:
                apply_atempo(temp_output, fitted_temp, applied_atempo, trim_silence=args.trim_silence)
                if fitted_temp.exists() and fitted_temp.stat().st_size > 0:
                    os.replace(fitted_temp, output)
                else:
                    os.replace(temp_output, output)
            finally:
                if fitted_temp.exists():
                    fitted_temp.unlink()
        else:
            os.replace(temp_output, output)
    finally:
        if temp_output.exists():
            temp_output.unlink()

    final_probe = verify_with_ffprobe(output)
    result = {
        "output": str(output.resolve()),
        "voice": args.voice if not args.ref_audio else f"cloned:{Path(args.ref_audio).name}",
        "ref_audio": str(args.ref_audio) if args.ref_audio else None,
        "init_seconds": round(init_s, 1),
        "infer_seconds": round(infer_s, 1),
        "raw_duration": round(raw_duration, 3),
        "target_duration": round(args.target_duration, 3) if args.target_duration > 0 else None,
        "applied_atempo": round(applied_atempo, 3) if do_atempo else 1.0,
        "atempo_adjusted": do_atempo,
        **final_probe
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
