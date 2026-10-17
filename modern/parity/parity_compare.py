"""Compare two sets of parity scenes, pixel by pixel.

    python modern/parity/parity_compare.py <dir-a> <dir-b> [--label NAME] [--out result.json]
        [--require-identical] [--bounds MIN_IOU MIN_IDENTICAL MAX_DIFF [MAX_MAD]]
        [--max-differ N] [--only TEXT] [--skip TEXT]

Each directory holds the PPMs that parity-scene writes (one per scene, and
for an 8-bit scene a PGM of its palette indices beside it). For
every scene this reports, over the pixels either side drew (the union of the
two coverage masks):

- coverage_iou: drawn-in-both over drawn-in-either; 1.0 means the same
  silhouette.
- identical: the share of union pixels with the same three bytes, rounded
  to four places.
- differ: how many union pixels are not the same, exactly.
- mad: the mean absolute difference per channel over the union, 0 to 255.
- max: the largest single channel difference.

Control: "torus-flat" in A against "control-torus-turned" in A, the same
renderer drawing a different pose. It must come out unlike (coverage IoU
under 0.9), or the measure cannot tell scenes apart. A run whose control
does not fail reports ok = false.

--require-identical makes the exit status 1 unless every scene is
byte-identical (differ is 0; the rounded share is not used), which is the claim for two runs of one deterministic build.
--bounds makes it 1 unless every scene has at least MIN_IOU coverage IoU, at
least MIN_IDENTICAL identical pixels, no channel off by more than MAX_DIFF and,
when given, a mean absolute difference of at most MAX_MAD.
--max-differ makes it 1 unless no scene has more than N differing pixels,
counted exactly.
Without it, the numbers are reported and only the control decides the exit
status. --only and --skip keep or drop the scenes whose names contain TEXT
(a comma-separated list: any one of them),
so one class of scene can be held to its own bounds. Standard library only.
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
    index = None
    pgm = path.with_suffix(".pgm")
    if pgm.exists():
        magic, size, maxval, index = pgm.read_bytes().split(b"\n", 3)
        if magic != b"P5" or maxval != b"255" or len(index) != w * h:
            raise SystemExit(f"{pgm}: not a {w}x{h} binary PGM")
    return w, h, pixels, index


def compare(a, b) -> dict:
    """An 8-bit scene has a .pgm of palette indices beside its .ppm. When both
    sides have one, a pixel is drawn when its index is not 0 and identical
    when the indices are equal. MAD and max are always in the PPM's colours."""
    (wa, ha, pa, ia), (wb, hb, pb, ib) = a, b
    if (wa, ha) != (wb, hb):
        raise SystemExit("size mismatch")
    indexed = ia is not None and ib is not None

    def drawn(p, idx, k):
        return idx[k] != 0 if indexed else p[3 * k:3 * k + 3] != b"\0\0\0"

    both = either = same = 0
    total = peak = 0
    for k in range(wa * ha):
        i = 3 * k
        da, db = drawn(pa, ia, k), drawn(pb, ib, k)
        if not (da or db):
            continue
        either += 1
        both += da and db
        same += (ia[k] == ib[k]) if indexed else (pa[i:i + 3] == pb[i:i + 3])
        for c in range(3):
            d = abs(pa[i + c] - pb[i + c])
            total += d
            peak = max(peak, d)
    return {
        "coverage_iou": round(both / either, 4) if either else 1.0,
        "identical": round(same / either, 4) if either else 1.0,
        "differ": either - same,
        "mad": round(total / (3 * either), 3) if either else 0.0,
        "max": peak,
        "drawn_a": sum(1 for k in range(wa * ha) if drawn(pa, ia, k)),
        "drawn_b": sum(1 for k in range(wa * ha) if drawn(pb, ib, k)),
        "by_index": indexed,
    }


def main(argv: list[str]) -> int:
    a, b = Path(argv[1]), Path(argv[2])
    label = argv[argv.index("--label") + 1] if "--label" in argv else f"{a.name} vs {b.name}"
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    scenes = sorted(p.stem for p in a.glob("*.ppm") if not p.stem.startswith("control-"))
    if not scenes or sorted(p.stem for p in b.glob("*.ppm") if not p.stem.startswith("control-")) != scenes:
        raise SystemExit("the two directories do not hold the same scenes")
    if "--only" in argv:
        keep = argv[argv.index("--only") + 1].split(",")
        scenes = [s for s in scenes if any(k in s for k in keep)]
    if "--skip" in argv:
        drop = argv[argv.index("--skip") + 1].split(",")
        scenes = [s for s in scenes if not any(d in s for d in drop)]
    if not scenes:
        raise SystemExit("no scene left after --only/--skip")
    result = {"label": label, "scenes": {s: compare(read_ppm(a / f"{s}.ppm"), read_ppm(b / f"{s}.ppm")) for s in scenes}}
    control = compare(read_ppm(a / f"{CONTROL[0]}.ppm"), read_ppm(a / f"{CONTROL[1]}.ppm"))
    result["control"] = {"pair": list(CONTROL), **control, "fails_as_required": control["coverage_iou"] < CONTROL_IOU_MAX}
    # exact: "identical" is rounded to four places, so one pixel in 20,000 would round to 1.0
    result["all_identical"] = all(m["differ"] == 0 for m in result["scenes"].values())
    result["ok"] = result["control"]["fails_as_required"] and (result["all_identical"] or "--require-identical" not in argv)
    if "--bounds" in argv:
        i = argv.index("--bounds")
        min_iou, min_same, max_diff = float(argv[i + 1]), float(argv[i + 2]), int(argv[i + 3])
        max_mad = float(argv[i + 4]) if len(argv) > i + 4 and not argv[i + 4].startswith("--") else 255.0
        result["bounds"] = {"min_coverage_iou": min_iou, "min_identical": min_same, "max_diff": max_diff, "max_mad": max_mad}
        result["within_bounds"] = all(m["coverage_iou"] >= min_iou and m["identical"] >= min_same and m["max"] <= max_diff
                                      and m["mad"] <= max_mad for m in result["scenes"].values())
        result["ok"] = result["ok"] and result["within_bounds"]
    if "--max-differ" in argv:
        result["max_differ"] = int(argv[argv.index("--max-differ") + 1])
        result["ok"] = result["ok"] and all(m["differ"] <= result["max_differ"] for m in result["scenes"].values())
    text = json.dumps(result, indent=2)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8")
    worst = min(m["coverage_iou"] for m in result["scenes"].values())
    print(f"parity {label}: {sum(m['differ'] == 0 for m in result['scenes'].values())} of {len(scenes)} scenes "
          f"identical, lowest coverage IoU {worst}, control {'fails' if result['control']['fails_as_required'] else 'DOES NOT FAIL'}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
