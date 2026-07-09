# BRender Evidence Consistency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make BRender's verified 12/12 portable-core checkpoint consistent across canonical records and enforce future cross-record agreement through `engine-revival validate`, then mirror the reviewed result into `brender-archival`.

**Architecture:** Add one optional `evidence_checkpoint` object to five existing record kinds and a generic validator that groups checkpoint-bearing records by checkpoint ID. Reconcile the five BRender state records and archival narrative against the same checkpoint, regenerate deterministic reports, and copy only reviewed shared files into the downstream mirror.

**Tech Stack:** Python 3.11+, pytest, JSON record schemas, the existing `engine_revival` CLI/report pipeline, Git worktrees, PowerShell.

## Global Constraints

- Canonical implementation repo: `C:\dev\worktrees\engine-revival-brender-evidence` on `fix/brender-evidence-consistency`.
- Activate an isolated environment for the active worktree, ensure that worktree is installed editable as documented in its `README.md`, use the canonical `engine-revival` console entry point, and verify the executable and imported module paths resolve to that worktree before running commands.
- Do not modify `C:\dev\local-model`, `E:\local-model-run`, `public/index`, `forum`, `gather`, `crucible`, `telos`, `mneme`, `relay`, `plexus`, `telos-v2`, `portfolio-site`, or `profile`.
- Never print live Claude child-process command lines or the exposed Hugging Face credential.
- Preserve historical `attempts/brender-v132-*.json` and external transcripts byte-for-byte.
- Do not claim x64, period `softrend`, native material resolution, FIXED variants, drivers, packaged release binaries, or a full viewer.
- `brender-archival` preserves its README, LICENSE, `pyproject.toml`, and gallery.
- No push, merge, release, or PR creation in this plan.

---

### Task 1: Add the reusable evidence-checkpoint validator

**Files:**

- Create: `tests/test_evidence_checkpoint_validate.py`
- Modify: `src/engine_revival/validate.py`
- Modify: `schemas/task.schema.json`
- Modify: `schemas/reproduction.schema.json`
- Modify: `schemas/build.schema.json`
- Modify: `schemas/harness.schema.json`
- Modify: `schemas/readiness.schema.json`

**Interfaces:**

- Consumes: `dict[str, list[RecordFile]]` already assembled by `validate_workspace()`.
- Produces: `_validate_evidence_checkpoints(records_by_kind) -> list[str]` and optional schema field `evidence_checkpoint: object`.
- Checkpoint fields: `id`, `stage`, `passed`, `total`, `source_snapshot`.

- [ ] **Step 1: Write the failing validator tests**

Create `tests/test_evidence_checkpoint_validate.py`:

