import json

from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def test_report_includes_production_readiness_index_and_database(tmp_path):
    seed_workspace(tmp_path)
    readiness = tmp_path / "docs" / "generated" / "production-readiness.md"
    database = tmp_path / "docs" / "generated" / "database.json"

    reports = write_reports(tmp_path)

    assert readiness in reports
    text = readiness.read_text(encoding="utf-8")
    assert "# Production Readiness" in text
    assert (
        "| Target | Stage | Build | Runtime | Tests | Package | "
        "Modernization | Score | Evidence | Next Actions |"
    ) in text
    assert (
        "| brender | baseline-assessment | not-started | not-started | "
        "not-started | not-started | not-started | 0 | none recorded | "
        "create repeatable build harness |"
    ) in text
    payload = json.loads(database.read_text(encoding="utf-8"))
    assert payload["counts"]["readiness"] == 22
    assert payload["readiness_by_target"]["brender"][0]["id"] == "brender-production-readiness"


def test_target_dossier_includes_production_readiness(tmp_path):
    seed_workspace(tmp_path)
    dossier = tmp_path / "docs" / "generated" / "targets" / "brender.md"

    assert dossier in write_reports(tmp_path)

    text = dossier.read_text(encoding="utf-8")
    assert "## Production Readiness" in text
    assert "| brender-production-readiness | baseline-assessment | not-started | 0 |" in text
    assert "create repeatable build harness" in text


def test_readiness_report_exposes_reproduction_and_snapshot_evidence(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "readiness" / "brender-production-readiness.json").write_text(
        """{
  "id": "brender-production-readiness",
  "target_id": "brender",
  "readiness_stage": "build-harness-candidate",
  "build_status": "source-inspected",
  "runtime_status": "not-started",
  "test_status": "not-started",
  "packaging_status": "not-started",
  "modernization_status": "toolchain-reconstruction-needed",
  "flagship_score": 12,
  "blockers": ["period make environment needs reconstruction"],
  "next_actions": ["create out-of-tree build environment manifest"],
  "public_notes": "BRender public source checkout matched the recorded snapshot commit.",
  "source_ids": ["initial-research-reports"],
  "reproduction_ids": ["brender-critical-edition-source-build"],
  "snapshot_ids": ["brender-v132-main-head"]
}""",
        encoding="utf-8",
    )
    readiness = tmp_path / "docs" / "generated" / "production-readiness.md"

    assert readiness in write_reports(tmp_path)

    text = readiness.read_text(encoding="utf-8")
    assert (
        "| brender | build-harness-candidate | source-inspected | not-started | "
        "not-started | not-started | toolchain-reconstruction-needed | 12 | "
        "brender-critical-edition-source-build; brender-v132-main-head | "
        "create out-of-tree build environment manifest |"
    ) in text
