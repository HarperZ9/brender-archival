# Roadmap to a user-ready BRender

The goal is a full modern 64-bit BRender that people can build with, and an
original game under an open licence that shows it off. Everything here stays
MIT, as Argonaut's BRender v1.3.2 was published. Each item names the check
that says it is done, and the order puts a win a player or developer can see
first.

## Where it stands (measured 16 October 2026)

| What | Windows x64 | Linux x64 | How it was measured |
|---|---|---|---|
| brview, the sample viewer | builds, 8 of 8 models load | builds, 8 of 8 models load | local MSVC build and WSL Ubuntu 24.04 GCC build, `BRVIEW_SMOKE=1` |
| The Keeper's Hour | builds; 5 rooms, 80 nodes, 3 of 3 endings, save, options, audio | the same lines, the same audio peak (0.923) and RMS (0.0626) | `KEEPERS_SMOKE=1` on both |
| 64-bit ladder (BRender 1.4) | 21 of 21 under CTest | 21 of 21 under CTest | `modern/ladder64`, Release, Ninja on Linux |
| Period ladder (BRender 1.3.2) | 21 of 21, Win32 only | not applicable | CI job `brender-native` |
| Downloads | brview 0.1.1 and The Keeper's Hour 0.3.1 zips | none before this roadmap | GitHub releases |
| Frame recorder determinism | two runs give the same bytes (CI) | software renderer: same bytes; OpenGL under Mesa llvmpipe: not deterministic (fixed later the same day, item 3) | `KEEPERS_RECORD` twice, frame hashes compared |

The Linux build needed no source change. Two packaging faults kept it from
shipping: the programs carried a run path into the build tree, and the
install step did not copy SDL3 under the name the loader looks for
(`libSDL3.so.0`).

The engine under the modern builds is BRender 1.4 from
[BlazingRenderer/BRender](https://github.com/BlazingRenderer/BRender) (MIT),
pinned by commit. It already brings a portable C software rasteriser
(softprim), an OpenGL 3.3 driver and SDL3 windowing. The period Win32 build
of 1.3.2 still stops short of a textured render through BRender's own
pentprim kernels (a measured vertex layout and state mismatch).

## The order

### 1. Linux x64 downloads (shipped with this roadmap)

brview and The Keeper's Hour build, run and package on 64-bit Linux, next to
Windows. The programs find `libSDL3.so.0` beside themselves through a
`$ORIGIN` run path, so the unpacked folder runs in place. CI builds both on
`ubuntu-24.04`, runs the same smoke checks as on Windows, runs the 21-step
ladder, and checks that the packaged copies resolve SDL3 from their own
folder. The release workflows add `*-linux-x64.tar.gz` with a SHA-256 beside
each. The binaries need glibc 2.38 or newer (measured: the highest symbol
version they reference).

Done when: a `keepers-v*` and a `brview-v*` release carry Linux tarballs
built by CI after the packaged smoke passes.

### 2. Display: resolution, widescreen and a period look (game shipped)

Shipped in The Keeper's Hour on 16 October 2026: pixel size 1 to 6 (the scene
drawn coarser and scaled up with whole, square pixels, text kept sharp), field
of view 40 to 90 degrees, and vsync, in the F2 options and saved. The field of
view is vertical, so widescreen is Hor+. `games/keepers-hour/tools/display_check.py`
checks it on frames at 4:3, 16:9 and 21:9 with failing controls, on both
renderers, in CI on Windows and Linux.

Not done: the same settings in brview, and a period mode through BRender's
8-bit palette path (the pixel size gives the coarse look, not the palette).

Done when: options persist; a test draws one room at three resolutions and
checks the aspect and the pixel scale; screenshots go in the README. Met for
the game.

### 3. Deterministic capture on every driver (shipped)

Under Mesa llvmpipe the OpenGL readback in `kh_frame_write` sometimes returned
the previous frame. Measured on 16 October 2026, four recordings of 15 frames:
every run repeated a frame and no two runs matched. With `glFinish` before the
readback, the same four runs gave 15 distinct frames, identical across runs.
Five 30-frame runs then gave 30 distinct frames each, identical across runs.
The game now finishes the OpenGL frame before each capture (capture only, so
play is not slowed), and CI records twice on both renderers on Linux and
fails if any frame repeats the one before it.

Not settled: why the readback ran ahead of the draws. BRender 1.4's OpenGL
driver keeps its uniform rings mapped (`GL_MAP_UNSYNCHRONIZED_BIT`, not
persistent) while it issues draws; as we read the GL specification, a draw
that reads a buffer mapped without the persistent bit is an error. That is
a candidate, not a finding. A report to
BlazingRenderer with this reproducer is for the author to decide.

