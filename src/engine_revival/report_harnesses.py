from __future__ import annotations

from pathlib import Path

from engine_revival.records import load_records


def harness_records(root: Path) -> list[dict[str, object]]:
    if not (root / "harnesses").exists():
        return []
    return sorted(
        [record.payload for record in load_records(root, "harness")],
        key=lambda payload: (str(payload["target_id"]), str(payload["id"])),
    )


def harness_index(root: Path) -> str:
    records = harness_records(root)
    lines = [
        "# Harnesses",
        "",
        "| Target | Harness | Status | Type | Build |",
        "|---|---|---|---|---|",
    ]
    for record in records:
        record_id = str(record["id"])
        lines.append(
            f"| {record['target_id']} | [{record_id}](harnesses/{record_id}.md) | "
            f"{record['status']} | {record['harness_type']} | {record['build_id']} |"
        )
    if not records:
        lines.append("| none | none | none | none | none |")
    return "\n".join(lines) + "\n"


def harness_page(
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
        f"| Status | {record['status']} |",
        f"| Type | {record['harness_type']} |",
        f"| Build | {record['build_id']} |",
        f"| Reproduction | {record['reproduction_id']} |",
        f"| Entrypoint | {record['entrypoint']} |",
        *_optional_field_rows(record, ("materializer_command", "output_policy")),
        "",
        "## Source Policy",
        "",
        str(record["source_policy"]),
        "",
        "## Public Notes",
        "",
        str(record["public_notes"]),
        "",
        "## Implementation Units",
        "",
        *_bullets(record.get("implementation_units")),
        "",
        "## Steps",
        "",
        *_bullets(record.get("steps")),
        "",
        "## Expected Outputs",
        "",
        *_bullets(record.get("expected_outputs")),
        "",
        "## Blockers",
        "",
        *_bullets(record.get("blockers")),
        "",
        "## Next Actions",
        "",
        *_bullets(record.get("next_actions")),
        "",
        "## Evidence Sources",
        "",
        *_source_table(record.get("source_ids"), sources),
    ]
    return "\n".join(lines) + "\n"


def harness_section(records: list[dict[str, object]]) -> list[str]:
    if not records:
        return []
    lines = [
        "",
        "## Harnesses",
        "",
        "| Harness | Status | Type | Build |",
        "|---|---|---|---|",
    ]
    for record in sorted(records, key=lambda payload: str(payload["id"])):
        lines.append(
            f"| {record['id']} | {record['status']} | {record['harness_type']} | "
            f"{record['build_id']} |"
        )
    return lines


def _bullets(value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["- none recorded"]
    return [f"- {item}" for item in value]


def _optional_field_rows(record: dict[str, object], keys: tuple[str, ...]) -> list[str]:
    labels = {
        "materializer_command": "Materializer",
        "output_policy": "Output Policy",
    }
    rows: list[str] = []
    for key in keys:
        value = record.get(key)
        if value:
            label = labels.get(key, key.replace("_", " ").title())
            rows.append(f"| {label} | {value} |")
    return rows


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
