# BRender Archival

BRender (Blazing Render) was Argonaut Software's real-time 3D engine, shipped
through the 1990s and used in titles such as Carmageddon, FX Fighter, and
Microsoft 3D Movie Maker. This packet is the public revival of BRender v1.3.2:
not a source mirror, but a reproducible harness and evidence trail showing that
the engine still builds and renders from public material.

## Provenance and rights

- Source: the public `foone/BRender-v1.3.2` snapshot, pinned at commit
  `d88d0ed41122664b9781015b517db64353e16f19`, MIT licensed. Provenance runs
  through Foone Turing, with the open-source release authorized by Argonaut's
  former CEO Jez San.
- This repository vendors none of that source and none of BRender's assets. The
  materializer generates a build harness that references a public checkout in
  place. Model and texture datafiles are read from that checkout at run time,
  never copied into this repository.

## What the revival delivers

A materializer turns the period makefile topology into an out-of-tree CMake
harness. The verified public boundary is Visual Studio Win32 Debug from the
public v1.3.2 snapshot pinned above.

Two rendering paths exist today:

1. Portable lane: a ladder of self-verifying smokes through BRender's own
   pixelmap/rasterizer core. It covers vector math, framework startup,
   wireframe, scene graph, solid fill, depth, texture, datafile models,
   multi-model loading, Gouraud shading, plotter SVG, audits, host semantics,
   file texture sampling, and deterministic shell lifecycle.
2. Period-pipeline lane (`brender_core_softrend_render`): softrend and pentprim
   are compiled from the pinned upstream tree, pentprim's primitive library is
   explicitly bound, and the harness drives `BrZbSceneRender` over a loaded
   `.dat` model. The
   current release evidence renders `dat/sph32.dat` as an eight-frame nonblack
   orbit and reports `final_frame_lit=19284 valid=true` for the release media
   source run.

The 2026-08-27 native verification result is 21/21 CTest targets passing.

## Release hardening

The release branch selectively ports only verified fixes that were still
missing from current `origin/main`:

- material-resolve scanline setup initializes the third edge from `w2` via
  `ew[2][0]`;
- generated C receipts use shared JSON string escaping for caller-supplied
  paths and identifiers;
- pixelmap and host file round trips refuse preexisting caller-owned workfiles
  and clean up only files they created;
- generated texture rungs resolve INDEX_8 texels through the loaded palette;
- stale investigation diagnostics are removed from generated release surfaces.

These are covered by focused Python tests before the implementation changes.

## Current limitations

These are documented boundaries, not release claims:

- Experimental textured TIA/PIZ2TIA execution reaches the kernel, but black
  output remains blocked by a measured vertex-layout/state mismatch. Completed
  textured period rendering is not claimed.
- x64 pointer-width portability is not claimed. The verified native build target
  is Win32.
- Assembly-only pentprim kernels outside the exercised RGB_888 ZB and
  experimental TIA path remain linkage stubs.
- The MSVC warning set is warning-only in the verified build, but has not been
  reduced to a zero-warning portability claim.
- This is an archival harness and release-evidence packet, not an endorsement,
  not a production renderer, and not a vendored source distribution.

## Reproduce it

```powershell
python -m pip install -e ".[test]"
engine-revival materialize-brender-harness `
  --source-root C:\path\to\BRender-v1.3.2 `
  --output-root C:\path\to\brender-portable-core-harness
cmake -S <harness> -B <build> -A Win32 "-DBRENDER_SOURCE_DIR=C:\path\to\BRender-v1.3.2"
cmake --build <build> --config Debug
ctest --test-dir <build> -C Debug --output-on-failure
```

The `brender_core_model_smoke` executable takes any `.dat` model path and writes
a PPM, so it doubles as a minimal model viewer for the period asset library.

## Release media and provenance

Current public media lives under
[`gallery/release-20260827/`](../gallery/release-20260827/). It is generated
from verified nonblack render output, or from factual diagrams/cards that cite
the same boundary. It excludes black diagnostic frames and generative imitation.

- [Provenance manifest](../gallery/release-20260827/provenance-manifest.json)
  records sanitized commands, source attribution, source SHA, input/output
  hashes, dimensions, nonblack metrics, and limitations.
- [Period pipeline still](../gallery/release-20260827/period-pipeline-still.png)
  is a lossless PNG from the final verified orbit frame.
- [Period pipeline orbit contact sheet](../gallery/release-20260827/period-pipeline-orbit-contact-sheet.png)
  shows the provenance-pinned eight-frame period-pipeline orbit.
- [Evidence card](../gallery/release-20260827/evidence-card.png),
  [pipeline diagram](../gallery/release-20260827/pipeline-diagram.png), and
  [1200x630 social card](../gallery/release-20260827/social-card-1200x630.png)
  are bounded release assets.

## Package it

```powershell
python scripts/package_brender_release.py `
  --source-root C:\path\to\BRender-v1.3.2 `
  --output-root C:\path\to\release-stage
```

The staging directory contains the materialized harness, README, CTest
transcripts, release media, provenance manifest, `SHA256SUMS.txt`, and
`package-receipt.json`. The package references the public checkout by path at
materialization time and does not copy upstream source or assets.

## What you can do with it today

- Build BRender's core from a public checkout on a modern MSVC Win32 toolchain.
- Run 21 native CTest targets over the portable and period-pipeline harness.
- Load and render BRender's own period models straight from their datafiles.
- Use the portable smokes as small, inspectable examples of BRender geometry,
  materials, texture sampling, and plotter output.
- Extend the period-pipeline lane one measured kernel or state boundary at a
  time without claiming unverified textured output.

## Records

The claims above are backed by structured records in this repository:
`readiness/brender-production-readiness.json`,
`harnesses/brender-v132-portable-core-plan.json`,
`tasks/brender-critical-edition-packet.json`, and
`reproductions/brender-critical-edition-source-build.json`. The generated target
dossier at `docs/generated/targets/brender.md` is the machine-updated view.
