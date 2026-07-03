# Accession Packages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add preservation-grade public accession metadata for planned, captured, verified, blocked, and metadata-only artifact packages.

**Architecture:** Extend the current JSON record system with an `accession` kind. Accessions link to existing artifacts and sources; raw archival masters stay outside git.

**Tech Stack:** Python 3.11+, stdlib `json/pathlib`, existing `engine_revival` package, pytest.

## Global Constraints

- Root: `C:\dev\public\engine-revival`.
- Do not download or mirror restricted SDKs, leaked source, game assets, private donor files, private contact data, credentials, or restricted media.
- Do not build the public website in this slice.
- Do not scan all of `C:\dev` in this slice.
- Do not implement a general web crawler or automatic downloader.
- Do not store archival masters in git.
- Generated docs stay under `docs/generated/`.
- Keep every edited file under 300 lines.

---

## File Structure

- Create `schemas/accession.schema.json`: accession field contract.
- Modify `src/engine_revival/records.py`: add `accession` directory mapping.
- Modify `src/engine_revival/validate.py`: accession artifact/source cross-references.
- Modify `src/engine_revival/audit.py`: accession public-safety checks.
- Modify `src/engine_revival/report.py`: generated accession summary.
- Create `accessions/*.json`: first public/open accession batch.
- Modify `tests/test_validate.py`, `tests/test_audit_public.py`, `tests/test_report.py`, `tests/test_dossier_records.py`, `tests/test_workflow_contract.py`.
- Modify `README.md`, `CONTRIBUTING.md`, `docs/RECOVERY-WORKFLOW.md`.

---

### Task 1: Add Accession Schema And Discovery

**Files:** Create `schemas/accession.schema.json`; modify `src/engine_revival/records.py`, `tests/test_validate.py`.

**Interfaces:** `RECORD_DIRS["accession"] == "accessions"`; `load_records(root, "accession") -> list[RecordFile]`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_validate.py`:

```python
import json


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_accession_workspace(root):
    _write_json(root / "targets" / "brender.json", {
        "id": "brender", "name": "Argonaut BRender", "category": "engine",
        "era": "1990s", "platforms": [], "priority": 89,
        "revival_lane": "critical-edition", "rights_posture": "open",
        "summary": "BRender target.", "public_status": "curated-public-sources",
        "restricted_status": "none-known"
    })
    _write_json(root / "sources" / "brender-source.json", {
        "id": "brender-source", "title": "BRender source",
        "source_type": "source-repository", "confidence": "high",
        "claim_scope": "Public BRender source release."
    })
    _write_json(root / "artifacts" / "brender-v132-source.json", {
        "id": "brender-v132-source", "target_id": "brender",
        "artifact_type": "source-release", "title": "BRender source",
        "origin": "public repository", "redistribution_status": "open",
        "access_level": "public", "evidence_quality": "public-source",
        "source_ids": ["brender-source"]
    })
    _write_json(root / "accessions" / "brender-v132-source-planned.json", {
        "id": "brender-v132-source-planned", "artifact_id": "brender-v132-source",
        "package_type": "source-snapshot", "capture_status": "planned",
        "storage_class": "external-url", "fixity_status": "not-started",
        "rights_review": "open-license", "public_notes": "Planned accession.",
        "source_ids": ["brender-source"]
    })


def test_valid_accession_fixture_passes_validation(tmp_path):
    _write_accession_workspace(tmp_path)
    assert validate_workspace(tmp_path) == []
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests\test_validate.py::test_valid_accession_fixture_passes_validation -q`
Expected: FAIL with missing accession schema or discovery behavior.

- [ ] **Step 3: Add schema and discovery**

Create `schemas/accession.schema.json`:

```json
{
  "kind": "accession",
  "required": ["id", "artifact_id", "package_type", "capture_status", "storage_class", "fixity_status", "rights_review", "public_notes"],
  "properties": {
    "id": "string", "artifact_id": "string", "package_type": "string",
    "capture_status": "string", "storage_class": "string",
    "fixity_status": "string", "rights_review": "string",
    "public_notes": "string", "source_ids": "array", "capture_uri": "string",
    "captured_at": "string", "captured_by": "string", "hashes": "object",
    "size_bytes": "integer", "tooling": "array", "review_notes": "string"
  }
}
```

In `src/engine_revival/records.py`, add `"accession": "accessions"` to `RECORD_DIRS`.

- [ ] **Step 4: Verify and commit**

Run: `python -m pytest tests\test_validate.py -q`
Expected: validation tests pass.
Commit: `git add schemas/accession.schema.json src/engine_revival/records.py tests/test_validate.py && git commit -m "feat: add accession record schema"`

---

### Task 2: Validate Accession References

**Files:** Modify `src/engine_revival/validate.py`, `tests/test_validate.py`.

**Interfaces:** `validate_workspace(root)` reports unknown `artifact_id` and accession `source_ids`.

- [ ] **Step 1: Write failing tests**

Append to `tests/test_validate.py`:

```python
def test_accession_artifact_id_must_reference_artifact(tmp_path):
    _write_accession_workspace(tmp_path)
    (tmp_path / "accessions" / "brender-v132-source-planned.json").unlink()
    _write_json(tmp_path / "accessions" / "bad.json", {
        "id": "bad", "artifact_id": "missing-artifact",
        "package_type": "metadata-only", "capture_status": "metadata-only",
        "storage_class": "not-held", "fixity_status": "not-applicable",
        "rights_review": "metadata-only", "public_notes": "Metadata only."
    })
    assert any("unknown artifact_id: missing-artifact" in message for message in validate_workspace(tmp_path))


