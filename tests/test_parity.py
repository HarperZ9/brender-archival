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
SCENES = ["sphere-flat", "sphere-lit", "sphere-smooth", "torus-flat", "torus-smooth", "teapot-smooth",
          "sphere-textured", "sphere-textured-turned", "torus-textured", "control-torus-turned"]


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
    for name in ("modern-linux-two-runs", "period-two-runs"):
        record = load(name)
        assert record["all_identical"] and record["ok"] and record["control"]["fails_as_required"], name
    cross = load("modern-windows-vs-linux")
    assert cross["within_bounds"] and all(m["coverage_iou"] == 1.0 and m["max"] <= 1 for m in cross["scenes"].values())
    for name in ("modern-vs-period", "modern-windows-vs-period"):
        record = load(name)
        scenes = record["scenes"]
        assert len(scenes) == 20 and record["control"]["fails_as_required"], name
        rgb = {k: m for k, m in scenes.items() if "index8" not in k}
        plain = {k: m for k, m in rgb.items() if "textured" not in k}
        textured = {k: m for k, m in rgb.items() if "textured" in k and "lit" not in k}
        lit = {k: m for k, m in rgb.items() if "textured-lit" in k}
        index8 = {k: m for k, m in scenes.items() if "index8" in k}
        assert (len(plain), len(textured), len(lit), len(index8)) == (6, 3, 2, 9)
        assert min(m["coverage_iou"] for m in plain.values()) == 0.9993
        assert min(m["identical"] for m in plain.values()) == 0.907
        assert max(m["mad"] for m in plain.values()) < 0.2
        assert min(m["coverage_iou"] for m in textured.values()) == 0.9992
        assert min(m["identical"] for m in textured.values()) == 0.9565
        assert max(m["mad"] for m in textured.values()) == 1.085
        assert min(m["coverage_iou"] for m in index8.values()) == 0.9983
        assert min(m["identical"] for m in index8.values()) == 0.9642
        assert max(m["mad"] for m in index8.values()) == 0.427
        # The 1998 stride defect: as shipped, the 24-bit lit textured scenes do not match.
        assert max(m["coverage_iou"] for m in lit.values()) < 0.7 and max(m["identical"] for m in lit.values()) < 0.01
        assert all(m["drawn_b"] > 0 for m in scenes.values()), "every period scene draws"
    shade4 = load("modern-vs-period-shade4")
    assert sorted(shade4["scenes"]) == ["sphere-textured-lit", "torus-textured-lit"]
    assert shade4["ok"] and shade4["within_bounds"] and shade4["control"]["fails_as_required"]
    assert min(m["coverage_iou"] for m in shade4["scenes"].values()) == 0.9998
    assert min(m["identical"] for m in shade4["scenes"].values()) == 0.9789


def test_ci_gates_the_modern_side_on_both_systems():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert ci.count("--require-identical") >= 2
    parity = ci[ci.index("\n  parity:"):]
    assert "needs: [brview, linux, brender-native]" in parity and "--bounds 1.0 0.999 1" in parity
    assert "--skip textured,index8 --bounds 0.999 0.90 255 0.25" in parity
    assert "--only textured --skip lit,index8 --bounds 0.999 0.95 255 1.2" in parity
    assert "PARITY_SHADE4" in ci and "--only textured-lit --skip index8 --bounds 0.999 0.97 255 0.3" in parity
    assert "--only index8 --skip textured --bounds 0.998 0.98 255 0.3" in parity
    assert "--only textured-index8,textured-lit-index8 --bounds 0.998 0.96 255 0.5" in parity
    native = ci[ci.index("\n  brender-native:"):ci.index("\n  ladder64:")]
    assert "parity-period-a parity-period-b" in native and "--require-identical" in native
    # perspective-correct 8-bit scenes: twice on the period side, then gated
    assert '--label "period perspective scenes, two runs" --only persp,steep --require-identical' in native
    assert "--only persp,steep --bounds 0.998 0.92 255 1.8" in parity


