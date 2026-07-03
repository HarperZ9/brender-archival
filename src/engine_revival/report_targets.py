from __future__ import annotations

from pathlib import Path

from engine_revival.records import RECORD_DIRS, load_records
from engine_revival.report_attempts import attempt_section
from engine_revival.report_builds import build_section
from engine_revival.report_harnesses import harness_section
from engine_revival.report_readiness import readiness_section


def _records_if_present(root: Path, kind: str) -> list[dict[str, object]]:
    directory = root / RECORD_DIRS[kind]
    if not directory.exists():
        return []
    return [record.payload for record in load_records(root, kind)]


def _source_ids_from(payloads: list[dict[str, object]]) -> set[str]:
    source_ids: set[str] = set()
    for payload in payloads:
        value = payload.get("source_ids", [])
        if isinstance(value, list):
            source_ids.update(str(source_id) for source_id in value)
    return source_ids


def _target_artifacts(root: Path, target_id: str) -> list[dict[str, object]]:
    return [
        payload for payload in _records_if_present(root, "artifact")
        if str(payload["target_id"]) == target_id
    ]


def _target_accessions(root: Path, artifacts: list[dict[str, object]]) -> list[dict[str, object]]:
    artifact_ids = {str(payload["id"]) for payload in artifacts}
    return [
        payload
        for payload in _records_if_present(root, "accession")
        if str(payload["artifact_id"]) in artifact_ids
    ]


def _target_snapshots(root: Path, artifacts: list[dict[str, object]]) -> list[dict[str, object]]:
    artifact_ids = {str(payload["id"]) for payload in artifacts}
    return [
        payload
        for payload in _records_if_present(root, "snapshot")
        if str(payload["artifact_id"]) in artifact_ids
    ]


def _target_records(root: Path, kind: str, target_id: str) -> list[dict[str, object]]:
    return [
        payload for payload in _records_if_present(root, kind)
        if str(payload["target_id"]) == target_id
    ]


def _target_sources(root: Path, records: list[dict[str, object]]) -> list[dict[str, object]]:
    source_ids = _source_ids_from(records)
    return [
        payload for payload in _records_if_present(root, "source")
        if str(payload["id"]) in source_ids
    ]


def _target_header(target: dict[str, object], target_id: str) -> list[str]:
    return [
        f"# {target['name']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Target ID | {target_id} |",
        f"| Category | {target['category']} |",
        f"| Priority | {target['priority']} |",
        f"| Rights | {target['rights_posture']} |",
        f"| Revival lane | {target['revival_lane']} |",
        f"| Public status | {target['public_status']} |",
        f"| Restricted status | {target['restricted_status']} |",
        "",
        "## Summary",
        "",
        str(target["summary"]),
    ]


def _target_artifact_section(artifacts: list[dict[str, object]]) -> list[str]:
    lines = ["", "## Artifacts", ""]
    if not artifacts:
        return lines + ["No artifact records yet."]
    lines.extend(["| Artifact | Type | Status | Access |", "|---|---|---|---|"])
    for payload in sorted(artifacts, key=lambda item: str(item["id"])):
        lines.append(
            f"| {payload['title']} | {payload['artifact_type']} | "
            f"{payload['redistribution_status']} | {payload['access_level']} |"
        )
    return lines


def _target_accession_section(accessions: list[dict[str, object]]) -> list[str]:
    lines = ["", "## Accessions", ""]
    if not accessions:
        return lines + ["No accession records yet."]
    lines.extend(["| Accession | Artifact | Capture | Storage | Rights |", "|---|---|---|---|---|"])
    for payload in sorted(accessions, key=lambda item: str(item["id"])):
        lines.append(
            f"| {payload['id']} | {payload['artifact_id']} | {payload['capture_status']} | "
            f"{payload['storage_class']} | {payload['rights_review']} |"
        )
    return lines


