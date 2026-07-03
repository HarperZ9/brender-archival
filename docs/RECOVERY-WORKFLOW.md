# Recovery Workflow

Use this workflow for each public archive addition.

1. Identify a public source or public-safe lead.
2. Create or update a `sources/*.json` record.
3. Create or update a `targets/*.json`, `artifacts/*.json`, or `tasks/*.json` record.
4. Create or update an `accessions/*.json` record when the lead has a planned,
   external, local, or metadata-only custody action.
5. Create or update a `builds/*.json` record when a source checkout, build
   environment, toolchain probe, or build-system inspection is recorded.
6. Create or update a `harnesses/*.json` record when a portable build plan,
   wrapper, project file set, or reproducible scaffolding path is designed.
7. Create or update an `attempts/*.json` record when a materializer, configure,
   build, test, runtime, packaging, or indexing command is run.
8. Create or update a `readiness/*.json` record when the target's rebuild,
   runtime, tests, packaging, or modernization status changes.
9. Run `engine-revival validate`.
10. Run `engine-revival audit-public`.
11. Run `engine-revival report`.
12. Review the generated docs before publishing.

When a lead points to restricted or unclear material, record only metadata and
use `restricted`, `unknown`, `rights-holder-needed`, `clean-room-only`, or
`do-not-redistribute`.
