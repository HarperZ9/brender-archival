from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from engine_revival.records import RECORD_DIRS, RecordFile, load_records


@dataclass(frozen=True)
class TargetSummary:
    id: str
    name: str
    priority: int
    rights_posture: str
    revival_lane: str
    artifact_count: int
    accession_count: int
    task_count: int
    milestone_count: int


def _load_if_present(root: Path, kind: str) -> list[RecordFile]:
    if not (root / RECORD_DIRS[kind]).exists():
        return []
    return load_records(root, kind)


def build_target_index(root: Path) -> list[TargetSummary]:
    artifacts = _load_if_present(root, "artifact")
    artifact_targets = {
        str(record.payload["id"]): str(record.payload["target_id"]) for record in artifacts
    }
    artifact_counts: dict[str, int] = {}
    for target_id in artifact_targets.values():
        artifact_counts[target_id] = artifact_counts.get(target_id, 0) + 1
    accession_counts: dict[str, int] = {}
    for record in _load_if_present(root, "accession"):
        target_id = artifact_targets.get(str(record.payload["artifact_id"]))
        if target_id:
            accession_counts[target_id] = accession_counts.get(target_id, 0) + 1
    task_counts: dict[str, int] = {}
    for record in _load_if_present(root, "task"):
        target_id = str(record.payload["target_id"])
        task_counts[target_id] = task_counts.get(target_id, 0) + 1
    milestone_counts: dict[str, int] = {}
    for record in _load_if_present(root, "milestone"):
        target_id = str(record.payload["target_id"])
        milestone_counts[target_id] = milestone_counts.get(target_id, 0) + 1
    summaries = [
        TargetSummary(
            id=str(record.payload["id"]),
            name=str(record.payload["name"]),
            priority=int(record.payload["priority"]),
            rights_posture=str(record.payload["rights_posture"]),
            revival_lane=str(record.payload["revival_lane"]),
            artifact_count=artifact_counts.get(str(record.payload["id"]), 0),
            accession_count=accession_counts.get(str(record.payload["id"]), 0),
            task_count=task_counts.get(str(record.payload["id"]), 0),
            milestone_count=milestone_counts.get(str(record.payload["id"]), 0),
        )
        for record in _load_if_present(root, "target")
    ]
    return sorted(summaries, key=lambda item: (-item.priority, item.name.lower()))


def render_target_table(targets: list[TargetSummary]) -> str:
    lines = [
        "| Priority | Target | Rights | Revival lane | Artifacts | Accessions | Tasks | Milestones |",
        "|---:|---|---|---|---:|---:|---:|---:|",
    ]
    for target in targets:
        target_link = f"[{target.name}](targets/{target.id}.md)"
        lines.append(
            f"| {target.priority} | {target_link} | {target.rights_posture} | "
            f"{target.revival_lane} | {target.artifact_count} | "
            f"{target.accession_count} | {target.task_count} | {target.milestone_count} |"
        )
    return "\n".join(lines) + "\n"
