#!/usr/bin/env python3
"""Test verification for EBU R128 (-14 LUFS) Loudness & Smart Ducking."""
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
SCRIPT_PATH = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "audio-master-lufs.py"
AUTOPILOT_MJS = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "autopilot.mjs"


def generate_tone(filepath: Path, duration_sec: float = 3.0, freq: float = 440.0, volume: float = 0.1, sample_rate: int = 48000):
    """Generate a clean sine wave at a specific volume."""
    n_samples = int(duration_sec * sample_rate)
    with wave.open(str(filepath), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            val = int(32767 * volume * math.sin(2 * math.pi * freq * i / sample_rate))
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wav.writeframes(frames)


def main():
    print("1. Verifying audio-master-lufs module import...")
    spec = importlib.util.spec_from_file_location("audio_master", str(SCRIPT_PATH))
    audio_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audio_mod)
    print("   -> OK: module loaded.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        raw_wav = tmp_path / "raw_quiet.wav"
        norm_wav = tmp_path / "normalized.wav"

        # 1. Quiet tone (~-26 LUFS)
        generate_tone(raw_wav, duration_sec=3.5, freq=440.0, volume=0.04)

        print("2. Measuring initial loudness...")
        m1 = audio_mod.measure_loudness(raw_wav)
        print(f"   -> Raw file LUFS: {m1.get('integrated_lufs')} LUFS (Status: {m1.get('status')})")
        assert m1.get("integrated_lufs") is not None, "Failed to measure integrated LUFS"
        assert m1["status"] in ["too_quiet", "needs_review"], f"Expected too_quiet/needs_review, got {m1['status']}"

        print("3. Performing 2-pass Loudness Normalization to -14 LUFS...")
        m2 = audio_mod.normalize_audio(raw_wav, norm_wav, target_lufs=-14.0, true_peak=-1.5)
        print(f"   -> Normalized LUFS: {m2.get('integrated_lufs')} LUFS, True-Peak: {m2.get('true_peak_dbfs')} dBFS")
        assert m2.get("integrated_lufs") is not None, "Failed to measure normalized LUFS"
        assert abs(m2["integrated_lufs"] - (-14.0)) <= 1.2, f"Target -14 LUFS not met: got {m2['integrated_lufs']}"
        assert m2["true_peak_dbfs"] <= -1.0, f"True-Peak exceeded -1.0 dBFS: got {m2['true_peak_dbfs']}"
        assert m2["status"] == "pass", f"Expected pass status, got {m2['status']}"
        print("   -> Normalization PASSED!")

        print("4. Testing Smart Ducking...")
        voice_wav = tmp_path / "voice.wav"
        bgm_wav = tmp_path / "bgm.wav"
        duck_wav = tmp_path / "duck_master.wav"

        # Voice: short bursts
        generate_tone(voice_wav, duration_sec=4.0, freq=300.0, volume=0.5)
        # BGM: continuous tone
        generate_tone(bgm_wav, duration_sec=4.0, freq=600.0, volume=0.3)

        duck_res = audio_mod.smart_ducking(voice_wav, bgm_wav, duck_wav, duck_db=-14.0, normalize=True)
        print(f"   -> Ducked Master LUFS: {duck_res.get('integrated_lufs')} LUFS (Status: {duck_res.get('status')})")
        assert duck_wav.exists() and duck_wav.stat().st_size > 1000, "Ducked file not produced"
        assert duck_res["status"] == "pass", f"Ducked master not normalized: {duck_res['status']}"
        print("   -> Smart Ducking PASSED!")

        print("5. Testing node autopilot.mjs measure-audio CLI...")
        cli_res = subprocess.run(
            ["node", str(AUTOPILOT_MJS), "measure-audio", str(norm_wav)],
            capture_output=True, text=True, check=True
        )
        cli_data = json.loads(cli_res.stdout)
        print(f"   -> CLI measurement: {cli_data.get('integrated_lufs')} LUFS (Status: {cli_data.get('status')})")
        assert cli_data.get("integrated_lufs") is not None, "CLI failed to measure LUFS"
        assert cli_data["status"] == "pass", "CLI measurement status mismatch"
        print("   -> CLI measure-audio PASSED!")

    print("\nALL EBU R128 LOUDNESS & SMART DUCKING CHECKS PASSED!")


if __name__ == "__main__":
    main()
