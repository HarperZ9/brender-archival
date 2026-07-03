# BRender Archival

BRender (Blazing Render) was Argonaut Software's real-time 3D engine, shipped
through the 1990s and used in titles such as Carmageddon and FX Fighter and in
Microsoft 3D Movie Maker. This packet is the revival of BRender v1.3.2: not a
mirror of the source, but a demonstration that the engine still builds and
renders, reproduced from public material with nothing proprietary vendored in.

## Provenance and rights

- Source: the public `foone/BRender-v1.3.2` snapshot, pinned at commit
  `d88d0ed4`, MIT licensed. Provenance runs through Foone Turing, with the
  open-source release authorized by Argonaut's former CEO Jez San.
- This repository vendors none of that source and none of BRender's assets. The
  materializer generates a build harness that references a public checkout in
  place. Model datafiles are read from the checkout at run time, never copied.

## What the revival delivers

A materializer turns the period makefile topology into an out-of-tree CMake
harness. It builds the FLOAT core library through BRender's own pure-C
memory-pixelmap path, with no dependence on the period 386-assembly software
renderer, and stands up a ladder of eight self-verifying render smokes:

1. Vector math smoke (`BrVector3`, `BrScalar`).
2. Framework startup smoke (`BrBegin` / `BrEnd`).
3. Wireframe render: a projected cube via `BrMatrix4Perspective` into a memory
   pixelmap.
4. Scene-graph render: a model out of the v1db scene database, projected by the
   engine's own `BrActorToScreenMatrix4`.
5. Solid flat-shaded render: a portable C scanline rasterizer with per-face
   lighting.
6. Per-pixel depth buffer: correct occlusion for arbitrary multi-object scenes.
7. Perspective-correct texture mapping.
8. Real datafile models: `BrModelLoad` reads native binary `.dat` models
   (duck, teapot, skull, torus) and renders them solid and depth-buffered.

Every stage passes under CTest on a Visual Studio Win32 target. The render
captures are generated as a public-safe release artifact.

## Reproduce it

```powershell
python -m pip install -e ".[test]"
engine-revival materialize-brender-harness `
  --source-root C:\path\to\BRender-v1.3.2 `
  --output-root C:\path\to\brender-portable-core-harness
cmake -S <harness> -B <build> -A Win32 "-DBRENDER_SOURCE_DIR=C:\path\to\BRender-v1.3.2"
cmake --build <build> --config Debug --target brender_core_model_smoke
ctest --test-dir <build> -C Debug --output-on-failure
```

The `brender_core_model_smoke` executable takes any `.dat` model path and writes
a PPM, so it doubles as a minimal model viewer for the period asset library.

## What you can do with it today

- Build BRender's core from a public checkout on a modern MSVC toolchain.
- Load and render BRender's own period models straight from their datafiles.
- Extend the portable rasterizer (Gouraud shading, materials, a wider viewer).
- Use the harness as the pattern for reviving other engines in this archive.

## Honestly deferred

These are documented, not claimed, so the revival is not oversold:

- BRender's period 386-assembly `softrend` renderer (the hard portability item).
- x64 pointer-width portability (the unreworked period code is 32-bit bound).
- Original material and texture resolution for loaded models.
- Multi-part datafile assembly (`BrModelLoadMany`).
- Release packaging and a full interactive viewer.

## Records

The claims above are backed by structured records in this repository:
`readiness/brender-production-readiness.json`,
`harnesses/brender-v132-portable-core-plan.json`,
`attempts/brender-v132-portable-core-*.json`, and
`reproductions/brender-critical-edition-source-build.json`. The generated target
dossier at `docs/generated/targets/brender.md` is the machine-updated view.
