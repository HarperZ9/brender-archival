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


def test_the_perspective_evidence_matches_the_readme():
    persp = json.loads((EVIDENCE / "modern-vs-period-persp-2026-10-17.json").read_text(encoding="utf-8"))
    scenes = persp["scenes"]
    assert len(scenes) == 7 and persp["ok"] and persp["within_bounds"] and persp["control"]["fails_as_required"]
    assert persp["bounds"] == {"min_coverage_iou": 0.998, "min_identical": 0.92, "max_diff": 255, "max_mad": 1.8}
    assert min(m["coverage_iou"] for m in scenes.values()) == 0.9983
    assert min(m["identical"] for m in scenes.values()) == 0.9259
    assert max(m["mad"] for m in scenes.values()) == 1.713
    assert all(m["by_index"] and m["drawn_b"] > 0 for m in scenes.values()), "every period scene draws, by index"
    # The steep plane scores the same with and without perspective.
    linear, curved = scenes["plane-textured-steep-linear-index8"], scenes["plane-textured-steep-persp-index8"]
    assert linear["coverage_iou"] == curved["coverage_iou"] and abs(linear["identical"] - curved["identical"]) < 0.01
    full = json.loads((EVIDENCE / "modern-vs-period-2026-10-17.json").read_text(encoding="utf-8"))
    assert len(full["scenes"]) == 27 and full["control"]["fails_as_required"]
    for name, m in scenes.items():
        assert full["scenes"][name] == m, name
    readme = (PARITY / "README.md").read_text(encoding="utf-8")
    assert "92.6% to\n  97.9%" in readme.replace("\r\n", "\n") and "## Perspective-correct texturing" in readme


def test_ci_gates_the_modern_side_on_both_systems():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert ci.count("--require-identical") >= 2
    parity = ci[ci.index("\n  parity:"):]
    assert "needs: [brview, linux, brender-native]" in parity and "--skip rgb555,rgb565 --bounds 1.0 0.999 1\n" in parity
    assert "--only rgb555,rgb565 --bounds 1.0 0.999 9" in parity
    assert "--skip textured,index8,rgb555,rgb565,zs --bounds 1.0 0.999 1 0.01" in parity
    assert "--only textured --skip lit,index8,rgb555,rgb565,zs --require-identical" in parity
    assert "PARITY_SHADE4" in ci and "--only textured-lit --skip index8,rgb555,rgb565,zs --bounds 1.0 0.999 13 0.01" in parity
    assert "--only index8 --skip textured --require-identical" in parity
    assert "--only textured-index8,textured-lit-index8 --max-differ 1" in parity
    native = ci[ci.index("\n  brender-native:"):ci.index("\n  ladder64:")]
    assert "parity-period-a parity-period-b" in native and "--require-identical" in native
    # perspective-correct 8-bit scenes: twice on the period side, then gated
    assert '--label "period perspective scenes, two runs" --only persp,steep --require-identical' in native
    assert "--only persp,steep --skip rgb5 --max-differ 1" in parity
    # 15/16-bit scenes: twice on the period side, untextured gated, textured reported
    assert '--label "period 15/16-bit scenes, two runs" --only rgb555,rgb565 --require-identical' in native
    assert "--only rgb555,rgb565 --skip textured,dither,zs,tip,mmxp --bounds 0.986 0.63 255 2.1" in parity
    assert "--only textured-rgb5,textured-gold-rgb5,textured-lit-rgb5\n" in parity


def _gates():
    """Every modern-against-period gate in the parity job: (label, keep, drop)."""
    import re
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    parity = ci[ci.index("\n  parity:"):]
    found = []
    for label, args in re.findall(r'parity-linux parity-period[a-z0-9-]* --label "([^"]+)"([^\n]*)', parity):
        words = args.split()
        keep = words[words.index("--only") + 1].split(",") if "--only" in words else None
        drop = words[words.index("--skip") + 1].split(",") if "--skip" in words else []
        found.append((label, keep, drop))
    return found