def test_accession_source_ids_must_reference_sources(tmp_path):
    _write_accession_workspace(tmp_path)
    _write_json(tmp_path / "accessions" / "bad-source.json", {
        "id": "bad-source", "artifact_id": "brender-v132-source",
        "package_type": "metadata-only", "capture_status": "metadata-only",
        "storage_class": "not-held", "fixity_status": "not-applicable",
        "rights_review": "metadata-only", "public_notes": "Metadata only.",
        "source_ids": ["missing-source"]
    })
    assert any("unknown source_id: missing-source" in message for message in validate_workspace(tmp_path))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests\test_validate.py::test_accession_artifact_id_must_reference_artifact tests\test_validate.py::test_accession_source_ids_must_reference_sources -q`
Expected: FAIL because accession references are not checked.

- [ ] **Step 3: Implement reference checks**

In `validate_workspace`, compute `artifact_ids` from `records_by_kind["artifact"]`, then iterate `records_by_kind["accession"]` and append messages:

```python
f"{record.path}: unknown artifact_id: {artifact_id}"
f"{record.path}: unknown source_id: {source_id}"
```

- [ ] **Step 4: Verify and commit**

Run: `python -m pytest tests\test_validate.py -q`
Expected: validation tests pass.
Commit: `git add src/engine_revival/validate.py tests/test_validate.py && git commit -m "feat: validate accession references"`

---

### Task 3: Audit Public Accession Safety

**Files:** Modify `src/engine_revival/audit.py`, `tests/test_audit_public.py`.

**Interfaces:** `audit_public_workspace(root)` audits `accessions/` when present.

- [ ] **Step 1: Write failing tests**

Append helper and tests to `tests/test_audit_public.py`:

```python
import json


def _write_accession(path, rights_review, storage_class, fixity_status="not-started"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "id": path.stem, "artifact_id": "restricted-sdk",
        "package_type": "external-custody", "capture_status": "blocked",
        "storage_class": storage_class, "fixity_status": fixity_status,
        "rights_review": rights_review, "public_notes": "Public-safe accession."
    }, indent=2) + "\n", encoding="utf-8")


def test_restricted_accession_with_public_storage_fails_public_audit(tmp_path):
    (tmp_path / "artifacts").mkdir()
    _write_accession(tmp_path / "accessions" / "restricted-public.json", "restricted", "local-public")
    assert any("restricted accession cannot use public storage" in message for message in audit_public_workspace(tmp_path))


