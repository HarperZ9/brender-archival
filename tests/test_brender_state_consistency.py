import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CHECKPOINT = {
    "id": "brender-v132-portable-core-plotter-2026-07-03",
    "stage": "portable-core-plotter-lane-passing",
    "passed": 12,
    "total": 12,
    "source_snapshot": "d88d0ed41122664b9781015b517db64353e16f19",
}
STATE_PATHS = (
    "tasks/brender-critical-edition-packet.json",
    "reproductions/brender-critical-edition-source-build.json",
    "builds/brender-v132-build-environment.json",
    "harnesses/brender-v132-portable-core-plan.json",
    "readiness/brender-production-readiness.json",
)


def _load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_brender_state_records_share_verified_plotter_checkpoint():
    for relative in STATE_PATHS:
        assert _load(relative)["evidence_checkpoint"] == EXPECTED_CHECKPOINT, relative


def test_brender_current_statuses_match_verified_scope():
    assert _load(STATE_PATHS[0])["status"] == "portable-render-lane-published"
    assert _load(STATE_PATHS[1])["status"] == "v132-portable-core-verified-3dmm-pending"
    assert _load(STATE_PATHS[2])["status"] == "portable-core-plotter-lane-passing"
    assert _load(STATE_PATHS[3])["status"] == "portable-core-plotter-lane-passing"
    readiness = _load(STATE_PATHS[4])
    assert readiness["build_status"] == "portable-core-plotter-lane-built"
    assert readiness["flagship_score"] == 86
    assert readiness["packaging_status"] == "not-started"


def test_brender_public_packet_describes_twelve_rungs_without_stale_deferral():
    task = _load(STATE_PATHS[0])
    assert "twelve verifying" in task["public_notes"]
    assert "CTest 12/12" in task["public_notes"]
    assert "score 86" in task["public_notes"]
    assert "eight verifying" not in task["public_notes"]
    assert all("eight verifying" not in output for output in task["outputs"])

    packet = (ROOT / "docs/BRENDER-ARCHIVAL.md").read_text(encoding="utf-8")
    assert "twelve self-verifying render smokes" in packet
    deferred = packet.split("## Honestly deferred", 1)[1].split("## Records", 1)[0]
    assert "Multi-part datafile assembly" not in deferred


def test_brender_archival_reproduction_builds_the_full_smoke_ladder():
    packet = (ROOT / "docs/BRENDER-ARCHIVAL.md").read_text(encoding="utf-8")
    reproduce = packet.split("## Reproduce it", 1)[1].split(
        "## What you can do with it today", 1
    )[0]
    assert "cmake --build <build> --config Debug\n" in reproduce
    assert "--target brender_core_model_smoke" not in reproduce


def test_brender_archival_next_steps_do_not_defer_delivered_gouraud_shading():
    packet = (ROOT / "docs/BRENDER-ARCHIVAL.md").read_text(encoding="utf-8")
    current = packet.split("## What you can do with it today", 1)[1].split(
        "## Honestly deferred", 1
    )[0]
    assert "Build on the portable rasterizer" in current
    assert "Extend the portable rasterizer (Gouraud shading" not in current


def test_brender_plan_uses_canonical_cli_from_isolated_editable_install():
    expected_preconditions = {
        "docs/superpowers/specs/2026-07-09-brender-evidence-consistency-design.md": (
            "CLI commands assume an isolated environment"
        ),
        "docs/superpowers/plans/2026-07-09-brender-evidence-consistency.md": (
            "Activate an isolated environment for the active worktree"
        ),
    }
    for relative, expected in expected_preconditions.items():
        document = (ROOT / relative).read_text(encoding="utf-8")
        normalized = " ".join(document.split())
        assert expected in normalized, relative
        assert "installed editable" in normalized, relative
        assert "verify the executable and imported module paths" in normalized, relative
        assert "python -m engine_revival.cli" not in document, relative
