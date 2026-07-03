import json

from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_attempt_dependencies(root):
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
    _write_json(root / "harnesses" / "brender-v132-portable-core-plan.json", {
        "id": "brender-v132-portable-core-plan",
        "target_id": "brender",
        "build_id": "brender-v132-build-environment",
        "reproduction_id": "brender-critical-edition-source-build",
        "status": "materializer-available",
        "harness_type": "portable-build-plan",
        "entrypoint": "docs/generated/harnesses/brender-v132-portable-core-plan.md",
        "source_policy": "Use public source only.",
        "implementation_units": ["core FLOAT library path"],
        "steps": ["materialize portable project files"],
        "expected_outputs": ["compiler transcript"],
        "blockers": ["first compiler run not captured"],
        "next_actions": ["run configure"],
        "public_notes": "Portable harness design.",
        "source_ids": ["initial-research-reports"],
    })


def _write_attempt(root):
    _write_json(root / "attempts" / "brender-v132-harness-materializer-smoke.json", {
        "id": "brender-v132-harness-materializer-smoke",
        "target_id": "brender",
        "attempt_type": "harness-materialization",
        "status": "completed",
        "command": "engine-revival materialize-brender-harness --source-root <checkout> --output-root <out>",
        "host_platform": "Windows local probe",
        "harness_id": "brender-v132-portable-core-plan",
        "build_id": "brender-v132-build-environment",
        "reproduction_id": "brender-critical-edition-source-build",
        "transcript_location": "external-workspace:not-committed",
        "result_summary": "Materializer wrote the expected out-of-tree scaffold files.",
        "artifacts_policy": "No generated binaries or copied source committed.",
        "public_notes": "Smoke run for the BRender harness materializer.",
        "source_ids": ["initial-research-reports"],
    })


def test_attempt_report_creates_index_detail_page_and_database_entries(tmp_path):
    seed_workspace(tmp_path)
    _write_attempt_dependencies(tmp_path)
    _write_attempt(tmp_path)
    index = tmp_path / "docs" / "generated" / "attempts.md"
    page = tmp_path / "docs" / "generated" / "attempts" / "brender-v132-harness-materializer-smoke.md"
    database = tmp_path / "docs" / "generated" / "database.json"

    reports = write_reports(tmp_path)

    assert index in reports
    assert page in reports
    assert (
        "| brender | [brender-v132-harness-materializer-smoke]"
        "(attempts/brender-v132-harness-materializer-smoke.md) | "
        "harness-materialization | completed | brender-v132-portable-core-plan |"
    ) in index.read_text(encoding="utf-8")
    page_text = page.read_text(encoding="utf-8")
    assert "# brender-v132-harness-materializer-smoke" in page_text
    assert "```powershell" in page_text
    assert "engine-revival materialize-brender-harness" in page_text
    assert "No generated binaries or copied source committed." in page_text
    payload = json.loads(database.read_text(encoding="utf-8"))
    assert payload["counts"]["attempts"] == 1
    assert payload["attempts_by_target"]["brender"][0]["id"] == (
        "brender-v132-harness-materializer-smoke"
    )


def test_target_dossier_includes_attempt_section(tmp_path):
    seed_workspace(tmp_path)
    _write_attempt_dependencies(tmp_path)
    _write_attempt(tmp_path)
    dossier = tmp_path / "docs" / "generated" / "targets" / "brender.md"

    assert dossier in write_reports(tmp_path)

    text = dossier.read_text(encoding="utf-8")
    assert "## Attempts" in text
    assert "| brender-v132-harness-materializer-smoke | harness-materialization | completed |" in text
