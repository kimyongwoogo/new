#!/usr/bin/env python3
"""Convert an HTML file into an MP4 video by rendering it in a browser.

The script loads a local HTML file in Playwright, captures frame-by-frame screenshots,
and then stitches those frames into an MP4 with ffmpeg.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

def parse_size(size_text: str) -> tuple[int, int]:
    """Parse viewport size strings such as 1280x720."""
    if "x" not in size_text:
        raise ValueError("화면 크기는 WIDTHxHEIGHT 형식이어야 합니다. 예: 1280x720")

    width_text, height_text = size_text.lower().split("x", maxsplit=1)
    width = int(width_text)
    height = int(height_text)

    if width <= 0 or height <= 0:
        raise ValueError("WIDTH와 HEIGHT는 1 이상의 정수여야 합니다.")

    return width, height


def ensure_dependencies() -> None:
    """Validate external binary dependencies."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg를 찾을 수 없습니다. ffmpeg를 설치 후 다시 실행해주세요.")


def capture_frames(
    html_file: Path,
    frame_dir: Path,
    width: int,
    height: int,
    fps: int,
    duration: float,
    wait_before_capture: float,
) -> int:
    """Capture frames from the rendered page and save PNG images."""
    frame_count = max(1, round(duration * fps))
    frame_interval_ms = 1000 / fps

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()

        page.goto(html_file.resolve().as_uri(), wait_until="networkidle")
        if wait_before_capture > 0:
            page.wait_for_timeout(wait_before_capture * 1000)

        for index in range(frame_count):
            out_file = frame_dir / f"frame_{index:06d}.png"
            page.screenshot(path=str(out_file))
            page.wait_for_timeout(frame_interval_ms)

        context.close()
        browser.close()

    return frame_count


def run_ffmpeg(frame_dir: Path, fps: int, output_file: Path, quality: int) -> None:
    """Encode image sequence to MP4 via ffmpeg."""
    input_pattern = frame_dir / "frame_%06d.png"

    command: Iterable[str] = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(input_pattern),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        str(quality),
        str(output_file),
    ]

    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "ffmpeg 인코딩에 실패했습니다.\n"
            f"명령어: {' '.join(command)}\n"
            f"stderr:\n{result.stderr.strip()}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HTML 파일을 MP4 영상으로 변환합니다.")
    parser.add_argument("html", type=Path, help="입력 HTML 파일 경로")
    parser.add_argument("output", type=Path, help="출력 MP4 파일 경로")
    parser.add_argument("--size", default="1280x720", help="영상 해상도 (기본값: 1280x720)")
    parser.add_argument("--fps", type=int, default=30, help="프레임레이트 (기본값: 30)")
    parser.add_argument("--duration", type=float, default=5.0, help="영상 길이(초) (기본값: 5)")
    parser.add_argument(
        "--wait-before-capture",
        type=float,
        default=0.5,
        help="촬영 시작 전 대기 시간(초) (기본값: 0.5)",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=20,
        help="ffmpeg libx264 품질(CRF, 낮을수록 고화질) (기본값: 20)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.html.exists():
        parser.error(f"입력 파일이 존재하지 않습니다: {args.html}")

    if args.fps <= 0:
        parser.error("--fps 는 1 이상의 정수여야 합니다.")

    if args.duration <= 0:
        parser.error("--duration 은 0보다 커야 합니다.")

    if not 0 <= args.crf <= 51:
        parser.error("--crf 값은 0~51 범위여야 합니다.")

    try:
        width, height = parse_size(args.size)
        ensure_dependencies()

        args.output.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="html2mp4_") as tmpdir:
            frame_dir = Path(tmpdir)
            frame_count = capture_frames(
                html_file=args.html,
                frame_dir=frame_dir,
                width=width,
                height=height,
                fps=args.fps,
                duration=args.duration,
                wait_before_capture=args.wait_before_capture,
            )
            run_ffmpeg(frame_dir=frame_dir, fps=args.fps, output_file=args.output, quality=args.crf)

        print(f"완료: {args.output} ({frame_count} 프레임)")
        return 0

    except Exception as exc:  # noqa: BLE001
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
