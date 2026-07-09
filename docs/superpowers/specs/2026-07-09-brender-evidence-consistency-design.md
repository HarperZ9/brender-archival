# BRender Evidence Consistency Design

Date: 2026-07-09
Status: Approved for implementation
Workspace: `C:\dev\worktrees\engine-revival-brender-evidence`
Canonical repository: `C:\dev\public\engine-revival`
Downstream mirror: `C:\dev\public\brender-archival`

CLI commands assume an isolated environment in which this worktree is
installed editable as documented in `README.md`, and use the canonical
`engine-revival` console entry point. Before running commands, verify the
executable and imported module paths resolve to this worktree.

## Purpose

Restore agreement between BRender's structured evidence records and the
verified 12-rung portable-core result, then make future disagreement fail the
existing `engine-revival validate` gate.

The repository currently validates schema shape and references but accepts a
contradictory state: readiness records CTest 12/12 and score 86 while the task,
reproduction, build, harness narrative, and archival packet still describe an
earlier 8/8 or startup-only state. That violates the repository's original
evidence-discipline design even though all existing tests pass.

## Scope

This slice will:

1. Add an optional structured `evidence_checkpoint` object to task,
   reproduction, build, harness, and readiness records.
2. Validate the shape and cross-record agreement of checkpoints in the existing
   workspace validator.
3. Attach one shared checkpoint to the five BRender records that describe the
   current portable-core result.
4. Reconcile stale status fields, blockers, next actions, expected outputs,
   steps, and public notes without rewriting immutable attempt transcripts.
5. Update the hand-written BRender archival narrative from eight to twelve
   rungs and remove multi-part loading from the deferred list.
6. Regenerate deterministic report views from the corrected records.
7. Mirror the reviewed semantic result into `brender-archival` only after the
   canonical repository passes every gate.

This slice will not:

- modify either live Fable workflow or any of its repositories;
- claim x64 support, period `softrend`, native material resolution, FIXED
  variants, drivers, release binaries, or a full interactive viewer;
- edit historical attempt records or compiler transcripts;
- add a new standalone tool or validation command;
- treat the existence of the standalone archive repository as binary release
  packaging.

## Evidence Checkpoint Contract

An optional checkpoint has this exact shape:

```json
{
  "id": "brender-v132-portable-core-plotter-2026-07-03",
  "stage": "portable-core-plotter-lane-passing",
  "passed": 12,
  "total": 12,
  "source_snapshot": "d88d0ed41122664b9781015b517db64353e16f19"
}
```

Fields:

- `id`: stable identity for one observed checkpoint.
- `stage`: shared capability stage, independent of record-specific workflow
  status.
- `passed` and `total`: observed test result; integers with
  `0 <= passed <= total` and `total > 0`.
- `source_snapshot`: exact source revision against which the result was
  observed.

Multiple records may describe different aspects of the same checkpoint. If
they share a checkpoint ID, all five values must match exactly.

## Validation Architecture

`validate_workspace()` remains the single validation entry point. A focused
helper will:

1. Inspect checkpoint-bearing task, reproduction, build, harness, and readiness
   records.
2. Reject missing keys, unexpected keys, wrong scalar types, invalid pass/total
   bounds, and empty strings.
3. Group valid checkpoints by checkpoint ID.
4. Compare each member to the first observed member.
5. Emit path-specific mismatch messages naming the checkpoint ID and differing
   field.

The checkpoint is optional for existing targets. A BRender-specific regression
test will require it on the five current BRender state records so accidental
omission cannot bypass the generic validator.

## Record Reconciliation

The following records will carry the shared checkpoint:

- `tasks/brender-critical-edition-packet.json`
- `reproductions/brender-critical-edition-source-build.json`
- `builds/brender-v132-build-environment.json`
- `harnesses/brender-v132-portable-core-plan.json`
- `readiness/brender-production-readiness.json`

Record-specific truth remains distinct:

- The task will say the standalone portable-render archive is published, not
  merely pending publication.
- The reproduction will say the v1.3.2 portable-core plotter lane is verified
  while the 3D Movie Maker branch remains pending; it will not claim the entire
  broader reproduction recipe is complete.
- The build and harness will describe all twelve passing rungs while retaining
  honest x64, driver, FIXED, warning, semantic-stub, and packaging limits.
- Readiness will retain `packaging_status: not-started` because a Git repository
  is not a packaged binary release.
- Attempt records remain immutable observations and are referenced rather than
  rewritten.

## Mirror Policy

`engine-revival` is the implementation source of truth. `brender-archival` is a
curated downstream mirror with its own README, AGPL license, package identity,
and gallery.

After canonical verification:

1. Record the canonical source commit.
2. Copy only reviewed shared semantic files.
3. Preserve the mirror's README, LICENSE, `pyproject.toml`, and gallery.
4. Run the mirror's full tests, validation, and public audit.
5. Leave both repositories on isolated feature branches; do not merge or push
   without a separate integration decision.

## Testing Strategy

TDD order:

1. Add validator tests for malformed bounds and cross-record mismatch; verify
   they fail because checkpoint validation does not exist.
2. Add the smallest validator implementation and schema declarations; verify
   the tests pass.
3. Add a BRender repository-state test requiring the shared checkpoint and
   current 12-rung claims; verify it fails against the stale records.
4. Reconcile records and hand-written documentation; verify the state test
   passes.
5. Regenerate reports and run targeted report tests.
6. Run the full canonical gates:

```powershell
python -m pytest -q
engine-revival validate
engine-revival audit-public
engine-revival report
git diff --check
```

7. Verify report generation is deterministic by running it a second time and
   confirming no new diff.
8. Repeat the applicable gates in the downstream mirror after the reviewed
   sync.

## Failure Handling

- Invalid checkpoint shape fails validation with the record path.
- Conflicting records fail validation with both the checkpoint ID and field.
- Historical claims that cannot be proved remain unchanged or explicitly
  pending.
- Generated-doc changes outside BRender-related views are treated as unexpected
  and investigated before commit.
- Any new activity in the two live Fable exclusion zones triggers a collision
  re-audit; it does not broaden this lane.

## Success Criteria

- The previously accepted contradictory fixture fails before implementation.
- Matching checkpoints validate.
- All five BRender state records share the exact verified checkpoint.
- No current BRender state record or hand-written packet claims only 8/8,
  score 78, startup-only coverage, or deferred multi-part loading.
- Immutable attempt records remain byte-for-byte unchanged.
- Canonical and mirror gates pass from clean isolated branches.
- The mirror preserves its project-specific release files and gallery.
