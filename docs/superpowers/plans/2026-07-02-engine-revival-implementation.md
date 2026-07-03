# Engine Revival Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first public tooling spine for `engine-revival`: schemas, CLI validation, public-safety audit, seeded records, generated indexes, and tests.

**Architecture:** Use a small `src/engine_revival` Python package. JSON records live in top-level record directories. Generated public docs live in `docs/generated/`.

**Tech Stack:** Python 3.11+, setuptools `src/` layout, stdlib `argparse/json/pathlib/dataclasses`, `pytest>=8`; no runtime dependencies in the first slice.

## Global Constraints

- Root: `C:\dev\public\engine-revival`.
- Never publish proprietary SDK binaries, leaked source, game assets, private donor material, private contact data, credentials, or restricted media.
- Initial record format: JSON.
- Initial CLI commands: `seed`, `validate`, `audit-public`, `index`, `report`.
- Controlled labels: `open`, `public-reference-only`, `restricted`, `unknown`, `clean-room-only`, `rights-holder-needed`, `do-not-redistribute`.
- Generated docs: `docs/generated/`.
- Tests must prove unsafe publication states are caught.

---

## File Structure

- `README.md`, `AGENTS.md`, `.gitignore`, `LICENSE`, `pyproject.toml`: public repo shell.
- `src/engine_revival/cli.py`: command dispatch and exit codes.
- `src/engine_revival/schema.py`: schema loading and required-field checks.
- `src/engine_revival/records.py`: JSON record discovery.
- `src/engine_revival/validate.py`: schema validation and cross-reference checks.
- `src/engine_revival/audit.py`: public boundary audit.
- `src/engine_revival/seed.py`: initial record generation.
- `src/engine_revival/indexer.py`, `src/engine_revival/report.py`: summaries.
- `schemas/*.json`, `targets/*.json`, `sources/*.json`, `tasks/*.json`: records.
- `tests/`: pytest coverage and fixtures.

---

### Task 1: Bootstrap Package And CLI Shell

**Files:** Create `README.md`, `AGENTS.md`, `.gitignore`, `LICENSE`, `pyproject.toml`, `src/engine_revival/__init__.py`, `src/engine_revival/cli.py`, `tests/test_cli_smoke.py`.

**Interfaces:** `engine_revival.cli.main(argv: Sequence[str] | None = None) -> int`; console script `engine-revival`.

- [ ] **Step 1: Write failing tests**

```python
from engine_revival.cli import main

def test_main_help_exits_zero(capsys):
    assert main(["--help"]) == 0
    assert "validate" in capsys.readouterr().out

def test_unknown_command_exits_nonzero(capsys):
    assert main(["not-a-command"]) == 2
    assert "invalid choice" in capsys.readouterr().err
```

- [ ] **Step 2: Run failing test**

Run: `python -m pytest tests/test_cli_smoke.py -q`
Expected: FAIL because `engine_revival` does not exist.

- [ ] **Step 3: Implement shell**

`pyproject.toml`: setuptools, `requires-python = ">=3.11"`, `dependencies = []`, optional `test = ["pytest>=8"]`, script `engine-revival = "engine_revival.cli:main"`. `cli.py`: `argparse`, subcommands `seed/validate/audit-public/index/report`, return `0` for parsed commands and `2` for parser errors. `README.md` states purpose, public boundary, and first workflow. `AGENTS.md` repeats never-commit rules and gates. `.gitignore` includes `.env`, `.env.*`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `*.egg-info/`, `build/`, `dist/`.

- [ ] **Step 4: Verify and commit**

Run: `python -m pytest tests/test_cli_smoke.py -q`
Expected: `2 passed`.
Commit: `git add README.md AGENTS.md .gitignore LICENSE pyproject.toml src tests && git commit -m "feat: bootstrap engine revival cli"`

---

### Task 2: Schemas And Schema Loader

**Files:** Create `schemas/{target,artifact,source,task,milestone}.schema.json`, `src/engine_revival/schema.py`, `tests/test_schema_loader.py`.

**Interfaces:** `SchemaSpec(kind: str, required: tuple[str, ...], properties: dict[str, str])`; `load_schema(root: Path, kind: str) -> SchemaSpec`; `validate_required_fields(record: dict[str, object], schema: SchemaSpec) -> list[str]`.

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path
from engine_revival.schema import load_schema, validate_required_fields
ROOT = Path(__file__).resolve().parents[1]

def test_load_target_schema_required_fields():
    schema = load_schema(ROOT, "target")
    assert {"id", "rights_posture"} <= set(schema.required)

def test_validate_required_fields_reports_missing_keys():
    assert "target missing required field: name" in validate_required_fields({"id": "brender"}, load_schema(ROOT, "target"))
