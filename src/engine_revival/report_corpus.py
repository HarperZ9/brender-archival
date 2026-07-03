from __future__ import annotations

from pathlib import Path

from engine_revival.records import RECORD_DIRS, load_records


def _records_if_present(root: Path, kind: str) -> list[dict[str, object]]:
    directory = root / RECORD_DIRS[kind]
    if not directory.exists():
        return []
    return [record.payload for record in load_records(root, kind)]


def packet_tasks(root: Path) -> list[dict[str, object]]:
    return [
        record.payload for record in load_records(root, "task")
        if record.payload["task_type"] == "build-archive-packet"
    ]


def _as_bullets(value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["- none recorded"]
    return [f"- {item}" for item in value]


def _source_table(
    source_ids: object,
    sources_by_id: dict[str, dict[str, object]],
) -> list[str]:
    if not isinstance(source_ids, list) or not source_ids:
        return ["- none recorded"]
    lines = [
        "| Source | Type | Confidence | Scope | URL |",
        "|---|---|---|---|---|",
    ]
    for source_id in source_ids:
        source = sources_by_id.get(str(source_id))
        if source:
            lines.append(
                f"| {source['title']} | {source['source_type']} | "
                f"{source['confidence']} | {source['claim_scope']} | "
                f"{source.get('url', '')} |"
            )
        else:
            lines.append(f"| {source_id} | unknown | unknown | source record missing |  |")
    return lines


def packet_index(root: Path) -> str:
    packets = sorted(packet_tasks(root), key=lambda item: str(item["id"]))
    lines = [
        "# Archive Packets",
        "",
        "| Target | Packet | Status | Notes |",
        "|---|---|---|---|",
    ]
    for packet in packets:
        packet_id = str(packet["id"])
        lines.append(
            f"| {packet['target_id']} | [{packet_id}](packets/{packet_id}.md) | "
            f"{packet['status']} | {packet['public_notes']} |"
        )
    if not packets:
        lines.append("| none | none | none | No archive packet tasks recorded yet. |")
    return "\n".join(lines) + "\n"


def packet_page(
    packet: dict[str, object],
    sources_by_id: dict[str, dict[str, object]] | None = None,
) -> str:
    sources = sources_by_id or {}
    lines = [
        f"# {packet['id']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Target | {packet['target_id']} |",
        f"| Status | {packet['status']} |",
        f"| Task type | {packet['task_type']} |",
        "",
        "## Public Notes",
        "",
        str(packet["public_notes"]),
        "",
        "## Inputs",
        "",
        *_as_bullets(packet.get("inputs")),
        "",
        "## Outputs",
        "",
        *_as_bullets(packet.get("outputs")),
        "",
        "## Blocked By",
        "",
        *_as_bullets(packet.get("blocked_by")),
        "",
        "## Evidence Sources",
        "",
        *_source_table(packet.get("source_ids"), sources),
    ]
    return "\n".join(lines) + "\n"


def reproduction_records(root: Path) -> list[dict[str, object]]:
    return _records_if_present(root, "reproduction")


def reproduction_index(root: Path) -> str:
    records = sorted(reproduction_records(root), key=lambda item: str(item["id"]))
    lines = [
        "# Reproductions",
        "",
        "| Target | Reproduction | Type | Status | Notes |",
        "|---|---|---|---|---|",
    ]
    for record in records:
        record_id = str(record["id"])
        lines.append(
            f"| {record['target_id']} | [{record_id}](reproductions/{record_id}.md) | "
            f"{record['reproduction_type']} | {record['status']} | {record['public_notes']} |"
        )
    if not records:
        lines.append("| none | none | none | none | No reproduction records yet. |")
    return "\n".join(lines) + "\n"


def reproduction_page(
    record: dict[str, object],
    sources_by_id: dict[str, dict[str, object]] | None = None,
) -> str:
    sources = sources_by_id or {}
    lines = [
        f"# {record['id']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Target | {record['target_id']} |",
        f"| Type | {record['reproduction_type']} |",
        f"| Status | {record['status']} |",
        "",
        "## Public Notes",
        "",
        str(record["public_notes"]),
        "",
        "## Environment",
        "",
        *_as_bullets(record.get("environment")),
        "",
        "## Steps",
        "",
        *_as_bullets(record.get("steps")),
        "",
        "## Expected Outputs",
        "",
        *_as_bullets(record.get("expected_outputs")),
        "",
        "## Artifacts",
        "",
        *_as_bullets(record.get("artifact_ids")),
        "",
        "## Evidence Sources",
        "",
        *_source_table(record.get("source_ids"), sources),
    ]
    return "\n".join(lines) + "\n"


def snapshot_records(root: Path) -> list[dict[str, object]]:
    return _records_if_present(root, "snapshot")


def snapshot_index(root: Path) -> str:
    records = sorted(snapshot_records(root), key=lambda item: str(item["id"]))
    lines = [
        "# Snapshots",
        "",
        "| Artifact | Snapshot | Type | Ref | Commit |",
        "|---|---|---|---|---|",
    ]
    for record in records:
        record_id = str(record["id"])
        lines.append(
            f"| {record['artifact_id']} | [{record_id}](snapshots/{record_id}.md) | "
            f"{record['snapshot_type']} | {record['ref']} | {record['commit']} |"
        )
    if not records:
        lines.append("| none | none | none | none | none |")
    return "\n".join(lines) + "\n"


def snapshot_page(
    record: dict[str, object],
    sources_by_id: dict[str, dict[str, object]] | None = None,
) -> str:
    sources = sources_by_id or {}
    lines = [
        f"# {record['id']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Artifact | {record['artifact_id']} |",
        f"| Type | {record['snapshot_type']} |",
        f"| Source URL | {record['source_url']} |",
        f"| Ref | {record['ref']} |",
        f"| Commit | {record['commit']} |",
        f"| Retrieved | {record['retrieved_at']} |",
        "",
        "## Capture Command",
        "",
        "```powershell",
        str(record["capture_command"]),
        "```",
        "",
        "## Public Notes",
        "",
        str(record["public_notes"]),
        "",
        "## Evidence Sources",
        "",
        *_source_table(record.get("source_ids"), sources),
    ]
    return "\n".join(lines) + "\n"


def _records_by_id(records: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(record["id"]): record for record in records}


def _records_by_target(records: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for record in records:
        target_id = str(record["target_id"])
        grouped.setdefault(target_id, []).append(record)
    return grouped


def _records_by_artifact(records: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for record in records:
        artifact_id = str(record["artifact_id"])
        grouped.setdefault(artifact_id, []).append(record)
    return grouped


def _accessions_by_target(
    accessions: list[dict[str, object]],
    artifacts: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    artifact_targets = {
        str(artifact["id"]): str(artifact["target_id"]) for artifact in artifacts
    }
    grouped: dict[str, list[dict[str, object]]] = {}
    for accession in accessions:
        target_id = artifact_targets.get(str(accession["artifact_id"]))
        if target_id:
            grouped.setdefault(target_id, []).append(accession)
    return grouped


def corpus_database(root: Path) -> dict[str, object]:
    targets = _records_if_present(root, "target")
    sources = _records_if_present(root, "source")
    artifacts = _records_if_present(root, "artifact")
    accessions = _records_if_present(root, "accession")
    tasks = _records_if_present(root, "task")
    milestones = _records_if_present(root, "milestone")
    reproductions = reproduction_records(root)
    snapshots = snapshot_records(root)
    readiness = _records_if_present(root, "readiness")
    builds = _records_if_present(root, "build")
    harnesses = _records_if_present(root, "harness")
    attempts = _records_if_present(root, "attempt")
    return {
        "schema": "engine-revival-corpus-v1",
        "counts": {
            "targets": len(targets),
            "sources": len(sources),
            "artifacts": len(artifacts),
            "accessions": len(accessions),
            "tasks": len(tasks),
            "milestones": len(milestones),
            "reproductions": len(reproductions),
            "snapshots": len(snapshots),
            "readiness": len(readiness),
            "builds": len(builds),
            "harnesses": len(harnesses),
            "attempts": len(attempts),
        },
        "targets": targets,
        "sources": sources,
        "artifacts": artifacts,
        "accessions": accessions,
        "tasks": tasks,
        "milestones": milestones,
        "reproductions": reproductions,
        "snapshots": snapshots,
        "readiness": readiness,
        "builds": builds,
        "harnesses": harnesses,
        "attempts": attempts,
        "targets_by_id": _records_by_id(targets),
        "sources_by_id": _records_by_id(sources),
        "artifacts_by_target": _records_by_target(artifacts),
        "accessions_by_target": _accessions_by_target(accessions, artifacts),
        "tasks_by_target": _records_by_target(tasks),
        "milestones_by_target": _records_by_target(milestones),
        "reproductions_by_target": _records_by_target(reproductions),
        "snapshots_by_artifact": _records_by_artifact(snapshots),
        "readiness_by_target": _records_by_target(readiness),
        "builds_by_target": _records_by_target(builds),
        "harnesses_by_target": _records_by_target(harnesses),
        "attempts_by_target": _records_by_target(attempts),
    }
