from __future__ import annotations

from pathlib import Path

from engine_revival.records import load_records


def _records_if_present(root: Path, kind: str) -> list[dict[str, object]]:
    directory = root / f"{kind}s"
    if kind == "accession":
        directory = root / "accessions"
    if not directory.exists():
        return []
    return [record.payload for record in load_records(root, kind)]


def artifact_records(root: Path) -> list[dict[str, object]]:
    if not (root / "artifacts").exists():
        return []
    return sorted(
        [record.payload for record in load_records(root, "artifact")],
        key=lambda payload: (str(payload["target_id"]), str(payload["id"])),
    )


def artifact_index(root: Path) -> str:
    artifacts = artifact_records(root)
    if not artifacts:
        return "# Artifacts\n\nNo artifact records yet.\n"
    lines = [
        "# Artifacts",
        "",
        "| Target | Artifact | Title | Type | Status | Access | Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for artifact in artifacts:
        artifact_id = str(artifact["id"])
        lines.append(
            f"| {artifact['target_id']} | [{artifact_id}](artifacts/{artifact_id}.md) | "
            f"{artifact['title']} | {artifact['artifact_type']} | "
            f"{artifact['redistribution_status']} | {artifact['access_level']} | "
            f"{artifact['evidence_quality']} |"
        )
    return "\n".join(lines) + "\n"


def artifact_relations(
    root: Path,
) -> tuple[
    dict[str, list[dict[str, object]]],
    dict[str, list[dict[str, object]]],
    dict[str, list[dict[str, object]]],
]:
    return (
        _records_by_artifact(_records_if_present(root, "accession")),
        _records_by_artifact(_records_if_present(root, "snapshot")),
        _reproductions_by_artifact(_records_if_present(root, "reproduction")),
    )


def artifact_page(
    artifact: dict[str, object],
    accessions: list[dict[str, object]],
    snapshots: list[dict[str, object]],
    reproductions: list[dict[str, object]],
    sources_by_id: dict[str, dict[str, object]] | None = None,
) -> str:
    sources = sources_by_id or {}
    field_rows = [
        ("Target", artifact["target_id"]),
        ("Title", artifact["title"]),
        ("Type", artifact["artifact_type"]),
        ("Origin", artifact["origin"]),
        ("Redistribution", artifact["redistribution_status"]),
        ("Access", artifact["access_level"]),
        ("Evidence Quality", artifact["evidence_quality"]),
        ("Version", artifact.get("version", "")),
        ("Date", artifact.get("date", "")),
        ("Location", artifact.get("location", "")),
    ]
    lines = [
        f"# {artifact['id']}",
        "",
        "| Field | Value |",
        "|---|---|",
        *[f"| {name} | {value} |" for name, value in field_rows if value != ""],
        "",
        "## Notes",
        "",
        str(artifact.get("notes", "none recorded")),
        "",
        "## Accessions",
        "",
        *_accession_table(accessions),
        "",
        "## Snapshots",
        "",
        *_snapshot_table(snapshots),
        "",
        "## Reproductions",
        "",
        *_reproduction_table(reproductions),
        "",
        "## Evidence Sources",
        "",
        *_source_table(artifact.get("source_ids"), sources),
    ]
    return "\n".join(lines) + "\n"


def _records_by_artifact(
    records: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for record in records:
        artifact_id = str(record["artifact_id"])
        grouped.setdefault(artifact_id, []).append(record)
    return grouped


def _reproductions_by_artifact(
    records: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for record in records:
        artifact_ids = record.get("artifact_ids", [])
        if isinstance(artifact_ids, list):
            for artifact_id in artifact_ids:
                grouped.setdefault(str(artifact_id), []).append(record)
    return grouped


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


def _accession_table(records: list[dict[str, object]]) -> list[str]:
    if not records:
        return ["No accession records."]
    lines = [
        "| Accession | Package | Capture | Fixity | Storage | Rights |",
        "|---|---|---|---|---|---|",
    ]
    for record in sorted(records, key=lambda item: str(item["id"])):
        accession_id = str(record["id"])
        lines.append(
            f"| [{accession_id}](../accessions/{accession_id}.md) | "
            f"{record['package_type']} | {record['capture_status']} | "
            f"{record['fixity_status']} | {record['storage_class']} | "
            f"{record['rights_review']} |"
        )
    return lines


def _snapshot_table(records: list[dict[str, object]]) -> list[str]:
    if not records:
        return ["No snapshot records."]
    lines = [
        "| Snapshot | Type | Ref | Commit | Retrieved |",
        "|---|---|---|---|---|",
    ]
    for record in sorted(records, key=lambda item: str(item["id"])):
        snapshot_id = str(record["id"])
        lines.append(
            f"| [{snapshot_id}](../snapshots/{snapshot_id}.md) | "
            f"{record['snapshot_type']} | {record['ref']} | {record['commit']} | "
            f"{record['retrieved_at']} |"
        )
    return lines


def _reproduction_table(records: list[dict[str, object]]) -> list[str]:
    if not records:
        return ["No reproduction records."]
    lines = [
        "| Reproduction | Type | Status | Notes |",
        "|---|---|---|---|",
    ]
    for record in sorted(records, key=lambda item: str(item["id"])):
        reproduction_id = str(record["id"])
        lines.append(
            f"| [{reproduction_id}](../reproductions/{reproduction_id}.md) | "
            f"{record['reproduction_type']} | {record['status']} | "
            f"{record['public_notes']} |"
        )
    return lines
