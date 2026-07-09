import json

from engine_revival.validate import validate_workspace


CHECKPOINT = {
    "id": "brender-v132-portable-core-plotter-2026-07-03",
    "stage": "portable-core-plotter-lane-passing",
    "passed": 12,
    "total": 12,
    "source_snapshot": "d88d0ed41122664b9781015b517db64353e16f19",
}


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_workspace(root, first_checkpoint, second_checkpoint):
    _write_json(root / "targets" / "brender.json", {
        "id": "brender",
        "name": "Argonaut BRender",
        "category": "engine",
        "era": "1990s",
        "platforms": ["Windows"],
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
    _write_json(root / "tasks" / "brender-first.json", {
        "id": "brender-first",
        "target_id": "brender",
        "task_type": "verification",
        "status": "verified",
        "public_notes": "First checkpoint carrier.",
        "evidence_checkpoint": first_checkpoint,
    })
    _write_json(root / "tasks" / "brender-second.json", {
        "id": "brender-second",
        "target_id": "brender",
        "task_type": "verification",
        "status": "verified",
        "public_notes": "Second checkpoint carrier.",
        "evidence_checkpoint": second_checkpoint,
    })
    _write_json(root / "milestones" / "brender-baseline.json", {
        "id": "brender-baseline",
        "target_id": "brender",
        "milestone_type": "baseline-public-record",
        "status": "curated",
        "evidence": "Initial public record fixture.",
        "source_ids": ["brender-source"],
    })


def _checkpoint_messages(root):
    return [message for message in validate_workspace(root) if "evidence_checkpoint" in message]


def test_matching_evidence_checkpoints_validate(tmp_path):
    _write_workspace(tmp_path, CHECKPOINT, CHECKPOINT.copy())
    assert _checkpoint_messages(tmp_path) == []


def test_mismatched_evidence_checkpoint_field_fails(tmp_path):
    mismatched = {**CHECKPOINT, "total": 11}
    _write_workspace(tmp_path, CHECKPOINT, mismatched)
    messages = _checkpoint_messages(tmp_path)
    assert any("field total differs" in message for message in messages)
    assert any(CHECKPOINT["id"] in message for message in messages)


def test_invalid_evidence_checkpoint_bounds_fail(tmp_path):
    invalid = {**CHECKPOINT, "passed": 13}
    _write_workspace(tmp_path, invalid, invalid.copy())
    assert any("passed must be <= total" in message for message in _checkpoint_messages(tmp_path))


def test_evidence_checkpoint_rejects_missing_and_unexpected_fields(tmp_path):
    malformed = {key: value for key, value in CHECKPOINT.items() if key != "stage"}
    malformed["note"] = "not part of the contract"
    _write_workspace(tmp_path, malformed, malformed.copy())
    messages = _checkpoint_messages(tmp_path)
    assert any("missing field: stage" in message for message in messages)
    assert any("unexpected field: note" in message for message in messages)
