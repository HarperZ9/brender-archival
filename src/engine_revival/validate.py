from __future__ import annotations

from pathlib import Path

from engine_revival.records import RECORD_DIRS, RecordFile, load_records
from engine_revival.schema import SchemaSpec, load_schema, validate_required_fields


TYPE_MAP = {
    "array": list,
    "integer": int,
    "object": dict,
    "string": str,
}


def _schema_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _validate_types(record: RecordFile, schema: SchemaSpec) -> list[str]:
    messages: list[str] = []
    for field, expected in schema.properties.items():
        if field not in record.payload:
            continue
        expected_type = TYPE_MAP.get(expected)
        if expected_type and not isinstance(record.payload[field], expected_type):
            messages.append(f"{record.path}: {field} must be {expected}")
    return messages


def _validate_kind(root: Path, kind: str) -> tuple[list[RecordFile], list[str]]:
    directory = root / RECORD_DIRS[kind]
    if not directory.exists():
        return [], []
    schema = load_schema(_schema_root(), kind)
    records = load_records(root, kind)
    messages: list[str] = []
    for record in records:
        for message in validate_required_fields(record.payload, schema):
            messages.append(f"{record.path}: {message}")
        messages.extend(_validate_types(record, schema))
    return records, messages


def _validate_unique_ids(records: list[RecordFile], kind: str) -> list[str]:
    messages: list[str] = []
    seen: dict[str, Path] = {}
    for record in records:
        record_id = str(record.payload.get("id"))
        if record_id in seen:
            messages.append(
                f"{record.path}: duplicate {kind} id: {record_id} also in {seen[record_id]}"
            )
        else:
            seen[record_id] = record.path
    return messages


def _validate_filename_ids(records: list[RecordFile], kind: str) -> list[str]:
    messages: list[str] = []
    for record in records:
        record_id = record.payload.get("id")
        if not isinstance(record_id, str):
            continue
        if record.path.stem != record_id:
            messages.append(
                f"{record.path}: {kind} id must match filename stem: {record_id} != {record.path.stem}"
            )
    return messages


def _validate_source_ids_present(records: list[RecordFile], kind: str) -> list[str]:
    messages: list[str] = []
    for record in records:
        source_ids = record.payload.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids:
            messages.append(f"{record.path}: {kind} must include source_ids")
    return messages


