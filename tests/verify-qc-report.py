#!/usr/bin/env python3
"""Test verification for automated QC & verification.json report generation."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QC_SCRIPT = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "qc-verification.py"
AUTOPILOT_MJS = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "autopilot.mjs"


def generate_sample_video(output_mp4: Path, duration_s: float = 4.0, freeze: bool = False, silence: bool = False):
    """Generate a valid MP4 test video using FFmpeg testsrc."""
    # Video source
    if freeze:
        # Static red frame for full duration
        v_filter = f"color=c=red:s=320x240:d={duration_s},fps=25"
    else:
        # Animated testsrc
        v_filter = f"testsrc=size=320x240:rate=25:duration={duration_s}"

    # Audio source
    if silence:
        # Complete silence
        a_filter = f"anullsrc=r=48000:cl=mono,atrim=0:{duration_s}"
    else:
        # Sine tone
        a_filter = f"sine=frequency=440:sample_rate=48000:duration={duration_s}"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", v_filter,
        "-f", "lavfi", "-i", a_filter,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11" if not silence else "anull",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(duration_s),
        str(output_mp4)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def main():
    print("1. Testing clean video QC (should pass)...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        clean_mp4 = tmp_path / "clean.mp4"
        verify_json = tmp_path / "clean_verify.json"

        generate_sample_video(clean_mp4, duration_s=4.0, freeze=False, silence=False)
        assert clean_mp4.exists(), "Clean MP4 generation failed"

        res = subprocess.run(
            [sys.executable, str(QC_SCRIPT), "--video", str(clean_mp4), "--output", str(verify_json)],
            capture_output=True, text=True, check=True
        )
        assert verify_json.exists(), "verification.json not generated"

        with open(verify_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "stream_info" in data, "Missing stream_info"
        assert "audio_metrics" in data, "Missing audio_metrics"
        assert "qc_evaluation" in data, "Missing qc_evaluation"
        qc = data["qc_evaluation"]
        print(f"   -> Score: {qc['score']}/100, QA Passed: {qc['qa_passed']}")
        assert qc["score"] >= 80, f"Expected clean video score >= 80, got {qc['score']}"
        print("   -> Clean video QC PASSED!")

        print("2. Testing video with Freeze Frame detection...")
        freeze_mp4 = tmp_path / "freeze.mp4"
        freeze_json = tmp_path / "freeze_verify.json"
        generate_sample_video(freeze_mp4, duration_s=4.5, freeze=True, silence=False)

        subprocess.run(
            [sys.executable, str(QC_SCRIPT), "--video", str(freeze_mp4), "--output", str(freeze_json)],
            capture_output=True, text=True, check=True
        )
        with open(freeze_json, "r", encoding="utf-8") as f:
            freeze_data = json.load(f)
        findings = [f["id"] for f in freeze_data["qc_evaluation"]["findings"]]
        print(f"   -> Findings on freeze video: {findings}")
        assert "freeze_frame" in findings, f"Expected freeze_frame finding, got {findings}"
        print("   -> Freeze frame detection PASSED!")

        print("3. Testing Audio Silence detection...")
        silence_mp4 = tmp_path / "silence.mp4"
        silence_json = tmp_path / "silence_verify.json"
        generate_sample_video(silence_mp4, duration_s=4.5, freeze=False, silence=True)

        subprocess.run(
            [sys.executable, str(QC_SCRIPT), "--video", str(silence_mp4), "--output", str(silence_json)],
            capture_output=True, text=True, check=True
        )
        with open(silence_json, "r", encoding="utf-8") as f:
            silence_data = json.load(f)
        silence_findings = [f["id"] for f in silence_data["qc_evaluation"]["findings"]]
        print(f"   -> Findings on silence video: {silence_findings}")
        assert "audio_silence" in silence_findings, f"Expected audio_silence finding, got {silence_findings}"
        print("   -> Audio silence detection PASSED!")

        print("4. Testing node autopilot.mjs qc CLI...")
        cli_res = subprocess.run(
            ["node", str(AUTOPILOT_MJS), "qc", str(clean_mp4)],
            capture_output=True, text=True, check=True
        )
        cli_output = json.loads(cli_res.stdout)
        assert cli_output.get("qa_passed") is not None, "CLI output missing qa_passed"
        print(f"   -> CLI score: {cli_output.get('score')}, QA Passed: {cli_output.get('qa_passed')}")
        print("   -> autopilot.mjs qc CLI PASSED!")

    print("\nALL POST-RENDER QC & VERIFICATION.JSON CHECKS PASSED!")


if __name__ == "__main__":
    main()
