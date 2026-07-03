from __future__ import annotations

from pathlib import Path

from engine_revival.records import load_records


def build_records(root: Path) -> list[dict[str, object]]:
    if not (root / "builds").exists():
        return []
    return sorted(
        [record.payload for record in load_records(root, "build")],
        key=lambda payload: (str(payload["target_id"]), str(payload["id"])),
    )


def build_index(root: Path) -> str:
    records = build_records(root)
    lines = [
        "# Build Environments",
        "",
        "| Target | Build | Status | Reproduction | Snapshots | Host | Build System |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in records:
        record_id = str(record["id"])
        lines.append(
            f"| {record['target_id']} | [{record_id}](builds/{record_id}.md) | "
            f"{record['status']} | {record['reproduction_id']} | "
            f"{_list_cell(record.get('snapshot_ids'))} | {record['host_platform']} | "
            f"{record['build_system']} |"
        )
    if not records:
        lines.append("| none | none | none | none | none | none | none |")
    return "\n".join(lines) + "\n"


def build_page(
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
        f"| Reproduction | {record['reproduction_id']} |",
        f"| Host Platform | {record['host_platform']} |",
        f"| Source Checkout | {record['source_checkout']} |",
        f"| Build System | {record['build_system']} |",
        f"| Snapshots | {_list_cell(record.get('snapshot_ids'))} |",
        "",
        "## Public Notes",
        "",
        str(record["public_notes"]),
        "",
        "## Required Variables",
        "",
        *_bullets(record.get("required_variables")),
        "",
        "## Toolchain Probe",
        "",
        *_object_list_table(record.get("toolchain_probe")),
        "",
        "## Observed Layout",
        "",
        *_object_value_table(record.get("observed_layout")),
        "",
        "## Make Rule Map",
        "",
        *_object_list_table(record.get("make_rule_map")),
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


def build_section(records: list[dict[str, object]]) -> list[str]:
    if not records:
        return []
    lines = [
        "",
        "## Build Environments",
        "",
        "| Build | Status | Host | Reproduction |",
        "|---|---|---|---|",
    ]
    for record in sorted(records, key=lambda payload: str(payload["id"])):
        lines.append(
            f"| {record['id']} | {record['status']} | {record['host_platform']} | "
            f"{record['reproduction_id']} |"
        )
    return lines


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


def _bullets(value: object) -> list[str]:
    if not isinstance(value, list) or not value:
        return ["- none recorded"]
    return [f"- {item}" for item in value]


def _list_cell(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none recorded"
    return "; ".join(str(item) for item in value)


def _object_list_table(value: object) -> list[str]:
    if not isinstance(value, dict) or not value:
        return ["- none recorded"]
    lines = ["| Probe | Result |", "|---|---|"]
    for key, items in sorted(value.items()):
        lines.append(f"| {key} | {_list_cell(items)} |")
    return lines


def _object_value_table(value: object) -> list[str]:
    if not isinstance(value, dict) or not value:
        return ["- none recorded"]
    lines = ["| Metric | Value |", "|---|---:|"]
    for key, item in sorted(value.items()):
        lines.append(f"| {key} | {item} |")
    return lines
