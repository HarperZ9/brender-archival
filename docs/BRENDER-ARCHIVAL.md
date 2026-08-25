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
harness. It builds the FLOAT core through BRender's own pure-C memory-pixelmap
path, and since 2026-08-24 it also builds and runs the **period softrend scene
graph and pentprim primitive library as live libraries** - not re-implemented,
compiled from the pinned upstream tree itself.

Two rendering paths exist today:

1. Portable lane: a ladder of self-verifying smokes through BRender's own
   pixelmap/rasterizer core (vector math through datafile models, plotter SVG,
   game shell), all green under CTest on Visual Studio Win32.
2. Period-pipeline lane (`brender_core_softrend_render`): BrBegin ->
   BrRendererBegin bound to pentprim's `Default-Primitives-Float` ->
   BrZbSceneRenderBegin/Continue/Add/End over a loaded `.dat` model. Face
   dispatch reaches match.c block selection, which selects
   `TriangleRenderPIZ2I_RGB_888`, implemented in C in `compat/
   brender-pentprim-c-port.c` (fixed 16.16 vertices, barycentric fill).
   Evidence: ctest 21/21; the rung emits `final_frame_lit=22884 valid=true`;
   the frame PPM is archived at `builds/brender-v132-sphere-frame4.ppm`.

Three integration facts about this snapshot are load-bearing and were
established by measurement, not guesswork: the one-shot `BrZbSceneRender`
never installs camera matrices (drive Begin -> Continue -> Add -> End);
the renderer requires an explicitly bound primitive library; and cameras face
down -Z (`Matrix4PerspectiveNew` asserts it).

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
- Plot period models on a pen plotter: `brender_core_plotter_smoke` emits
  hidden-line-removed SVG polylines from any `.dat` model.
- Use the harness as the pattern for reviving other engines in this archive.

## Honestly deferred

These are documented, not claimed, so the revival is not oversold:

- The textured path: match.c currently selects the non-textured
  `PIZ2I` family because the material colour map does not reach
  `prim.colour_map.buffer`; the TIA trapezoid kernel is a flat-fill
  placeholder, so no per-pixel texture sampling through pentprim yet.
- Depth comparison in the C `TriangleRenderPIZ2I_RGB_888` kernel is disabled
  (z is recorded, not tested); the SZ sign/scale convention needs pinning by
  measurement before a compare is honest.
- The remaining ~200 assembly-only rasterizer kernels (lines, perspective-
  correct textured families, palette targets) stay as linkage stubs in
  `compat/brender-pentprim-c-port.c`; inventory in
  `builds/pentprim-c-port-surface.txt`.
- x64 pointer-width portability (the unreworked period code is 32-bit bound).
- Release packaging and a full interactive viewer.

## Records

The claims above are backed by structured records in this repository:
`readiness/brender-production-readiness.json`,
`harnesses/brender-v132-portable-core-plan.json`,
`attempts/brender-v132-portable-core-*.json`, and
`reproductions/brender-critical-edition-source-build.json`. The generated target
dossier at `docs/generated/targets/brender.md` is the machine-updated view.
