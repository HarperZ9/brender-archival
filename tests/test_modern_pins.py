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


def test_programs_are_window_only_with_an_sdl_entry_point():
    cmake = (ROOT / "modern" / "CMakeLists.txt").read_text(encoding="utf-8")
    game = (ROOT / "games" / "keepers-hour" / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "add_executable(brview WIN32" in cmake
    assert "add_executable(keepers-hour WIN32" in game
    for src in ("modern/viewer/brview.c", "games/keepers-hour/src/kh_main.c"):
        assert "#include <SDL3/SDL_main.h>" in (ROOT / src).read_text(encoding="utf-8"), src


def test_release_checksum_is_written_with_a_unix_newline():
    release = (ROOT / ".github" / "workflows" / "release-brview.yml").read_text(encoding="utf-8")
    assert "WriteAllText" in release and "Out-File" not in release


def _workflow(name: str) -> str:
    return (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")


def test_every_ci_job_pins_the_same_commits_as_cmake():
    cmake = (ROOT / "modern" / "CMakeLists.txt").read_text(encoding="utf-8")
    ci = _workflow("ci.yml")
    br14 = set(re.findall(r"BLAZINGRENDERER_COMMIT:\s*([0-9a-f]{40})", ci))
    br132 = set(re.findall(r"BRENDER_COMMIT:\s*([0-9a-f]{40})", ci))
    assert br14 == {_pin(cmake, "BLAZINGRENDERER_COMMIT")}
    assert br132 == {_pin(cmake, "BRENDER132_COMMIT")}


def test_linux_builds_run_the_same_checks_as_windows():
    ci = _workflow("ci.yml")
    linux = ci[ci.index("\n  linux:"):]
    for line in (
        "brview smoke: 8 scenes, 0 failed to load, run ok",
        "keepers endings: 3 of 3 reached, save ok",
        "keepers options: rebind and save ok",
        "--component Unspecified",
        'test "$listed" = "$EXPECTED_RUNGS"',
    ):
        assert line in linux, line


def test_linux_programs_find_sdl3_beside_themselves():
    cmake = (ROOT / "modern" / "CMakeLists.txt").read_text(encoding="utf-8")
    game = (ROOT / "games" / "keepers-hour" / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'INSTALL_RPATH "$ORIGIN"' in cmake
    assert "$<TARGET_SONAME_FILE_NAME:SDL3::SDL3>" in cmake
    assert 'brview_sdl3_beside(brview . "")' in cmake
    assert "brview_sdl3_beside(keepers-hour keepers-hour keepers)" in game
    # the helper replaces the Windows-only copies, so SDL3 is installed once
    assert "install(FILES $<TARGET_FILE:SDL3::SDL3>" not in game


def test_ci_and_releases_share_one_linux_dependency_list():
    script = (ROOT / "scripts" / "linux-build-deps.sh").read_text(encoding="utf-8")
    assert "\r" not in script
    for backend in ("libx11-dev", "libwayland-dev", "libpulse-dev", "libasound2-dev", "glslang-tools", "spirv-cross"):
        assert backend in script, backend
    for name in ("ci.yml", "release-brview.yml", "release-keepers.yml"):
        assert "bash scripts/linux-build-deps.sh" in _workflow(name), name


def test_releases_publish_a_linux_tarball_after_a_packaged_smoke():
    for name, product in (("release-brview.yml", "brview"), ("release-keepers.yml", "keepers-hour")):
        text = _workflow(name)
        job = text[text.index("\n  linux-x64:"):]
        assert f'"{product}-${{GITHUB_REF_NAME#' in job and "-linux-x64.tar.gz" in job
        assert job.index("runs in place") < job.index("gh release upload"), name
        assert 'sha256sum "$name" > "$name.sha256"' in job


def test_the_brview_zip_holds_only_the_viewer():
    assert "--prefix stage/brview --component Unspecified" in _workflow("release-brview.yml")
