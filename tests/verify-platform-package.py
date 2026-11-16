#!/usr/bin/env python3
"""Test verification for Multi-Platform Package Exporter & Motion Notification."""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGER_SCRIPT = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "platform-packager.py"
AUTOPILOT_MJS = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "autopilot.mjs"


def main():
    print("1. Verifying platform-packager module import...")
    spec = importlib.util.spec_from_file_location("packager", str(PACKAGER_SCRIPT))
    pkg_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pkg_mod)
    print("   -> OK: module loaded.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_video = tmp_path / "test_portrait.mp4"
        test_project = tmp_path / "project.json"

        # Generate a small 1s portrait video (720x1280)
        print("2. Generating test 9:16 portrait video...")
        cmd_v = [
            "ffmpeg", "-v", "error", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=720x1280:d=1",
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
            "-c:v", "libx264", "-t", "1",
            "-c:a", "aac", "-shortest",
            str(test_video)
        ]
        subprocess.run(cmd_v, check=True)
        assert test_video.exists(), "Failed to create test video"

        # Create dummy project.json
        project_data = {
            "title": "Bí Quyết Quản Lý Thời Gian",
            "style": "B2",
            "shots": [
                {"id": "hook", "start": 0.0, "end": 0.4, "layers": [{"type": "text", "text": "Bạn luôn thiếu thời gian?"}]},
                {"id": "agitate", "start": 0.4, "end": 0.8, "layers": [{"type": "text", "text": "Vì sao công việc dồn ứ?"}]},
                {"id": "solution", "start": 0.8, "end": 1.0, "layers": [{"type": "text", "text": "Phương pháp Pomodoro"}]}
            ],
            "captions": [
                {"start": 0.0, "end": 0.4, "text": "Bạn luôn cảm thấy thiếu thời gian mỗi ngày?"},
                {"start": 0.4, "end": 0.8, "text": "Nguyên nhân chính là do sự trì hoãn."},
                {"start": 0.8, "end": 1.0, "text": "Hãy áp dụng ngay quy tắc 25 phút này nhé."}
            ]
        }
        with open(test_project, "w", encoding="utf-8") as f:
            json.dump(project_data, f, ensure_ascii=False)

        # 3. Test python packaging function
        print("3. Testing package_platform_distribution (TikTok, Reels, Shorts, YouTube)...")
        pkg_out = tmp_path / "dist_package"
        res_pkg = pkg_mod.package_platform_distribution(
            input_path=test_video,
            output_dir=pkg_out,
            platforms=["tiktok", "reels", "shorts", "youtube"],
            title_override="Bí Quyết Quản Lý Thời Gian",
            hashtags_override=["#stickman", "#timemanagement", "#kienthuc"]
        )

        # Assert TikTok
        assert (pkg_out / "tiktok" / "video_9x16.mp4").exists()
        assert (pkg_out / "tiktok" / "caption.txt").exists()
        assert (pkg_out / "tiktok" / "hashtags.txt").exists()
        print("   -> TikTok assets generated - OK")

        # Assert Reels
        assert (pkg_out / "reels" / "video_9x16.mp4").exists()
        assert (pkg_out / "reels" / "caption.txt").exists()
        assert "Lưu video" in (pkg_out / "reels" / "caption.txt").read_text(encoding="utf-8")
        print("   -> Instagram Reels assets generated - OK")

        # Assert Shorts
        assert (pkg_out / "shorts" / "video_9x16.mp4").exists()
        shorts_title = (pkg_out / "shorts" / "title.txt").read_text(encoding="utf-8")
        assert "#shorts" in shorts_title
        print("   -> YouTube Shorts assets generated - OK")

        # Assert YouTube (16:9 Cinema Blurred Background)
        yt_v = pkg_out / "youtube" / "video_16x9.mp4"
        assert yt_v.exists()
        yt_probe = pkg_mod.probe_video(yt_v)
        assert yt_probe["width"] == 1920 and yt_probe["height"] == 1080, f"Expected 1920x1080, got {yt_probe}"
        yt_desc = (pkg_out / "youtube" / "description.txt").read_text(encoding="utf-8")
        assert "📌 DẤU MỐC THỜI GIAN (CHAPTERS):" in yt_desc
        assert "00:00" in yt_desc
        print("   -> YouTube 16:9 with Cinema Blurred Background generated - OK")

        # Assert summary.json
        summary_file = pkg_out / "summary.json"
        assert summary_file.exists()
        summary_data = json.loads(summary_file.read_text(encoding="utf-8"))
        assert len(summary_data["platforms"]) == 4
        print("   -> Packaging summary.json verified - OK")

        # 4. Test Autopilot CLI subcommand
        print("4. Testing autopilot.mjs package CLI...")
        cli_out = tmp_path / "cli_pkg"
        res_cli = subprocess.run([
            "node", str(AUTOPILOT_MJS), "package", str(test_video),
            "--output", str(cli_out),
            "--platforms", "tiktok,shorts",
            "--title", "Thử nghiệm Autopilot Package"
        ], capture_output=True, text=True)
        assert res_cli.returncode == 0, f"CLI package failed: {res_cli.stderr}"
        assert (cli_out / "tiktok" / "video_9x16.mp4").exists()
        assert (cli_out / "shorts" / "video_9x16.mp4").exists()
        print("   -> node autopilot.mjs package verified - OK")

    print("\nALL MULTI-PLATFORM PACKAGE VERIFICATION TESTS PASSED! (100%)")


if __name__ == "__main__":
    main()
