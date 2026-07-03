from __future__ import annotations

from pathlib import Path

from engine_revival.records import load_records


def readiness_records(root: Path) -> list[dict[str, object]]:
    if not (root / "readiness").exists():
        return []
    return sorted(
        [record.payload for record in load_records(root, "readiness")],
        key=lambda payload: (-int(payload["flagship_score"]), str(payload["target_id"])),
    )


def readiness_by_target(
    records: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for record in records:
        grouped.setdefault(str(record["target_id"]), []).append(record)
    return grouped


def readiness_index(root: Path) -> str:
    records = readiness_records(root)
    lines = [
        "# Production Readiness",
        "",
        (
            "| Target | Stage | Build | Runtime | Tests | Package | "
            "Modernization | Score | Evidence | Next Actions |"
        ),
        "|---|---|---|---|---|---|---|---:|---|---|",
    ]
    for record in records:
        lines.append(
            f"| {record['target_id']} | {record['readiness_stage']} | "
            f"{record['build_status']} | {record['runtime_status']} | "
            f"{record['test_status']} | {record['packaging_status']} | "
            f"{record['modernization_status']} | {record['flagship_score']} | "
            f"{_evidence_cell(record)} | {_list_cell(record.get('next_actions'))} |"
        )
    if not records:
        lines.append("| none | none | none | none | none | none | none | 0 | none | none |")
    return "\n".join(lines) + "\n"


def readiness_section(records: list[dict[str, object]]) -> list[str]:
    lines = ["", "## Production Readiness", ""]
    if not records:
        return lines + ["No production-readiness record yet."]
    lines.extend(
        [
            "| Readiness | Stage | Build | Score | Next Actions |",
            "|---|---|---|---:|---|",
        ]
    )
    for record in sorted(
        records,
        key=lambda payload: (-int(payload["flagship_score"]), str(payload["id"])),
    ):
        lines.append(
            f"| {record['id']} | {record['readiness_stage']} | "
            f"{record['build_status']} | {record['flagship_score']} | "
            f"{_list_cell(record.get('next_actions'))} |"
        )
    return lines


def _evidence_cell(record: dict[str, object]) -> str:
    evidence: list[str] = []
    for key in (
        "reproduction_ids",
        "snapshot_ids",
        "build_ids",
        "harness_ids",
        "attempt_ids",
    ):
        value = record.get(key)
        if isinstance(value, list):
            evidence.extend(str(item) for item in value)
    if not evidence:
        return "none recorded"
    return "; ".join(evidence)


def _list_cell(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none recorded"
    return "; ".join(str(item) for item in value)
