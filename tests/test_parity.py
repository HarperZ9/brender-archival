"""The parity comparison measures what it says, and the committed evidence
says what the README says."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARITY = ROOT / "modern" / "parity"
TOOL = PARITY / "parity_compare.py"
EVIDENCE = PARITY / "evidence"
SCENES = ["sphere-flat", "sphere-lit", "sphere-smooth", "torus-flat", "torus-smooth", "teapot-smooth", "control-torus-turned"]


def _ppm(path: Path, disc: tuple[int, int, int] | None, cx: int = 160, r: int = 60, shift: int = 0) -> None:
    w, h = 320, 240
    px = bytearray(w * h * 3)
    if disc:
        for y in range(h):
            for x in range(w):
                if (x - cx) ** 2 + (y - 120) ** 2 <= r * r:
                    px[3 * (y * w + x):3 * (y * w + x) + 3] = bytes(min(255, c + shift) for c in disc)
    path.write_bytes(b"P6\n320 240\n255\n" + bytes(px))


def _dir(tmp: Path, name: str, shift: int = 0, control_cx: int = 260) -> Path:
    d = tmp / name
    d.mkdir()
    for s in SCENES:
        _ppm(d / f"{s}.ppm", (200, 170, 110), cx=control_cx if s.startswith("control-") else 160, shift=shift)
    return d


def _run(*args: str) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)
    text = proc.stdout
    return proc.returncode, json.loads(text[:text.rindex("}") + 1])


def test_identical_runs_pass_and_the_control_fails(tmp_path):
    code, result = _run(str(_dir(tmp_path, "a")), str(_dir(tmp_path, "b")), "--require-identical")
    assert code == 0 and result["all_identical"] and result["control"]["fails_as_required"]


def test_a_one_level_shift_fails_identical_but_passes_matching_bounds(tmp_path):
    a, b = _dir(tmp_path, "a"), _dir(tmp_path, "b", shift=1)
    assert _run(str(a), str(b), "--require-identical")[0] == 1
    code, result = _run(str(a), str(b), "--bounds", "1.0", "0.0", "1")
    assert code == 0 and result["scenes"]["sphere-flat"]["max"] == 1
    assert _run(str(a), str(b), "--bounds", "1.0", "0.999", "1")[0] == 1


def test_a_control_that_matches_makes_the_run_fail(tmp_path):
    """If the control pose draws the same picture, the measure cannot tell scenes apart."""
    a = _dir(tmp_path, "a", control_cx=160)
    code, result = _run(str(a), str(_dir(tmp_path, "b")))
    assert code == 1 and not result["control"]["fails_as_required"]


def test_the_evidence_matches_the_readme():
    def load(name):
        return json.loads((EVIDENCE / f"{name}-2026-10-16.json").read_text(encoding="utf-8"))
    linux = load("modern-linux-two-runs")
    assert linux["all_identical"] and linux["ok"]
    cross = load("modern-windows-vs-linux")
    assert cross["within_bounds"] and all(m["coverage_iou"] == 1.0 and m["max"] <= 1 for m in cross["scenes"].values())
    period = load("modern-vs-period")
    scenes = period["scenes"]
    assert all(scenes[s]["drawn_b"] == 0 for s in ("sphere-flat", "sphere-lit", "torus-flat"))
    assert all(0.6 <= scenes[s]["coverage_iou"] <= 0.77 for s in ("sphere-smooth", "torus-smooth", "teapot-smooth"))
    assert not period["all_identical"]
    rerun = load("period-two-runs")
    assert not rerun["all_identical"] and not rerun["control"]["fails_as_required"]


def test_ci_gates_the_modern_side_on_both_systems():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert ci.count("--require-identical") >= 2
    parity = ci[ci.index("\n  parity:"):]
    assert "needs: [brview, linux]" in parity and "--bounds 1.0 0.999 1" in parity
