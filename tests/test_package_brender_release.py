"""Tests for the release packaging script."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from scripts.package_brender_release import package_release

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PATH_MARKERS = tuple(
    f"C:{separator}{root}"
    for root in ("Use" + "rs", "de" + "v")
    for separator in ("/", "\\")
)
TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "utf-16", "utf-16-le")


def _decode_staged_text(path: Path) -> str | None:
    payload = path.read_bytes()
    for encoding in TEXT_ENCODINGS:
        try:
            text = payload.decode(encoding)
        except UnicodeDecodeError:
            continue
        if "\x00" not in text:
            return text
    return None

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_brender_harness_materializer import _write_source_fixture


def test_package_stages_harness_docs_evidence_and_receipt(tmp_path):
    source = tmp_path / "source"
    _write_source_fixture(source)
    output_root = tmp_path / "dist"

    written = package_release(source, output_root)
    output = output_root / "brender-revival-release"

    assert (output / "harness" / "CMakeLists.txt").is_file()
    assert (output / "README.md").is_file()
    assert (output / "evidence" / "ctest-twenty-rungs.log").is_file()
    assert (output / "evidence" / "ctest-twentyone-targets.log").is_file()
    assert (output / "media" / "period-pipeline-still.png").is_file()
    assert (output / "media" / "period-pipeline-orbit-contact-sheet.png").is_file()
    assert (output / "media" / "social-card-1200x630.png").is_file()
    assert (output / "media" / "provenance-manifest.json").is_file()
    assert (output / "SHA256SUMS.txt").is_file()
    assert (output / "package-receipt.json").is_file()
    assert (output / "package-receipt.json") in written

    receipt = json.loads((output / "package-receipt.json").read_text(encoding="utf-8"))
    assert receipt["schema"] == "brender-archival.release-package/v1"
    assert receipt["sha256"]["README.md"] == hashlib.sha256(
        (output / "README.md").read_bytes()
    ).hexdigest()

    sums = {
        line.split("  ", 1)[1].strip(): line.split("  ", 1)[0]
        for line in (output / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    assert sums["README.md"] == receipt["sha256"]["README.md"]
    assert "harness/CMakeLists.txt" in sums
    assert "media/provenance-manifest.json" in sums

    source_manifest = json.loads(
        (REPO_ROOT / "gallery" / "release-20260827" / "provenance-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    for media_output in source_manifest["outputs"]:
        staged_media_path = f"media/{Path(media_output['path']).name}"
        assert staged_media_path in sums


def test_package_replaces_previous_staging(tmp_path):
    source = tmp_path / "source"
    _write_source_fixture(source)

    package_release(source, tmp_path)
    stale = tmp_path / "brender-revival-release" / "harness" / "stale-marker.txt"
    stale.write_text("stale", encoding="utf-8")

    package_release(source, tmp_path)

    assert not stale.exists()


def test_package_stages_no_private_absolute_paths_in_text_files(tmp_path):
    source = tmp_path / "source"
    _write_source_fixture(source)
    output_root = tmp_path / "dist"

    package_release(source, output_root)
    output = output_root / "brender-revival-release"

    violations: list[str] = []
    for path in sorted(output.rglob("*")):
        if not path.is_file():
            continue
        text = _decode_staged_text(path)
        if text is None:
            continue
        for marker in PRIVATE_PATH_MARKERS:
            if marker in text:
                relative = path.relative_to(output).as_posix()
                violations.append(f"{relative} contains {marker}")

    assert violations == []