def test_metadata_only_restricted_accession_not_held_passes_public_audit(tmp_path):
    (tmp_path / "artifacts").mkdir()
    _write_accession(tmp_path / "accessions" / "metadata-only.json", "restricted", "not-held", "not-applicable")
    assert audit_public_workspace(tmp_path) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests\test_audit_public.py -q`
Expected: FAIL because accessions are not audited.

- [ ] **Step 3: Implement accession audit**

In `audit.py`, check accession records when `(root / "accessions").exists()`. Fail when `rights_review in {"restricted", "unknown", "rights-holder-needed"}` and `storage_class == "local-public"`. Reuse `UNSAFE_WORDS` over accession payload text.

- [ ] **Step 4: Verify and commit**

Run: `python -m pytest tests\test_audit_public.py tests\test_validate.py -q`
Expected: selected tests pass.
Commit: `git add src/engine_revival/audit.py tests/test_audit_public.py && git commit -m "feat: audit accession public safety"`

---

### Task 4: Generate Accession Report

**Files:** Modify `src/engine_revival/report.py`, `tests/test_report.py`.

**Interfaces:** `write_reports(root)` includes `docs/generated/accessions.md`.

- [ ] **Step 1: Write failing test**

Append to `tests/test_report.py`:

```python
def test_write_reports_creates_accession_summary(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "accessions").mkdir()
    (tmp_path / "artifacts" / "brender-source.json").write_text('{"id":"brender-source","target_id":"brender","artifact_type":"source-release","title":"BRender source","origin":"public","redistribution_status":"open","access_level":"public","evidence_quality":"public-source"}', encoding="utf-8")
    (tmp_path / "accessions" / "brender-source-planned.json").write_text('{"id":"brender-source-planned","artifact_id":"brender-source","package_type":"source-snapshot","capture_status":"planned","storage_class":"external-url","fixity_status":"not-started","rights_review":"open-license","public_notes":"Planned public source accession."}', encoding="utf-8")
    accessions = tmp_path / "docs" / "generated" / "accessions.md"
    assert accessions in write_reports(tmp_path)
    assert "brender-source" in accessions.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests\test_report.py::test_write_reports_creates_accession_summary -q`
Expected: FAIL because `accessions.md` is not generated.

- [ ] **Step 3: Implement report**

Add `_accession_summary(root: Path) -> str` with columns `Artifact`, `Package`, `Capture`, `Fixity`, `Storage`, `Rights`, `Notes`. Sort by `(artifact_id, id)`. Add `_write(generated / "accessions.md", _accession_summary(root))` to `write_reports`.

- [ ] **Step 4: Verify and commit**

Run: `python -m pytest tests\test_report.py -q`
Expected: report tests pass.
Commit: `git add src/engine_revival/report.py tests/test_report.py && git commit -m "feat: report accession status"`

---

### Task 5: Seed First Public Accession Batch

**Files:** Create `accessions/*.json`; modify `tests/test_dossier_records.py`, generated docs.

**Interfaces:** First accession IDs use `<artifact-id>-planned`.

- [ ] **Step 1: Write failing dossier test**

Add these paths to `tests/test_dossier_records.py`: `accessions/aqsis-renderer-source-planned.json`, `accessions/brender-3dmm-source-planned.json`, `accessions/brender-v132-source-planned.json`, `accessions/crystal-space-github-source-repository-planned.json`, `accessions/mesa-source-repository-planned.json`, `accessions/ogre-source-repository-planned.json`, `accessions/open-inventor-source-release-planned.json`, `accessions/openphigs-source-reimplementation-planned.json`, `accessions/pixie-renderer-source-mirror-planned.json`, `accessions/quesa-source-reimplementation-planned.json`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests\test_dossier_records.py -q`
Expected: FAIL listing missing accession files.

- [ ] **Step 3: Add accession records**

For each listed artifact, create:

```json
{
  "id": "<artifact-id>-planned",
  "artifact_id": "<artifact-id>",
  "package_type": "source-snapshot",
  "capture_status": "planned",
  "storage_class": "external-url",
  "fixity_status": "not-started",
  "rights_review": "open-license",
  "public_notes": "Planned accession for public/open source metadata; archival master not stored in git.",
  "source_ids": ["<existing-artifact-source-id>"]
}
```

Use `rights_review: "public-ok"` for `openphigs-source-reimplementation` and mention license review before mirroring in `public_notes`.

- [ ] **Step 4: Verify and commit**

Run: `engine-revival validate; engine-revival audit-public; engine-revival report; python -m pytest tests\test_dossier_records.py tests\test_report.py -q`
Expected: all commands exit `0`; selected tests pass.
Commit: `git add accessions tests/test_dossier_records.py docs/generated && git commit -m "feat: seed public accession records"`

---

### Task 6: Document Workflow And Run Gates

**Files:** Modify `README.md`, `CONTRIBUTING.md`, `docs/RECOVERY-WORKFLOW.md`, `tests/test_workflow_contract.py`.

**Interfaces:** Contributor docs describe accession records; workflow contract expects `accessions.md`.

- [ ] **Step 1: Add workflow assertion**

In `tests/test_workflow_contract.py`, assert:

```python
assert tmp_path / "docs" / "generated" / "accessions.md" in write_reports(tmp_path)
```

- [ ] **Step 2: Update docs**

Add `Generated accessions` to README. Add an accession-record step to `docs/RECOVERY-WORKFLOW.md`. Add a `## Accession Records` section to `CONTRIBUTING.md` stating that accession records may include public URLs, checksums, storage class, capture status, and rights review, but must not include archival masters, restricted binaries, private donor material, credentials, or private contact details.

- [ ] **Step 3: Run final verification**

Run: `python -m pytest -q`; `engine-revival validate`; `engine-revival audit-public`; `engine-revival report`; `git diff --check`; narrow secret scan over README, CONTRIBUTING, docs, sources, artifacts, accessions, and targets.
Expected: tests pass, commands exit `0`, no diff-check errors, no secret matches.

- [ ] **Step 4: Commit**

Commit: `git add README.md CONTRIBUTING.md docs tests && git commit -m "docs: document accession workflow"`

---

## Self-Review Checklist

- Task 1 covers schema/discovery.
- Task 2 covers artifact/source reference validation.
- Task 3 covers public audit rules.
- Task 4 covers generated accession reporting.
- Task 5 covers the first public/open accession batch.
- Task 6 covers docs and final gates.
- No task downloads, mirrors, or commits restricted artifacts.

