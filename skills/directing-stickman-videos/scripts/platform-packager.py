#!/usr/bin/env python3
"""Multi-Platform Video Export & Packaging Engine for Stickman Autopilot.

Packages Stickman production videos for TikTok, Instagram Reels, YouTube Shorts,
and YouTube (Standard 16:9 landscape) with automated:
1. Aspect ratio adaptation (Native 9:16 vertical pass-through, or Studio Cinema
   Blurred Background for 9:16 -> 16:9 / 16:9 -> 9:16 conversion).
2. Platform-optimized captions, hooks, and hashtags.
3. YouTube SEO metadata with automatic Shot Timestamp Chapters.
4. Packaging manifest (`package/summary.json`).

Usage:
    # Package directly from project.json:
    python3 scripts/platform-packager.py --input productions/my-film/project.json

    # Package from rendered film.mp4:
    python3 scripts/platform-packager.py --input productions/my-film/outputs/film.mp4 \
        --title "Bí mật người que" --platforms tiktok,youtube,shorts,reels
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def probe_video(video_path: Path) -> Dict[str, Any]:
    """Inspects video stream dimensions, duration, and codec info via ffprobe."""
    ffprobe = shutil.which("ffprobe") or "ffprobe"
    cmd = [
        ffprobe,
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(video_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {video_path}: {res.stderr}")
    data = json.loads(res.stdout)
    video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video_stream:
        raise ValueError(f"No video stream found in {video_path}")
    
    width = int(video_stream.get("width", 720))
    height = int(video_stream.get("height", 1280))
    duration = float(data.get("format", {}).get("duration", 0.0) or video_stream.get("duration", 0.0))
    return {
        "width": width,
        "height": height,
        "duration": duration,
        "is_portrait": height > width,
        "aspect_ratio": f"{width}:{height}"
    }


def find_project_and_video(input_path: Path) -> Tuple[Path, Optional[Path], Optional[Dict[str, Any]]]:
    """Resolves video path, project.json path, and parsed project dict."""
    input_path = input_path.resolve()
    project_data = None
    project_path = None
    video_path = None

    if input_path.is_file() and input_path.suffix == ".json":
        project_path = input_path
        with open(project_path, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        # Search for rendered film.mp4 or preview.mp4
        candidates = [
            input_path.parent / "outputs" / "film.mp4",
            input_path.parent / "outputs" / "preview.mp4",
            input_path.parent / "film.mp4",
            input_path.parent / "preview.mp4"
        ]
        for c in candidates:
            if c.is_file():
                video_path = c
                break
        if not video_path:
            raise FileNotFoundError(f"No film.mp4 or preview.mp4 found for project {input_path}. Please render first!")
    elif input_path.is_file() and input_path.suffix in [".mp4", ".mov", ".mkv"]:
        video_path = input_path
        # Search nearby project.json
        candidates = [
            input_path.parent / "project.json",
            input_path.parent.parent / "project.json"
        ]
        for c in candidates:
            if c.is_file():
                project_path = c
                with open(project_path, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
                break
    else:
        raise FileNotFoundError(f"Input must be project.json or .mp4 file: {input_path}")

    return video_path, project_path, project_data


def format_timestamp(seconds: float) -> str:
    """Formats seconds into MM:SS for YouTube chapters."""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def generate_chapters(project_data: Optional[Dict[str, Any]]) -> str:
    """Builds YouTube chapters from shot boundaries or key captions."""
    if not project_data or "shots" not in project_data or not project_data["shots"]:
        return "00:00 - Mở đầu\n00:05 - Nội dung chính\n00:30 - Kết luận & Lời khuyên"
    
    shots = project_data["shots"]
    chapters = []
    for i, s in enumerate(shots):
        start = float(s.get("start", 0.0))
        time_str = format_timestamp(start)
        title = s.get("title") or s.get("id") or f"Phần {i + 1}"
        # If shot has layers with text, extract short headline
        for l in s.get("layers", []):
            if l.get("type") == "text" and l.get("text"):
                clean = re.sub(r"\s+", " ", l["text"]).strip()
                if len(clean) <= 40:
                    title = clean
                    break
        chapters.append(f"{time_str} - {title}")
    
    # YouTube requires chapter 1 to start at 00:00
    if not chapters[0].startswith("00:00"):
        chapters.insert(0, "00:00 - Mở đầu")
    return "\n".join(chapters)


def generate_content_summary(project_data: Optional[Dict[str, Any]]) -> str:
    """Extracts a short overview from project captions."""
    if not project_data or "captions" not in project_data or not project_data["captions"]:
        return "Video hoạt hình Stickman thú vị, ngắn gọn và trực quan với các thông điệp giá trị."
    caps = [c.get("text", "") for c in project_data["captions"][:6] if c.get("text")]
    return " ".join(caps)


def render_blurred_background_video(
    src_path: Path,
    dst_path: Path,
    target_width: int,
    target_height: int
) -> bool:
    """Transforms video aspect ratio with blurred background padding."""
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    if target_width > target_height:
        # Target 16:9 Landscape (e.g. 1920x1080) from Portrait
        filt = (
            f"[0:v]split[bg][fg];"
            f"[bg]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},boxblur=25:5[bg_blur];"
            f"[fg]scale=-1:{target_height}[fg_scaled];"
            f"[bg_blur][fg_scaled]overlay=(W-w)/2:0"
        )
    else:
        # Target 9:16 Portrait (e.g. 1080x1920) from Landscape
        filt = (
            f"[0:v]split[bg][fg];"
            f"[bg]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},boxblur=25:5[bg_blur];"
            f"[fg]scale={target_width}:-1[fg_scaled];"
            f"[bg_blur][fg_scaled]overlay=0:(H-h)/2"
        )
        
    cmd = [
        ffmpeg,
        "-v", "error",
        "-y",
        "-i", str(src_path),
        "-filter_complex", filt,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(dst_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg aspect ratio transform failed: {res.stderr}")
    return dst_path.exists()


def copy_stream(src_path: Path, dst_path: Path) -> bool:
    """Fast stream copy with zero transcoding."""
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-v", "error",
        "-y",
        "-i", str(src_path),
        "-c", "copy",
        "-movflags", "+faststart",
        str(dst_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        # Fallback to copy file
        shutil.copyfile(src_path, dst_path)
    return dst_path.exists()


def package_platform_distribution(
    input_path: Path,
    output_dir: Optional[Path] = None,
    platforms: Optional[List[str]] = None,
    title_override: Optional[str] = None,
    description_override: Optional[str] = None,
    hashtags_override: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Packages a video project into distribution-ready platform folders."""
    video_path, project_path, project_data = find_project_and_video(input_path)
    video_info = probe_video(video_path)
    
    if output_dir is None:
        if project_path:
            output_dir = project_path.parent / "outputs" / "package"
        else:
            output_dir = video_path.parent / "package"
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    title = title_override or (project_data.get("title") if project_data else None) or (project_data.get("topic") if project_data else None) or video_path.stem
    if title.lower() in ["film", "preview"]:
        title = "Hoạt Hình Người Que Stickman"
        
    summary_text = description_override or generate_content_summary(project_data)
    chapters_text = generate_chapters(project_data)
    
    platforms = [p.strip().lower() for p in (platforms or ["tiktok", "reels", "shorts", "youtube"])]
    results: Dict[str, Any] = {
        "title": title,
        "source_video": str(video_path),
        "source_dimensions": f"{video_info['width']}x{video_info['height']}",
        "duration_seconds": video_info["duration"],
        "package_dir": str(output_dir),
        "packaged_at": datetime.datetime.now().isoformat(),
        "platforms": {}
    }
    
    print("\n" + "=" * 80)
    print("📦 [STICKMAN MULTI-PLATFORM EXPORT & PACKAGING]")
    print(f"   ► Tiêu đề video: {title}")
    print(f"   ► Nguồn: {video_path.name} ({video_info['width']}x{video_info['height']}, {video_info['duration']:.1f}s)")
    print(f"   ► Thư mục xuất: {output_dir}")
    print(f"   ► Nền tảng: {', '.join(platforms).upper()}")
    print("=" * 80 + "\n")
    
    # 1. TIKTOK
    if "tiktok" in platforms:
        p_dir = output_dir / "tiktok"
        p_dir.mkdir(parents=True, exist_ok=True)
        v_out = p_dir / "video_9x16.mp4"
        if video_info["is_portrait"]:
            copy_stream(video_path, v_out)
        else:
            print("   ⏳ [TikTok] Đang chuyển đổi 16:9 -> 9:16 (blurred padding)...")
            render_blurred_background_video(video_path, v_out, 1080, 1920)
            
        caption = f"{title}\n\n👉 Xem hết để không bỏ lỡ thông tin quan trọng! Thả tim & Follow kênh nhé! ❤️\n"
        custom_tags = hashtags_override or ["#stickman", "#hoathinh", "#kienthuc", "#xuhuong", "#fyp", "#learnontiktok"]
        hashtags = " ".join(custom_tags)
        
        (p_dir / "caption.txt").write_text(caption, encoding="utf-8")
        (p_dir / "hashtags.txt").write_text(hashtags, encoding="utf-8")
        results["platforms"]["tiktok"] = {
            "video": str(v_out),
            "video_size_bytes": v_out.stat().st_size,
            "caption": str(p_dir / "caption.txt"),
            "hashtags": str(p_dir / "hashtags.txt")
        }
        print(f"   ✓ [TikTok] Đóng gói thành công -> {p_dir}")

    # 2. INSTAGRAM REELS
    if "reels" in platforms:
        p_dir = output_dir / "reels"
        p_dir.mkdir(parents=True, exist_ok=True)
        v_out = p_dir / "video_9x16.mp4"
        if video_info["is_portrait"]:
            copy_stream(video_path, v_out)
        else:
            print("   ⏳ [Reels] Đang chuyển đổi 16:9 -> 9:16 (blurred padding)...")
            render_blurred_background_video(video_path, v_out, 1080, 1920)
            
        caption = (
            f"{title}\n\n"
            f"💡 Bạn đã biết điều này chưa? Cùng xem ngay video ngắn này nhé.\n\n"
            f"📌 Lưu video này để xem lại khi cần!\n"
            f"👉 Nhấn Follow kênh để nhận thêm nhiều nội dung thú vị mỗi ngày.\n\n"
        )
        custom_tags = hashtags_override or ["#reels", "#stickman", "#animation", "#learnsomethingnew", "#viralreels", "#reelsvietnam", "#storytelling"]
        hashtags = " ".join(custom_tags)
        
        (p_dir / "caption.txt").write_text(caption, encoding="utf-8")
        (p_dir / "hashtags.txt").write_text(hashtags, encoding="utf-8")
        results["platforms"]["reels"] = {
            "video": str(v_out),
            "video_size_bytes": v_out.stat().st_size,
            "caption": str(p_dir / "caption.txt"),
            "hashtags": str(p_dir / "hashtags.txt")
        }
        print(f"   ✓ [Instagram Reels] Đóng gói thành công -> {p_dir}")

    # 3. YOUTUBE SHORTS
    if "shorts" in platforms:
        p_dir = output_dir / "shorts"
        p_dir.mkdir(parents=True, exist_ok=True)
        v_out = p_dir / "video_9x16.mp4"
        if video_info["is_portrait"]:
            copy_stream(video_path, v_out)
        else:
            print("   ⏳ [Shorts] Đang chuyển đổi 16:9 -> 9:16 (blurred padding)...")
            render_blurred_background_video(video_path, v_out, 1080, 1920)
            
        shorts_title = f"{title} #shorts"[:95]
        desc = (
            f"{title}\n\n"
            f"{summary_text}\n\n"
            f"👍 Like & Subscribe kênh Stickman Video Director để xem thêm nhiều video hữu ích nhé!\n"
            f"#shorts #stickman #hoathinh #nguoique"
        )
        (p_dir / "title.txt").write_text(shorts_title, encoding="utf-8")
        (p_dir / "description.txt").write_text(desc, encoding="utf-8")
        results["platforms"]["shorts"] = {
            "video": str(v_out),
            "video_size_bytes": v_out.stat().st_size,
            "title": str(p_dir / "title.txt"),
            "description": str(p_dir / "description.txt")
        }
        print(f"   ✓ [YouTube Shorts] Đóng gói thành công -> {p_dir}")

    # 4. YOUTUBE STANDARD (16:9 LANDSCAPE)
    if "youtube" in platforms:
        p_dir = output_dir / "youtube"
        p_dir.mkdir(parents=True, exist_ok=True)
        v_out = p_dir / "video_16x9.mp4"
        if not video_info["is_portrait"]:
            copy_stream(video_path, v_out)
        else:
            print("   ⏳ [YouTube 16:9] Đang tạo Cinema Blurred Background (1920x1080)...")
            render_blurred_background_video(video_path, v_out, 1920, 1080)
            
        yt_title = f"{title} | Hoạt Hình Người Que Stickman Explainer"
        yt_desc = (
            f"{title}\n\n"
            f"Chào mừng bạn đến với kênh! Trong video này chúng ta sẽ khám phá:\n"
            f"{summary_text}\n\n"
            f"📌 DẤU MỐC THỜI GIAN (CHAPTERS):\n"
            f"{chapters_text}\n\n"
            f"🔔 Đừng quên bấm ĐĂNG KÝ (Subscribe) và bật Chuông Thông Báo để không bỏ lỡ các tập phim mới nhất!\n"
            f"-----------------------------------------\n"
            f"#stickman #hoathinhnguoique #kienthuc #giaithich #motiongraphics"
        )
        yt_tags = "stickman, người que, hoạt hình, kiến thức, video giải thích, học tập, công nghệ, tư duy, phát triển bản thân"
        
        (p_dir / "title.txt").write_text(yt_title, encoding="utf-8")
        (p_dir / "description.txt").write_text(yt_desc, encoding="utf-8")
        (p_dir / "tags.txt").write_text(yt_tags, encoding="utf-8")
        results["platforms"]["youtube"] = {
            "video": str(v_out),
            "video_size_bytes": v_out.stat().st_size,
            "title": str(p_dir / "title.txt"),
            "description": str(p_dir / "description.txt"),
            "tags": str(p_dir / "tags.txt")
        }
        print(f"   ✓ [YouTube 16:9] Đóng gói thành công -> {p_dir}")

    # Save packaging summary manifest
    summary_path = output_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 HOÀN THÀNH ĐÓNG GÓI! Báo cáo tổng hợp: {summary_path}\n")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", "-i", required=True, help="Input video file (.mp4) or project.json")
    parser.add_argument("--output", "-o", help="Output package directory (default: <parent>/package)")
    parser.add_argument("--platforms", default="tiktok,reels,shorts,youtube", help="Comma-separated platform keys")
    parser.add_argument("--title", help="Custom video title override")
    parser.add_argument("--description", help="Custom description override")
    parser.add_argument("--hashtags", help="Custom comma-separated hashtags override")
    args = parser.parse_args()

    custom_tags = [t.strip() for t in args.hashtags.split(",")] if args.hashtags else None
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]

    out_p = Path(args.output).resolve() if args.output else None
    package_platform_distribution(
        input_path=Path(args.input),
        output_dir=out_p,
        platforms=platforms,
        title_override=args.title,
        description_override=args.description,
        hashtags_override=custom_tags
    )


if __name__ == "__main__":
    main()