def test_perspective_scenes_stay_out_of_the_older_class_gates():
    """The new scene names must not change what the existing --only/--skip
    gates select, and the perspective gate must select exactly them."""
    import re
    source = (PARITY / "parity-scene.c").read_text(encoding="utf-8")
    names = [n for n in re.findall(r'^\s*\{"([a-z0-9-]+)"', source, re.M) if not n.startswith("control-")]
    persp = [n for n in names if "persp" in n or "steep" in n]
    assert len(names) == 27 and len(persp) == 7
    assert all(n.endswith("-index8") and "textured" in n for n in persp)
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    parity = ci[ci.index("\n  parity:"):]
    gates = re.findall(r'parity-linux parity-period[a-z0-9-]* --label "[^"]+"([^\n]*)', parity)
    assert len(gates) == 7
    for args in gates:
        words = args.split()
        keep = words[words.index("--only") + 1].split(",") if "--only" in words else None
        drop = words[words.index("--skip") + 1].split(",") if "--skip" in words else []
        chosen = [n for n in names if (keep is None or any(k in n for k in keep)) and not any(d in n for d in drop)]
        if keep == ["persp", "steep"]:
            assert sorted(chosen) == sorted(persp)
        else:
            assert chosen and not set(chosen) & set(persp), args


def test_a_mean_difference_bound_can_fail_a_run(tmp_path):
    a, b = _dir(tmp_path, "a"), _dir(tmp_path, "b", shift=1)
    assert _run(str(a), str(b), "--bounds", "1.0", "0.0", "255", "1.0")[0] == 0
    assert _run(str(a), str(b), "--bounds", "1.0", "0.0", "255", "0.5")[0] == 1


def test_only_and_skip_select_a_class_of_scene(tmp_path):
    a, b = _dir(tmp_path, "a"), _dir(tmp_path, "b")
    _, only = _run(str(a), str(b), "--only", "textured")
    _, skip = _run(str(a), str(b), "--skip", "textured")
    assert sorted(only["scenes"]) == ["sphere-textured", "sphere-textured-turned", "torus-textured"]
    assert len(skip["scenes"]) == 6 and not any("textured" in k for k in skip["scenes"])


def test_only_and_skip_take_comma_lists(tmp_path):
    a, b = _dir(tmp_path, "a"), _dir(tmp_path, "b")
    _, both = _run(str(a), str(b), "--only", "sphere-flat,torus")
    assert sorted(both["scenes"]) == ["sphere-flat", "torus-flat", "torus-smooth", "torus-textured"]
    _, rest = _run(str(a), str(b), "--skip", "textured,smooth")
    assert sorted(rest["scenes"]) == ["sphere-flat", "sphere-lit", "torus-flat"]


def _pgm(path: Path, indices: bytes) -> None:
    path.write_bytes(b"P5\n320 240\n255\n" + indices)


def test_eight_bit_scenes_compare_by_palette_index(tmp_path):
    """Two indices that the palette shows in the same colour are still two
    indices: an 8-bit scene matches only when the indices match."""
    a, b = _dir(tmp_path, "a"), _dir(tmp_path, "b")
    ia = bytearray(320 * 240)
    ia[1000:2000] = bytes([7]) * 1000
    ib = bytearray(ia)
    ib[1500:1600] = bytes([8]) * 100
    _pgm(a / "sphere-flat.pgm", bytes(ia))
    _pgm(b / "sphere-flat.pgm", bytes(ib))
    _, result = _run(str(a), str(b), "--only", "sphere-flat")
    scene = result["scenes"]["sphere-flat"]
    assert scene["by_index"] and scene["drawn_a"] == 1000 and scene["identical"] == 0.9
    assert scene["mad"] == 0.0  # the PPMs (colours) are the same


def test_opengl_against_software_evidence_and_gate():
    record = json.loads((EVIDENCE / "gl-vs-software-2026-10-16.json").read_text(encoding="utf-8"))
    assert record["ok"] and record["opengl_runs_identical"] and record["control"]["fails_as_required"]
    assert len(record["scenes"]) == 18
    unlit = {k: m for k, m in record["scenes"].items() if m["class"] == "unlit"}
    assert len(unlit) == 8 and all(m["identical"] == m["coverage_iou"] for m in unlit.values()), \
        "wherever both renderers draw an unlit model, the colour is the same"
    assert record["classes"]["unlit"]["lowest_coverage_iou"] == 0.9774
    assert record["classes"]["textured"]["lowest_identical"] == 0.7829
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "gl_vs_software.py build/brview --bounds-unlit 0.975 0.975 4.5 --bounds-textured 0.99 0.77 4.5 --require-identical-runs" in ci
