"""The modern build and its CI agree on what they pin and what they expect."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _pin(text: str, name: str) -> str:
    match = re.search(rf"{name}[:\s]+([0-9a-f]{{40}})", text)
    assert match, name
    return match.group(1)


def test_blazingrenderer_commit_is_the_same_in_cmake_and_ci():
    cmake = (ROOT / "modern" / "CMakeLists.txt").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert _pin(cmake, "BLAZINGRENDERER_COMMIT") == _pin(ci, "BLAZINGRENDERER_COMMIT")
    assert _pin(cmake, "BRENDER132_COMMIT") == _pin(ci, "BRENDER_COMMIT")


def test_ci_expects_the_number_of_bundled_scenes():
    scenes = (ROOT / "modern" / "viewer" / "brview_scenes.c").read_text(encoding="utf-8")
    count = len(re.findall(r'^\s*\{"[^"]+", "[\w.]+\.dat"', scenes, re.M))
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert f"brview smoke: {count} scenes, 0 failed to load" in ci


def test_every_bundled_file_is_shipped():
    scenes = (ROOT / "modern" / "viewer" / "brview_scenes.c").read_text(encoding="utf-8")
    cmake = (ROOT / "modern" / "CMakeLists.txt").read_text(encoding="utf-8")
    shipped = set(re.search(r"set\(BRVIEW_DAT(.*?)\)", cmake, re.S).group(1).split())
    used = set(re.findall(r'"([\w]+\.(?:dat|pix))"', scenes)) | {"std.pal"}
    assert used <= shipped, used - shipped