```python
import json

from engine_revival.validate import validate_workspace


CHECKPOINT = {
    "id": "brender-v132-portable-core-plotter-2026-07-03",
    "stage": "portable-core-plotter-lane-passing",
    "passed": 12,
    "total": 12,
    "source_snapshot": "d88d0ed41122664b9781015b517db64353e16f19",
}


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_workspace(root, first_checkpoint, second_checkpoint):
    _write_json(root / "targets" / "brender.json", {
        "id": "brender",
        "name": "Argonaut BRender",
        "category": "engine",
        "era": "1990s",
        "platforms": ["Windows"],
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
    _write_json(root / "tasks" / "brender-first.json", {
        "id": "brender-first",
        "target_id": "brender",
        "task_type": "verification",
        "status": "verified",
        "public_notes": "First checkpoint carrier.",
        "evidence_checkpoint": first_checkpoint,
    })
    _write_json(root / "tasks" / "brender-second.json", {
        "id": "brender-second",
        "target_id": "brender",
        "task_type": "verification",
        "status": "verified",
        "public_notes": "Second checkpoint carrier.",
        "evidence_checkpoint": second_checkpoint,
    })
    _write_json(root / "milestones" / "brender-baseline.json", {
        "id": "brender-baseline",
        "target_id": "brender",
        "milestone_type": "baseline-public-record",
        "status": "curated",
        "evidence": "Initial public record fixture.",
        "source_ids": ["brender-source"],
    })


def _checkpoint_messages(root):
    return [message for message in validate_workspace(root) if "evidence_checkpoint" in message]


def test_matching_evidence_checkpoints_validate(tmp_path):
    _write_workspace(tmp_path, CHECKPOINT, CHECKPOINT.copy())
    assert _checkpoint_messages(tmp_path) == []


def test_mismatched_evidence_checkpoint_field_fails(tmp_path):
    mismatched = {**CHECKPOINT, "total": 11}
    _write_workspace(tmp_path, CHECKPOINT, mismatched)
    messages = _checkpoint_messages(tmp_path)
    assert any("field total differs" in message for message in messages)
    assert any(CHECKPOINT["id"] in message for message in messages)


def test_invalid_evidence_checkpoint_bounds_fail(tmp_path):
    invalid = {**CHECKPOINT, "passed": 13}
    _write_workspace(tmp_path, invalid, invalid.copy())
    assert any("passed must be <= total" in message for message in _checkpoint_messages(tmp_path))


def test_evidence_checkpoint_rejects_missing_and_unexpected_fields(tmp_path):
    malformed = {key: value for key, value in CHECKPOINT.items() if key != "stage"}
    malformed["note"] = "not part of the contract"
    _write_workspace(tmp_path, malformed, malformed.copy())
    messages = _checkpoint_messages(tmp_path)
    assert any("missing field: stage" in message for message in messages)
    assert any("unexpected field: note" in message for message in messages)
```

- [ ] **Step 2: Run the tests to verify RED**

Run:

```powershell
python -m pytest tests/test_evidence_checkpoint_validate.py -q
```

Expected: the mismatch, bounds, and shape tests fail because the validator does not inspect `evidence_checkpoint`; the matching case may already pass.

- [ ] **Step 3: Declare the optional schema field**

In each of the five schema files, add this property inside `properties`:

```json
"evidence_checkpoint": "object"
```

Do not add it to `required`; existing records remain valid.

- [ ] **Step 4: Implement the minimal generic validator**

Add below `_validate_source_ids_present()` in `src/engine_revival/validate.py`:

```python
CHECKPOINT_KINDS = ("task", "reproduction", "build", "harness", "readiness")
CHECKPOINT_FIELDS = ("id", "stage", "passed", "total", "source_snapshot")
CHECKPOINT_STRING_FIELDS = ("id", "stage", "source_snapshot")


def _validate_evidence_checkpoints(
    records_by_kind: dict[str, list[RecordFile]],
) -> list[str]:
    messages: list[str] = []
    first_by_id: dict[str, tuple[RecordFile, dict[str, object]]] = {}

    for kind in CHECKPOINT_KINDS:
        for record in records_by_kind[kind]:
            checkpoint = record.payload.get("evidence_checkpoint")
            if checkpoint is None:
                continue
            if not isinstance(checkpoint, dict):
                continue  # _validate_types already reports this.

            missing = [field for field in CHECKPOINT_FIELDS if field not in checkpoint]
            unexpected = sorted(set(checkpoint) - set(CHECKPOINT_FIELDS))
            for field in missing:
                messages.append(
                    f"{record.path}: evidence_checkpoint missing field: {field}"
                )
            for field in unexpected:
                messages.append(
                    f"{record.path}: evidence_checkpoint unexpected field: {field}"
                )
            if missing or unexpected:
                continue

            shape_valid = True
            for field in CHECKPOINT_STRING_FIELDS:
                value = checkpoint[field]
                if not isinstance(value, str) or not value.strip():
                    messages.append(
                        f"{record.path}: evidence_checkpoint {field} must be non-empty string"
                    )
                    shape_valid = False
            for field in ("passed", "total"):
                value = checkpoint[field]
                if not isinstance(value, int) or isinstance(value, bool):
                    messages.append(
                        f"{record.path}: evidence_checkpoint {field} must be integer"
                    )
                    shape_valid = False
            if not shape_valid:
                continue

            passed = int(checkpoint["passed"])
            total = int(checkpoint["total"])
            if total <= 0:
                messages.append(
                    f"{record.path}: evidence_checkpoint total must be > 0"
                )
            if passed < 0:
                messages.append(
                    f"{record.path}: evidence_checkpoint passed must be >= 0"
                )
            if passed > total:
                messages.append(
                    f"{record.path}: evidence_checkpoint passed must be <= total"
                )

            checkpoint_id = str(checkpoint["id"])
            first = first_by_id.get(checkpoint_id)
            if first is None:
                first_by_id[checkpoint_id] = (record, checkpoint)
                continue
            first_record, first_checkpoint = first
            for field in CHECKPOINT_FIELDS[1:]:
                if checkpoint[field] != first_checkpoint[field]:
                    messages.append(
                        f"{record.path}: evidence_checkpoint {checkpoint_id} field {field} "
                        f"differs from {first_record.path}: "
                        f"{checkpoint[field]!r} != {first_checkpoint[field]!r}"
                    )
    return messages
```

