from __future__ import annotations

from pathlib import Path

from engine_revival.records import load_records


def accession_records(root: Path) -> list[dict[str, object]]:
    if not (root / "accessions").exists():
        return []
    return [record.payload for record in load_records(root, "accession")]


def accession_index(root: Path) -> str:
    records = sorted(
        accession_records(root),
        key=lambda payload: (str(payload["artifact_id"]), str(payload["id"])),
    )
    lines = [
        "# Accessions",
        "",
        "| Artifact | Accession | Package | Capture | Fixity | Storage | Rights | Notes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for payload in records:
        accession_id = str(payload["id"])
        lines.append(
            f"| {payload['artifact_id']} | [{accession_id}](accessions/{accession_id}.md) | "
            f"{payload['package_type']} | {payload['capture_status']} | "
            f"{payload['fixity_status']} | {payload['storage_class']} | "
            f"{payload['rights_review']} | {payload['public_notes']} |"
        )
    if not records:
        lines.append("| none | none | none | none | none | none | none | No accession records yet. |")
    return "\n".join(lines) + "\n"


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


def _hash_table(hashes: object) -> list[str]:
    if not isinstance(hashes, dict) or not hashes:
        return ["- none recorded"]
    lines = ["| Object | Algorithm | Value |", "|---|---|---|"]
    for object_name, algorithms in sorted(hashes.items()):
        if isinstance(algorithms, dict):
            for algorithm, value in sorted(algorithms.items()):
                lines.append(f"| {object_name} | {algorithm} | {value} |")
        else:
            lines.append(f"| {object_name} | value | {algorithms} |")
    return lines


def _bullets(value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["- none recorded"]
    return [f"- {item}" for item in value]


def accession_page(
    payload: dict[str, object],
    sources_by_id: dict[str, dict[str, object]] | None = None,
) -> str:
    sources = sources_by_id or {}
    field_rows = [
        ("Artifact", payload["artifact_id"]),
        ("Package", payload["package_type"]),
        ("Capture", payload["capture_status"]),
        ("Fixity", payload["fixity_status"]),
        ("Storage", payload["storage_class"]),
        ("Rights", payload["rights_review"]),
        ("Capture URI", payload.get("capture_uri", "")),
        ("Captured At", payload.get("captured_at", "")),
        ("Captured By", payload.get("captured_by", "")),
        ("Size Bytes", payload.get("size_bytes", "")),
    ]
    lines = [
        f"# {payload['id']}",
        "",
        "| Field | Value |",
        "|---|---|",
        *[f"| {name} | {value} |" for name, value in field_rows if value != ""],
        "",
        "## Public Notes",
        "",
        str(payload["public_notes"]),
        "",
        "## Review Notes",
        "",
        str(payload.get("review_notes", "none recorded")),
        "",
        "## Tooling",
        "",
        *_bullets(payload.get("tooling")),
        "",
        "## Hashes",
        "",
        *_hash_table(payload.get("hashes")),
        "",
        "## Evidence Sources",
        "",
        *_source_table(payload.get("source_ids"), sources),
    ]
    return "\n".join(lines) + "\n"