def _scene_names():
    import re
    source = (PARITY / "parity-scene.c").read_text(encoding="utf-8")
    return [n for n in re.findall(r'^\s*\{"([a-z0-9-]+)"', source, re.M) if not n.startswith("control-")]


def _chosen(names, keep, drop):
    return [n for n in names if (keep is None or any(k in n for k in keep)) and not any(d in n for d in drop)]


def test_perspective_scenes_stay_out_of_the_older_class_gates():
    """The new scene names must not change what the existing --only/--skip
    gates select, and the perspective gate must select exactly them."""
    names = _scene_names()
    persp = [n for n in names if ("persp" in n or "steep" in n) and n.endswith("-index8")]
    assert len(names) == 91 and len(persp) == 7
    assert all("textured" in n for n in persp)
    gates = _gates()
    assert len(gates) == 21
    for label, keep, drop in gates:
        chosen = _chosen(names, keep, drop)
        if keep == ["persp", "steep"]:
            assert sorted(chosen) == sorted(persp)
        else:
            assert chosen and not set(chosen) & set(persp), label


# What each gate selected before the 15/16-bit scenes existed (the 27 names of
# the perspective PR); the new names must leave every one of them unchanged.
OLD_GATE_COUNTS = {
    "modern against period, untextured": 6,
    "modern against period, textured": 3,
    "modern against period, 8-bit untextured": 5,
    "modern against period, 8-bit textured": 4,
    "modern against period, 8-bit perspective": 7,
    "modern against period, 24-bit lit textured (1998 stride defect)": 2,
    "modern against period, 24-bit lit textured, shade table at stride 4": 2,
}


def test_hicolor_scenes_leave_every_older_gate_as_it_was():
    names = _scene_names()
    later = ("-pal", "dither", "-zs", "-tip", "-mmxp")
    hicolor = [n for n in names if n.endswith(("-rgb555", "-rgb565")) and not any(t in n for t in later)]
    older = [n for n in names if not n.endswith(("-rgb555", "-rgb565")) and "-zs" not in n]
    assert len(older) == 27 and len(hicolor) == 20
    assert sorted(n[:-7] for n in hicolor if n.endswith("555")) == sorted(n[:-7] for n in hicolor if n.endswith("565"))
    gates = {label: (keep, drop) for label, keep, drop in _gates()}
    for label, count in OLD_GATE_COUNTS.items():
        keep, drop = gates[label]
        assert _chosen(names, keep, drop) == _chosen(older, keep, drop), label
        assert len(_chosen(older, keep, drop)) == count, label
    untextured = _chosen(names, *gates["modern against period, 15/16-bit untextured"])
    textured = _chosen(names, *gates["modern against period, 15/16-bit textured (1.4 draws the MMX path)"])
    assert sorted(untextured) == sorted(n for n in hicolor if "textured" not in n) and len(untextured) == 10
    assert sorted(textured) == sorted(n for n in hicolor if "textured" in n) and len(textured) == 10


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


def test_the_hicolor_evidence_matches_the_readme():
    """15/16-bit: the period kernels draw every scene; BRender 1.4 draws the MMX
    path, so the untextured scenes compare and the textured ones do not."""
    record = json.loads((EVIDENCE / "modern-vs-period-hicolor-2026-10-17.json").read_text(encoding="utf-8"))
    scenes = record["scenes"]
    assert len(scenes) == 20 and record["control"]["fails_as_required"]
    assert all(m["drawn_b"] > 0 for m in scenes.values()), "every period scene draws"
    plain = {k: m for k, m in scenes.items() if "textured" not in k}
    textured = {k: m for k, m in scenes.items() if "textured" in k}
    assert len(plain) == 10 and len(textured) == 10
    assert min(m["coverage_iou"] for m in plain.values()) == 0.9869
    assert min(m["identical"] for m in plain.values()) == 0.632
    assert max(m["mad"] for m in plain.values()) == 2.081
    # flat scenes: every pixel both sides draw is the same colour
    for name in ("sphere-flat-rgb555", "sphere-flat-rgb565", "torus-flat-rgb555", "torus-flat-rgb565"):
        assert scenes[name]["identical"] == scenes[name]["coverage_iou"], name
    # BRender 1.4 does not texture these maps: no textured pixel agrees
    assert all(m["identical"] == 0.0 for m in textured.values())
    cross = json.loads((EVIDENCE / "modern-windows-vs-linux-hicolor-2026-10-17.json").read_text(encoding="utf-8"))
    assert len(cross["scenes"]) == 47 and cross["within_bounds"]
    assert all(m["identical"] == 1.0 for k, m in cross["scenes"].items() if k.endswith(("rgb555", "rgb565")))
    readme = (PARITY / "README.md").read_text(encoding="utf-8")
    assert "## 15 and 16-bit buffers (RGB_555, RGB_565)" in readme and "match.c:593" in readme


