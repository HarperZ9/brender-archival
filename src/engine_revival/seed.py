from __future__ import annotations

import json
from pathlib import Path


INITIAL_TARGETS: tuple[dict[str, object], ...] = (
    {"id": "brender", "name": "Argonaut BRender", "category": "engine", "priority": 89, "revival_lane": "critical-edition", "rights_posture": "open"},
    {"id": "ps1-programmer-tool", "name": "PS1 Programmer's Tool / SDevTC / Net Yaroze", "category": "platform-toolchain", "priority": 84, "revival_lane": "clean-room-api-compatible", "rights_posture": "clean-room-only"},
    {"id": "renderware-ps2", "name": "RenderWare PS2", "category": "middleware", "priority": 82, "revival_lane": "compatibility-reimplementation", "rights_posture": "restricted"},
    {"id": "gool-goal", "name": "GOOL and GOAL", "category": "engine-language", "priority": 80, "revival_lane": "tooling-only-legal-copy-assets", "rights_posture": "clean-room-only"},
    {"id": "ps2-prodg-eb-linux", "name": "PS2 ProDG / EB / Linux stack", "category": "platform-toolchain", "priority": 78, "revival_lane": "clean-room-and-corporate-outreach", "rights_posture": "rights-holder-needed"},
    {"id": "tri-ace-ps2-renderer", "name": "tri-Ace PS2 renderer", "category": "rendering-technique", "priority": 74, "revival_lane": "documentation-based-reconstruction", "rights_posture": "public-reference-only"},
    {"id": "renderman-interface", "name": "RenderMan Interface", "category": "rendering-standard", "priority": 74, "revival_lane": "documentation-anchor", "rights_posture": "public-reference-only"},
    {"id": "psygnosis-studio-liverpool", "name": "Psygnosis / Studio Liverpool", "category": "studio-lineage", "priority": 73, "revival_lane": "asset-pipeline-reconstruction", "rights_posture": "public-reference-only"},
    {"id": "quickdraw-3d", "name": "QuickDraw 3D", "category": "graphics-api", "priority": 73, "revival_lane": "distribution-media-recovery", "rights_posture": "public-reference-only"},
    {"id": "open-inventor", "name": "Open Inventor", "category": "graphics-library", "priority": 72, "revival_lane": "public-source-preservation", "rights_posture": "open"},
    {"id": "mesa", "name": "Mesa", "category": "graphics-library", "priority": 72, "revival_lane": "public-source-preservation", "rights_posture": "open"},
    {"id": "ogre", "name": "OGRE", "category": "engine", "priority": 72, "revival_lane": "public-source-preservation", "rights_posture": "open"},
    {"id": "softimage-alias-bridge", "name": "Softimage / Alias bridge", "category": "dcc-pipeline", "priority": 71, "revival_lane": "pipeline-history", "rights_posture": "public-reference-only"},
    {"id": "quesa", "name": "Quesa", "category": "compatibility-library", "priority": 70, "revival_lane": "public-source-preservation", "rights_posture": "open"},
    {"id": "japan-studio-team-ico", "name": "Japan Studio / Team Ico", "category": "studio-lineage", "priority": 69, "revival_lane": "oral-history-and-binary-archaeology", "rights_posture": "restricted"},
    {"id": "crystal-space", "name": "Crystal Space", "category": "engine", "priority": 68, "revival_lane": "public-source-preservation", "rights_posture": "open"},
    {"id": "iris-gl-opengl-bridge", "name": "IRIS GL / OpenGL bridge", "category": "graphics-lineage", "priority": 68, "revival_lane": "upstream-dependency-atlas", "rights_posture": "public-reference-only"},
    {"id": "aqsis", "name": "Aqsis", "category": "renderer", "priority": 66, "revival_lane": "public-source-preservation", "rights_posture": "open"},
    {"id": "pixie", "name": "Pixie", "category": "renderer", "priority": 65, "revival_lane": "public-source-preservation", "rights_posture": "open"},
    {"id": "phigs", "name": "PHIGS", "category": "graphics-standard", "priority": 62, "revival_lane": "upstream-dependency-atlas", "rights_posture": "public-reference-only"},
    {"id": "reality-lab", "name": "RenderMorphics Reality Lab", "category": "middleware", "priority": 77, "revival_lane": "private-lead-public-metadata", "rights_posture": "rights-holder-needed"},
    {"id": "opengl-performer", "name": "OpenGL Performer", "category": "graphics-library", "priority": 76, "revival_lane": "partial-public-archive", "rights_posture": "public-reference-only"},
)


def _write_json(path: Path, payload: dict[str, object]) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return True


def _target_payload(target: dict[str, object]) -> dict[str, object]:
    rights = str(target["rights_posture"])
    restricted = "none-known" if rights == "open" else "metadata-only"
    return {
        **target,
        "era": "1980s-2000s",
        "platforms": [],
        "summary": f"Seed public record for {target['name']}.",
        "public_status": "seeded",
        "restricted_status": restricted,
        "related_targets": [],
    }


def _task_payload(target: dict[str, object]) -> dict[str, object]:
    target_id = str(target["id"])
    return {
        "id": f"{target_id}-triage",
        "target_id": target_id,
        "task_type": "triage-public-record",
        "status": "seeded",
        "public_notes": f"Create public-safe sources and artifact records for {target['name']}.",
    }


def _milestone_payload(target: dict[str, object]) -> dict[str, object]:
    target_id = str(target["id"])
    return {
        "id": f"{target_id}-baseline",
        "target_id": target_id,
        "milestone_type": "baseline-public-record",
        "status": "seeded",
        "evidence": f"Initial public-safe revival record created for {target['name']}.",
        "source_ids": ["initial-research-reports"],
    }


def _readiness_payload(target: dict[str, object]) -> dict[str, object]:
    target_id = str(target["id"])
    return {
        "id": f"{target_id}-production-readiness",
        "target_id": target_id,
        "readiness_stage": "baseline-assessment",
        "build_status": "not-started",
        "runtime_status": "not-started",
        "test_status": "not-started",
        "packaging_status": "not-started",
        "modernization_status": "not-started",
        "flagship_score": 0,
        "blockers": ["production rebuild path not yet verified"],
        "next_actions": ["create repeatable build harness"],
        "public_notes": (
            f"Baseline production-readiness record for {target['name']}. "
            "No flagship-quality claim is made until build, runtime, tests, "
            "packaging, and modernization evidence are recorded."
        ),
        "source_ids": ["initial-research-reports"],
    }


def seed_workspace(root: Path) -> list[Path]:
    written: list[Path] = []
    source = {
        "id": "initial-research-reports",
        "title": "Initial engine revival research reports",
        "source_type": "local-research-summary",
        "confidence": "moderate",
        "claim_scope": "initial target selection",
        "notes": "Replace seed source with public citations during curation.",
    }
    if _write_json(root / "sources" / "initial-research-reports.json", source):
        written.append(root / "sources" / "initial-research-reports.json")
    for target in INITIAL_TARGETS:
        target_path = root / "targets" / f"{target['id']}.json"
        task_path = root / "tasks" / f"{target['id']}-triage.json"
        milestone_path = root / "milestones" / f"{target['id']}-baseline.json"
        readiness_path = root / "readiness" / f"{target['id']}-production-readiness.json"
        if _write_json(target_path, _target_payload(target)):
            written.append(target_path)
        if _write_json(task_path, _task_payload(target)):
            written.append(task_path)
        if _write_json(milestone_path, _milestone_payload(target)):
            written.append(milestone_path)
        if _write_json(readiness_path, _readiness_payload(target)):
            written.append(readiness_path)
    return written
