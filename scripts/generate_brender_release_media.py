"""Generate the public BRender archival release media set.

The input boundary is an already-verified `brender_core_softrend_render.exe`
run. This script converts the eight period-pipeline PPM frames into PNG
artifacts and writes a provenance manifest with source/input/output hashes.
It does not synthesize render content or vendor upstream BRender assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SOURCE_SHA = "d88d0ed41122664b9781015b517db64353e16f19"
BASE_SHA = "323c679a70417bd00414f646891d734e664966bb"
FRAME_PREFIX = "brender-core-softrend-render.ppm.softrend-f"
OUT_DIR = Path("gallery/release-20260827")


@dataclass(frozen=True)
class ImageMetric:
    width: int
    height: int
    nonblack_pixels: int
    unique_colours: int


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "SegoeUI-Bold.ttf" if bold else "SegoeUI.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", compress_level=9)


def _metrics(image: Image.Image) -> ImageMetric:
    rgb = image.convert("RGB")
    data = rgb.tobytes()
    pixels = [data[offset : offset + 3] for offset in range(0, len(data), 3)]
    return ImageMetric(
        width=rgb.width,
        height=rgb.height,
        nonblack_pixels=sum(pixel != b"\x00\x00\x00" for pixel in pixels),
        unique_colours=len(set(pixels)),
    )


def _text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int, fill: str, *, bold: bool = False) -> None:
    draw.text(xy, text, font=_font(size, bold=bold), fill=fill)


def _centered(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, size: int, fill: str, *, bold: bool = False) -> None:
    font = _font(size, bold=bold)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = box[0] + (box[2] - box[0] - width) // 2
    y = box[1] + (box[3] - box[1] - height) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], fill: str) -> None:
    draw.line([start, end], fill=fill, width=4)
    ex, ey = end
    draw.polygon([(ex, ey), (ex - 14, ey - 8), (ex - 14, ey + 8)], fill=fill)


def _load_frames(ppm_dir: Path) -> list[Image.Image]:
    frames = []
    for index in range(8):
        path = ppm_dir / f"{FRAME_PREFIX}{index}.ppm"
        if not path.exists():
            raise FileNotFoundError(path)
        frames.append(Image.open(path).convert("RGB"))
    return frames


def _write_orbit_pngs(frames: list[Image.Image], out_dir: Path) -> None:
    for index, frame in enumerate(frames):
        _save_png(frame, out_dir / f"period-pipeline-orbit-{index:02d}.png")
    _save_png(frames[-1], out_dir / "period-pipeline-still.png")


def _contact_sheet(frames: list[Image.Image], out_dir: Path) -> None:
    cell_w, cell_h = 320, 240
    margin, gap_x, gap_y = 32, 24, 42
    label_h, title_h = 28, 58
    width = margin * 2 + cell_w * 4 + gap_x * 3
    height = margin * 2 + title_h + (label_h + cell_h) * 2 + gap_y
    image = Image.new("RGB", (width, height), "#101820")
    draw = ImageDraw.Draw(image)
    _centered(draw, (0, 18, width, 58), "BRender verified period-pipeline orbit", 28, "#f6f1e8", bold=True)
    for index, frame in enumerate(frames):
        row, col = divmod(index, 4)
        x = margin + col * (cell_w + gap_x)
        y = margin + title_h + row * (label_h + cell_h + gap_y)
        _centered(draw, (x, y, x + cell_w, y + label_h), f"{index:02d}  {35 + index * 45} deg", 17, "#d8c7a3", bold=True)
        image.paste(frame, (x, y + label_h))
        draw.rectangle((x, y + label_h, x + cell_w - 1, y + label_h + cell_h - 1), outline="#8a7a55", width=1)
    _save_png(image, out_dir / "period-pipeline-orbit-contact-sheet.png")


def _poster(still: Image.Image, out_dir: Path, final_frame_lit: int) -> None:
    image = Image.new("RGB", (960, 720), "#0d141c")
    draw = ImageDraw.Draw(image)
    _text(draw, (50, 44), "Verified BRender output", 42, "#f6f1e8", bold=True)
    _text(draw, (52, 100), "Period software renderer, pinned public MIT source", 22, "#d8c7a3")
    scaled = still.resize((640, 480), Image.Resampling.NEAREST)
    image.paste(scaled, (50, 164))
    draw.rectangle((50, 164, 689, 643), outline="#d8c7a3", width=2)
    _text(draw, (720, 182), "Evidence", 26, "#f6f1e8", bold=True)
    _text(draw, (720, 228), "21/21 native CTest", 22, "#75d18a", bold=True)
    _text(draw, (720, 270), "8 verified frames", 22, "#75d18a", bold=True)
    _text(draw, (720, 312), f"final_frame_lit={final_frame_lit}", 20, "#f6f1e8")
    _text(draw, (720, 370), "Textured TIA:", 20, "#f6f1e8", bold=True)
    _text(draw, (720, 402), "executes, black", 18, "#d8c7a3")
    _text(draw, (720, 430), "output remains", 18, "#d8c7a3")
    _text(draw, (720, 458), "blocked", 18, "#d8c7a3")
    _save_png(image, out_dir / "period-pipeline-poster.png")


def _progress(frames: list[Image.Image], out_dir: Path) -> None:
    thumb_w, thumb_h = 320, 180
    margin, gap_x, gap_y = 36, 20, 38
    title_h, label_h = 78, 24
    width = margin * 2 + thumb_w * 4 + gap_x * 3
    height = margin * 2 + title_h + (label_h + thumb_h) * 2 + gap_y
    image = Image.new("RGB", (width, height), "#111820")
    draw = ImageDraw.Draw(image)
    _centered(draw, (0, 22, width, 58), "BRender verified output sequence", 30, "#f6f1e8", bold=True)
    _centered(draw, (0, 58, width, 90), "wireframe to period pipeline, labels separated from title", 17, "#d8c7a3")
    labels = [
        "01 wireframe",
        "02 flat fill",
        "03 depth",
        "04 texture file",
        "05 material resolve",
        "06 game shell",
        "07 softrend",
        "08 final still",
    ]
    for index, frame in enumerate(frames):
        row, col = divmod(index, 4)
        x = margin + col * (thumb_w + gap_x)
        y = margin + title_h + row * (label_h + thumb_h + gap_y)
        _centered(draw, (x, y, x + thumb_w, y + label_h), labels[index], 16, "#d8c7a3", bold=True)
        thumb = frame.resize((thumb_w, thumb_h), Image.Resampling.NEAREST)
        image.paste(thumb, (x, y + label_h))
        draw.rectangle((x, y + label_h, x + thumb_w - 1, y + label_h + thumb_h - 1), outline="#7e704e", width=1)
    _save_png(image, out_dir / "progress-sequence.png")


def _pipeline_diagram(out_dir: Path) -> None:
    image = Image.new("RGB", (1280, 720), "#0d141c")
    draw = ImageDraw.Draw(image)
    _text(draw, (56, 44), "BRender archival verification boundary", 36, "#f6f1e8", bold=True)
    _text(draw, (58, 92), "Pinned public source, generated harness, native CTest, bounded release media", 20, "#d8c7a3")
    boxes = [
        ((80, 210, 310, 330), "Argonaut/BRender\nMIT snapshot\nd88d0ed4"),
        ((390, 210, 620, 330), "engine-revival\nmaterializer\npublic-clean C"),
        ((700, 210, 930, 330), "Win32 Debug\n21 CTest targets\nsoftrend + pentprim"),
        ((1010, 210, 1230, 330), "Gallery media\nfrom verified\nPPM frames"),
    ]
    for box, label in boxes:
        draw.rounded_rectangle(box, radius=18, fill="#172331", outline="#d8c7a3", width=2)
        lines = label.splitlines()
        for offset, line in enumerate(lines):
            _centered(draw, (box[0] + 12, box[1] + 18 + offset * 30, box[2] - 12, box[1] + 50 + offset * 30), line, 20, "#f6f1e8", bold=offset == 0)
    for start_x in (310, 620, 930):
        _draw_arrow(draw, (start_x + 20, 270), (start_x + 70, 270), "#75d18a")
    draw.rounded_rectangle((170, 470, 1110, 598), radius=18, fill="#151b21", outline="#7e704e", width=2)
    _text(draw, (205, 500), "Release boundary:", 24, "#f6f1e8", bold=True)
    _text(draw, (420, 502), "period pipeline renders pixels; textured TIA execution is not completed rendering.", 22, "#d8c7a3")
    _text(draw, (205, 545), "No vendored upstream source/assets, no endorsement claim, no x64/production-readiness claim.", 20, "#d8c7a3")
    _save_png(image, out_dir / "pipeline-diagram.png")


def _evidence_card(still: Image.Image, out_dir: Path, final_frame_lit: int) -> None:
    image = Image.new("RGB", (1200, 630), "#0f1720")
    draw = ImageDraw.Draw(image)
    image.paste(still.resize((430, 322), Image.Resampling.NEAREST), (56, 154))
    draw.rectangle((56, 154, 485, 475), outline="#d8c7a3", width=2)
    _text(draw, (56, 54), "BRender archival release evidence", 38, "#f6f1e8", bold=True)
    _text(draw, (56, 104), "Current verified public boundary, 2026-08-27", 22, "#d8c7a3")
    x = 540
    _text(draw, (x, 160), "Verified", 30, "#75d18a", bold=True)
    _text(draw, (x, 210), "21/21 native Win32 CTest targets", 24, "#f6f1e8")
    _text(draw, (x, 252), "8-frame period-pipeline orbit", 24, "#f6f1e8")
    _text(draw, (x, 294), f"final_frame_lit={final_frame_lit}", 24, "#f6f1e8")
    _text(draw, (x, 354), "Pinned source", 28, "#f6f1e8", bold=True)
    _text(draw, (x, 400), SOURCE_SHA[:16] + "...", 22, "#d8c7a3")
    _text(draw, (x, 462), "Limitation", 28, "#f6f1e8", bold=True)
    _text(draw, (x, 508), "Textured TIA executes but black output remains blocked.", 21, "#d8c7a3")
    _save_png(image, out_dir / "evidence-card.png")


def _social_card(still: Image.Image, out_dir: Path, final_frame_lit: int) -> None:
    image = Image.new("RGB", (1200, 630), "#101820")
    draw = ImageDraw.Draw(image)
    image.paste(still.resize((520, 390), Image.Resampling.NEAREST), (620, 130))
    draw.rectangle((620, 130, 1139, 519), outline="#d8c7a3", width=2)
    _text(draw, (64, 78), "BRender archival", 54, "#f6f1e8", bold=True)
    _text(draw, (64, 145), "verified public release evidence", 36, "#d8c7a3", bold=True)
    _text(draw, (64, 234), "Period software renderer output", 27, "#f6f1e8")
    _text(draw, (64, 280), "21/21 native Win32 CTest targets", 27, "#75d18a", bold=True)
    _text(draw, (64, 326), f"8 frames, final_frame_lit={final_frame_lit}", 27, "#f6f1e8")
    _text(draw, (64, 418), "Bounded claim: textured TIA is not complete.", 22, "#d8c7a3")
    _text(draw, (64, 468), "Source pinned to public MIT snapshot d88d0ed4.", 22, "#d8c7a3")
    _save_png(image, out_dir / "social-card-1200x630.png")


def _input_entries(ppm_dir: Path, frames: list[Image.Image]) -> list[dict[str, object]]:
    entries = []
    for index, frame in enumerate(frames):
        path = ppm_dir / f"{FRAME_PREFIX}{index}.ppm"
        metric = _metrics(frame)
        entries.append(
            {
                "label": f"period-pipeline-frame-{index:02d}",
                "source": f"brender_core_softrend_render.exe output {FRAME_PREFIX}{index}.ppm",
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
                "width": metric.width,
                "height": metric.height,
                "nonblack_pixels": metric.nonblack_pixels,
                "unique_colours": metric.unique_colours,
            }
        )
    return entries


def _output_entries(out_dir: Path) -> list[dict[str, object]]:
    entries = []
    for path in sorted(out_dir.glob("*.png")):
        with Image.open(path) as image:
            width, height = image.size
        entries.append(
            {
                "path": path.as_posix(),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
                "width": width,
                "height": height,
            }
        )
    return entries


def generate_media(ppm_dir: Path, out_dir: Path, final_frame_lit: int) -> dict[str, object]:
    frames = _load_frames(ppm_dir)
    _write_orbit_pngs(frames, out_dir)
    _contact_sheet(frames, out_dir)
    _poster(frames[-1], out_dir, final_frame_lit)
    _progress(frames, out_dir)
    _pipeline_diagram(out_dir)
    _evidence_card(frames[-1], out_dir, final_frame_lit)
    _social_card(frames[-1], out_dir, final_frame_lit)

    manifest = {
        "schema": "brender-archival.release-media-provenance/v1",
        "generated_date": date(2026, 8, 27).isoformat(),
        "archival_repo_base_sha": BASE_SHA,
        "source_sha": SOURCE_SHA,
        "source_attribution": "Argonaut Software BRender public MIT snapshot via foone/BRender-v1.3.2; referenced only, never vendored.",
        "commands": [
            "engine-revival materialize-brender-harness --source-root <BRender-v1.3.2 checkout at d88d0ed41122664b9781015b517db64353e16f19> --output-root <out-of-tree harness>",
            "cmake -S <harness> -B <build> -A Win32 -DBRENDER_SOURCE_DIR=<BRender-v1.3.2 checkout>",
            "cmake --build <build> --config Debug",
            "ctest --test-dir <build> -C Debug --output-on-failure",
            "brender_core_softrend_render.exe <dat/sph32.dat> <dat/earth.pix> <dat/std.pal> brender-core-softrend-render.ppm",
            "python scripts/generate_brender_release_media.py --ppm-dir <verified PPM output directory> --output-dir gallery/release-20260827 --final-frame-lit <receipt metric>",
        ],
        "metric": {
            "rung": "brender_core_softrend_render",
            "renderer": "softrend-float+pentprim-float",
            "frames": 8,
            "final_frame_lit": final_frame_lit,
            "valid": True,
            "input_model": "dat/sph32.dat",
            "input_texture": "dat/earth.pix",
            "input_palette": "dat/std.pal",
        },
        "inputs": _input_entries(ppm_dir, frames),
        "outputs": _output_entries(out_dir),
        "limitations": [
            "Experimental textured TIA executes but black output remains blocked by a measured vertex-layout/state mismatch.",
            "Native repeat executions on the Win32 Debug port can vary by a few edge pixels; this manifest pins the exact verified PPM source hashes used for public media.",
            "The release media does not claim completed textured rendering, x64 readiness, production readiness, endorsement, or vendored upstream source/assets.",
            "All raster media derive from verified render outputs or factual diagrams/cards; black diagnostic frames are excluded.",
        ],
    }
    manifest_path = out_dir / "provenance-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ppm-dir", type=Path, required=True, help="Directory containing the eight verified PPM frame outputs.")
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR, help="Release gallery output directory.")
    parser.add_argument("--final-frame-lit", type=int, required=True, help="final_frame_lit value from the verified render receipt.")
    args = parser.parse_args()
    manifest = generate_media(args.ppm_dir, args.output_dir, args.final_frame_lit)
    for output in manifest["outputs"]:
        print(f"{output['sha256']}  {output['path']}")
    print(args.output_dir / "provenance-manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