# The four gates against the period build through the MMX table
# (engine-revival 0.9.0) and what each must select.
MMX_GATES = {
    "modern against period (MMX), 15/16-bit untextured": 10,
    "modern against period (MMX), 15/16-bit maps the MMX table does not texture": 10,
    "modern against period (MMX), 15/16-bit textured": 10,
    "modern against period (MMX), 15/16-bit dithered": 4,
    "modern against period (MMX), TIP shapes the MMX table does not texture": 6,
    "modern against period (MMX), perspective rows, subdivided": 4,
    "modern against period (MMX), z-sorted (1998 MMX table takes them)": 16,
}


def test_mmx_gates_split_the_hicolor_scenes_between_them():
    """The 8-bit palette and dithered scenes (MMX textured rows) leave every
    older gate as it was, and the seven MMX gates share the 60 15/16-bit scenes
    out between them, each scene to exactly one."""
    names = _scene_names()
    hicolor = [n for n in names if n.endswith(("-rgb555", "-rgb565"))]
    new = [n for n in hicolor if "-pal" in n or "dither" in n]
    assert len(hicolor) == 60 and len(new) == 14
    assert sorted(n[:-7] for n in new if n.endswith("555")) == sorted(n[:-7] for n in new if n.endswith("565"))
    gates = {label: (keep, drop) for label, keep, drop in _gates()}
    for label, (keep, drop) in gates.items():
        if label not in MMX_GATES:
            assert not set(_chosen(names, keep, drop)) & set(new), label
    chosen = []
    for label, count in MMX_GATES.items():
        picked = _chosen(names, *gates[label])
        assert len(picked) == count, label
        chosen += picked
    assert sorted(chosen) == sorted(hicolor)


