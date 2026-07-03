import json

from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_build(root):
    _write_json(root / "builds" / "brender-v132-build-environment.json", {
        "id": "brender-v132-build-environment",
        "target_id": "brender",
        "reproduction_id": "brender-critical-edition-source-build",
        "status": "source-inspected",
        "host_platform": "Windows local probe",
        "source_checkout": "out-of-tree public checkout",
        "snapshot_ids": ["brender-v132-main-head"],
        "toolchain_probe": {"available": ["cmake"], "missing": ["make"]},
        "build_system": "period makefiles with BR_* environment imports",
        "required_variables": ["BR_SOURCE_DIR", "BR_MAKEFILE"],
        "observed_layout": {"makefiles": 68},
        "blockers": ["period make environment needs reconstruction"],
        "next_actions": ["create portable harness"],
        "public_notes": "Build environment inspected.",
        "source_ids": ["initial-research-reports"],
    })


def _write_harness(root):
    _write_json(root / "harnesses" / "brender-v132-portable-core-plan.json", {
        "id": "brender-v132-portable-core-plan",
        "target_id": "brender",
        "build_id": "brender-v132-build-environment",
        "reproduction_id": "brender-critical-edition-source-build",
        "status": "designed",
        "harness_type": "portable-build-plan",
        "entrypoint": "docs/generated/harnesses/brender-v132-portable-core-plan.md",
        "materializer_command": "engine-revival materialize-brender-harness --source-root <checkout> --output-root <out>",
        "source_policy": "Use only the public BRender checkout; do not vendor source.",
        "implementation_units": ["core FLOAT library path", "driver variant matrix"],
        "steps": ["materialize portable project files"],
        "expected_outputs": ["compiler transcript"],
        "blockers": ["first compiler run not captured"],
        "next_actions": ["emit portable CMake harness"],
        "public_notes": "Portable harness design for the BRender core path.",
        "source_ids": ["initial-research-reports"],
    })


def test_harness_report_creates_index_detail_page_and_database_entries(tmp_path):
    seed_workspace(tmp_path)
    _write_build(tmp_path)
    _write_harness(tmp_path)
    index = tmp_path / "docs" / "generated" / "harnesses.md"
    page = tmp_path / "docs" / "generated" / "harnesses" / "brender-v132-portable-core-plan.md"
    database = tmp_path / "docs" / "generated" / "database.json"

    reports = write_reports(tmp_path)

    assert index in reports
    assert page in reports
    assert (
        "| brender | [brender-v132-portable-core-plan](harnesses/brender-v132-portable-core-plan.md) | "
        "designed | portable-build-plan | brender-v132-build-environment |"
    ) in index.read_text(encoding="utf-8")
    page_text = page.read_text(encoding="utf-8")
    assert "# brender-v132-portable-core-plan" in page_text
    assert "| Materializer | engine-revival materialize-brender-harness" in page_text
    assert "## Source Policy" in page_text
    assert "Use only the public BRender checkout" in page_text
    assert "- core FLOAT library path" in page_text
    payload = json.loads(database.read_text(encoding="utf-8"))
    assert payload["counts"]["harnesses"] == 1
    assert payload["harnesses_by_target"]["brender"][0]["id"] == "brender-v132-portable-core-plan"


def test_target_dossier_includes_harness_section(tmp_path):
    seed_workspace(tmp_path)
    _write_build(tmp_path)
    _write_harness(tmp_path)
    dossier = tmp_path / "docs" / "generated" / "targets" / "brender.md"

    assert dossier in write_reports(tmp_path)

    text = dossier.read_text(encoding="utf-8")
    assert "## Harnesses" in text
    assert "| brender-v132-portable-core-plan | designed | portable-build-plan |" in text