Call it immediately after all record kinds have been loaded in `validate_workspace()`:

```python
    messages.extend(_validate_evidence_checkpoints(records_by_kind))
```

- [ ] **Step 5: Run targeted and regression tests to verify GREEN**

Run:

```powershell
python -m pytest tests/test_evidence_checkpoint_validate.py tests/test_validate.py tests/test_cli_smoke.py -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit Task 1**

```powershell
git add schemas/task.schema.json schemas/reproduction.schema.json schemas/build.schema.json schemas/harness.schema.json schemas/readiness.schema.json src/engine_revival/validate.py tests/test_evidence_checkpoint_validate.py
git diff --cached --check
git commit -m "feat: validate shared evidence checkpoints"
```

---

### Task 2: Reconcile the canonical BRender state

**Files:**

- Create: `tests/test_brender_state_consistency.py`
- Modify: `tasks/brender-critical-edition-packet.json`
- Modify: `reproductions/brender-critical-edition-source-build.json`
- Modify: `builds/brender-v132-build-environment.json`
- Modify: `harnesses/brender-v132-portable-core-plan.json`
- Modify: `readiness/brender-production-readiness.json`
- Modify: `docs/BRENDER-ARCHIVAL.md`
- Regenerate: BRender-related files under `docs/generated/` plus `docs/generated/database.json`

**Interfaces:**

- Consumes: the generic checkpoint contract from Task 1 and historical attempt/transcript evidence already referenced by readiness.
- Produces: five aligned checkpoint-bearing records and current generated public views.

- [ ] **Step 1: Write the failing repository-state test**

Create `tests/test_brender_state_consistency.py`:

```python
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CHECKPOINT = {
    "id": "brender-v132-portable-core-plotter-2026-07-03",
    "stage": "portable-core-plotter-lane-passing",
    "passed": 12,
    "total": 12,
    "source_snapshot": "d88d0ed41122664b9781015b517db64353e16f19",
}
STATE_PATHS = (
    "tasks/brender-critical-edition-packet.json",
    "reproductions/brender-critical-edition-source-build.json",
    "builds/brender-v132-build-environment.json",
    "harnesses/brender-v132-portable-core-plan.json",
    "readiness/brender-production-readiness.json",
)


def _load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_brender_state_records_share_verified_plotter_checkpoint():
    for relative in STATE_PATHS:
        assert _load(relative)["evidence_checkpoint"] == EXPECTED_CHECKPOINT, relative


def test_brender_current_statuses_match_verified_scope():
    assert _load(STATE_PATHS[0])["status"] == "portable-render-lane-published"
    assert _load(STATE_PATHS[1])["status"] == "v132-portable-core-verified-3dmm-pending"
    assert _load(STATE_PATHS[2])["status"] == "portable-core-plotter-lane-passing"
    assert _load(STATE_PATHS[3])["status"] == "portable-core-plotter-lane-passing"
    readiness = _load(STATE_PATHS[4])
    assert readiness["build_status"] == "portable-core-plotter-lane-built"
    assert readiness["flagship_score"] == 86
    assert readiness["packaging_status"] == "not-started"