def _target_task_section(tasks: list[dict[str, object]]) -> list[str]:
    lines = ["", "## Tasks", ""]
    if not tasks:
        return lines + ["No task records yet."]
    lines.extend(["| Task | Type | Status | Notes |", "|---|---|---|---|"])
    for payload in sorted(tasks, key=lambda item: str(item["id"])):
        lines.append(
            f"| {payload['id']} | {payload['task_type']} | "
            f"{payload['status']} | {payload['public_notes']} |"
        )
    return lines


def _target_milestone_section(milestones: list[dict[str, object]]) -> list[str]:
    lines = ["", "## Milestones", ""]
    if not milestones:
        return lines + ["No milestone records yet."]
    lines.extend(["| Milestone | Type | Status | Evidence |", "|---|---|---|---|"])
    for payload in sorted(milestones, key=lambda item: str(item["id"])):
        lines.append(
            f"| {payload['id']} | {payload['milestone_type']} | "
            f"{payload['status']} | {payload['evidence']} |"
        )
    return lines


def _target_reproduction_section(reproductions: list[dict[str, object]]) -> list[str]:
    if not reproductions:
        return []
    lines = [
        "",
        "## Reproductions",
        "",
        "| Reproduction | Type | Status | Notes |",
        "|---|---|---|---|",
    ]
    for payload in sorted(reproductions, key=lambda item: str(item["id"])):
        lines.append(
            f"| {payload['id']} | {payload['reproduction_type']} | "
            f"{payload['status']} | {payload['public_notes']} |"
        )
    return lines


def _target_snapshot_section(snapshots: list[dict[str, object]]) -> list[str]:
    if not snapshots:
        return []
    lines = [
        "",
        "## Snapshots",
        "",
        "| Snapshot | Artifact | Ref | Commit |",
        "|---|---|---|---|",
    ]
    for payload in sorted(snapshots, key=lambda item: str(item["id"])):
        lines.append(
            f"| {payload['id']} | {payload['artifact_id']} | "
            f"{payload['ref']} | {payload['commit']} |"
        )
    return lines


def _target_source_section(sources: list[dict[str, object]]) -> list[str]:
    lines = ["", "## Evidence Sources", ""]
    if not sources:
        return lines + ["No linked source records yet."]
    lines.extend(["| Source | Type | Confidence | Scope | URL |", "|---|---|---|---|---|"])
    for payload in sorted(sources, key=lambda item: str(item["id"])):
        lines.append(
            f"| {payload['title']} | {payload['source_type']} | {payload['confidence']} | "
            f"{payload['claim_scope']} | {payload.get('url', '')} |"
        )
    return lines


def target_dossier(root: Path, target: dict[str, object]) -> str:
    target_id = str(target["id"])
    artifacts = _target_artifacts(root, target_id)
    accessions = _target_accessions(root, artifacts)
    tasks = _target_records(root, "task", target_id)
    milestones = _target_records(root, "milestone", target_id)
    reproductions = _target_records(root, "reproduction", target_id)
    readiness = _target_records(root, "readiness", target_id)
    builds = _target_records(root, "build", target_id)
    harnesses = _target_records(root, "harness", target_id)
    attempts = _target_records(root, "attempt", target_id)
    snapshots = _target_snapshots(root, artifacts)
    sources = _target_sources(
        root,
        artifacts + accessions + tasks + milestones
        + reproductions + readiness + builds + harnesses + attempts + snapshots,
    )
    lines = _target_header(target, target_id)
    lines.extend(_target_artifact_section(artifacts))
    lines.extend(_target_accession_section(accessions))
    lines.extend(readiness_section(readiness))
    lines.extend(_target_task_section(tasks))
    lines.extend(_target_milestone_section(milestones))
    lines.extend(_target_reproduction_section(reproductions))
    lines.extend(build_section(builds))
    lines.extend(harness_section(harnesses))
    lines.extend(attempt_section(attempts))
    lines.extend(_target_snapshot_section(snapshots))
    lines.extend(_target_source_section(sources))
    return "\n".join(lines) + "\n"
