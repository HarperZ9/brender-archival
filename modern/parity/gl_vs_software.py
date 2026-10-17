"""Does BRender 1.4's OpenGL driver draw the same pixels as its software
rasteriser? Draw every brview model both ways and compare.

    python modern/parity/gl_vs_software.py <brview> [--out result.json] [--stills DIR]
        [--bounds-unlit IOU SAME MAD] [--bounds-textured IOU SAME MAD] [--require-identical-runs]

Needs OpenGL: CI runs it on Linux with Mesa's llvmpipe (SDL_VIDEODRIVER=offscreen).
Each still is brview's BRVIEW_SHOT of one model (BRVIEW_SCENE), 640 x 480, at
the default view. Three classes, because the two renderers light differently
(the OpenGL driver lights per pixel, the software rasteriser per vertex):

- unlit: no lighting, no texture (BRVIEW_UNLIT=1, BRVIEW_TEXTURE=0). Each model
  is one flat colour, so the comparison isolates coverage: which pixels each
  renderer fills. "identical" counts pixels whose channels all agree within 2.
- textured: no lighting, with the model's texture (the earth and the torus).
  This adds texture sampling.
- lit: brview's normal look. Reported, not bounded: per-pixel against
  per-vertex lighting is a known, intended difference.

Per scene: coverage IoU (pixels that differ from the background colour, read
from the top-left corner, in both frames over either), identical share and
MAD over those pixels, and the largest channel difference. The control
compares OpenGL's unlit first model against the software unlit second model;
it must come out unlike (coverage IoU under 0.9). --require-identical-runs
draws the OpenGL stills twice and requires the same bytes. Standard library
only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

W, H = 640, 480
SCENES = {0: "earth", 1: "teapot", 2: "skull", 3: "argo", 4: "ship", 5: "duck", 6: "torus", 7: "terrain"}
TEXTURED = (0, 6)
NEAR = 2               # "identical" tolerance per channel, in levels
CONTROL_IOU_MAX = 0.9


def read_ppm(path: Path):
    parts = path.read_bytes().split(b"\n", 3)
    w, h = (int(v) for v in parts[1].split())
    return w, h, parts[3]


def still(exe: str, out: Path, scene: int, kind: str, opengl: bool):
    env = dict(os.environ, BRVIEW_SHOT=str(out), BRVIEW_SCENE=str(scene), BRVIEW_PERIOD="0",
               BRVIEW_UNLIT="0" if kind == "lit" else "1", BRVIEW_TEXTURE="0" if kind == "unlit" else "1")
    args = [exe, "-w", str(W), "-h", str(H)] + ([] if opengl else ["--force-software"])
    subprocess.run(args, env=env, check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    img = read_ppm(out)
    if img[:2] != (W, H):
        raise SystemExit(f"{out.name}: expected {W}x{H}, got {img[0]}x{img[1]}")
    return img


def compare(a, b) -> dict:
    pa, pb = a[2], b[2]
    bga, bgb = pa[0:3], pb[0:3]
    both = either = same = total = peak = only_a = only_b = 0
    for i in range(0, W * H * 3, 3):
        da, db = pa[i:i + 3] != bga, pb[i:i + 3] != bgb
        if not (da or db):
            continue
        either += 1
        both += da and db
        only_a += da and not db
        only_b += db and not da
        diffs = [abs(pa[i + c] - pb[i + c]) for c in range(3)]
        total += sum(diffs)
        peak = max(peak, max(diffs))
        same += max(diffs) <= NEAR
    return {
        "coverage_iou": round(both / either, 4) if either else 1.0,
        "identical": round(same / either, 4) if either else 1.0,
        "mad": round(total / (3 * either), 3) if either else 0.0,
        "max": peak,
        "drawn": either,
        "only_opengl": only_a,
        "only_software": only_b,
    }


def bounds_of(argv: list[str], flag: str):
    if flag not in argv:
        return None
    i = argv.index(flag)
    return float(argv[i + 1]), float(argv[i + 2]), float(argv[i + 3])


def within(m: dict, b) -> bool:
    return m["coverage_iou"] >= b[0] and m["identical"] >= b[1] and m["mad"] <= b[2]


def draw_all(exe: str, t: Path, opengl: bool, tag: str) -> dict:
    out = {}
    for scene in SCENES:
        for kind in ("unlit", "textured", "lit"):
            if kind == "textured" and scene not in TEXTURED:
                continue
            out[(scene, kind)] = still(exe, t / f"{tag}-{SCENES[scene]}-{kind}.ppm", scene, kind, opengl)
    return out


def main(argv: list[str]) -> int:
    exe = argv[1]
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    keep = Path(argv[argv.index("--stills") + 1]) if "--stills" in argv else None
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        gl = draw_all(exe, t, True, "opengl")
        sw = draw_all(exe, t, False, "software")
        rerun = draw_all(exe, t, True, "opengl-again") if "--require-identical-runs" in argv else None
        if keep:
            keep.mkdir(parents=True, exist_ok=True)
            for p in t.glob("*.ppm"):
                if not p.name.startswith("opengl-again"):
                    (keep / p.name).write_bytes(p.read_bytes())
    result = {"scenes": {}, "classes": {}}
    for (scene, kind), img in gl.items():
        result["scenes"][f"{SCENES[scene]}-{kind}"] = {"class": kind, **compare(img, sw[(scene, kind)])}
    control = compare(gl[(0, "unlit")], sw[(1, "unlit")])
    result["control"] = {"pair": ["opengl earth-unlit", "software teapot-unlit"], **control,
                         "fails_as_required": control["coverage_iou"] < CONTROL_IOU_MAX}
    ok = result["control"]["fails_as_required"]
    if rerun is not None:
        result["opengl_runs_identical"] = all(gl[k][2] == rerun[k][2] for k in gl)
        ok = ok and result["opengl_runs_identical"]
    for kind, flag in (("unlit", "--bounds-unlit"), ("textured", "--bounds-textured"), ("lit", "--bounds-lit")):
        b = bounds_of(argv, flag)
        members = {k: m for k, m in result["scenes"].items() if m["class"] == kind}
        summary = {"lowest_coverage_iou": min(m["coverage_iou"] for m in members.values()),
                   "lowest_identical": min(m["identical"] for m in members.values()),
                   "highest_mad": max(m["mad"] for m in members.values())}
        if b is not None:
            summary["bounds"] = {"min_coverage_iou": b[0], "min_identical": b[1], "max_mad": b[2]}
            summary["within_bounds"] = all(within(m, b) for m in members.values())
            ok = ok and summary["within_bounds"]
        result["classes"][kind] = summary
    result["ok"] = ok
    text = json.dumps(result, indent=2)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8")
    print(f"opengl against software: {len(result['scenes'])} stills, control "
          f"{'fails' if result['control']['fails_as_required'] else 'DOES NOT FAIL'}, {'ok' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