Done when: the Linux CI records twice on OpenGL with identical bytes. Met.

### 4. Packaging people expect (prepared; submission waits for the author)

Prepared on 16 October 2026, in `packaging/` (see its README):

- **AppImage** for both programs. It is built from the staged release folder
  with a pinned, hash-checked AppImage runtime, run headless in CI with
  `--appimage-extract-and-run`, and attached to every release from the next
  tag on.
- **winget** manifests for both programs (schema 1.6.0; `winget validate`
  passes) and **Scoop** manifests with `checkver` and `autoupdate`. Both are
  generated from the hash the release workflow published, so they can only
  name a build that passed the packaged smoke run.
- An **itch.io** page draft for the game.

Not done:

- No submission to winget-pkgs, a Scoop bucket or itch.io. Those are
  third-party services, and the author decides.
- No install test through winget or Scoop. winget needs local manifests
  enabled or a submission; Scoop is not installed here.
- No macOS build and no signed checksums.

Done when: each channel installs the current release on a clean machine in CI
(or on a recorded manual run where CI cannot reach). AppImage: met in CI.

### 5. Renderer parity, measured (instrument built; the 1998 side is not ready)

The game's `tools/parity.py` compares the OpenGL and software stills by edge
correlation, because the two drivers shade differently. Pixel parity is the
stronger claim and holds only where both paths are deterministic and use the
same arithmetic.

Built on 16 October 2026, in `modern/parity/` (see its README):

- one scene program compiled against both engines;
- a pixel comparison with a wrong-pose control that must fail;
- CI checks on the modern side.

Measured:

- BRender 1.4's software rasteriser gives the same bytes on every run, and
  the same coverage on Windows (MSVC) and Linux (GCC). At most 0.02% of
  pixels are off by one level.
- The period 1.3.2 build is not a usable reference yet. Its flat paths draw
  nothing, and its Gouraud path saturates and drops faces (coverage IoU 0.60
  to 0.76 against 1.4). It also varies between runs. Its kernels are this
  project's C ports of Argonaut's assembly, most of them stubs, so the gap
  measures those ports, not the 1998 engine. No parity claim is made.

Next: fix the period C ports in `engine-revival` until all seven scenes draw
deterministically, then rerun the comparison and gate it in CI. OpenGL
against software, with stated bounds, follows.

Done when: a parity record (JSON) for each pair is committed and CI
recomputes it. Met for modern Windows against modern Linux; not met for the
period comparison.

### 6. Modern GPU backends

BRender 1.4 has OpenGL 3.3. Add Vulkan first (it runs on Windows and Linux),
then Direct3D 11 or 12 if Windows needs it. Each backend is a BRender driver
written here under MIT, offered upstream to BlazingRenderer, and held to the
item 5 parity bounds against the software rasteriser.

Done when: the game runs on the new backend with `--driver vulkan`, and its
parity record passes.

### 7. Developer docs and samples

A "first BRender program" guide, a sample project a developer can copy (a
window, a model, a light, input), an API tour of the parts a game uses, and a
CMake package so another project can `find_package(BRender)`. The ladder rungs
double as small, tested samples.

Done when: the sample builds from a clean clone on both platforms in CI, and
the guide's commands are run by CI.

### 8. The Keeper's Hour to 1.0

Hand-made `.dat` furniture in place of the shapes built in code, text size and
contrast options, a Steam Deck control check, save slots, a playtest round
with notes kept, and the trailer cut from the deterministic recorder.

Done when: the 1.0 checklist in `games/keepers-hour/DESIGN.md` passes and the
release carries Windows and Linux builds.

### 9. BRender content in raw-native

raw-native, the author's C++23 engine, may load and render BRender content.
The proposal is
[ADR 0001](adr/0001-raw-native-reads-brender-content.md): convert first, load
natively later.

### Archival lane, in parallel

The period Win32 build of BRender 1.3.2 keeps its own ladder. The textured
pentprim path (branch `feat/textured-dispatch`) stays an archival task: it
proves the 1998 kernels, and the modern builds above do not wait on it.

## What this roadmap does not claim

No Vulkan or Direct3D backend exists here yet. No pixel parity between the
period and modern rasterisers is measured yet. macOS is untested. The Linux
builds are checked headless (SDL offscreen, Mesa llvmpipe) in CI and on WSL;
a desktop session on real hardware is not part of the CI record.
