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

### 2. Display: resolution, widescreen and a period look (met)

Shipped in The Keeper's Hour on 16 October 2026: pixel size 1 to 6 (the scene
drawn coarser and scaled up with whole, square pixels, text kept sharp), field
of view 40 to 90 degrees, and vsync, in the F2 options and saved. The field of
view is vertical, so widescreen is Hor+. `games/keepers-hour/tools/display_check.py`
checks it on frames at 4:3, 16:9 and 21:9 with failing controls, on both
renderers, in CI on Windows and Linux.

brview has the same settings since 16 October 2026 ([ and ] pixel size,
- and = field of view, V vsync, saved), from one display module shared with
the game (`modern/display`), checked by the same tool in CI.

The period look (16 October 2026), in the game's F2 options and on brview's
8 key: the scene drawn into an 8-bit buffer by BRender's own palette path and
shown through its palette. The game builds a 256-colour palette from its own
materials and maps (ramps for lit surfaces, median-cut colours for the
pictures, a 64-row shade table); brview uses the 1998 `std.pal` and
`shade.tab`. Software renderer only. `display_check.py` checks it draws in
256 colours or fewer and shows the same scene, with controls. The 8-bit
kernels are measured against the 1998 ones in item 5.

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

### 5. Renderer parity, measured (24-bit, 8-bit and 15/16-bit, untextured, textured and perspective-correct: met)

`modern/parity/` (see its README) draws one set of scenes on the 1998
rasteriser and on BRender 1.4's, and compares them pixel by pixel with a
control that must fail.

Measured on 16 October 2026, after engine-revival ported the 1998 kernels
line by line (`tt24_piz.asm` in 0.4.0, `t_piza.asm` under Argonaut's
`awtmz.c` setup in 0.5.0, `zb8.asm`, `fti8_piz.asm` and `fpsetup.asm` in
0.6.0):

- The 1998 build gives the same bytes on every run.
- **Untextured** (unlit, flat lit and Gouraud): coverage IoU 0.9993 or
  better, 90.7% to 100% of pixels identical, mean difference under 0.2
  levels.
- **Textured** (unlit): coverage IoU 0.9992 or better, 95.7% to 99.7% of
  pixels identical, mean difference at most 1.09 levels.
- **8-bit through the palette** (untextured, textured and lit textured):
  coverage IoU 0.9983 or better, 96.4% to 99.9% of pixels on the same
  palette index, mean difference at most 0.43 levels.
- **8-bit perspective-correct** (17 October 2026, engine-revival 0.7.0
  ports `fti8pizp.asm` and `pfpsetup.asm`, checked byte for byte against the
  assembled 1998 code): coverage IoU 0.9983 or better, 92.6% to 97.9% on the
  same index, MAD at most 1.71. The lowest, a steep plane, scores the same
  without perspective; its difference comes from the vertex data, not the
  kernels.
- **24-bit lit textured**: a 1998 defect. The kernel reads its 3-byte shade
  table at a 4-byte stride and draws garbage. Laid at that stride (period
  side only, as a measurement), the scenes match: coverage IoU 0.9998 or
  better, 97.9% and 99.5% identical.
- **15/16-bit** (17 October 2026, engine-revival 0.8.0 ports `tt15_piz.asm`,
  `tt16_piz.asm`, `zb16p2ul.asm` and `t_piza.asm`'s 16-bit instances, checked
  byte for byte against the assembled 1998 code): the period build draws all
  twenty RGB_555 and RGB_565 scenes, textured ones included. BRender 1.4
  reproduces pentprim's MMX path for these formats, which the 1998 matcher
  uses instead of the general tables on an MMX processor. That path draws
  these maps untextured, so only the untextured scenes compare: coverage IoU
  0.9869 or better, MAD at most 2.08, with the colour identical wherever both
  draw a flat scene.