def validate_workspace(root: Path) -> list[str]:
    messages: list[str] = []
    if not (root / "targets").exists():
        messages.append("missing record directory: targets")
        return messages

    records_by_kind: dict[str, list[RecordFile]] = {}
    for kind in RECORD_DIRS:
        records, kind_messages = _validate_kind(root, kind)
        records_by_kind[kind] = records
        messages.extend(kind_messages)
        messages.extend(_validate_unique_ids(records, kind))
        messages.extend(_validate_filename_ids(records, kind))

    target_ids = {str(record.payload.get("id")) for record in records_by_kind["target"]}
    source_ids = {str(record.payload.get("id")) for record in records_by_kind["source"]}
    artifact_ids = {str(record.payload.get("id")) for record in records_by_kind["artifact"]}
    reproduction_ids = {
        str(record.payload.get("id")) for record in records_by_kind["reproduction"]
    }
    snapshot_ids = {str(record.payload.get("id")) for record in records_by_kind["snapshot"]}
    build_ids = {str(record.payload.get("id")) for record in records_by_kind["build"]}
    harness_ids = {str(record.payload.get("id")) for record in records_by_kind["harness"]}
    attempt_ids = {str(record.payload.get("id")) for record in records_by_kind["attempt"]}
    task_ids = {str(record.payload.get("id")) for record in records_by_kind["task"]}
    task_target_ids = {
        str(record.payload.get("target_id")) for record in records_by_kind["task"]
    }
    milestone_target_ids = {
        str(record.payload.get("target_id")) for record in records_by_kind["milestone"]
    }
    messages.extend(_validate_source_ids_present(records_by_kind["artifact"], "artifact"))
    messages.extend(_validate_source_ids_present(records_by_kind["milestone"], "milestone"))
    messages.extend(_validate_source_ids_present(records_by_kind["reproduction"], "reproduction"))
    messages.extend(_validate_source_ids_present(records_by_kind["snapshot"], "snapshot"))
    messages.extend(_validate_source_ids_present(records_by_kind["readiness"], "readiness"))
    messages.extend(_validate_source_ids_present(records_by_kind["build"], "build"))
    messages.extend(_validate_source_ids_present(records_by_kind["harness"], "harness"))
    messages.extend(_validate_source_ids_present(records_by_kind["attempt"], "attempt"))
    for kind in ("artifact", "task", "milestone"):
        for record in records_by_kind[kind]:
            target_id = str(record.payload.get("target_id"))
            if target_id not in target_ids:
                messages.append(f"{record.path}: unknown target_id: {target_id}")
            for source_id in record.payload.get("source_ids", []):
                if str(source_id) not in source_ids:
                    messages.append(f"{record.path}: unknown source_id: {source_id}")
            if kind == "task":
                for blocked_id in record.payload.get("blocked_by", []):
                    if str(blocked_id) not in task_ids:
                        messages.append(
                            f"{record.path}: unknown blocked_by task_id: {blocked_id}"
                        )
    messages.extend(_validate_source_ids_present(records_by_kind["accession"], "accession"))
    for record in records_by_kind["accession"]:
        artifact_id = str(record.payload.get("artifact_id"))
        if artifact_id not in artifact_ids:
            messages.append(f"{record.path}: unknown artifact_id: {artifact_id}")
        for source_id in record.payload.get("source_ids", []):
            if str(source_id) not in source_ids:
                messages.append(f"{record.path}: unknown source_id: {source_id}")
    for record in records_by_kind["reproduction"]:
        target_id = str(record.payload.get("target_id"))
        if target_id not in target_ids:
            messages.append(f"{record.path}: unknown target_id: {target_id}")
        for artifact_id in record.payload.get("artifact_ids", []):
            if str(artifact_id) not in artifact_ids:
                messages.append(f"{record.path}: unknown artifact_id: {artifact_id}")
        for task_id in record.payload.get("task_ids", []):
            if str(task_id) not in task_ids:
                messages.append(f"{record.path}: unknown task_id: {task_id}")
        for source_id in record.payload.get("source_ids", []):
            if str(source_id) not in source_ids:
                messages.append(f"{record.path}: unknown source_id: {source_id}")
    for record in records_by_kind["snapshot"]:
        artifact_id = str(record.payload.get("artifact_id"))
        if artifact_id not in artifact_ids:
            messages.append(f"{record.path}: unknown artifact_id: {artifact_id}")
        for source_id in record.payload.get("source_ids", []):
            if str(source_id) not in source_ids:
                messages.append(f"{record.path}: unknown source_id: {source_id}")
    for record in records_by_kind["readiness"]:
        target_id = str(record.payload.get("target_id"))
        if target_id not in target_ids:
            messages.append(f"{record.path}: unknown target_id: {target_id}")
        for source_id in record.payload.get("source_ids", []):
            if str(source_id) not in source_ids:
                messages.append(f"{record.path}: unknown source_id: {source_id}")
        for reproduction_id in record.payload.get("reproduction_ids", []):
            if str(reproduction_id) not in reproduction_ids:
                messages.append(
                    f"{record.path}: unknown reproduction_id: {reproduction_id}"
                )
        for snapshot_id in record.payload.get("snapshot_ids", []):
            if str(snapshot_id) not in snapshot_ids:
                messages.append(f"{record.path}: unknown snapshot_id: {snapshot_id}")
        for build_id in record.payload.get("build_ids", []):
            if str(build_id) not in build_ids:
                messages.append(f"{record.path}: unknown build_id: {build_id}")
        for harness_id in record.payload.get("harness_ids", []):
            if str(harness_id) not in harness_ids:
                messages.append(f"{record.path}: unknown harness_id: {harness_id}")
        for attempt_id in record.payload.get("attempt_ids", []):
            if str(attempt_id) not in attempt_ids:
                messages.append(f"{record.path}: unknown attempt_id: {attempt_id}")
    for record in records_by_kind["build"]:
        target_id = str(record.payload.get("target_id"))
        if target_id not in target_ids:
            messages.append(f"{record.path}: unknown target_id: {target_id}")
        reproduction_id = str(record.payload.get("reproduction_id"))
        if reproduction_id not in reproduction_ids:
            messages.append(f"{record.path}: unknown reproduction_id: {reproduction_id}")
        for snapshot_id in record.payload.get("snapshot_ids", []):
            if str(snapshot_id) not in snapshot_ids:
                messages.append(f"{record.path}: unknown snapshot_id: {snapshot_id}")
        for source_id in record.payload.get("source_ids", []):
            if str(source_id) not in source_ids:
                messages.append(f"{record.path}: unknown source_id: {source_id}")
    for record in records_by_kind["attempt"]:
        target_id = str(record.payload.get("target_id"))
        if target_id not in target_ids:
            messages.append(f"{record.path}: unknown target_id: {target_id}")
        harness_id = record.payload.get("harness_id")
        if harness_id and str(harness_id) not in harness_ids:
            messages.append(f"{record.path}: unknown harness_id: {harness_id}")
        build_id = record.payload.get("build_id")
        if build_id and str(build_id) not in build_ids:
            messages.append(f"{record.path}: unknown build_id: {build_id}")
        reproduction_id = record.payload.get("reproduction_id")
        if reproduction_id and str(reproduction_id) not in reproduction_ids:
            messages.append(f"{record.path}: unknown reproduction_id: {reproduction_id}")
        for source_id in record.payload.get("source_ids", []):
            if str(source_id) not in source_ids:
                messages.append(f"{record.path}: unknown source_id: {source_id}")
    for record in records_by_kind["harness"]:
        target_id = str(record.payload.get("target_id"))
        if target_id not in target_ids:
            messages.append(f"{record.path}: unknown target_id: {target_id}")
        build_id = str(record.payload.get("build_id"))
        if build_id not in build_ids:
            messages.append(f"{record.path}: unknown build_id: {build_id}")
        reproduction_id = str(record.payload.get("reproduction_id"))
        if reproduction_id not in reproduction_ids:
            messages.append(f"{record.path}: unknown reproduction_id: {reproduction_id}")
        for source_id in record.payload.get("source_ids", []):
            if str(source_id) not in source_ids:
                messages.append(f"{record.path}: unknown source_id: {source_id}")
    accession_artifact_ids = {
        str(record.payload.get("artifact_id")) for record in records_by_kind["accession"]
    }
    for artifact_id in sorted(artifact_ids - accession_artifact_ids):
        messages.append(f"missing accession for artifact_id: {artifact_id}")
    for target_id in sorted(target_ids - task_target_ids):
        messages.append(f"missing task for target_id: {target_id}")
    for target_id in sorted(target_ids - milestone_target_ids):
        messages.append(f"missing milestone for target_id: {target_id}")
    return messages
