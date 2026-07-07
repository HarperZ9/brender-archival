# Revival Mission

This archive is not meant to be a receipt vault. Provenance, fixity, and
re-verification are required hygiene, but they are not the thing that makes the
work valuable.

The goal is to become the public source of record for lost, fragmented, and
historically important rendering engines and game engines.

## Two Roles

The archive does two things, and keeps them distinct:

1. It hosts archival restorations of the engines it rebuilds itself, with a
   reproducible harness and a verified build. BRender is the first.
2. It acts as a directory for finding other lost engine resources. When a
   project is actively maintained, the archive does not fork or re-host it; it
   points to the maintainer. See [the directory](DIRECTORY.md).

A project being open source is not the same as it being lost. Reviving a living
project would just be a stale mirror, so living projects are indexed, not
rebuilt.

## What This Means

For each engine or technology lineage, the archive should move through five
concrete layers:

1. Reproduce what can be lawfully rebuilt: source branches, examples, build
   recipes, toolchain assumptions, API references, and runnable demonstrations.
2. Archive what can be safely preserved: public source, public documentation,
   release notes, manuals, checksums, metadata, mirrors, and accession records.
3. Database the corpus: targets, artifacts, sources, accessions, tasks,
   milestones, packet records, relationships, status, and rights posture.
4. Index the field: make every target, package, source, and recovery task
   discoverable through generated pages and machine-readable exports.
5. Curate project packets: one focused packet per engine or lineage, with
   reproduction steps where possible and public-safe restricted-material notes
   where direct restoration is not publishable.
6. Productionize viable engines: move open or clean-room-compatible work toward
   repeatable builds, runnable demos, regression tests, release packaging,
   modern platform support, and developer-grade documentation.

## Revival Lanes

- `reproducible-public-engine`: public/open material can be rebuilt or mirrored.
- `critical-edition`: public material exists, but needs version taxonomy,
  commentary, build normalization, and technical references.
- `clean-room-compatible`: original material is restricted, so the work is API,
  file-format, behavior, or tooling reconstruction.
- `public-reference-only`: the publishable output is a dossier, index, timeline,
  source bibliography, or restricted lead map.
- `rights-holder-needed`: public metadata is safe, but direct publication needs
  permission or partnership.

## Packet Standard

A complete packet should answer:

- What is the engine, renderer, toolchain, or lineage?
- What public artifacts survive?
- What can be rebuilt, mirrored, or executed?
- What remains missing, private, restricted, or rights-holder-gated?
- Which source records support each claim?
- What is the next concrete reproduction or preservation task?
- What can a developer, historian, or preservationist do with it today?

## Database Standard

The generated corpus database at `docs/generated/database.json` is the public
machine-readable spine. It should remain deterministic, source-linked, and
safe to publish. Human-readable pages are views over that corpus, not a
replacement for it.

## Source Of Record Standard

This repo should prefer structured records over scattered prose. New findings
belong in JSON records first, then generated indexes and packets should expose
them. When a target becomes reproducible, the archive should record the exact
build path, environment assumptions, source lineage, and public-safe outputs.

## Flagship Engine Standard

A revived engine is not flagship-quality because a source package exists. It
becomes a flagship candidate only when the public record can show build status,
runtime status, tests, packaging, modernization work, blockers, and next actions.
`builds/*.json` records capture concrete build-environment probes,
`harnesses/*.json` records capture portable scaffolding plans or wrappers,
`attempts/*.json` records preserve command outcomes and transcripts, and
`readiness/*.json` records track the target's overall state without overstating
progress.
