#!/usr/bin/env python3
"""Motion Graphics Overlay & Dynamic Background Renderer for Stickman.

Bridges the 20 Reference Motion Styles from Claude Code Skill v3.5.2
(/Users/xitrum/Documents/Dev/library/Motion-graphics-skill-stack-store/20-reference-motion-styles)
into Stickman Video Director as dynamic backdrops and transparent effect overlays.

Key Concepts:
1. Dynamic Background:
   - Placed behind the stickman character to replace flat monochrome space with
     living, breathing visual worlds (e.g., technical blueprints, flowing gradient mesh,
     neon grids, 8-bit retro rooms).
2. Transparent Overlay:
   - Rendered with an alpha channel (WebM VP9 yuva420p / ProRes 4444) and layered
     over the scene with blending modes (Screen, Multiply, Overlay).
   - Examples: floating dust particles, CRT scanlines/noise, halftone printing dots,
     comic-book action speedlines.

Usage:
    # List all 20 motion styles:
    python3 scripts/motion-overlay-renderer.py --list

    # Render a dynamic background video:
    python3 scripts/motion-overlay-renderer.py --style blueprint --mode background \
        --duration 5.0 --output productions/assets/bg_blueprint.mp4

    # Render a transparent overlay (VHS scanlines / Particles):
    python3 scripts/motion-overlay-renderer.py --style retro-vhs --mode overlay \
        --duration 5.0 --output productions/assets/overlay_vhs.webm
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_LIBRARY_PATHS = [
    Path("/Users/xitrum/Documents/Dev/library/Motion-graphics-skill-stack-store/20-reference-motion-styles"),
    Path.home() / "Documents/Dev/library/Motion-graphics-skill-stack-store/20-reference-motion-styles",
    Path("D:/Video creator/Motion-graphics-skill-stack-store/20-reference-motion-styles")
]

MOTION_STYLES_CATALOG = {
    "motion-particles": {
        "id": "particles",
        "name": "Particles Swarm",
        "best_use": "overlay",
        "stickman_role": "Đốm sáng lơ lửng, bụi ma thuật, không gian lắng đọng hoặc suy ngẫm",
        "compatible_styles": ["B1", "B2", "B4"],
        "blend_mode": "screen"
    },
    "motion-retro-vhs": {
        "id": "retro-vhs",
        "name": "80s Retro VHS & CRT Scanlines",
        "best_use": "overlay",
        "stickman_role": "Sọc quét TV cổ điển, hạt nhiễu analog, cảnh hồi tưởng hoặc phóng sự điều tra",
        "compatible_styles": ["B3", "B4"],
        "blend_mode": "screen"
    },
    "motion-blueprint": {
        "id": "blueprint",
        "name": "Technical Blueprint Grid",
        "best_use": "background",
        "stickman_role": "Lưới tọa độ bản vẽ kỹ thuật màu xanh, phân tích logic, công nghệ, kiến trúc",
        "compatible_styles": ["B2", "B1"],
        "blend_mode": "normal"
    },
    "motion-neon-glow": {
        "id": "neon-glow",
        "name": "Flickering Cyber Neon",
        "best_use": "background",
        "stickman_role": "Bảng hiệu neon nhấp nháy trong đêm, không gian cyberpunk hoặc tiêu đề mở màn ấn tượng",
        "compatible_styles": ["B2", "B3"],
        "blend_mode": "screen"
    },
    "motion-comic-book": {
        "id": "comic-book",
        "name": "Comic Book Action Halftone",
        "best_use": "both",
        "stickman_role": "Khung tranh truyện tranh, tia hành động tốc độ, đòn đánh nổ tung, reaction meme",
        "compatible_styles": ["B1", "B6"],
        "blend_mode": "multiply"
    },
    "motion-kinetic-type": {
        "id": "kinetic-type",
        "name": "Kinetic Typography Motion",
        "best_use": "overlay",
        "stickman_role": "Chữ nảy TikTok, text chạy rượt đuổi, nhấn mạnh từ khóa đinh",
        "compatible_styles": ["B1", "B2", "B6"],
        "blend_mode": "normal"
    },
    "motion-wireframe-3d": {
        "id": "wireframe-3d",
        "name": "Wireframe 3D Perspective",
        "best_use": "background",
        "stickman_role": "Mô hình khung dây 3D xoay chiều, không gian ảo Metaverse hoặc tính toán số liệu",
        "compatible_styles": ["B2", "B4"],
        "blend_mode": "screen"
    },
    "motion-gradient-mesh": {
        "id": "gradient-mesh",
        "name": "Flowing Gradient Mesh",
        "best_use": "background",
        "stickman_role": "Sóng màu chuyển sắc pastel êm dịu, hiện đại, phong cách podcast/tâm sự",
        "compatible_styles": ["B2", "B5"],
        "blend_mode": "normal"
    },
    "motion-halftone": {
        "id": "halftone",
        "name": "Halftone Print Art",
        "best_use": "overlay",
        "stickman_role": "Hiệu ứng chấm in báo vintage, phóng sự ảnh, tạp chí báo chí",
        "compatible_styles": ["B1", "B3"],
        "blend_mode": "overlay"
    },
    "motion-pixel-art": {
        "id": "pixel-art",
        "name": "8-bit Retro Game Pixel",
        "best_use": "background",
        "stickman_role": "Thế giới game cổ điển 8-bit, vượt ải Mario, nhận thưởng XP, tình huống hài hước",
        "compatible_styles": ["B1", "B6"],
        "blend_mode": "normal"
    },
    "motion-liquid-morph": {
        "id": "liquid-morph",
        "name": "Iridescent Liquid Chrome",
        "best_use": "background",
        "stickman_role": "Khối chất lỏng biến hình, tư duy linh hoạt, sáng tạo không giới hạn",
        "compatible_styles": ["B2", "B5"],
        "blend_mode": "normal"
    },
    "motion-holographic": {
        "id": "holographic",
        "name": "Holographic Foil Ring",
        "best_use": "both",
        "stickman_role": "Vòng hào quang 3 chiều lấp lánh, bảo chứng chất lượng, huy hiệu chiến thắng",
        "compatible_styles": ["B2", "B4"],
        "blend_mode": "screen"
    },
    "motion-glassmorphism": {
        "id": "glassmorphism",
        "name": "Frosted Glass UI Widgets",
        "best_use": "overlay",
        "stickman_role": "Các thẻ thông tin kính mờ nổi bồng bềnh, bảng số liệu, biểu đồ công nghệ",
        "compatible_styles": ["B2", "B5"],
        "blend_mode": "normal"
    },
    "motion-isometric": {
        "id": "isometric",
        "name": "Isometric Block City",
        "best_use": "background",
        "stickman_role": "Thành phố khối lập phương 3D, bất động sản, tài chính, quy hoạch hệ thống",
        "compatible_styles": ["B2"],
        "blend_mode": "normal"
    },
    "motion-clay-3d": {
        "id": "clay-3d",
        "name": "Claymorphism 3D Toys",
        "best_use": "background",
        "stickman_role": "Đồ chơi đất nặn nảy bồng bềnh, vui nhộn, tâm lý học trẻ em",
        "compatible_styles": ["B1", "B5"],
        "blend_mode": "normal"
    },
    "motion-ascii-art": {
        "id": "ascii-art",
        "name": "Terminal ASCII Matrix",
        "best_use": "background",
        "stickman_role": "Màn hình hacker, ký tự mã lệnh rơi, an ninh mạng, lập trình viên",
        "compatible_styles": ["B2", "B4"],
        "blend_mode": "screen"
    },
    "motion-split-flap": {
        "id": "split-flap",
        "name": "Airport Split-Flap Board",
        "best_use": "both",
        "stickman_role": "Bảng lật số/chữ sân bay lách cách, lịch trình du lịch, đếm ngược sự kiện",
        "compatible_styles": ["B2", "B3"],
        "blend_mode": "normal"
    },
    "motion-bauhaus": {
        "id": "bauhaus",
        "name": "Bauhaus Geometric Grid",
        "best_use": "background",
        "stickman_role": "Hình học tối giản Bauhaus, tư duy thiết kế, nguyên lý cơ bản",
        "compatible_styles": ["B1", "B2"],
        "blend_mode": "normal"
    },
    "motion-art-deco": {
        "id": "art-deco",
        "name": "Art Deco Gold Reveal",
        "best_use": "background",
        "stickman_role": "Đường nét hoàng gia mạ vàng sang trọng, giới thượng lưu, giải thưởng",
        "compatible_styles": ["B4", "B3"],
        "blend_mode": "normal"
    },
    "motion-neo-brutalism": {
        "id": "neo-brutalism",
        "name": "Neo-Brutalism High Contrast",
        "best_use": "both",
        "stickman_role": "Đường viền đen dày, bóng đổ gắt 100%, màu neon pop-art gắt, Gen Z viral",
        "compatible_styles": ["B1", "B6"],
        "blend_mode": "normal"
    }
}


def find_motion_store_dir() -> Path | None:
    env_dir = os.environ.get("MOTION_STYLES_DIR")
    if env_dir and Path(env_dir).is_dir():
        return Path(env_dir).resolve()
    for p in DEFAULT_LIBRARY_PATHS:
        if p.is_dir():
            return p.resolve()
    return None


def generate_procedural_fallback_video(
    style_id: str,
    output_path: Path,
    width: int = 720,
    height: int = 1280,
    duration: float = 4.0,
    alpha: bool = False
) -> Path:
    """Generates procedural motion graphics using native FFmpeg filters (zero dependencies).
    
    Acts as a high-speed, zero-dependency engine when Playwright is unavailable.
    """
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Style-specific procedural generators
    if "retro-vhs" in style_id:
        # Scanlines, vignette and subtle analog drift
        vf = (
            f"color=c=#100c14:s={width}x{height}:d={duration},"
            f"drawgrid=w={width}:h=4:t=1:c=white@0.08,"
            f"noise=alls=12:allf=t+u,"
            f"vignette=PI/4"
        )
    elif "blueprint" in style_id:
        # Technical blue grid with moving coordinates
        vf = (
            f"color=c=#0a1d37:s={width}x{height}:d={duration},"
            f"drawgrid=w=40:h=40:t=1:c=cyan@0.22,"
            f"drawgrid=w=200:h=200:t=2:c=cyan@0.45"
        )
    elif "neon" in style_id:
        # Pulsing dark neon atmosphere
        vf = (
            f"color=c=#0d001a:s={width}x{height}:d={duration},"
            f"drawgrid=w=64:h=64:t=1:c=magenta@0.18,"
            f"vignette=PI/3"
        )
    elif "particles" in style_id:
        # Floating dust particles simulation
        vf = (
            f"color=c=black:s={width}x{height}:d={duration},"
            f"noise=c1s=35:c1f=t:allf=p,"
            f"threshold=threshold=220,"
            f"boxblur=2:1"
        )
    else:
        # Default modern ambient dark grid
        vf = (
            f"color=c=#14171a:s={width}x{height}:d={duration},"
            f"drawgrid=w=60:h=60:t=1:c=white@0.06,"
            f"vignette=PI/5"
        )

    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi", "-i", vf,
        "-t", str(duration)
    ]

    if alpha and output_path.suffix.lower() == ".webm":
        cmd += ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "28", str(output_path)]
    else:
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", str(output_path)]

    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def render_motion_template(
    style_name: str,
    output_path: Path,
    width: int = 720,
    height: int = 1280,
    duration: float = 4.0,
    alpha: bool = False,
    text: str = "",
    sub_text: str = ""
) -> Path:
    """Renders a motion template using Playwright, falling back to native procedural generation."""
    # Normalize style name (e.g. "blueprint" -> "motion-blueprint")
    canonical_style = style_name if style_name.startswith("motion-") else f"motion-{style_name}"
    store_dir = find_motion_store_dir()

    template_dir = store_dir / canonical_style if store_dir else None
    template_html = template_dir / "template.html" if template_dir else None

    # Check if Playwright is importable
    playwright_available = False
    try:
        import playwright  # noqa: F401
        playwright_available = True
    except ImportError:
        pass

    if playwright_available and template_html and template_html.is_file():
        render_script = template_dir / "render.py"
        cmd = [
            sys.executable, str(render_script),
            str(template_html), str(output_path),
            "--w", str(width), "--h", str(height),
            "--dur", str(duration)
        ]
        if alpha:
            cmd.append("--alpha")
        if text:
            cmd += ["--text", text]
        if sub_text:
            cmd += ["--sub", sub_text]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if output_path.exists() and output_path.stat().st_size > 1000:
                return output_path
        except Exception:
            pass

    # Fallback to high-speed native procedural generator
    return generate_procedural_fallback_video(
        canonical_style,
        output_path,
        width=width,
        height=height,
        duration=duration,
        alpha=alpha
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="List all 20 motion graphics templates and their roles")
    parser.add_argument("--style", default="blueprint", help="Motion style key (e.g. blueprint, retro-vhs, particles, neon-glow)")
    parser.add_argument("--mode", choices=["background", "overlay"], default="background", help="Render mode")
    parser.add_argument("--duration", type=float, default=4.0, help="Duration in seconds (default: 4.0)")
    parser.add_argument("--width", type=int, default=720, help="Canvas width (default: 720)")
    parser.add_argument("--height", type=int, default=1280, help="Canvas height (default: 1280)")
    parser.add_argument("--text", default="", help="Optional main text label inside template")
    parser.add_argument("--sub", default="", help="Optional secondary text label")
    parser.add_argument("--output", help="Output file path (.mp4 for background, .webm/.mov for alpha overlay)")
    args = parser.parse_args()

    store_dir = find_motion_store_dir()

    if args.list:
        print(f"STORE LOCATION: {store_dir or 'Not found (using native procedural fallbacks)'}\n")
        print("DANH SÁCH 20 PHONG CÁCH MOTION GRAPHICS TEMPLATES:")
        print("-" * 80)
        for key, info in MOTION_STYLES_CATALOG.items():
            best = info["best_use"].upper()
            styles_compat = ", ".join(info["compatible_styles"])
            print(f"[{info['id']:16s}] ({best:10s}) : {info['name']}")
            print(f"   * Vai trò Stickman: {info['stickman_role']}")
            print(f"   * Hợp với phong cách: {styles_compat} (Blend mode: {info['blend_mode']})\n")
        return

    if not args.output:
        ext = ".webm" if args.mode == "overlay" else ".mp4"
        out_p = Path(f"{args.style}_{args.mode}{ext}")
    else:
        out_p = Path(args.output).expanduser().resolve()

    alpha_flag = (args.mode == "overlay")
    res_path = render_motion_template(
        args.style,
        out_p,
        width=args.width,
        height=args.height,
        duration=args.duration,
        alpha=alpha_flag,
        text=args.text,
        sub_text=args.sub
    )
    print(json.dumps({
        "style": args.style,
        "mode": args.mode,
        "alpha": alpha_flag,
        "output": str(res_path.resolve()),
        "duration": args.duration,
        "resolution": f"{args.width}x{args.height}"
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
