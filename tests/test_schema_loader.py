from pathlib import Path

from engine_revival.schema import load_schema, validate_required_fields

ROOT = Path(__file__).resolve().parents[1]


def test_load_target_schema_required_fields():
    schema = load_schema(ROOT, "target")
    assert {"id", "rights_posture"} <= set(schema.required)


def test_validate_required_fields_reports_missing_keys():
    schema = load_schema(ROOT, "target")
    messages = validate_required_fields({"id": "brender"}, schema)
    assert "target missing required field: name" in messages


def test_load_reproduction_schema_required_fields():
    schema = load_schema(ROOT, "reproduction")
    assert {"id", "target_id", "environment", "steps", "expected_outputs"} <= set(schema.required)


def test_load_snapshot_schema_required_fields():
    schema = load_schema(ROOT, "snapshot")
    assert {"id", "artifact_id", "source_url", "commit", "capture_command"} <= set(schema.required)
