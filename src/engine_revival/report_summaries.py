from __future__ import annotations

from collections import Counter
from pathlib import Path

from engine_revival.indexer import TargetSummary
from engine_revival.records import RECORD_DIRS, load_records


def records_if_present(root: Path, kind: str) -> list[dict[str, object]]:
    directory = root / RECORD_DIRS[kind]
    if not directory.exists():
        return []
    return [record.payload for record in load_records(root, kind)]


def rights_summary(targets: list[TargetSummary]) -> str:
    counts = Counter(target.rights_posture for target in targets)
    lines = ["# Rights Summary", "", "| Rights posture | Count |", "|---|---:|"]
    for posture, count in sorted(counts.items()):
        lines.append(f"| {posture} | {count} |")
    return "\n".join(lines) + "\n"


def source_summary(root: Path) -> str:
    if not (root / "sources").exists():
        return "# Sources\n\nNo source records yet.\n"
    usage_counts = _source_usage_counts(root)
    lines = [
        "# Sources",
        "",
        "| Source | Type | Confidence | Uses | Scope | URL |",
        "|---|---|---|---:|---|---|",
    ]
    for record in load_records(root, "source"):
        payload = record.payload
        lines.append(
            f"| {payload['title']} | {payload['source_type']} | {payload['confidence']} | "
            f"{usage_counts.get(str(payload['id']), 0)} | {payload['claim_scope']} | "
            f"{payload.get('url', '')} |"
        )
    return "\n".join(lines) + "\n"


def task_summary(root: Path) -> str:
    if not (root / "tasks").exists():
        return "# Tasks\n\nNo task records yet.\n"
    lines = [
        "# Tasks",
        "",
        "| Target | Task | Type | Status | Notes |",
        "|---|---|---|---|---|",
    ]
    records = sorted(
        load_records(root, "task"),
        key=lambda record: (record.payload["target_id"], record.payload["id"]),
    )
    for record in records:
        payload = record.payload
        lines.append(
            f"| {payload['target_id']} | {payload['id']} | {payload['task_type']} | "
            f"{payload['status']} | {payload['public_notes']} |"
        )
    return "\n".join(lines) + "\n"


def milestone_summary(root: Path) -> str:
    if not (root / "milestones").exists():
        return "# Milestones\n\nNo milestone records yet.\n"
    lines = [
        "# Milestones",
        "",
        "| Target | Milestone | Type | Status | Evidence |",
        "|---|---|---|---|---|",
    ]
    records = sorted(
        load_records(root, "milestone"),
        key=lambda record: (record.payload["target_id"], record.payload["id"]),
    )
    for record in records:
        payload = record.payload
        lines.append(
            f"| {payload['target_id']} | {payload['id']} | {payload['milestone_type']} | "
            f"{payload['status']} | {payload['evidence']} |"
        )
    return "\n".join(lines) + "\n"


def coverage_summary(root: Path) -> str:
    targets = records_if_present(root, "target")
    sources = records_if_present(root, "source")
    artifacts = records_if_present(root, "artifact")
    accessions = records_if_present(root, "accession")
    tasks = records_if_present(root, "task")
    milestones = records_if_present(root, "milestone")
    target_ids = {str(payload["id"]) for payload in targets}
    source_ids = {str(payload["id"]) for payload in sources}
    used_source_ids = {
        source_id for source_id, count in _source_usage_counts(root).items() if count > 0
    }
    task_target_ids = {str(payload["target_id"]) for payload in tasks}
    milestone_target_ids = {str(payload["target_id"]) for payload in milestones}
    artifact_ids = {str(payload["id"]) for payload in artifacts}
    accession_artifact_ids = {str(payload["artifact_id"]) for payload in accessions}
    lines = [
        "# Coverage",
        "",
        "| Metric | Covered | Total |",
        "|---|---:|---:|",
        f"| Artifact accession coverage | {len(artifact_ids & accession_artifact_ids)} | {len(artifact_ids)} |",
        f"| Target task coverage | {len(target_ids & task_target_ids)} | {len(target_ids)} |",
        f"| Target milestone coverage | {len(target_ids & milestone_target_ids)} | {len(target_ids)} |",
        f"| Source usage coverage | {len(source_ids & used_source_ids)} | {len(source_ids)} |",
        "",
        "| Record kind | Count |",
        "|---|---:|",
    ]
    for kind in (
        "target",
        "source",
        "artifact",
        "accession",
        "task",
        "milestone",
        "reproduction",
        "snapshot",
        "readiness",
        "build",
        "harness",
        "attempt",
    ):
        lines.append(f"| {kind} | {len(records_if_present(root, kind))} |")
    lines.extend(_missing_section("Missing Artifact Accessions", artifact_ids - accession_artifact_ids))
    lines.extend(_missing_section("Missing Target Tasks", target_ids - task_target_ids))
    lines.extend(_missing_section("Missing Target Milestones", target_ids - milestone_target_ids))
    lines.extend(_missing_section("Unused Sources", source_ids - used_source_ids))
    return "\n".join(lines) + "\n"


def _source_usage_counts(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for kind in (
        "artifact",
        "accession",
        "task",
        "milestone",
        "reproduction",
        "snapshot",
        "readiness",
        "build",
        "harness",
        "attempt",
    ):
        for payload in records_if_present(root, kind):
            value = payload.get("source_ids", [])
            if isinstance(value, list):
                for source_id in set(str(item) for item in value):
                    counts[source_id] = counts.get(source_id, 0) + 1
    return counts


def _missing_section(title: str, missing_ids: set[str]) -> list[str]:
    lines = ["", f"## {title}", ""]
    if missing_ids:
        lines.extend(f"- `{missing_id}`" for missing_id in sorted(missing_ids))
    else:
        lines.append(f"No {title.lower()}.")
    return lines
