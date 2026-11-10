#!/usr/bin/env python3
"""VieNeu local TTS adapter for Autopilot (no Gemini, no cloud).

PATCH (fork 2026-11-09): the Autopilot renderer only needs a local
`narration.wav`; the bundled Gemini speech adapter is one way to make it,
not a requirement. This script makes that file with VieNeu-TTS v3 Turbo
running locally (CPU/ONNX, Apache-2.0), e.g. Vietnamese narration with the
"Hải Đăng" voice. Verified 2026-11-09 on a CPU-only VM (vieneu 3.8.3,
onnxruntime 1.31.1): init ~13s + ~11s inference for 5.7s of audio.

Usage (run with the VieNeu venv python, or let the script re-exec into it):
    python3 scripts/vieneu-local.py --text "Xin chào." --output narration.wav
    python3 scripts/vieneu-local.py --text-file script.txt --output narration.wav \
        --voice "Hải Đăng"
    python3 scripts/vieneu-local.py --list-voices

Configuration (environment, all optional):
    VIENEU_VENV        Python venv with vieneu installed (default ~/workspace/vieneu-venv)
    VIENEU_MODELS_DIR  Materialized model directory (default ~/workspace/vieneu-models)
    VIENEU_VOICE       Default voice (default "Hải Đăng")

Why the wrapper exists: stock `Vieneu()` downloads each model file with
`hf_hub_download`, which scatters files across separate HF blob directories,
while the ONNX graphs reference external data by relative path — ONNX
Runtime then fails with "External data path escapes model directory".
The fix is to materialize all model files as real files in one directory
(`cp -rL` from the HF cache into VIENEU_MODELS_DIR, with subdirectories
`v3-turbo-onnx/` for the graphs and `moss-codec-onnx/` for the codec) and
load them via `load_vieneu()` below. Never call bare `Vieneu()` here.
Output is verified with ffprobe when available.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_VOICE = "Hải Đăng"
_CODEC_REPO = "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX"


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
    parser.add_argument("--precision", default="fp32",
                        help="ONNX precision, fp32 (default) or int8 (faster)")
    parser.add_argument("--models-dir",
                        default=os.environ.get("VIENEU_MODELS_DIR",
                                               "~/workspace/vieneu-models"),
                        help="Materialized VieNeu model directory")
    args = parser.parse_args()
    if not args.list_voices and not args.output:
        parser.error("--output is required (unless --list-voices)")
    output = Path(args.output).expanduser() if args.output else None
    if output and output.exists() and not args.replace:
        parser.error(f"Output already exists: {output}; choose another path or pass --replace")
    _ensure_vieneu()
    models_dir = Path(args.models_dir).expanduser()
    t0 = time.time()
    tts = load_vieneu(models_dir, precision=args.precision)
    init_s = time.time() - t0
    print(f"VieNeu ready in {init_s:.1f}s (backend={getattr(tts, 'backend', '?')})",
          flush=True)
    if args.list_voices:
        voices = None
        for getter in (lambda: tts.list_preset_voices(),
                       lambda: __import__("vieneu").list_preset_voices()):
            try:
                voices = getter()
                break
            except Exception:
                continue
        print(json.dumps({"voices": voices}, ensure_ascii=False, indent=2))
        return
    text = args.text if args.text is not None else Path(
        args.text_file).read_text(encoding="utf-8").strip()
    if not text:
        parser.error("Text is empty")
    t1 = time.time()
    audio = tts.infer(text, voice=args.voice)
    infer_s = time.time() - t1
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_name(output.stem + ".pending" + output.suffix)
    if temp_output.exists():
        raise SystemExit(f"Temporary output exists; inspect it before retrying: {temp_output}")
    try:
        tts.save(audio, str(temp_output))
        if not temp_output.is_file() or temp_output.stat().st_size == 0:
            raise SystemExit("VieNeu did not produce a non-empty WAV")
        os.replace(temp_output, output)
    finally:
        if temp_output.exists():
            temp_output.unlink()
    result = {"output": str(output.resolve()), "voice": args.voice,
              "init_seconds": round(init_s, 1),
              "infer_seconds": round(infer_s, 1),
              **verify_with_ffprobe(output)}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