- **15/16-bit through the MMX table** (17 October 2026, engine-revival 0.9.0
  ports pentprim's MMX family, checked byte for byte against the assembled
  1998 code; the period build runs it with `BRENDER_PENTPRIM_MMX`): the 1998
  path BRender 1.4 reproduces, so textured scenes compare too. 34 scenes, 8-bit
  palette maps and dithering included: coverage IoU 0.9970 or better, 96.6% to
  99.9% identical, MAD at most 0.48. Fed 1.4's own vertices, the 1998 kernels
  draw 1.4's frames byte for byte, so the rest comes from the vertices.
- CI checks every change: determinism on all three builds, and both scene
  classes within their measured bounds. The 1998 renderer rung now gates on
  a textured frame.

The first measurement that day found the 1998 build unusable. The C port
shadowed BRender's component slots, its Gouraud and depth logic were wrong,
and its texture setup was missing. The parity README keeps that record.

OpenGL against software (BRender 1.4, Mesa llvmpipe, 16 October 2026): every
brview model fills the same pixels to a coverage IoU of 0.9774 or better, with
the same colour wherever both draw; the remaining pixels sit on edges, split
about evenly. Lit stills differ by design (per-pixel against per-vertex
lighting), and the software rasteriser does not light 24-bit textures without
a shade table, as in 1998. CI gates it on Linux (`modern/parity/README.md`).

- **The same angle on both sides** (17 October 2026): the period geometry
  difference was the angle macro. BRender 1.3.2's `BR_ANGLE_DEG` is 182 units
  a degree, truncated; 1.4's is exact. With the same angle on both sides, 50
  of 61 scenes are byte-identical to 1.4 on Windows (first reported as 56,
  before the comparison counted pixels exactly); the rest differ in 1 to 5
  pixels by one level.
- **Z-sorted, TIP256 and the MMX perspective rows** (17 October 2026):
  engine-revival 0.10.0 ports the last kernels these scenes reach and
  softrend's subdivision. The z-sorted 15/16-bit scenes and the MMX
  perspective rows match 1.4 to one pixel. 1.4 has no TIP kernel and refuses
  z-sorted TIP; the 1998 MMX table takes z-sorted triangles (BlazingRenderer's
  fix in 1.4). Both are reported.

- **Where the last pixels come from** (17 October 2026): the residues trace
  to the two versions' sine and cosine. Built with 1.3.2's trig, BRender 1.4
  draws all 85 scenes both versions draw alike byte for byte as the period
  build does; CI holds that variant to byte identity.

Still open: the 8-bit perspective kernels for maps that are not 256 wide
have no scene.

Done when: a parity record (JSON) for each pair is committed and CI
recomputes it. Met for RGB_888 untextured, textured and lit textured (the
last through the stride measurement), for INDEX_8, and for RGB_555 and
RGB_565 untextured.

### 6. Modern GPU backends (Vulkan stage A: built)

BRender 1.4 has OpenGL 3.3. Add Vulkan first (it runs on Windows and Linux),
then Direct3D 11 or 12 if Windows needs it. Each backend is a BRender driver
written here under MIT, offered upstream to BlazingRenderer, and held to the
item 5 parity bounds against the software rasteriser.

The plan is ADR 0002 (`docs/adr/0002-vulkan-backend.md`), in three stages:

- **A, a headless Vulkan rasteriser, is built** (`modern/vulkan/`,
  `-DBRENDER_VULKAN=ON`). On Mesa lavapipe it draws the same triangles as
  the software rasteriser to a coverage IoU of 0.9897 or better, or 0.9137
  for thin slivers. The colour is within one level wherever both draw. The
  two differ only at edges, where they follow different edge rules. Two runs
  give the same bytes. CI checks it on Linux.
- **B, a Vulkan primitive library under softrend, is built** (`vkprim`,
  `vk-scenes`). It rasterises softprim's own screen-space vertices with
  Vulkan, with depth, into BRender's buffers. On six untextured scenes it
  reaches coverage IoU 0.9764 to 0.9959. Flat colours are identical wherever
  both draw, and Gouraud MAD is under 3. CI checks it on Linux.
  Textures are next.
- **C, a full renderer facility like glrend, comes after B.**

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