def test_brender_public_packet_describes_twelve_rungs_without_stale_deferral():
    task = _load(STATE_PATHS[0])
    assert "twelve verifying" in task["public_notes"]
    assert "CTest 12/12" in task["public_notes"]
    assert "score 86" in task["public_notes"]
    assert "eight verifying" not in task["public_notes"]
    assert all("eight verifying" not in output for output in task["outputs"])

    packet = (ROOT / "docs/BRENDER-ARCHIVAL.md").read_text(encoding="utf-8")
    assert "twelve self-verifying render smokes" in packet
    deferred = packet.split("## Honestly deferred", 1)[1].split("## Records", 1)[0]
    assert "Multi-part datafile assembly" not in deferred
```

- [ ] **Step 2: Run the state test to verify RED**

Run:

```powershell
python -m pytest tests/test_brender_state_consistency.py -q
```

Expected: failures report missing checkpoints, stale statuses, and the eight-rung narrative.

- [ ] **Step 3: Add the identical checkpoint to all five records**

Add exactly this object to each record:

```json
"evidence_checkpoint": {
  "id": "brender-v132-portable-core-plotter-2026-07-03",
  "stage": "portable-core-plotter-lane-passing",
  "passed": 12,
  "total": 12,
  "source_snapshot": "d88d0ed41122664b9781015b517db64353e16f19"
}
```

- [ ] **Step 4: Reconcile record-specific status and narrative**

Apply these exact status values:

```text
task.status = portable-render-lane-published
reproduction.status = v132-portable-core-verified-3dmm-pending
build.status = portable-core-plotter-lane-passing
harness.status = portable-core-plotter-lane-passing
readiness.build_status = portable-core-plotter-lane-built
readiness.packaging_status = not-started
readiness.flagship_score = 86
```

The task public note must state:

```text
The BRender critical-edition portable pure-C render lane is published as the standalone brender-archival repository. From the pinned public v1.3.2 snapshot at d88d0ed41122664b9781015b517db64353e16f19, the engine-revival materializer builds the FLOAT core library and twelve verifying CTest rungs: vector math, framework startup, wireframe, v1db scene graph, flat fill, depth buffering, perspective-correct texturing, native datafile model loading, UV material rendering, multi-part loading, Gouraud shading, and hidden-line SVG plotter output. CTest 12/12 passed and readiness score 86 is recorded. Deferred work remains explicit: x64 pointer-width portability, period softrend translation, native .mat/.pal/.pix resolution, semantic compatibility-stub coverage, FIXED variants, drivers, packaged release binaries, and a full viewer.
```

Use this exact task output label:

```text
twelve verifying render smokes (vector math through hidden-line plotter)
```

The reproduction public note must say the v1.3.2 portable-core lane is verified
through 12/12 CTest, while the separate 3D Movie Maker branch attempt remains
pending. Keep the unexecuted 3D Movie Maker step in `steps` and do not call the
whole recipe complete.

The build and harness notes must enumerate the 12-rung coverage and retain the
real limitations. Replace the build's startup-only blocker with:

```text
runtime coverage reaches the twelve-rung portable-core ladder through plotter output; semantic compatibility-stub coverage, drivers, period softrend, and full renderer parity are not covered
```

Add these missing harness expected outputs before `driver variant build matrix`:

```json
"UV-material render smoke executable, PPM image, and CTest transcript",
"multi-part datafile render smoke executable, PPM image, and CTest transcript",
"Gouraud render smoke executable, PPM image, and CTest transcript",
"hidden-line plotter smoke executable, SVG/PPM images, and CTest transcript"
```

Replace the harness build step with:

```text
build all twelve brender_core_* smoke targets and run CTest with the selected multi-config build configuration
```

Readiness public notes must summarize the same twelve-rung result, preserve
`packaging_status: not-started`, and must not repeat the obsolete claim that
shaded/textured scene rendering or datafile loading are unclaimed.

- [ ] **Step 5: Update the hand-written archival packet**

Change `docs/BRENDER-ARCHIVAL.md` to say `twelve self-verifying render smokes`
and list these additional rungs after native model loading:

```markdown
9. UV material render: a loaded model uses its own texture coordinates with the
   portable perspective-correct rasterizer.
