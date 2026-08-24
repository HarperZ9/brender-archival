"""Tests for the release packaging script."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from scripts.package_brender_release import package_release

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


def test_package_replaces_previous_staging(tmp_path):
    source = tmp_path / "source"
    _write_source_fixture(source)

    package_release(source, tmp_path)
    stale = tmp_path / "brender-revival-release" / "harness" / "stale-marker.txt"
    stale.write_text("stale", encoding="utf-8")

    package_release(source, tmp_path)

    assert not stale.exists()
