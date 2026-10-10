"""Does The Keeper's Hour draw the same scene on OpenGL and on BRender's
software rasteriser? Draw a still of every room both ways and compare.

    python games/keepers-hour/tools/parity.py <keepers-hour.exe> [--out evidence.json]

Needs a machine with OpenGL (the CI runners have none), so it runs locally and
its result is committed as evidence. Standard library only.

The two renderers light differently (the OpenGL driver lights per pixel; the
1990s rasteriser does not), so exact equality is not the claim. The claim is
that both draw the same scene: the same shapes in the same places.

How the bounds were set, in order (2026-10-10):
1. First bounds, fixed before measuring: silhouette IoU >= 0.95, mean absolute
   difference <= 24, 75% of pixels within 48 in luminance. All five rooms
   passed, and so did a wrong-room control (the lamp room on OpenGL against
   the radio room in software). Those bounds could not tell rooms apart, so
   they are kept only as information.
2. The verdict now rests on edges: the correlation of luminance gradients on a
   64 x 36 grid. Measured: same room 0.78 to 0.86; wrong rooms 0.04 to 0.73.
   The bound 0.76 sits in that gap. It was chosen after seeing these numbers,
   so it is a calibrated bound, not a pre-registered one, and the margin is
   small (0.73 against 0.76 for the radio room and the keeper's room, which
   share a layout).
3. Every run repeats the control: every wrong-room pair must fail.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOMS = ["lamp", "stairs", "radio", "keeper", "gallery"]
EDGE_CORRELATION_MIN = 0.76
SILHOUETTE_IOU_MIN = 0.95
SKY = {"gallery": (10, 14, 30)}
DEFAULT_SKY = (6, 7, 12)
GRID = (64, 36)


def read_ppm(path: Path):
    parts = path.read_bytes().split(b"\n", 3)
    w, h = (int(v) for v in parts[1].split())
    return w, h, parts[3]


def still(exe: str, room: str, out: Path, software: bool) -> None:
    env = dict(os.environ, KEEPERS_ROOM=room, KEEPERS_SHOT=str(out))
    args = [exe] + (["--force-software"] if software else [])
    subprocess.run(args, env=env, check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def luma_grid(img) -> list[float]:
    w, h, px = img
    gw, gh = GRID
    out = []
    for gy in range(gh):
        for gx in range(gw):
            total = count = 0
            for y in range(gy * h // gh, (gy + 1) * h // gh, 4):
                for x in range(gx * w // gw, (gx + 1) * w // gw, 4):
                    i = 3 * (y * w + x)
                    total += 0.299 * px[i] + 0.587 * px[i + 1] + 0.114 * px[i + 2]
                    count += 1
            out.append(total / count)
    return out


def edges(g: list[float]) -> list[float]:
    gw, gh = GRID
    return [abs(g[y * gw + x + 1] - g[y * gw + x]) + abs(g[(y + 1) * gw + x] - g[y * gw + x])
            for y in range(gh - 1) for x in range(gw - 1)]


def correlation(a: list[float], b: list[float]) -> float:
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else 0.0


def silhouette_iou(a, b, sky) -> float:
    pa, pb = a[2], b[2]
    union = inter = 0
    for i in range(0, len(pa), 3):
        sa = max(abs(pa[i + k] - sky[k]) for k in range(3)) > 6
        sb = max(abs(pb[i + k] - sky[k]) for k in range(3)) > 6
        union += sa or sb
        inter += sa and sb
    return inter / union if union else 1.0


def main(argv: list[str]) -> int:
    exe = argv[0]
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    with tempfile.TemporaryDirectory() as tmp:
        imgs = {}
        for room in ROOMS:
            for kind, software in (("gl", False), ("sw", True)):
                path = Path(tmp) / f"{room}-{kind}.ppm"
                still(exe, room, path, software)
                imgs[(room, kind)] = read_ppm(path)
    e = {key: edges(luma_grid(img)) for key, img in imgs.items()}
    rooms, control = {}, {}
    for room in ROOMS:
        corr = correlation(e[(room, "gl")], e[(room, "sw")])
        iou = silhouette_iou(imgs[(room, "gl")], imgs[(room, "sw")], SKY.get(room, DEFAULT_SKY))
        rooms[room] = {"edge_correlation": round(corr, 3), "silhouette_iou": round(iou, 4),
                       "pass": corr >= EDGE_CORRELATION_MIN and iou >= SILHOUETTE_IOU_MIN}
        for other in ROOMS:
            if other != room:
                control[f"{room}-gl/{other}-sw"] = round(correlation(e[(room, "gl")], e[(other, "sw")]), 3)
    control_ok = all(v < EDGE_CORRELATION_MIN for v in control.values())
    result = {
        "bounds": {"edge_correlation_min": EDGE_CORRELATION_MIN, "silhouette_iou_min": SILHOUETTE_IOU_MIN,
                   "calibrated": "after seeing the 2026-10-10 measurements; see the module docstring"},
        "rooms": rooms,
        "wrong_room_control": {"max": max(control.values()), "all_fail": control_ok, "pairs": control},
        "pass": control_ok and all(r["pass"] for r in rooms.values()),
    }
    for room, m in rooms.items():
        print(room, m)
    print("wrong-room control: max", result["wrong_room_control"]["max"], "all fail" if control_ok else "SOME PASS")
    print("parity", "pass" if result["pass"] else "fail")
    if out:
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
