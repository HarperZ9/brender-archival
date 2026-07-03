import json

from engine_revival.validate import validate_workspace


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_snapshot_workspace(root):
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


def test_snapshot_links_must_reference_artifact_and_sources(tmp_path):
    _write_snapshot_workspace(tmp_path)
    _write_json(tmp_path / "snapshots" / "bad-snapshot.json", {
        "id": "bad-snapshot",
        "artifact_id": "missing-artifact",
        "snapshot_type": "git-remote-head",
        "source_url": "https://example.invalid/repo.git",
        "ref": "refs/heads/main",
        "commit": "0" * 40,
        "retrieved_at": "2026-07-03",
        "capture_command": "git ls-remote --symref https://example.invalid/repo.git HEAD refs/heads/*",
        "public_notes": "Bad snapshot links.",
        "source_ids": ["missing-source"],
    })
    messages = validate_workspace(tmp_path)
    assert any("unknown artifact_id: missing-artifact" in message for message in messages)
    assert any("unknown source_id: missing-source" in message for message in messages)


def test_snapshot_must_include_source_ids(tmp_path):
    _write_snapshot_workspace(tmp_path)
    _write_json(tmp_path / "snapshots" / "brender-source-main.json", {
        "id": "brender-source-main",
        "artifact_id": "brender-v132-source",
        "snapshot_type": "git-remote-head",
        "source_url": "https://github.com/foone/BRender-v1.3.2.git",
        "ref": "refs/heads/main",
        "commit": "d88d0ed41122664b9781015b517db64353e16f19",
        "retrieved_at": "2026-07-03",
        "capture_command": "git ls-remote --symref https://github.com/foone/BRender-v1.3.2.git HEAD refs/heads/*",
        "public_notes": "BRender source snapshot.",
    })
    messages = validate_workspace(tmp_path)
    assert any("snapshot must include source_ids" in message for message in messages)
