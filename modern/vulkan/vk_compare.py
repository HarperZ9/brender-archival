"""Compare vk-triangle's Vulkan frames with its software frames.

    python modern/vulkan/vk_compare.py <out-dir> [--out result.json] [--bounds IOU WITHIN_ONE MAD]

<out-dir> holds software/<scene>.ppm and vulkan/<scene>.ppm. Per scene,
over the pixels either side drew (anything not black): coverage IoU, the
share of those pixels with the same three bytes, MAD, the largest channel
difference, how many pixels only one side drew, and the share of the pixels
both drew whose channels agree within one level. The control compares
Vulkan's "triangle" with the software "quad"; it must come out unlike
(coverage IoU under 0.9). Standard library only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CONTROL_IOU_MAX = 0.9


def read_ppm(path: Path):
    parts = path.read_bytes().split(b"\n", 3)
    w, h = (int(v) for v in parts[1].split())
    return w, h, parts[3]


def compare(a, b) -> dict:
    pa, pb = a[2], b[2]
    both = either = same = near = total = peak = only_a = only_b = 0
    for i in range(0, len(pa), 3):
        da, db = pa[i:i + 3] != b"\0\0\0", pb[i:i + 3] != b"\0\0\0"
        if not (da or db):
            continue
        either += 1
        both += da and db
        only_a += da and not db
        only_b += db and not da
        diffs = [abs(pa[i + c] - pb[i + c]) for c in range(3)]
        same += max(diffs) == 0
        near += da and db and max(diffs) <= 1
        total += sum(diffs)
        peak = max(peak, max(diffs))
    return {"coverage_iou": round(both / either, 4) if either else 1.0, "identical": round(same / either, 4) if either else 1.0,
            "mad": round(total / (3 * either), 3) if either else 0.0, "max": peak, "drawn": either,
            "within_one_where_both": round(near / both, 4) if both else 1.0,
            "only_vulkan": only_a, "only_software": only_b}


def main(argv: list[str]) -> int:
    root = Path(argv[1])
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    scenes = sorted(p.stem for p in (root / "software").glob("*.ppm"))
    result = {"scenes": {s: compare(read_ppm(root / "vulkan" / f"{s}.ppm"), read_ppm(root / "software" / f"{s}.ppm")) for s in scenes}}
    control = compare(read_ppm(root / "vulkan" / "triangle.ppm"), read_ppm(root / "software" / "quad.ppm"))
    result["control"] = {"pair": ["vulkan triangle", "software quad"], **control,
                         "fails_as_required": control["coverage_iou"] < CONTROL_IOU_MAX}
    ok = result["control"]["fails_as_required"]
    if "--bounds" in argv:
        i = argv.index("--bounds")
        b = float(argv[i + 1]), float(argv[i + 2]), float(argv[i + 3])
        result["bounds"] = {"min_coverage_iou": b[0], "min_within_one_where_both": b[1], "max_mad": b[2]}
        result["within_bounds"] = all(m["coverage_iou"] >= b[0] and m["within_one_where_both"] >= b[1] and m["mad"] <= b[2]
                                      for m in result["scenes"].values())
        ok = ok and result["within_bounds"]
    result["ok"] = ok
    text = json.dumps(result, indent=2)
    print(text)
    if out:
        out.write_text(text + "\n", encoding="utf-8")
    worst = min(m["coverage_iou"] for m in result["scenes"].values())
    print(f"vulkan against software: {len(scenes)} scenes, lowest coverage IoU {worst}, control "
          f"{'fails' if result['control']['fails_as_required'] else 'DOES NOT FAIL'}, {'ok' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
