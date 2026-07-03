from __future__ import annotations

from pathlib import Path

from engine_revival.records import load_records


def attempt_records(root: Path) -> list[dict[str, object]]:
    if not (root / "attempts").exists():
        return []
    return sorted(
        [record.payload for record in load_records(root, "attempt")],
        key=lambda payload: (str(payload["target_id"]), str(payload["id"])),
    )


def attempt_index(root: Path) -> str:
    records = attempt_records(root)
    lines = [
        "# Attempts",
        "",
        "| Target | Attempt | Type | Status | Harness |",
        "|---|---|---|---|---|",
    ]
    for record in records:
        record_id = str(record["id"])
        lines.append(
            f"| {record['target_id']} | [{record_id}](attempts/{record_id}.md) | "
            f"{record['attempt_type']} | {record['status']} | "
            f"{record.get('harness_id', 'none recorded')} |"
        )
    if not records:
        lines.append("| none | none | none | none | none |")
    return "\n".join(lines) + "\n"


def attempt_page(
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
        f"| Type | {record['attempt_type']} |",
        f"| Host | {record['host_platform']} |",
        *_optional_field_rows(record, ("harness_id", "build_id", "reproduction_id", "exit_code")),
        f"| Transcript | {record['transcript_location']} |",
        "",
        "## Command",
        "",
        "```powershell",
        str(record["command"]),
        "```",
        "",
        "## Result Summary",
        "",
        str(record["result_summary"]),
        "",
        "## Artifacts Policy",
        "",
        str(record["artifacts_policy"]),
        "",
        "## Public Notes",
        "",
        str(record["public_notes"]),
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


def attempt_section(records: list[dict[str, object]]) -> list[str]:
    if not records:
        return []
    lines = [
        "",
        "## Attempts",
        "",
        "| Attempt | Type | Status | Summary |",
        "|---|---|---|---|",
    ]
    for record in sorted(records, key=lambda payload: str(payload["id"])):
        lines.append(
            f"| {record['id']} | {record['attempt_type']} | "
            f"{record['status']} | {record['result_summary']} |"
        )
    return lines


def _bullets(value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["- none recorded"]
    return [f"- {item}" for item in value]


def _optional_field_rows(record: dict[str, object], keys: tuple[str, ...]) -> list[str]:
    labels = {
        "harness_id": "Harness",
        "build_id": "Build",
        "reproduction_id": "Reproduction",
        "exit_code": "Exit Code",
    }
    rows: list[str] = []
    for key in keys:
        value = record.get(key)
        if value is not None and value != "":
            rows.append(f"| {labels.get(key, key)} | {value} |")
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