def test_ci_runs_the_period_build_through_the_mmx_table():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    native = ci[ci.index("\n  brender-native:"):ci.index("\n  ladder64:")]
    assert "-DBRENDER_PENTPRIM_MMX=ON" in native
    assert '--label "period through the MMX table, two runs" --require-identical' in native
    assert "--only rgb555,rgb565 --require-identical" in native
    assert "parity-period-a parity-period-mmx-a" in native and "--skip rgb555,rgb565 --require-identical" in native
    assert "name: parity-period-mmx" in native
    parity = ci[ci.index("\n  parity:"):]
    assert "--only rgb555,rgb565 --skip textured,dither,zs,tip,mmxp --bounds 1.0 0.999 9 0.01" in parity
    assert "--only textured-rgb5,textured-gold-rgb5,textured-lit-rgb5 --bounds 1.0 0.999 9 0.01" in parity
    assert "--only textured-pal --skip dither --require-identical" in parity
    assert "--only dither --require-identical" in parity
    period = (PARITY / "period" / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "BRENDER_PENTPRIM_MMX" in period


def test_the_mmx_evidence_matches_the_readme():
    """15/16-bit through the 1998 MMX table: every scene draws on both sides,
    textured included, and the numbers are the README's."""
    record = json.loads((EVIDENCE / "modern-vs-period-mmx-2026-10-17.json").read_text(encoding="utf-8"))
    scenes = record["scenes"]
    assert len(scenes) == 34 and record["ok"] and record["control"]["fails_as_required"]
    assert all(m["drawn_a"] > 0 and m["drawn_b"] > 0 for m in scenes.values())
    pal = {k: m for k, m in scenes.items() if "-pal" in k and "dither" not in k}
    assert len(pal) == 10
    assert min(m["coverage_iou"] for m in scenes.values()) == 0.997
    assert min(m["identical"] for m in scenes.values()) == 0.9659
    assert max(m["mad"] for m in scenes.values()) == 0.476
    assert min(m["identical"] for m in pal.values()) == 0.9659 and max(m["identical"] for m in pal.values()) == 0.9809
    # flat scenes: every pixel both sides draw has the same colour
    for name in ("sphere-flat-rgb555", "sphere-flat-rgb565", "torus-flat-rgb555", "torus-flat-rgb565"):
        assert scenes[name]["identical"] == scenes[name]["coverage_iou"], name
    # against the general tables the textured scenes had no pixel in common
    general = json.loads((EVIDENCE / "modern-vs-period-hicolor-2026-10-17.json").read_text(encoding="utf-8"))
    for name, m in general["scenes"].items():
        if "textured" in name:
            assert m["identical"] == 0.0 and scenes[name]["identical"] > 0.97, name
    cross = json.loads((EVIDENCE / "modern-windows-vs-linux-mmx-2026-10-17.json").read_text(encoding="utf-8"))
    assert len(cross["scenes"]) == 61 and cross["within_bounds"]
    assert all(m["identical"] == 1.0 for k, m in cross["scenes"].items() if "-pal" in k or "dither" in k)
    readme = (PARITY / "README.md").read_text(encoding="utf-8")
    assert "## 15 and 16-bit through the MMX table" in readme and "MmxPackDirectDither" in readme


def test_the_shared_angle_evidence_matches_the_readme():
    """With the same angle on both sides the rasterisers draw the same frames:
    what is left is BRender 1.4's own Windows-against-Linux variance and the
    1998 stride defect."""
    def load(name):
        return json.loads((EVIDENCE / f"{name}-angle-2026-10-17.json").read_text(encoding="utf-8"))
    rgb8, mmx, shade4, cross = (load("modern-vs-period"), load("modern-vs-period-mmx"),
                                load("modern-vs-period-shade4"), load("modern-windows-vs-linux"))
    for record in (rgb8, mmx, shade4, cross):
        assert record["ok"] and record["control"]["fails_as_required"]
    assert len(rgb8["scenes"]) == 27 and len(mmx["scenes"]) == 34 and len(cross["scenes"]) == 61
    left = {k for k, m in rgb8["scenes"].items() if m["identical"] != 1.0}
    assert left == {"sphere-smooth", "teapot-smooth", "torus-smooth", "sphere-textured-lit", "torus-textured-lit"}
    for name in ("sphere-smooth", "teapot-smooth", "torus-smooth"):
        assert rgb8["scenes"][name]["max"] == 1 and rgb8["scenes"][name]["identical"] >= 0.9995, name
    # the stride defect is still the stride defect
    assert all(rgb8["scenes"][n]["identical"] < 0.01 for n in ("sphere-textured-lit", "torus-textured-lit"))
    assert sum(m["identical"] == 1.0 for m in mmx["scenes"].values()) == 30
    assert all(m["coverage_iou"] == 1.0 and m["max"] <= 9 for m in mmx["scenes"].values())
    # every MMX scene that is not identical differs between 1.4's own Windows and Linux builds too
    for name, m in mmx["scenes"].items():
        if m["identical"] != 1.0:
            assert cross["scenes"][name]["identical"] != 1.0, name
    assert min(m["identical"] for m in shade4["scenes"].values()) == 0.9999
    source = (PARITY / "parity-scene.c").read_text(encoding="utf-8")
    assert "BR_ANGLE_DEG(" not in source.split("*/", 3)[-1], "every angle goes through PARITY_ANGLE"
    assert source.count("PARITY_ANGLE(") >= 6
    readme = (PARITY / "README.md").read_text(encoding="utf-8")
    assert "## The same angle on both sides" in readme and "50 of the 61 older scenes are byte-identical" in readme


# The gates for the z-sorted and TIP256 scenes (engine-revival 0.10.0) against
# the general period build, and what each must select.
ZS_GATES = {
    "modern against period, 15/16-bit z-sorted": 10,
    "modern against period, 24-bit z-sorted": 3,
    "modern against period, 24-bit z-sorted lit textured (1998 stride defect)": 1,
    "modern against period, TIP256 (1.4 has no TIP kernel)": 12,
}


def test_zsorted_and_tip_scenes_have_gates_of_their_own():
    """The 30 new scenes come in 555/565 pairs (and four 24-bit ones); no
    older gate selects any of them; the general gates take the z-sorted and
    TIP scenes, each to one gate, and the MMX perspective scenes go to the MMX
    gates only."""
    names = _scene_names()
    new = [n for n in names if any(t in n for t in ("-zs", "-tip", "-mmxp"))]
    assert len(new) == 30
    assert sorted(n[:-7] for n in new if n.endswith("555")) == sorted(n[:-7] for n in new if n.endswith("565"))
    assert sorted(n for n in new if not n.endswith(("-rgb555", "-rgb565"))) == [
        "sphere-flat-zs", "sphere-smooth-zs", "sphere-textured-lit-zs", "sphere-textured-zs"]
    gates = {label: (keep, drop) for label, keep, drop in _gates()}
    for label, (keep, drop) in gates.items():
        if label not in ZS_GATES and label not in MMX_GATES and "stride 4" not in label:
            assert not set(_chosen(names, keep, drop)) & set(new), label
    chosen = []
    for label, count in ZS_GATES.items():
        picked = _chosen(names, *gates[label])
        assert len(picked) == count and set(picked) <= set(new), label
        chosen += picked
    assert len(chosen) == len(set(chosen))
    assert sorted(chosen) == sorted(n for n in new if "mmxp" not in n)
    stride4 = _chosen(names, *gates["modern against period, 24-bit z-sorted lit textured, shade table at stride 4"])
    assert stride4 == ["sphere-textured-lit-zs"]


def test_ci_gates_the_zsorted_tip_and_mmx_perspective_scenes():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    native = ci[ci.index("\n  brender-native:"):ci.index("\n  ladder64:")]
    assert '--label "period z-sorted and TIP256 scenes, two runs" --only zs,tip --require-identical' in native
    parity = ci[ci.index("\n  parity:"):]
    assert "--only zs-rgb5 --skip tip --max-differ 1" in parity
    assert "--only flat-zs,smooth-zs,textured-zs --skip rgb5,lit --bounds 1.0 0.999 1 0.01" in parity
    assert "parity-period-shade4 --label \"modern against period, 24-bit z-sorted lit textured, shade table at stride 4\" --only textured-lit-zs --skip rgb5 --require-identical" in parity
    assert "parity-period-mmx --label \"modern against period (MMX), TIP shapes the MMX table does not texture\" --only tip --skip zs --bounds 1.0 0.999 9 0.01" in parity
    assert "--only mmxp --bounds 1.0 0.999 80 0.01" in parity
    # the older gates keep exactly what they had
    assert "--skip textured,dither,zs,tip,mmxp --bounds 0.986 0.63 255 2.1" in parity
    assert "--only persp,steep --skip rgb5 --max-differ 1" in parity
    source = (PARITY / "parity-scene.c").read_text(encoding="utf-8")
    assert "BrZsSceneRender(" in source and "material->opacity" in source


def test_one_differing_pixel_fails_require_identical_and_max_differ_counts_exactly(tmp_path):
    """The share of identical pixels is rounded to four places; identity is
    decided on the exact count, so one pixel in a disc of 31,000 still fails."""
    a, b = _dir(tmp_path, "a"), _dir(tmp_path, "b")
    for side in (a, b):
        _ppm(side / "sphere-flat.ppm", (200, 170, 110), r=100)
    target = b / "sphere-flat.ppm"
    data = bytearray(target.read_bytes())
    data[len(b"P6\n320 240\n255\n") + 3 * (120 * 320 + 160)] ^= 1
    target.write_bytes(bytes(data))
    code, result = _run(str(a), str(b), "--require-identical")
    assert code == 1 and result["scenes"]["sphere-flat"]["differ"] == 1
    assert result["scenes"]["sphere-flat"]["identical"] == 1.0, "the rounded share alone would have passed it"
    assert _run(str(a), str(b), "--max-differ", "1")[0] == 0
    assert _run(str(a), str(b), "--max-differ", "0")[0] == 1


def test_the_zsorted_evidence_matches_the_readme():
    def load(name):
        return json.loads((EVIDENCE / f"{name}-zs-2026-10-17.json").read_text(encoding="utf-8"))
    gen, mmx, shade4, cross = (load("modern-vs-period"), load("modern-vs-period-mmx"),
                               load("modern-vs-period-shade4"), load("modern-windows-vs-linux"))
    for record in (gen, mmx, shade4, cross):
        assert record["ok"] and record["control"]["fails_as_required"]
    assert len(gen["scenes"]) == 26 and len(mmx["scenes"]) == 26 and len(cross["scenes"]) == 30
    g = gen["scenes"]
    zs16 = {k: m["differ"] for k, m in g.items() if k.endswith(("rgb555", "rgb565")) and "-zs" in k and "tip" not in k}
    assert len(zs16) == 10 and sum(d == 0 for d in zs16.values()) == 8
    assert {k for k, d in zs16.items() if d} == {"sphere-smooth-zs-rgb555", "sphere-smooth-zs-rgb565"}
    assert max(zs16.values()) == 1
    assert g["sphere-flat-zs"]["differ"] == 0 and g["sphere-textured-zs"]["differ"] == 0
    assert g["sphere-smooth-zs"]["differ"] == 5 and g["sphere-smooth-zs"]["max"] == 1
    assert g["sphere-textured-lit-zs"]["identical"] < 0.01 and shade4["scenes"]["sphere-textured-lit-zs"]["differ"] == 0
    # 1.4 refuses z-sorted TIP and does not texture TIP shapes at all
    assert all(m["drawn_a"] == 0 and m["drawn_b"] > 0 for k, m in g.items() if "tip" in k and "-zs" in k)
    assert all(m["identical"] == 0.0 for k, m in g.items() if "tip" in k)
    m = mmx["scenes"]
    tip = {k: v["differ"] for k, v in m.items() if "tip" in k and "-zs" not in k}
    assert len(tip) == 6 and sorted(tip.values()) == [0, 0, 1, 1, 1, 1]
    mmxp = {k: v["differ"] for k, v in m.items() if "mmxp" in k}
    assert mmxp == {"plane-mmxp-steep-rgb555": 0, "plane-mmxp-steep-rgb565": 0,
                    "sphere-mmxp-rgb555": 1, "sphere-mmxp-rgb565": 1}
    assert m["sphere-flat-zs-rgb555"]["differ"] == 195
    assert [k for k, v in cross["scenes"].items() if v["differ"]] == ["sphere-smooth-zs"]
    readme = (PARITY / "README.md").read_text(encoding="utf-8")
    assert "## Z-sorted, TIP256 and the MMX perspective rows" in readme and "96f9537d" in readme
    assert "7,450 of the steep plane's 9,107 pixels" in readme


def test_the_exact_recount_matches_the_correction():
    """Counted exactly, the shared-angle result is 50 of 61 on Windows, and
    every scene the rounding hid differs in one pixel."""
    def load(name):
        return json.loads((EVIDENCE / f"{name}-exact-2026-10-17.json").read_text(encoding="utf-8"))
    def same(record):
        return sum(m["differ"] == 0 for m in record["scenes"].values())
    lin, lin_mmx, win, win_mmx = (load("modern-vs-period"), load("modern-vs-period-mmx"),
                                  load("modern-windows-vs-period"), load("modern-windows-vs-period-mmx"))
    assert (same(lin), same(lin_mmx), same(win), same(win_mmx)) == (20, 26, 20, 30)
    assert same(win) + same(win_mmx) == 50 and len(win["scenes"]) + len(win_mmx["scenes"]) == 61
    for record in (lin, lin_mmx, win, win_mmx):
        for name, m in record["scenes"].items():
            if m["identical"] == 1.0:
                assert m["differ"] <= 1, name
    assert load("modern-vs-period-shade4")["scenes"]["torus-textured-lit"]["differ"] == 1
    readme = (PARITY / "README.md").read_text(encoding="utf-8")
    assert "**Correction, 17 October 2026, later the same day.**" in readme
    assert "**50 of the 61 older scenes are byte-identical**" in readme


# BRender 1.4 with BRender 1.3.2's sine and cosine (PARITY_PERIOD_SINE)
# against the period builds: the gates and the scenes each takes.
SINE_GATES = {
    "modern with the 1998 sine against period, 24-bit and 8-bit": ("parity-period", 23),
    "modern with the 1998 sine against period, 8-bit lit textured": ("parity-period", 5),
    "modern with the 1998 sine against period, 24-bit lit textured, stride 4": ("parity-period-shade4", 3),
    "modern with the 1998 sine against period, 15/16-bit z-sorted": ("parity-period", 10),
    "modern with the 1998 sine against period (MMX), 15/16-bit": ("parity-period-mmx", 44),
}


def _sine_gates():
    import re
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    parity = ci[ci.index("\n  parity:"):]
    found = {}
    for period, label, args in re.findall(r'run: python3 modern/parity/parity_compare.py parity-windows-sine (parity-period[a-z0-9-]*) --label "([^"]+)"([^\n]*)', parity):
        words = args.split()
        keep = words[words.index("--only") + 1].split(",") if "--only" in words else None
        drop = words[words.index("--skip") + 1].split(",") if "--skip" in words else []
        assert "--require-identical" in words, label
        found[label] = (period, keep, drop)
    return found


def test_the_period_sine_gates_take_every_scene_both_versions_draw_alike_once():
    """Byte for byte, each scene to one gate; left out are only the six
    z-sorted TIP scenes, which BRender 1.4 refuses to draw."""
    names = _scene_names()
    gates = _sine_gates()
    assert set(gates) == set(SINE_GATES)
    chosen = []
    for label, (period, count) in SINE_GATES.items():
        got_period, keep, drop = gates[label]
        picked = _chosen(names, keep, drop)
        assert got_period == period and len(picked) == count, label
        chosen += picked
    assert len(chosen) == len(set(chosen)) == 85
    assert sorted(set(names) - set(chosen)) == sorted(
        f"{s}-zs-{f}" for s in ("plane-tip-steep", "sphere-tip", "sphere-tip-blend") for f in ("rgb555", "rgb565"))


def test_ci_builds_brender_14_with_the_period_sine_and_keeps_a_control():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    windows = ci[ci.index("\n  brview:"):ci.index("\n  linux:")]
    assert "cmake -S modern -B build-sine -A x64 -DPARITY_PERIOD_SINE=ON" in windows
    assert "--target parity-scene" in windows and "name: parity-windows-sine" in windows
    parity = ci[ci.index("\n  parity:"):]
    assert "name: parity-windows-sine" in parity
    control = parity[parity.index("control, BRender 1.4 as published fails"):]
    assert "if python3 modern/parity/parity_compare.py parity-windows parity-period" in control
    assert "--skip rgb5,textured-lit --require-identical; then" in control and "exit 1" in control


def test_the_period_sine_patch_matches_the_pinned_brender_14():
    """The copy is patched only where 1.4 defines BR_SIN and BR_COS, and the
    configure step stops if the pinned source no longer reads that way."""
    cmake = (PARITY / "period-sine.cmake").read_text(encoding="utf-8")
    assert '#define BR_SIN(a)           ((br_scalar)sinf(BrAngleToRadian(a)))' in cmake
    assert '#define BR_COS(a)           ((br_scalar)cosf(BrAngleToRadian(a)))' in cmake
    assert "& 0xffff) * (3.14159265358979323846 / 32768.0)" in cmake and "FATAL_ERROR" in cmake
    top = (ROOT / "modern" / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'option(PARITY_PERIOD_SINE' in top and "parity_period_sine(" in top
    assert top.index("option(PARITY_PERIOD_SINE") < top.index("FetchContent_MakeAvailable(blazingrenderer)")
