#!/usr/bin/env python3
"""Word-timestamp alignment with faster-whisper (CPU-friendly).

PATCH (fork 2026-11-09): scripts/align_captions.py requires openai-whisper,
which pulls a ~1 GB CUDA torch wheel and does not run on CPU-only machines.
faster-whisper uses the same official Whisper model via CTranslate2
(CPU, int8) and emits identical word-level timestamps. Output format matches
align_captions.py exactly, so `node scripts/autopilot.mjs captions` accepts
it unchanged: {"words": [{"start", "end", "word"}], "method": ...}.

Usage:
    python3 scripts/align_captions_fast.py narration.wav --output words.json \
        --language vi --model base
    # Optionally correct Whisper's word TEXT 1:1 to the approved script,
    # keeping timestamps untouched (Whisper often mis-hears words):
    python3 scripts/align_captions_fast.py narration.wav --output words.json \
        --language vi --script approved-script.txt

Requires: faster-whisper, soundfile, ffmpeg (for the 16 kHz resample).
Model downloads from Hugging Face on first use; pass --model to pick another
official Whisper size. Human text/timing review is still required.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="base")
    parser.add_argument("--language")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--vad-filter", action="store_true",
                        help="Enable Silero VAD filtering (helps long audio)")
    parser.add_argument("--script",
                        help="Approved script text file; if its word count "
                        "matches Whisper's, word TEXT is replaced 1:1 "
                        "(timestamps unchanged)")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; will not overwrite")
    if not args.audio.is_file():
        parser.error("Audio file not found")
    try:
        import soundfile as sf
        from faster_whisper import WhisperModel
    except ImportError as e:
        parser.error(
            "Missing dependency (%s): pip install faster-whisper soundfile "
            "(plus ffmpeg on PATH)" % e.name)
    # faster-whisper's PyAV file decode rejects some PyAV builds, so decode
    # with ffmpeg to 16 kHz mono PCM first and feed a numpy array instead.
    with tempfile.TemporaryDirectory(prefix="align-fast-") as tmp:
        wav16 = Path(tmp) / "audio-16k.wav"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(args.audio),
             "-ar", "16000", "-ac", "1", str(wav16)],
            check=True)
        audio, sr = sf.read(str(wav16), dtype="float32")
        assert sr == 16000, sr
        model = WhisperModel(args.model, device=args.device,
                             compute_type=args.compute_type)
        segments, info = model.transcribe(
            audio, language=args.language, word_timestamps=True,
            vad_filter=args.vad_filter)
        print(f"detected language: {info.language} "
              f"(prob {info.language_probability:.2f})", flush=True)
        words = []
        for segment in segments:
            for w in (segment.words or []):
                if w.end > w.start:
                    words.append({"start": round(w.start, 3),
                                  "end": round(w.end, 3),
                                  "word": w.word.strip()})
    if not words:
        parser.error("No aligned words returned; inspect the audio")
    method = (f"faster-whisper {args.model}, word_timestamps, "
              f"language={args.language}; human text/timing review required")
    if args.script:
        approved = Path(args.script).read_text(encoding="utf-8").split()
        if len(approved) == len(words):
            words = [{"start": w["start"], "end": w["end"], "word": correct}
                     for w, correct in zip(words, approved)]
            method += ("; word text human-corrected 1:1 to approved script, "
                       "timestamps unchanged")
            print(f"script word-text correction applied: {len(words)} words",
                  flush=True)
        else:
            print(f"Warning: script has {len(approved)} words but Whisper "
                  f"returned {len(words)}; keeping Whisper words unchanged. "
                  f"Review the text manually.", file=sys.stderr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump({"words": words, "method": method}, output,
                  ensure_ascii=False, indent=2)
    print(json.dumps({"output": str(args.output.resolve()),
                      "words": len(words)}))


if __name__ == "__main__":
    main()
