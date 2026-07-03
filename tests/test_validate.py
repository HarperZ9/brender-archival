import json
from pathlib import Path

from engine_revival.records import load_records
from engine_revival.validate import validate_workspace

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_accession_workspace(root):
    _write_json(root / "targets" / "brender.json", {
        "id": "brender",
        "name": "Argonaut BRender",
        "category": "engine",
        "era": "1990s",
        "platforms": [],
        "priority": 89,
        "revival_lane": "critical-edition",
        "rights_posture": "open",
        "summary": "BRender target.",
        "public_status": "curated-public-sources",
        "restricted_status": "none-known",
    })
    _write_json(root / "sources" / "brender-source.json", {
        "id": "brender-source",
        "title": "BRender source",
        "source_type": "source-repository",
        "confidence": "high",
        "claim_scope": "Public BRender source release.",
    })
    _write_json(root / "artifacts" / "brender-v132-source.json", {
        "id": "brender-v132-source",
        "target_id": "brender",
        "artifact_type": "source-release",
        "title": "BRender source",
        "origin": "public repository",
        "redistribution_status": "open",
        "access_level": "public",
        "evidence_quality": "public-source",
        "source_ids": ["brender-source"],
    })
    _write_json(root / "accessions" / "brender-v132-source-planned.json", {
        "id": "brender-v132-source-planned",
        "artifact_id": "brender-v132-source",
        "package_type": "source-snapshot",
        "capture_status": "planned",
        "storage_class": "external-url",
        "fixity_status": "not-started",
        "rights_review": "open-license",
        "public_notes": "Planned accession.",
        "source_ids": ["brender-source"],
    })
    _write_json(root / "tasks" / "brender-triage.json", {
        "id": "brender-triage",
        "target_id": "brender",
        "task_type": "triage",
        "status": "planned",
        "public_notes": "Triage the BRender record.",
    })
    _write_json(root / "milestones" / "brender-baseline.json", {
        "id": "brender-baseline",
        "target_id": "brender",
        "milestone_type": "baseline-public-record",
        "status": "planned",
        "evidence": "Initial public record fixture.",
        "source_ids": ["brender-source"],
    })


def test_valid_fixture_has_no_validation_errors():
    assert validate_workspace(ROOT / "tests" / "fixtures" / "valid-mini") == []


def test_valid_accession_fixture_passes_validation(tmp_path):
    _write_accession_workspace(tmp_path)
    assert validate_workspace(tmp_path) == []
    loaded = load_records(tmp_path, "accession")
    assert loaded[0].payload["artifact_id"] == "brender-v132-source"


def test_repo_without_records_reports_missing_directories(tmp_path):
    assert "missing record directory: targets" in validate_workspace(tmp_path)


def test_artifact_source_ids_must_reference_sources(tmp_path):
    (tmp_path / "targets").mkdir()
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "sources").mkdir()
    (tmp_path / "targets" / "brender.json").write_text(
        """{
  "id": "brender",
  "name": "Argonaut BRender",
  "category": "engine",
  "era": "1990s",
  "platforms": [],
  "priority": 89,
  "revival_lane": "critical-edition",
  "rights_posture": "open",
  "summary": "BRender target.",
  "public_status": "seeded",
  "restricted_status": "none-known"
}""",
        encoding="utf-8",
    )
    (tmp_path / "artifacts" / "bad-source.json").write_text(
        """{
  "id": "bad-source",
  "target_id": "brender",
  "artifact_type": "source",
  "title": "Bad source link",
  "origin": "fixture",
  "redistribution_status": "open",
  "access_level": "public",
  "evidence_quality": "fixture",
  "source_ids": ["missing-source"]
}""",
        encoding="utf-8",
    )
    messages = validate_workspace(tmp_path)
    assert any("unknown source_id: missing-source" in message for message in messages)


def test_artifact_must_include_source_ids(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "artifacts" / "brender-v132-source.json", {
        "id": "brender-v132-source",
        "target_id": "brender",
        "artifact_type": "source-release",
        "title": "BRender source",
        "origin": "public repository",
        "redistribution_status": "open",
        "access_level": "public",
        "evidence_quality": "public-source",
    })
    messages = validate_workspace(tmp_path)
    assert any("artifact must include source_ids" in message for message in messages)


def test_accession_artifact_id_must_reference_artifact(tmp_path):
    _write_accession_workspace(tmp_path)
    (tmp_path / "accessions" / "brender-v132-source-planned.json").unlink()
    _write_json(tmp_path / "accessions" / "bad.json", {
        "id": "bad",
        "artifact_id": "missing-artifact",
        "package_type": "metadata-only",
        "capture_status": "metadata-only",
        "storage_class": "not-held",
        "fixity_status": "not-applicable",
        "rights_review": "metadata-only",
        "public_notes": "Metadata only.",
    })
    messages = validate_workspace(tmp_path)
    assert any("unknown artifact_id: missing-artifact" in message for message in messages)