```

- [ ] **Step 2: Run failing test**

Run: `python -m pytest tests/test_schema_loader.py -q`
Expected: FAIL because schemas and loader do not exist.

- [ ] **Step 3: Implement schemas and loader**

Each schema JSON contains `kind`, `required`, `properties`. Required fields: target `id/name/category/era/platforms/priority/revival_lane/rights_posture/summary/public_status/restricted_status`; artifact `id/target_id/artifact_type/title/origin/redistribution_status/access_level/evidence_quality`; source `id/title/source_type/confidence/claim_scope`; task `id/target_id/task_type/status/public_notes`; milestone `id/target_id/milestone_type/status/evidence`. `schema.py` loads JSON and reports missing required fields as `<kind> missing required field: <field>`.

- [ ] **Step 4: Verify and commit**

Run: `python -m pytest tests/test_schema_loader.py -q`
Expected: `2 passed`.
Commit: `git add schemas src/engine_revival/schema.py tests/test_schema_loader.py && git commit -m "feat: add archive record schemas"`

---

### Task 3: Record Discovery And Validation

**Files:** Create `src/engine_revival/records.py`, `src/engine_revival/validate.py`, `tests/fixtures/valid-mini/{targets,artifacts,sources}/`, `tests/test_validate.py`; modify `src/engine_revival/cli.py`.

**Interfaces:** `RecordFile(kind: str, path: Path, payload: dict[str, object])`; `load_records(root: Path, kind: str) -> list[RecordFile]`; `validate_workspace(root: Path) -> list[str]`.

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path
from engine_revival.validate import validate_workspace
ROOT = Path(__file__).resolve().parents[1]

def test_valid_fixture_has_no_validation_errors():
    assert validate_workspace(ROOT / "tests" / "fixtures" / "valid-mini") == []

def test_repo_without_records_reports_missing_directories(tmp_path):
    assert "missing record directory: targets" in validate_workspace(tmp_path)
```

- [ ] **Step 2: Implement validation**

Create valid fixture records for BRender target, one artifact, and one source. `records.py` defines `RECORD_DIRS = {"target": "targets", "artifact": "artifacts", "source": "sources", "task": "tasks", "milestone": "milestones"}` and loads sorted `*.json`. `validate.py` checks required directories, required fields, and artifact/task/milestone `target_id` references. CLI `validate` prints errors and exits `1` when errors exist.

- [ ] **Step 3: Verify and commit**

Run: `python -m pytest tests/test_validate.py tests/test_cli_smoke.py -q`
Expected: selected tests pass.
Commit: `git add src tests && git commit -m "feat: validate archive records"`

---

### Task 4: Public-Safety Audit

**Files:** Create `src/engine_revival/audit.py`, `tests/fixtures/unsafe-records/artifacts/restricted-sdk.json`, `tests/test_audit_public.py`; modify `src/engine_revival/cli.py`.

**Interfaces:** `audit_public_workspace(root: Path) -> list[str]`.

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path
from engine_revival.audit import audit_public_workspace
ROOT = Path(__file__).resolve().parents[1]

def test_valid_fixture_passes_public_audit():
    assert audit_public_workspace(ROOT / "tests" / "fixtures" / "valid-mini") == []

def test_restricted_publishable_artifact_fails_public_audit():
    messages = audit_public_workspace(ROOT / "tests" / "fixtures" / "unsafe-records")
    assert any("restricted material cannot be publishable" in message for message in messages)
