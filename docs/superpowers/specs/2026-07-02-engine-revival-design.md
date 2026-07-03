# Engine Revival Public Archive Design

Date: 2026-07-02
Status: Approved for implementation planning
Workspace: `C:\dev\public\engine-revival`

## Purpose

`engine-revival` is a public-facing, tooling-first archive for reviving,
documenting, and curating historical game engines, rendering libraries, CGI
toolkits, platform SDKs, and studio technology lineages.

The first responsibility is evidence discipline: public records must be
accurate, reviewable, and safe to publish. A visual exhibit or website can later
consume the same records.

## Context

Seed research:

- `C:\Users\Zain\Downloads\deep-research-report2.md`
- `C:\Users\Zain\Downloads\deep-research-report3.md`

The reports define two lanes:

- Stabilize public/open recoverable material: BRender, Open Inventor, Quesa,
  Mesa, Crystal Space, OGRE, Aqsis, Pixie.
- Track fragmented or rights-constrained material through public-safe metadata:
  RenderWare PS2, Reality Lab, OpenGL Performer, QuickDraw 3D, PS1/PS2
  toolchains, GOOL/GOAL, tri-Ace rendering, Psygnosis, Japan Studio/Team Ico.

## Goals

- Create a public repo at `C:\dev\public\engine-revival`.
- Define schemas for targets, artifacts, sources, tasks, and milestones.
- Provide a Python CLI for validation, public-safety audit, indexing, seeding,
  and Markdown report generation.
- Seed all initial targets from the two reports.
- Make public/restricted boundaries explicit and mechanically checked.

## Non-Goals

- Do not publish proprietary SDK binaries, leaked source, game assets, private
  donor files, private contact data, credentials, or restricted media.
- Do not build the public website in the first implementation slice.
- Do not attempt exact restoration for restricted targets in this repo.
- Do not make unverified legal claims. Rights labels describe archive posture,
  not legal advice.

## Architecture

The repo has four layers.

`schemas/`: JSON Schemas for target, artifact, source, task, and milestone
records. Schemas define required IDs, status labels, confidence fields, and
public-safety fields.

`engine_revival/`: Python package and CLI. It validates records, builds indexes,
emits provenance summaries, and catches unsafe or ambiguous publication states.

Record directories: `targets/`, `artifacts/`, `sources/`, `tasks/`. First
record format is JSON for straightforward schema validation.

`docs/`: generated and hand-written public docs: target matrix, priority table,
rights/status summary, recovery workflow, contribution guide, archival ethics,
lead submission guidance, and per-target summaries. Generated docs go under
`docs/generated/`.

## Data Model

`target`: recoverable engine, SDK, toolchain, renderer, studio lineage,
middleware family, or upstream graphics system.

Required: `id`, `name`, `category`, `era`, `platforms`, `priority`,
`revival_lane`, `rights_posture`, `summary`, `public_status`,
`restricted_status`.

Optional: `related_targets`, `notes`, `tags`.

`artifact`: specific source, repo, manual, disc, ISO, paper, release note, SDK
package, talk, press disc, or other recoverable item.

Required: `id`, `target_id`, `artifact_type`, `title`, `origin`,
`redistribution_status`, `access_level`, `evidence_quality`.

Optional: `version`, `date`, `location`, `hashes`, `source_ids`, `notes`.

`source`: citation or provenance pointer.

Required: `id`, `title`, `source_type`, `confidence`, `claim_scope`.

Optional: `url`, `local_pointer`, `publisher`, `retrieved_at`, `notes`.

`revival_task`: concrete recovery or reconstruction task.

Required: `id`, `target_id`, `task_type`, `status`, `public_notes`.

Optional: `owner`, `inputs`, `outputs`, `blocked_by`, `source_ids`.

`milestone`: target state checkpoint.

Required: `id`, `target_id`, `milestone_type`, `status`, `evidence`.

## Controlled Labels

Initial labels:

- `open`
- `public-reference-only`
- `restricted`
- `unknown`
- `clean-room-only`
- `rights-holder-needed`
- `do-not-redistribute`

The CLI must fail records that imply publication or redistribution while also
using `restricted`, `unknown`, `rights-holder-needed`, or
`do-not-redistribute`.

## CLI Surface

`engine-revival seed`: creates starter public-safe records for the initial
target set. It must not overwrite edited records.

`engine-revival validate`: validates records against schemas and reports exact
file paths for failures.

`engine-revival audit-public`: fails records that omit rights posture or access
level, use ambiguous redistribution language, attach restricted material as a
publishable artifact, or describe private/proprietary files as public
deliverables.

`engine-revival index`: builds generated target matrix, priority table,
rights/status rollup, and task board data.

`engine-revival report`: generates Markdown summaries under `docs/generated/`.

First successful workflow:

```powershell
python -m pip install -e ".[test]"
engine-revival seed
engine-revival validate
engine-revival audit-public
engine-revival index
engine-revival report
python -m pytest
```

## Initial Target Set

- BRender
- PS1 Programmer's Tool / SDevTC / Net Yaroze
- RenderWare PS2
- GOOL and GOAL
- PS2 ProDG / EB / Linux stack
- tri-Ace PS2 renderer
- Psygnosis / Studio Liverpool
- Japan Studio / Team Ico
- Open Inventor
- Quesa
- Mesa
- Crystal Space
- OGRE
- Aqsis
- Pixie
- RenderMorphics Reality Lab
- OpenGL Performer
- QuickDraw 3D
- RenderMan Interface
- PHIGS
- IRIS GL / OpenGL bridge
- Softimage / Alias bridge

## Public Boundary

Allowed:

- public metadata
- public citations
- checksums of public artifacts
- public-safe summaries
- clean-room notes
- rights/status labels
- task records
- generated public docs
- schemas and validation tools

Not allowed:

- proprietary SDK binaries
- leaked source
- private donor files
- private contact data
- credentials
- real game assets
- restricted media images
- access instructions for restricted material

Restricted leads are represented as metadata with access status, not as files.

## Verification

Tests must assert:

- schema validation accepts good records and rejects malformed records
- generated docs are stable for seeded records
- `audit-public` fails unsafe publication states
- status labels are controlled and consistent
- target IDs referenced by artifacts, tasks, and milestones exist
- CLI commands exit nonzero on invalid input

Success is not "the CLI runs." Success is catching unsafe or incoherent public
archive states before publication.

## Implementation Slices

1. Repo bootstrap: package metadata, AGENTS, README, tests, minimal CLI.
2. Schemas: target, artifact, source, task, milestone.
3. Validation engine: discovery, schema validation, cross-reference checks.
4. Public audit: rights/access enforcement and unsafe-language checks.
5. Seed data: initial target records from the reports.
6. Index/report generation: generated docs and summary tables.
7. Verification hardening: targeted tests and sample invalid fixtures.

## Approval Record

Approved decisions:

- Use `C:\dev` as the canonical workspace.
- Make the archive public-facing from the start.
- Create `C:\dev\public\engine-revival`.
- Choose a tooling-first archive approach.
- Use the architecture, data model, CLI workflow, public boundary, and
  verification model in this spec.
