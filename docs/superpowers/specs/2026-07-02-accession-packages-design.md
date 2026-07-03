# Accession Packages Design

Date: 2026-07-02
Status: Draft for review
Workspace: `C:\dev\public\engine-revival`

## Purpose

The archive now has public targets, sources, artifacts, validation, public
audit, and generated reports. The next gap is preservation-grade accession
metadata: a public way to say which artifact was captured, how it was captured,
which checksums prove fixity, what storage class holds the archival master, and
whether the package is safe to publish.

An accession package is a metadata record. It does not make restricted material
public and it does not require committing binaries into git.

## Goals

- Add first-class `accessions/*.json` records linked to existing artifacts.
- Track provenance, capture method, fixity, custody, review status, and storage
  class for each accession.
- Extend validation so accessions reference known artifacts and sources.
- Extend the public audit so restricted or unclear artifacts cannot be described
  as publicly downloadable accessions.
- Generate a public accession report that separates captured, planned, blocked,
  and metadata-only packages.
- Seed a small first batch for already-public/open artifacts, starting with
  BRender, Mesa, OGRE, Open Inventor, Quesa, Aqsis, Pixie, Crystal Space, and
  OpenPHIGS where public licensing permits.

## Non-Goals

- Do not download or mirror restricted SDKs, leaked source, game assets, private
  donor files, private contact data, credentials, or restricted media.
- Do not build the public website in this slice.
- Do not scan all of `C:\dev` in this slice.
- Do not implement a general web crawler or automatic downloader.
- Do not store archival masters in git unless a later design explicitly allows a
  small public document or fixture.

## Approaches Considered

Recommended: **metadata-first accession records**. Add `accessions/` as a new
record kind and keep raw captured objects outside git by default. This fits the
current JSON/schema/validation architecture and gives the public archive stronger
provenance without increasing legal or storage risk.

Alternative: **artifact hashes only**. Put all fixity data inside
`artifacts/*.json`. This is simpler but collapses "artifact exists" and "we
captured a specific archival package" into one record, which makes custody,
review state, and multiple captures hard to represent.

Alternative: **local mirror first**. Download public packages into a committed or
ignored mirror tree, then generate metadata from files. This is useful later, but
it is too much for the next slice because it mixes network IO, storage policy,
license review, and schema design.

## Data Model

New record kind: `accession`.

Required fields:

- `id`: stable record ID.
- `artifact_id`: existing artifact record ID.
- `package_type`: one of `source-snapshot`, `release-archive`,
  `documentation-snapshot`, `repository-mirror`, `metadata-only`,
  `physical-media-image`, `external-custody`.
- `capture_status`: one of `planned`, `captured`, `verified`, `blocked`,
  `metadata-only`.
- `storage_class`: one of `external-url`, `local-private`, `local-public`,
  `institutional`, `not-held`.
- `fixity_status`: one of `not-started`, `recorded`, `verified`,
  `not-applicable`.
- `rights_review`: one of `public-ok`, `open-license`, `metadata-only`,
  `restricted`, `unknown`, `rights-holder-needed`.
- `public_notes`: public-safe summary of what the accession represents.

Optional fields:

- `source_ids`: public source records supporting the package.
- `capture_uri`: public URL or non-secret local pointer class.
- `captured_at`: ISO date.
- `captured_by`: public role label such as `archive-maintainer`, not personal
  private contact data.
- `hashes`: object keyed by algorithm, usually `sha256`.
- `size_bytes`: integer file size for captured files.
- `tooling`: public-safe tool names and versions used to capture or verify.
- `review_notes`: public-safe caveats.

## Validation

`engine-revival validate` should:

- Load `accessions/*.json` when the directory exists.
- Validate required accession fields and primitive field types.
- Fail unknown `artifact_id` references.
- Fail unknown `source_ids`.
- Validate `size_bytes` is an integer when present.
- Validate `hashes` is an object when present.

## Public Audit

`engine-revival audit-public` should:

- Fail an accession if `rights_review` is `restricted`, `unknown`, or
  `rights-holder-needed` and `storage_class` is `local-public`.
- Fail an accession if `capture_uri` or notes contain unsafe phrases already
  blocked for artifacts, such as leaked source, private contact, or download the
  SDK.
- Allow `metadata-only` accessions for restricted leads only when
  `storage_class` is `not-held` and `fixity_status` is `not-applicable`.
- Allow public/open accession records to include checksums and public URLs.

## Reporting

`engine-revival report` should add `docs/generated/accessions.md` with:

- artifact ID
- package type
- capture status
- fixity status
- storage class
- rights review
- public notes

The report should keep records sorted by artifact ID, then accession ID, so diffs
remain stable.

## First Seed Batch

The first implementation should add accession records only for public/open
material where the current repo already has high-confidence artifact/source
records:

- `brender-v132-source`
- `brender-3dmm-source`
- `mesa-source-repository`
- `ogre-source-repository`
- `open-inventor-source-release`
- `quesa-source-reimplementation`
- `aqsis-renderer-source`
- `pixie-renderer-source-mirror`
- `crystal-space-github-source-repository`
- `openphigs-source-reimplementation`

These may start as `planned` or `metadata-only` if no local capture has been
performed yet. The implementation must not claim `verified` until hashes are
actually recorded and checked.

## CLI Surface

The next implementation slice should keep the CLI small:

- `engine-revival validate`: includes accessions.
- `engine-revival audit-public`: includes accessions.
- `engine-revival report`: writes `accessions.md`.

No downloader command is included yet. A later slice can add capture automation
after the metadata and audit rules are stable.

## Testing

Tests must cover:

- valid accession fixture passes validation
- missing required accession field fails validation
- unknown `artifact_id` fails validation
- unknown source ID fails validation
- restricted accession with public storage fails public audit
- metadata-only restricted accession with `not-held` storage passes audit
- generated accession report is stable and contains the first seed batch

## Success Criteria

This slice is complete when:

- accession schema exists
- accession records are discoverable and validated
- public audit blocks unsafe accession states
- generated docs include accession status
- first public/open seed batch has accession records
- full tests, validation, public audit, report generation, diff check, file-size
  check, and secret scan all pass

