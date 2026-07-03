# Contributing

`engine-revival` accepts public-safe metadata, citations, clean-room notes, and
recovery tasks for historical engine and toolchain revival.

## Add A Target

Create `targets/<id>.json` with the fields required by
`schemas/target.schema.json`. Use a stable lowercase ID with hyphens. Keep the
summary factual and public-safe.

## Add An Artifact

Create `artifacts/<id>.json` for a specific public source, manual, disc listing,
paper, talk, repository, release note, or package record. Do not attach files.
Use `redistribution_status` and `access_level` to describe whether the artifact
can be referenced, mirrored, or only tracked as metadata.

## Add An Accession

Create `accessions/<artifact-id>-<status>.json` when tracking capture, custody,
fixity, or review status for an artifact. Use `storage_class` to separate
external URLs, local non-public holdings, public mirrors, and metadata-only
records. Restricted or unclear accessions must not use `local-public`.

## Choose Rights Labels

Use the most conservative accurate label:

- `open`: public license or public source release.
- `public-reference-only`: public facts can be cited, but files are not hosted here.
- `restricted`: known restricted material.
- `unknown`: unclear status.
- `clean-room-only`: only compatibility notes and independent implementation work.
- `rights-holder-needed`: needs permission before redistribution.
- `do-not-redistribute`: metadata only.

## Submit Public Leads

Submit leads as source, artifact, or task records. Include publisher, title,
version, date, and public URL when available. Private contact data belongs
outside this public repo.

## Do Not Submit

Do not submit proprietary SDKs, leaked source, game assets, private donor files,
private contact data, credentials, restricted disc images, or access
instructions for restricted material.
