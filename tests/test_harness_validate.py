import json

from engine_revival.validate import validate_workspace


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_base_workspace(root):
    _write_json(root / "targets" / "brender.json", {
        "id": "brender",
        "name": "Argonaut BRender",
        "category": "engine",
        "era": "1990s",
        "platforms": [],
        "priority": 89,
        "revival_lane": "critical-edition",
        "rights_posture": "open",
        "summary": "BRender target.",
        "public_status": "curated-public-sources",
        "restricted_status": "none-known",
    })
    _write_json(root / "sources" / "brender-source.json", {
        "id": "brender-source",
        "title": "BRender source",
        "source_type": "source-repository",
        "confidence": "high",
        "claim_scope": "Public BRender source release.",
    })
    _write_json(root / "artifacts" / "brender-v132-source.json", {
        "id": "brender-v132-source",
        "target_id": "brender",
        "artifact_type": "source-release",
        "title": "BRender source",
        "origin": "public repository",
        "redistribution_status": "open",
        "access_level": "public",
        "evidence_quality": "public-source",
        "source_ids": ["brender-source"],
    })
    _write_json(root / "accessions" / "brender-v132-source-planned.json", {
        "id": "brender-v132-source-planned",
        "artifact_id": "brender-v132-source",
        "package_type": "source-snapshot",
        "capture_status": "planned",
        "storage_class": "external-url",
        "fixity_status": "not-started",
        "rights_review": "open-license",
        "public_notes": "Planned public source accession.",
        "source_ids": ["brender-source"],
    })
    _write_json(root / "reproductions" / "brender-critical-edition-source-build.json", {
        "id": "brender-critical-edition-source-build",
        "target_id": "brender",
        "reproduction_type": "source-build",
        "status": "planned",
        "environment": ["public source checkout"],
        "steps": ["inspect source tree"],
        "expected_outputs": ["build harness notes"],
        "artifact_ids": ["brender-v132-source"],
        "public_notes": "Build BRender from public source.",
        "source_ids": ["brender-source"],
    })
    _write_json(root / "snapshots" / "brender-v132-main-head.json", {
        "id": "brender-v132-main-head",
        "artifact_id": "brender-v132-source",
        "snapshot_type": "git-remote-head",
        "source_url": "https://github.com/example/brender.git",
        "ref": "refs/heads/main",
        "commit": "d88d0ed41122664b9781015b517db64353e16f19",
        "retrieved_at": "2026-07-03",
        "capture_command": "git ls-remote https://github.com/example/brender.git HEAD",
        "public_notes": "Exact upstream source snapshot.",
        "source_ids": ["brender-source"],
    })
    _write_json(root / "builds" / "brender-v132-build-environment.json", {
        "id": "brender-v132-build-environment",
        "target_id": "brender",
        "reproduction_id": "brender-critical-edition-source-build",
        "status": "source-inspected",
        "host_platform": "Windows local probe",
        "source_checkout": "out-of-tree public checkout",
        "snapshot_ids": ["brender-v132-main-head"],
        "toolchain_probe": {"available": ["cmake"], "missing": ["make"]},
        "build_system": "period makefiles with BR_* environment imports",
        "required_variables": ["BR_SOURCE_DIR", "BR_MAKEFILE"],
        "observed_layout": {"makefiles": 68},
        "blockers": ["period make environment needs reconstruction"],
        "next_actions": ["create portable harness"],
        "public_notes": "Build environment inspected.",
        "source_ids": ["brender-source"],
    })
    _write_json(root / "tasks" / "brender-triage.json", {
        "id": "brender-triage",
        "target_id": "brender",
        "task_type": "triage",
        "status": "planned",
        "public_notes": "Triage BRender.",
    })
    _write_json(root / "milestones" / "brender-baseline.json", {
        "id": "brender-baseline",
        "target_id": "brender",
        "milestone_type": "baseline-public-record",
        "status": "planned",
        "evidence": "Initial public record fixture.",
        "source_ids": ["brender-source"],
    })


def _write_harness(root, **overrides):
    payload = {
        "id": "brender-v132-portable-core-plan",
        "target_id": "brender",
        "build_id": "brender-v132-build-environment",
        "reproduction_id": "brender-critical-edition-source-build",
        "status": "designed",
        "harness_type": "portable-build-plan",
        "entrypoint": "docs/generated/harnesses/brender-v132-portable-core-plan.md",
        "source_policy": "Use only the public BRender checkout; do not vendor source.",
        "implementation_units": ["core FLOAT library path"],
        "steps": ["materialize portable project files"],
        "expected_outputs": ["compiler transcript"],
        "blockers": ["first compiler run not captured"],
        "next_actions": ["emit portable CMake harness"],
        "public_notes": "Portable harness design for the BRender core path.",
        "source_ids": ["brender-source"],
    }
    payload.update(overrides)
    _write_json(root / "harnesses" / f"{payload['id']}.json", payload)


def test_valid_harness_record_passes_validation(tmp_path):
    _write_base_workspace(tmp_path)
    _write_harness(tmp_path)

    assert validate_workspace(tmp_path) == []


def test_harness_links_must_reference_known_records(tmp_path):
    _write_base_workspace(tmp_path)
    _write_harness(
        tmp_path,
        target_id="missing-target",
        build_id="missing-build",
        reproduction_id="missing-reproduction",
        source_ids=["missing-source"],
    )

    messages = validate_workspace(tmp_path)

    assert any("unknown target_id: missing-target" in message for message in messages)
    assert any("unknown build_id: missing-build" in message for message in messages)
    assert any("unknown reproduction_id: missing-reproduction" in message for message in messages)
    assert any("unknown source_id: missing-source" in message for message in messages)


def test_harness_must_include_source_ids(tmp_path):
    _write_base_workspace(tmp_path)
    _write_harness(tmp_path, source_ids=[])

    messages = validate_workspace(tmp_path)

    assert any("harness must include source_ids" in message for message in messages)
