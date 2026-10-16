# ADR 0001: raw-native reads BRender content, converter first

**Status:** Proposed. **Date:** 2026-10-16.

## Context

The author approved on 2026-10-09 that raw-native, the author's C++23 engine,
may load and render BRender content. This repository revives BRender under
MIT; raw-native is a separate repository under FSL-1.1-MIT, run by other
sessions, with its own rules:

- raw-native ADR 0005 (dependency policy): the CPU reference path is
  standard-library-only; other libraries are vendored, pinned by SHA-256,
  licence-checked and wrapped by an interface the engine owns. MIT is allowed.
- raw-native's M3 scenes use only assets it generates (author, 2026-10-10:
  "No test models, only full owned assets").
- raw-native already reads glTF 2.0 (`src/assets/gltf.cpp`).

BRender content means three file kinds. Each has an MIT reference
implementation in the public BRender v1.3.2 source:

| Kind | Files | Reference code in BRender v1.3.2 |
|---|---|---|
| Models, materials, actors | `.dat`, `.mat`, `.act` (chunked datafiles, binary or text) | `core/fw/datafile.c`, `core/v1db/v1dbfile.c` |
| Pixelmaps (textures, shade and blend tables) | `.pix`, `.tab` | `core/pixelmap/pmfile.c` |
| Palettes | `.pal` | pixelmap datafiles, as above |

## Options

**A. Link BRender into raw-native.** Rejected. It adds a C engine to a C++23
codebase whose ADR 0005 keeps the pixel path free of outside code, and it
couples two release cycles.

**B. Convert, then load glTF.** A command in this repository,
`brender-to-gltf`, reads `.dat`, `.mat`, `.pix` and `.pal` through BRender
1.4 itself (`BrModelLoad`, `BrMaterialLoad`, `BrPixelmapLoad`) and writes
glTF 2.0 with PNG textures. raw-native loads the result with the loader it
already has. Nothing in raw-native changes. The converter is MIT and lives
here, so the format knowledge stays with the engine that defines it.

**C. A native reader in raw-native.** A dependency-free, MIT, single-header
reader (`brfile.hpp`) written in this repository and vendored into raw-native
under ADR 0005 (pinned by SHA-256, listed in `third_party/MANIFEST.md`),
behind an interface raw-native owns. This gives runtime loading without a
conversion step.

## Decision (proposed)

Do B now and C only when a raw-native feature needs runtime loading.

B first because it is checkable end to end without touching raw-native: the
converter loads each model with BRender, writes glTF, reads the glTF back,
and compares vertex positions, UVs, face indices and material colours with
the BRender in-memory model (exact for indices, within 1e-6 for floats). A
wrong-model control must fail the comparison. The 1998 sample models (MIT,
Argonaut) and The Keeper's Hour's own models (CC BY 4.0, authored here) are
the corpus.

For C, the reader must match the converter on the same corpus, byte for byte
on the decoded arrays, before raw-native vendors it.

## Licences and assets

- The converter and any reader are original code in this repository, MIT,
  with BRender's MIT notice kept beside them because they follow BRender's
  file formats.
- The 1998 sample models are MIT (copyright 1998 Argonaut Software Limited).
  They are not "owned assets" in raw-native's sense, so raw-native's M3
  acceptance scenes do not use them. A raw-native BRender sample scene may use
  them under the author's 2026-10-09 approval, labelled as Argonaut content.
- The Keeper's Hour's models and art are owned by the author (CC BY 4.0) and
  can serve as owned assets in raw-native if the author agrees.

## How we would learn this is wrong

- glTF loses something BRender content needs (for example indexed-colour
  shade tables or BRender's per-face material flags). The converter's
  comparison then reports a field it cannot carry, and option C moves up.
- raw-native's sessions prefer to own the reader. Then C is written in
  raw-native under its licence, and this repository supplies the test corpus
  and the expected arrays.

## Coordination

raw-native is owned by other sessions. This record is a proposal; the
raw-native side is proposed in a pull request description there, with no
change to raw-native's code until its owners accept it.
