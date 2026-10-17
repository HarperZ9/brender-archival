"""Check the display options of The Keeper's Hour on real frames.

    python games/keepers-hour/tools/display_check.py <keepers-hour> [--out result.json] [--opengl]
    python games/keepers-hour/tools/display_check.py <brview> --program brview [--opengl]

Draws stills headless, with no text or panels: the game's lamp room
(KEEPERS_SHOT, KEEPERS_PIXEL, KEEPERS_FOV), or brview's first model
(BRVIEW_SHOT, BRVIEW_PIXEL, BRVIEW_FOV). Both programs share the display
code in modern/display. It checks four claims. Each claim has a control that must fail, so a check that
passes everything is caught.

1. Whole pixels. At pixel size 4 in a 1280 x 720 window, every 4 x 4 block of
   the frame holds one colour. Control: at pixel size 1, most blocks hold more
   than one colour.
2. Pixel size changes the picture. The pixel size 4 frame differs from the
   pixel size 1 frame, and averaging the pixel size 1 frame over 4 x 4 blocks
   lands near the pixel size 4 frame (both draw the same scene).
3. Widescreen is Hor+, at three window shapes. The field of view is vertical,
   so a 1280 x 720 frame (16:9) holds the 960 x 720 frame (4:3) in its middle
   960 columns, and a 1680 x 720 frame (21:9) holds the 1280 x 720 frame in
   its middle 1280 columns. Control: a 960 x 720 frame at another field of
   view does not match.
4. Field of view changes the picture: 40 and 90 degrees differ.
5. The period look (software only) draws in 256 colours or fewer, through
   BRender's 8-bit path, and shows the same scene. Controls: the period frame
   is not the true-colour frame (the 8-bit path ran), and the true-colour
   frame of the same scene uses more than 256 colours. (brview's earth drew
   unlit in software with 100 colours until 17 October 2026, when brview
   gained a shade table; it now measures 987.)

--stills DIR keeps the period and true-colour stills (as PPM) for a look.

The software rasteriser is the default because it gives the same bytes on
every run. --opengl uses the OpenGL driver instead. Standard library only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HORPLUS_MATCH_MIN = 0.98   # share of middle-column pixels within 8 levels
HORPLUS_CONTROL_MAX = 0.90  # the control must match less than this
BLOCK_UNIFORM_MIN = 1.0     # pixel size 4: every block one colour
BLOCK_CONTROL_MAX = 0.95    # pixel size 1: at most this share of blocks one colour.
# 0.80 at first; raised on 16 October 2026 after measuring brview, whose flat
# background leaves 83% of blocks uniform at pixel size 1 (the game: 61% to
# 63%). Calibrated, not predicted; the pixel size 4 frame must still be 100%.
DOWNSAMPLE_MAD_MAX = 24.0   # mean absolute difference, block mean against pixel size 4


def read_ppm(path: Path):
    parts = path.read_bytes().split(b"\n", 3)
    w, h = (int(v) for v in parts[1].split())
    return w, h, parts[3]


PREFIX = "KEEPERS"


PERIOD_COLOURS_MAX = 256     # an 8-bit frame
PERIOD_SCENE_MAD_MAX = 30.0  # period against true colour, mean level difference. Measured 16 October
# 2026: 10.5 (the game, lamp room) and 24.0 (brview, earth; 19.5 once lit
# through a shade table on 17 October; its background
# differs too). Calibrated, not predicted.


def still(exe: str, out: Path, width: int, height: int, pixel: int, fov: int, opengl: bool, period: bool = False):
    env = dict(os.environ, **{f"{PREFIX}_SHOT": str(out), f"{PREFIX}_PIXEL": str(pixel), f"{PREFIX}_FOV": str(fov)})
    env[f"{PREFIX}_PERIOD"] = "1" if period else "0"
    if PREFIX == "KEEPERS":
        env["KEEPERS_ROOM"] = "lamp"
    args = [exe, "-w", str(width), "-h", str(height)] + ([] if opengl else ["--force-software"])
    subprocess.run(args, env=env, check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    img = read_ppm(out)
    if img[:2] != (width, height):
        raise SystemExit(f"{out.name}: expected {width}x{height}, got {img[0]}x{img[1]}")
    return img


def uniform_blocks(img, k: int) -> float:
    w, h, px = img
    total = same = 0
    for by in range(0, h - k + 1, k):
        for bx in range(0, w - k + 1, k):
            first = px[3 * (by * w + bx): 3 * (by * w + bx) + 3]
            ok = all(px[3 * ((by + y) * w + bx + x): 3 * ((by + y) * w + bx + x) + 3] == first
                     for y in range(k) for x in range(k))
            total += 1
            same += ok
    return same / total


def block_mean_mad(sharp, chunky, k: int) -> float:
    w, h, a = sharp
    b = chunky[2]
    diff = count = 0
    for by in range(0, h - k + 1, k):
        for bx in range(0, w - k + 1, k):
            for c in range(3):
                mean = sum(a[3 * ((by + y) * w + bx + x) + c] for y in range(k) for x in range(k)) / (k * k)
                diff += abs(mean - b[3 * (by * w + bx) + c])
                count += 1
    return diff / count


def colours(img) -> int:
    px = img[2]
    return len({px[i:i + 3] for i in range(0, len(px), 3)})


def mad(a, b) -> float:
    return sum(abs(x - y) for x, y in zip(a[2], b[2])) / len(a[2])


def middle_match(wide, narrow) -> float:
    ww, h, a = wide
    nw, _, b = narrow
    off = (ww - nw) // 2
    near = 0
    for y in range(h):
        for x in range(nw):
            i, j = 3 * (y * ww + x + off), 3 * (y * nw + x)
            near += max(abs(a[i + c] - b[j + c]) for c in range(3)) <= 8
    return near / (nw * h)


def main(argv: list[str]) -> int:
    global PREFIX
    exe = argv[1]
    if "--program" in argv:
        PREFIX = {"keepers-hour": "KEEPERS", "brview": "BRVIEW"}[argv[argv.index("--program") + 1]]
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    opengl = "--opengl" in argv
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        sharp = still(exe, t / "p1.ppm", 1280, 720, 1, 55, opengl)
        chunky = still(exe, t / "p4.ppm", 1280, 720, 4, 55, opengl)
        narrow = still(exe, t / "n.ppm", 960, 720, 1, 55, opengl)
        ultra = still(exe, t / "u.ppm", 1680, 720, 1, 55, opengl)
        narrow_other = still(exe, t / "n70.ppm", 960, 720, 1, 70, opengl)
        fov40 = still(exe, t / "f40.ppm", 1280, 720, 1, 40, opengl)
        fov90 = still(exe, t / "f90.ppm", 1280, 720, 1, 90, opengl)
        period = None if opengl else still(exe, t / "period.ppm", 1280, 720, 1, 55, opengl, period=True)
        if "--stills" in argv:
            keep = Path(argv[argv.index("--stills") + 1])
            keep.mkdir(parents=True, exist_ok=True)
            name = "brview" if PREFIX == "BRVIEW" else "keepers-hour"
            for src, tag in ((t / "p1.ppm", "true-colour"), (t / "period.ppm", "period"), (t / "p4.ppm", "pixel4")):
                if src.exists():
                    (keep / f"{name}-{'opengl' if opengl else 'software'}-{tag}.ppm").write_bytes(src.read_bytes())
    m = {
        "program": "brview" if PREFIX == "BRVIEW" else "keepers-hour",
        "renderer": "opengl" if opengl else "software",
        "blocks_uniform_pixel4": round(uniform_blocks(chunky, 4), 4),
        "blocks_uniform_pixel1_control": round(uniform_blocks(sharp, 4), 4),
        "pixel4_differs_from_pixel1": sharp[2] != chunky[2],
        "pixel1_block_mean_vs_pixel4_mad": round(block_mean_mad(sharp, chunky, 4), 3),
        "horplus_middle_match": round(middle_match(sharp, narrow), 4),
        "horplus_ultrawide_match": round(middle_match(ultra, sharp), 4),
        "horplus_control_fov70": round(middle_match(sharp, narrow_other), 4),
        "fov40_differs_from_fov90": fov40[2] != fov90[2],
    }
    if period is not None:
        m["period_colours"] = colours(period)
        m["true_colour_colours_control"] = colours(sharp)
        m["period_vs_true_colour_mad"] = round(mad(period, sharp), 3)
    checks = {
        "whole_pixels": m["blocks_uniform_pixel4"] >= BLOCK_UNIFORM_MIN,
        "whole_pixels_control_fails": m["blocks_uniform_pixel1_control"] <= BLOCK_CONTROL_MAX,
        "pixel_size_changes_picture": m["pixel4_differs_from_pixel1"],
        "same_scene_at_both_sizes": m["pixel1_block_mean_vs_pixel4_mad"] <= DOWNSAMPLE_MAD_MAX,
        "widescreen_is_horplus": m["horplus_middle_match"] >= HORPLUS_MATCH_MIN,
        "ultrawide_is_horplus": m["horplus_ultrawide_match"] >= HORPLUS_MATCH_MIN,
        "horplus_control_fails": m["horplus_control_fov70"] < HORPLUS_CONTROL_MAX,
        "fov_changes_picture": m["fov40_differs_from_fov90"],
    }
    if period is not None:
        checks["period_is_256_colours"] = m["period_colours"] <= PERIOD_COLOURS_MAX
        checks["period_path_used"] = period[2] != sharp[2]
        checks["period_control_fails"] = m["true_colour_colours_control"] > PERIOD_COLOURS_MAX
        checks["period_same_scene"] = 0 < m["period_vs_true_colour_mad"] <= PERIOD_SCENE_MAD_MAX
    result = {"measured": m, "checks": checks, "ok": all(checks.values())}
    text = json.dumps(result, indent=2)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8")
    print(f"{m['program']} display: {sum(checks.values())} of {len(checks)} checks pass")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
