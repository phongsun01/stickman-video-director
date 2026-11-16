#!/usr/bin/env python3
"""Test verification for VieNeu Voice Catalog & atempo mechanics."""
import importlib.util
import json
import math
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIENEU_SCRIPT = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "vieneu-local.py"


def generate_test_wav(filepath: Path, duration_sec: float = 2.0, sample_rate: int = 44100):
    """Generate a simple sine wave WAV file for testing."""
    n_samples = int(duration_sec * sample_rate)
    with wave.open(str(filepath), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            # 440 Hz tone
            val = int(16000 * math.sin(2 * math.pi * 440 * i / sample_rate))
            frames.extend(struct.pack("<h", val))
        wav.writeframes(frames)


def main():
    print("1. Verifying --list-voices CLI...")
    res = subprocess.run(
        [sys.executable, str(VIENEU_SCRIPT), "--list-voices"],
        capture_output=True, text=True, check=True
    )
    data = json.loads(res.stdout)
    catalog = data.get("catalog", [])
    assert len(catalog) >= 10, f"Expected at least 10 voices in catalog, got {len(catalog)}"
    voice_ids = [v["id"] for v in catalog]
    assert "Thiện Minh" in voice_ids, "Thiện Minh missing"
    assert "Trúc Ly" in voice_ids, "Trúc Ly missing"
    assert "Hải Đăng" in voice_ids, "Hải Đăng missing"
    print(f"   -> OK: {len(catalog)} voices listed in catalog.")

    print("2. Verifying apply_atempo pitch-preserving timing...")
    # Import apply_atempo & verify_with_ffprobe dynamically
    spec = importlib.util.spec_from_file_location("vieneu_local", str(VIENEU_SCRIPT))
    vieneu_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vieneu_mod)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        orig_wav = tmp_path / "original_2s.wav"
        fitted_wav = tmp_path / "fitted.wav"

        # 2.0s input
        generate_test_wav(orig_wav, duration_sec=2.0)
        orig_probe = vieneu_mod.verify_with_ffprobe(orig_wav)
        orig_dur = orig_probe.get("duration", 0)
        assert abs(orig_dur - 2.0) < 0.1, f"Orig duration mismatch: {orig_dur}"

        # Speed up by 1.5x -> target ~1.33s
        vieneu_mod.apply_atempo(orig_wav, fitted_wav, tempo=1.5)
        probe_fast = vieneu_mod.verify_with_ffprobe(fitted_wav)
        fast_dur = probe_fast.get("duration", 0)
        expected_fast = 2.0 / 1.5
        assert abs(fast_dur - expected_fast) < 0.15, f"Fast duration mismatch: got {fast_dur}, expected {expected_fast}"
        print(f"   -> Fast (1.5x) duration: {fast_dur:.2f}s (expected ~{expected_fast:.2f}s) - OK")

        # Slow down by 0.8x -> target ~2.5s
        slow_wav = tmp_path / "slow.wav"
        vieneu_mod.apply_atempo(orig_wav, slow_wav, tempo=0.8)
        probe_slow = vieneu_mod.verify_with_ffprobe(slow_wav)
        slow_dur = probe_slow.get("duration", 0)
        expected_slow = 2.0 / 0.8
        assert abs(slow_dur - expected_slow) < 0.15, f"Slow duration mismatch: got {slow_dur}, expected {expected_slow}"
        print(f"   -> Slow (0.8x) duration: {slow_dur:.2f}s (expected ~{expected_slow:.2f}s) - OK")

    print("\nALL VIENEU CATALOG & ATEMPO TESTS PASSED!")


if __name__ == "__main__":
    main()
