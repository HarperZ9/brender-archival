"""The Vulkan backend's stage A (docs/adr/0002-vulkan-backend.md): its evidence
and its CI gate stay what the ADR says."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VULKAN = ROOT / "modern" / "vulkan"


def test_the_stage_a_evidence_matches_the_adr():
    record = json.loads((VULKAN / "vk-triangle-2026-10-17.json").read_text(encoding="utf-8"))
    scenes = record["scenes"]
    assert sorted(scenes) == ["offset", "quad", "slivers", "triangle"]
    assert record["ok"] and record["within_bounds"] and record["control"]["fails_as_required"]
    assert scenes["triangle"]["coverage_iou"] == 0.9913 and scenes["quad"]["coverage_iou"] == 1.0
    assert scenes["slivers"]["coverage_iou"] == 0.9137
    assert all(m["within_one_where_both"] >= 0.997 for m in scenes.values())
    adr = (ROOT / "docs" / "adr" / "0002-vulkan-backend.md").read_text(encoding="utf-8")
    assert "0.9913" in adr and "0.9137" in adr and "16,000" in adr


def test_ci_runs_stage_a_on_lavapipe_twice_within_the_bounds():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "VK_DRIVER_FILES: /usr/share/vulkan/icd.d/lvp_icd.json" in ci and "VKO_DEVICE_TYPE: cpu" in ci
    assert "-DBRENDER_VULKAN=ON" in ci and "diff -r vk-a vk-b" in ci
    assert "vk_compare.py vk-a --bounds 0.91 0.997 14.5" in ci
    cmake = (ROOT / "modern" / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'option(BRENDER_VULKAN "Build the Vulkan rasteriser proof (vk-triangle)" OFF)' in cmake