```

- [ ] **Step 2: Implement audit**

Unsafe fixture uses `redistribution_status: "restricted"` and `access_level: "publishable"`. Audit fails when restricted labels `restricted/unknown/rights-holder-needed/do-not-redistribute` combine with levels `public/publishable/downloadable`. It also fails phrases `upload included`, `download the sdk`, `leaked source`, `private contact`. CLI `audit-public` prints messages and exits `1` on failures.

- [ ] **Step 3: Verify and commit**

Run: `python -m pytest tests/test_audit_public.py tests/test_validate.py tests/test_cli_smoke.py -q`
Expected: selected tests pass.
Commit: `git add src tests && git commit -m "feat: audit public archive records"`

---

### Task 5: Seed Initial Target Records

**Files:** Create `src/engine_revival/seed.py`, `tests/test_seed.py`; modify `src/engine_revival/cli.py`; generated `targets/*.json`, `sources/*.json`, `tasks/*.json`.

**Interfaces:** `INITIAL_TARGETS: tuple[dict[str, object], ...]`; `seed_workspace(root: Path) -> list[Path]`.

- [ ] **Step 1: Write failing tests**

```python
import json
from engine_revival.seed import INITIAL_TARGETS, seed_workspace

def test_initial_targets_include_required_research_targets():
    ids = {str(target["id"]) for target in INITIAL_TARGETS}
    assert {"brender", "renderware-ps2", "ps1-programmer-tool", "opengl-performer"} <= ids
    assert len(ids) == 22

def test_seed_workspace_writes_target_records(tmp_path):
    written = seed_workspace(tmp_path)
    payload = json.loads((tmp_path / "targets" / "brender.json").read_text(encoding="utf-8"))
    assert tmp_path / "targets" / "brender.json" in written
    assert payload["rights_posture"] == "open"
```

- [ ] **Step 2: Implement seed**

IDs: `brender`, `ps1-programmer-tool`, `renderware-ps2`, `gool-goal`, `ps2-prodg-eb-linux`, `tri-ace-ps2-renderer`, `psygnosis-studio-liverpool`, `japan-studio-team-ico`, `open-inventor`, `quesa`, `mesa`, `crystal-space`, `ogre`, `aqsis`, `pixie`, `reality-lab`, `opengl-performer`, `quickdraw-3d`, `renderman-interface`, `phigs`, `iris-gl-opengl-bridge`, `softimage-alias-bridge`. Expand defaults for `era`, `platforms`, `summary`, `public_status`, `restricted_status`, `related_targets`. `seed` writes missing files and never overwrites edited records.

- [ ] **Step 3: Verify and commit**

Run: `engine-revival seed; engine-revival validate; engine-revival audit-public; python -m pytest tests/test_seed.py tests/test_validate.py tests/test_audit_public.py -q`
Expected: all commands exit `0`; selected tests pass.
Commit: `git add src tests targets sources tasks && git commit -m "feat: seed initial revival targets"`

---

### Task 6: Index And Report Generation

**Files:** Create `src/engine_revival/indexer.py`, `src/engine_revival/report.py`, `tests/test_report.py`; modify `src/engine_revival/cli.py`; generated `docs/generated/index.md`, `docs/generated/targets.md`, `docs/generated/rights-summary.md`.

**Interfaces:** `TargetSummary(id: str, name: str, priority: int, rights_posture: str, revival_lane: str)`; `build_target_index(root: Path) -> list[TargetSummary]`; `write_reports(root: Path) -> list[Path]`.

- [ ] **Step 1: Write failing test**

```python
from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace

def test_write_reports_creates_public_index(tmp_path):
    seed_workspace(tmp_path)
    index = tmp_path / "docs" / "generated" / "index.md"
    assert index in write_reports(tmp_path)
    assert "Argonaut BRender" in index.read_text(encoding="utf-8")
```

- [ ] **Step 2: Implement reports**

Sort targets by descending priority then name. Generated docs start with `<!-- generated by engine-revival report -->`. `index` prints a Markdown table to stdout. `report` writes generated docs and prints each path.

- [ ] **Step 3: Verify and commit**

Run: `engine-revival validate; engine-revival audit-public; engine-revival index; engine-revival report; python -m pytest tests/test_report.py tests/test_seed.py tests/test_validate.py tests/test_audit_public.py -q`
Expected: all commands exit `0`; selected tests pass.
Commit: `git add src tests docs/generated && git commit -m "feat: generate public revival reports"`

---

### Task 7: Final Docs And Integration Gate

**Files:** Create `CONTRIBUTING.md`, `docs/PUBLIC-BOUNDARY.md`, `docs/RECOVERY-WORKFLOW.md`, `tests/test_workflow_contract.py`; modify `README.md`.

**Interfaces:** consumes all CLI commands; produces end-to-end public archive contract test.

- [ ] **Step 1: Write workflow contract test**

```python
from engine_revival.audit import audit_public_workspace
from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace
from engine_revival.validate import validate_workspace

def test_seeded_public_archive_contract(tmp_path):
    seed_workspace(tmp_path)
    assert validate_workspace(tmp_path) == []
    assert audit_public_workspace(tmp_path) == []
    assert tmp_path / "docs" / "generated" / "index.md" in write_reports(tmp_path)
```

- [ ] **Step 2: Add docs**

`CONTRIBUTING.md` explains adding records, choosing rights labels, and submitting public leads. `docs/PUBLIC-BOUNDARY.md` repeats allowed and disallowed material from the spec. `docs/RECOVERY-WORKFLOW.md` lists: identify source, create source record, create target/artifact record, validate, audit, report, review. `README.md` links those docs plus generated index files.

- [ ] **Step 3: Verify and commit**

Run: `engine-revival validate; engine-revival audit-public; engine-revival report; python -m pytest -q`
Expected: all commands exit `0`; all tests pass.
Commit: `git add README.md CONTRIBUTING.md docs tests && git commit -m "docs: document public archive workflow"`

---

## Self-Review Checklist

- Tasks cover bootstrap, schemas, validation, public audit, seeding, reports, docs, and verification.
- Public boundary is enforced in Task 4 and documented in Task 7.
- Task 5 includes all 22 approved targets.
- Interfaces use consistent `Path`, `list[str]`, `list[Path]`, and dataclass naming.
- Plan stays under the 300-line workspace gate.
