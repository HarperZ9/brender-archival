"""Compare two sets of parity scenes, pixel by pixel.

    python modern/parity/parity_compare.py <dir-a> <dir-b> [--label NAME] [--out result.json]
        [--require-identical] [--bounds MIN_IOU MIN_IDENTICAL MAX_DIFF [MAX_MAD]]

Each directory holds the PPMs that parity-scene writes (one per scene). For
every scene this reports, over the pixels either side drew (the union of the
two coverage masks):

- coverage_iou: drawn-in-both over drawn-in-either; 1.0 means the same
  silhouette.
- identical: the share of union pixels with the same three bytes.
- mad: the mean absolute difference per channel over the union, 0 to 255.
- max: the largest single channel difference.

Control: "torus-flat" in A against "control-torus-turned" in A, the same
renderer drawing a different pose. It must come out unlike (coverage IoU
under 0.9), or the measure cannot tell scenes apart. A run whose control
does not fail reports ok = false.

--require-identical makes the exit status 1 unless every scene is
byte-identical, which is the claim for two runs of one deterministic build.
--bounds makes it 1 unless every scene has at least MIN_IOU coverage IoU, at
least MIN_IDENTICAL identical pixels, no channel off by more than MAX_DIFF and,
when given, a mean absolute difference of at most MAX_MAD.
Without it, the numbers are reported and only the control decides the exit
status. Standard library only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CONTROL = ("torus-flat", "control-torus-turned")
CONTROL_IOU_MAX = 0.9


def read_ppm(path: Path):
    magic, size, maxval, pixels = path.read_bytes().split(b"\n", 3)
    w, h = (int(v) for v in size.split())
    if magic != b"P6" or maxval != b"255" or len(pixels) != w * h * 3:
        raise SystemExit(f"{path}: not a {w}x{h} binary PPM")
    return w, h, pixels


def compare(a, b) -> dict:
    (wa, ha, pa), (wb, hb, pb) = a, b
    if (wa, ha) != (wb, hb):
        raise SystemExit("size mismatch")
    both = either = same = 0
    total = peak = 0
    for i in range(0, len(pa), 3):
        da, db = pa[i:i + 3] != b"\0\0\0", pb[i:i + 3] != b"\0\0\0"
        if not (da or db):
            continue
        either += 1
        both += da and db
        same += pa[i:i + 3] == pb[i:i + 3]
        for c in range(3):
            d = abs(pa[i + c] - pb[i + c])
            total += d
            peak = max(peak, d)
    return {
        "coverage_iou": round(both / either, 4) if either else 1.0,
        "identical": round(same / either, 4) if either else 1.0,
        "mad": round(total / (3 * either), 3) if either else 0.0,
        "max": peak,
        "drawn_a": sum(1 for i in range(0, len(pa), 3) if pa[i:i + 3] != b"\0\0\0"),
        "drawn_b": sum(1 for i in range(0, len(pb), 3) if pb[i:i + 3] != b"\0\0\0"),
    }


def main(argv: list[str]) -> int:
    a, b = Path(argv[1]), Path(argv[2])
    label = argv[argv.index("--label") + 1] if "--label" in argv else f"{a.name} vs {b.name}"
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    scenes = sorted(p.stem for p in a.glob("*.ppm") if not p.stem.startswith("control-"))
    if not scenes or sorted(p.stem for p in b.glob("*.ppm") if not p.stem.startswith("control-")) != scenes:
        raise SystemExit("the two directories do not hold the same scenes")
    result = {"label": label, "scenes": {s: compare(read_ppm(a / f"{s}.ppm"), read_ppm(b / f"{s}.ppm")) for s in scenes}}
    control = compare(read_ppm(a / f"{CONTROL[0]}.ppm"), read_ppm(a / f"{CONTROL[1]}.ppm"))
    result["control"] = {"pair": list(CONTROL), **control, "fails_as_required": control["coverage_iou"] < CONTROL_IOU_MAX}
    result["all_identical"] = all(m["identical"] == 1.0 for m in result["scenes"].values())
    result["ok"] = result["control"]["fails_as_required"] and (result["all_identical"] or "--require-identical" not in argv)
    if "--bounds" in argv:
        i = argv.index("--bounds")
        min_iou, min_same, max_diff = float(argv[i + 1]), float(argv[i + 2]), int(argv[i + 3])
        max_mad = float(argv[i + 4]) if len(argv) > i + 4 and not argv[i + 4].startswith("--") else 255.0
        result["bounds"] = {"min_coverage_iou": min_iou, "min_identical": min_same, "max_diff": max_diff, "max_mad": max_mad}
        result["within_bounds"] = all(m["coverage_iou"] >= min_iou and m["identical"] >= min_same and m["max"] <= max_diff
                                      and m["mad"] <= max_mad for m in result["scenes"].values())
        result["ok"] = result["ok"] and result["within_bounds"]
    text = json.dumps(result, indent=2)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8")
    worst = min(m["coverage_iou"] for m in result["scenes"].values())
    print(f"parity {label}: {sum(m['identical'] == 1.0 for m in result['scenes'].values())} of {len(scenes)} scenes "
          f"identical, lowest coverage IoU {worst}, control {'fails' if result['control']['fails_as_required'] else 'DOES NOT FAIL'}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