def test_accession_source_ids_must_reference_sources(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "accessions" / "bad-source.json", {
        "id": "bad-source",
        "artifact_id": "brender-v132-source",
        "package_type": "metadata-only",
        "capture_status": "metadata-only",
        "storage_class": "not-held",
        "fixity_status": "not-applicable",
        "rights_review": "metadata-only",
        "public_notes": "Metadata only.",
        "source_ids": ["missing-source"],
    })
    messages = validate_workspace(tmp_path)
    assert any("unknown source_id: missing-source" in message for message in messages)


def test_accession_must_include_source_ids(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "accessions" / "brender-v132-source-planned.json", {
        "id": "brender-v132-source-planned",
        "artifact_id": "brender-v132-source",
        "package_type": "source-snapshot",
        "capture_status": "planned",
        "storage_class": "external-url",
        "fixity_status": "not-started",
        "rights_review": "open-license",
        "public_notes": "Planned accession.",
    })
    messages = validate_workspace(tmp_path)
    assert any("accession must include source_ids" in message for message in messages)


def test_artifact_must_have_accession_record(tmp_path):
    _write_accession_workspace(tmp_path)
    (tmp_path / "accessions" / "brender-v132-source-planned.json").unlink()
    messages = validate_workspace(tmp_path)
    assert any("missing accession for artifact_id: brender-v132-source" in message for message in messages)


def test_duplicate_record_ids_fail_validation(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "sources" / "duplicate.json", {
        "id": "brender-source",
        "title": "Duplicate BRender source",
        "source_type": "source-repository",
        "confidence": "low",
        "claim_scope": "Duplicate fixture.",
    })
    messages = validate_workspace(tmp_path)
    assert any("duplicate source id: brender-source" in message for message in messages)


def test_record_id_must_match_filename_stem(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "sources" / "wrong-file-name.json", {
        "id": "renamed-source",
        "title": "Renamed source",
        "source_type": "source-repository",
        "confidence": "low",
        "claim_scope": "Filename drift fixture.",
    })
    messages = validate_workspace(tmp_path)
    assert any("source id must match filename stem" in message for message in messages)


def test_task_blocked_by_must_reference_tasks(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "tasks" / "brender-package.json", {
        "id": "brender-package",
        "target_id": "brender",
        "task_type": "package",
        "status": "planned",
        "public_notes": "Package the BRender record.",
        "blocked_by": ["missing-task"],
    })
    messages = validate_workspace(tmp_path)
    assert any("unknown blocked_by task_id: missing-task" in message for message in messages)


def test_targets_must_have_task_records(tmp_path):
    _write_accession_workspace(tmp_path)
    (tmp_path / "tasks" / "brender-triage.json").unlink()
    messages = validate_workspace(tmp_path)
    assert any("missing task for target_id: brender" in message for message in messages)


def test_milestone_source_ids_must_reference_sources(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "milestones" / "bad-source.json", {
        "id": "bad-source",
        "target_id": "brender",
        "milestone_type": "baseline-public-record",
        "status": "planned",
        "evidence": "Milestone with bad source link.",
        "source_ids": ["missing-source"],
    })
    messages = validate_workspace(tmp_path)
    assert any("unknown source_id: missing-source" in message for message in messages)


def test_milestone_must_include_source_ids(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "milestones" / "brender-baseline.json", {
        "id": "brender-baseline",
        "target_id": "brender",
        "milestone_type": "baseline-public-record",
        "status": "planned",
        "evidence": "Initial public record fixture.",
    })
    messages = validate_workspace(tmp_path)
    assert any("milestone must include source_ids" in message for message in messages)


def test_targets_must_have_milestone_records(tmp_path):
    _write_accession_workspace(tmp_path)
    (tmp_path / "milestones" / "brender-baseline.json").unlink()
    messages = validate_workspace(tmp_path)
    assert any("missing milestone for target_id: brender" in message for message in messages)


def test_reproduction_links_must_reference_sources_and_artifacts(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "reproductions" / "bad-reproduction.json", {
        "id": "bad-reproduction",
        "target_id": "brender",
        "reproduction_type": "source-build",
        "status": "planned",
        "environment": ["host compiler"],
        "steps": ["clone source"],
        "expected_outputs": ["build artifacts"],
        "artifact_ids": ["missing-artifact"],
        "public_notes": "Bad reproduction links.",
        "source_ids": ["missing-source"],
    })
    messages = validate_workspace(tmp_path)
    assert any("unknown artifact_id: missing-artifact" in message for message in messages)
    assert any("unknown source_id: missing-source" in message for message in messages)


def test_reproduction_must_include_source_ids(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "reproductions" / "brender-build.json", {
        "id": "brender-build",
        "target_id": "brender",
        "reproduction_type": "source-build",
        "status": "planned",
        "environment": ["host compiler"],
        "steps": ["clone source"],
        "expected_outputs": ["build artifacts"],
        "artifact_ids": ["brender-v132-source"],
        "public_notes": "BRender build recipe.",
    })
    messages = validate_workspace(tmp_path)
    assert any("reproduction must include source_ids" in message for message in messages)