10. Multi-part assembly: `BrModelLoadMany` loads and depth-composites all 12
    parts of the coupe datafile.
11. Gouraud shading: per-vertex normals produce smooth gradients.
12. Plotter lane: hidden-line-removed, crease-filtered SVG polylines from a
    loaded period model.
```

Remove `Multi-part datafile assembly (BrModelLoadMany)` from `Honestly deferred`.
Leave native material/texture resolution deferred because the present material
smoke uses a generated texture rather than period `.mat/.pal/.pix` resolution.

- [ ] **Step 6: Run the state and validator tests to verify GREEN**

Run:

```powershell
python -m pytest tests/test_brender_state_consistency.py tests/test_evidence_checkpoint_validate.py tests/test_validate.py -q
engine-revival validate
```

Expected: all selected tests pass and validation prints no messages.

- [ ] **Step 7: Regenerate deterministic public views**

Run:

```powershell
engine-revival report
```

Review `git diff --name-only`. Generated changes must be explainable by the five
corrected records; investigate any unrelated target content change.

Capture hashes, regenerate a second time, and compare:

```powershell
$before = Get-ChildItem docs\generated -Recurse -File | ForEach-Object {
  [pscustomobject]@{ Path = $_.FullName; Hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
}
engine-revival report | Out-Null
$after = Get-ChildItem docs\generated -Recurse -File | ForEach-Object {
  [pscustomobject]@{ Path = $_.FullName; Hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
}
Compare-Object $before $after -Property Path,Hash
```

Expected: `Compare-Object` emits no rows.

- [ ] **Step 8: Run targeted report and public-boundary tests**

```powershell
python -m pytest tests/test_packet_report.py tests/test_reproduction_report.py tests/test_build_report.py tests/test_harness_report.py tests/test_readiness_report.py tests/test_target_dossier_report.py tests/test_audit_public.py -q
engine-revival audit-public
```

Expected: all tests pass and the audit prints no messages.

- [ ] **Step 9: Commit Task 2**

```powershell
git add tasks/brender-critical-edition-packet.json reproductions/brender-critical-edition-source-build.json builds/brender-v132-build-environment.json harnesses/brender-v132-portable-core-plan.json readiness/brender-production-readiness.json docs/BRENDER-ARCHIVAL.md docs/generated tests/test_brender_state_consistency.py
git diff --cached --check
git commit -m "fix: reconcile BRender verified evidence state"
```

---

### Task 3: Verify the canonical branch against the complete contract

**Files:** No planned source changes. Any failure requires returning to the
task that owns the affected file and adding a reproducing test first.

**Interfaces:** Produces the canonical commit that is eligible for mirroring.

- [ ] **Step 1: Run every canonical gate fresh**

```powershell
python -m pytest -q
engine-revival validate
engine-revival audit-public
engine-revival report | Out-Null
git diff --exit-code
git diff --check
git status --short --branch
```

Expected: 0 test failures; validate/audit print no messages; report creates no
new diff; `git diff --exit-code` and `git diff --check` return 0; worktree is
clean on `fix/brender-evidence-consistency`.

- [ ] **Step 2: Prove immutable attempts were not changed**

```powershell
git diff main...HEAD -- attempts
```

Expected: no output.

- [ ] **Step 3: Record the canonical source commit for the mirror**

```powershell
git rev-parse HEAD
git log --oneline main..HEAD
```

Use the exact resulting HEAD in the downstream mirror commit message.

---

### Task 4: Mirror the reviewed semantic result into brender-archival

**Files:** Copy the reviewed files changed by Tasks 1-2, excluding the mirror's
`README.md`, `LICENSE`, `pyproject.toml`, and `gallery/`.

**Interfaces:**

- Consumes: clean canonical branch and its exact HEAD commit.
- Produces: isolated `brender-archival` feature branch with matching shared
  semantic files and preserved project-specific release identity.

- [ ] **Step 1: Create and baseline the mirror worktree**

From `C:\dev\public\brender-archival`, verify clean state and create:

```powershell
git status --short --branch
git worktree add C:\dev\worktrees\brender-archival-evidence -b fix/brender-evidence-consistency main
```

Then run:

```powershell
python -m pytest -q
engine-revival validate
engine-revival audit-public
```

Expected baseline: all commands return 0 before copying.

- [ ] **Step 2: Snapshot protected mirror-specific files**

In `C:\dev\worktrees\brender-archival-evidence`:

```powershell
$protected = @('README.md','LICENSE','pyproject.toml') + @(
  Get-ChildItem gallery -Recurse -File | ForEach-Object { $_.FullName.Substring($PWD.Path.Length + 1) }
)
$before = @{}
foreach ($path in $protected) { $before[$path] = (Get-FileHash $path -Algorithm SHA256).Hash }
```

Keep the snapshot and copy operation in the same PowerShell process so `$before`
remains available.

- [ ] **Step 3: Copy only the canonical reviewed delta**

In that same PowerShell process:

```powershell
$canonical = 'C:\dev\worktrees\engine-revival-brender-evidence'
$mirror = 'C:\dev\worktrees\brender-archival-evidence'
$changed = git -C $canonical diff --name-only main...HEAD
$excluded = @('README.md','LICENSE','pyproject.toml')
foreach ($relative in $changed) {
  if ($excluded -contains $relative -or $relative -like 'gallery/*') { continue }
  $source = Join-Path $canonical $relative
  $target = Join-Path $mirror $relative
  $parent = Split-Path -Parent $target
  if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
  Copy-Item -LiteralPath $source -Destination $target -Force
}
$changedProtected = foreach ($path in $protected) {
  if ((Get-FileHash $path -Algorithm SHA256).Hash -ne $before[$path]) { $path }
}
if ($changedProtected) { throw "Protected mirror files changed: $($changedProtected -join ', ')" }
```

Expected: no protected file changes.

- [ ] **Step 4: Verify mirror contents and gates**

```powershell
git status --short
python -m pytest -q
engine-revival validate
engine-revival audit-public
engine-revival report | Out-Null
git diff --check
```

Run `engine-revival report` a second time and verify it adds no
new diff. Confirm `git diff -- README.md LICENSE pyproject.toml gallery` emits no
output.

- [ ] **Step 5: Commit the mirror with canonical provenance**

Read the exact canonical hash:

```powershell
$canonicalHead = git -C C:\dev\worktrees\engine-revival-brender-evidence rev-parse HEAD
git add -A
git diff --cached --check
git commit -m "sync: reconcile BRender evidence from engine-revival $canonicalHead"
```

- [ ] **Step 6: Run final mirror verification after commit**

```powershell
python -m pytest -q
engine-revival validate
engine-revival audit-public
git diff --exit-code
git status --short --branch
```

Expected: all tests pass, validate/audit print no messages, and the mirror
worktree is clean on `fix/brender-evidence-consistency`.

---

## Plan Self-Review Checklist

- [x] Every design requirement maps to a task.
- [x] Validator types and field names are identical across tests, schemas, code,
  and records.
- [x] The reproduction remains partially pending for 3D Movie Maker.
- [x] Packaging remains `not-started`.
- [x] Historical attempt records are untouched.
- [x] Mirror-specific files are hash-protected.
- [x] No command touches a live Fable exclusion path.
- [x] No placeholder or implied follow-up is required to execute a code step.
