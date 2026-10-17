# Changelog

## Unreleased: Vulkan, stage A

- ADR 0002 sets out the Vulkan backend in three stages, each measured against the software rasteriser: A, a headless Vulkan rasteriser; B, a Vulkan primitive library under softrend; C, a renderer facility like glrend.
- Stage A is in `modern/vulkan/`, built with `-DBRENDER_VULKAN=ON`. It needs the Vulkan headers and loader and `glslangValidator`. `vk-triangle` draws flat-coloured screen-space triangles with Vulkan and with BRender 1.4's software rasteriser, and `vk_compare.py` compares them.
- Measured 17 October 2026 on Mesa lavapipe: coverage IoU 0.9913 for a triangle, 1.0 for a quad split along a diagonal, and 0.9137 for thin slivers. The colour is within one level wherever both draw, and two runs give the same bytes.
- Found on the software side: some flat colours come out one level low (232, 180, 92 is written as 231, 179, 92), and a shared diagonal gives 80 more pixels to the first triangle. Vulkan writes exact colours and splits the diagonal evenly.
- CI runs stage A on Linux with lavapipe forced and holds it to the measured bounds. It keeps the frames as the `vulkan-triangle` artifact.

## Unreleased: The Keeper's Hour 0.6.0, toward 1.0

- A title screen: the lamp room turns slowly behind the name, with Begin the night, Carry on (when a night is saved), Options and Quit, by keyboard, gamepad or mouse. It replaces the old "resume" conversation.
- Text size (F2): Auto or 1 to 3. Every word is BRender's 7 x 9 font drawn at a whole-number scale, so it stays crisp; Auto takes one step per 640 x 400 of window (2 at 1080p). Panels, the dawn card and the options grow with it. On OpenGL the scaled glyphs go straight onto the frame; on the software renderer through a memory strip, as 1x text already did.
- Dawn: once the keeper opens the decision the sky greys at the edges, and at an ending it turns to dawn. The period look's palette carries three steps of it.
- One item to keep: the letter's second page now pays off. The decision offers the item; the logbook is always there, and the kettle, the photograph and the radio join it if you found them in the night. The dawn card names what you kept, and says "not asked tonight" for a voice you never rolled instead of "heard 0 of 0".
- The logbook's "Marigold called." waits until you have heard the Marigold (on the lamp, or on the radio as "A ship called on the radio.").
- For stills: `KEEPERS_OPEN` takes several nodes ("a,b,c"), `KEEPERS_END=1` shows the dawn card and `KEEPERS_TITLE=1` the title. Script: 85 nodes.

## Unreleased: OpenGL against software

- `modern/parity/gl_vs_software.py` draws every brview model on BRender 1.4's OpenGL driver and on its software rasteriser and compares them, unlit, textured and lit, with a wrong-model control and a byte-for-byte repeat of the OpenGL stills. Measured 16 October 2026 (Mesa llvmpipe): coverage IoU 0.9774 or better and the same colour wherever both draw; textures agree on about 79% of pixels; lit stills differ by design. CI runs it on Linux within the measured bounds.
- Found: the software rasteriser does not light a 24-bit textured material without a shade table (the lit and unlit stills are the same bytes), as in 1998; OpenGL lights it.
- brview: `BRVIEW_SCENE`, `BRVIEW_TEXTURE` and `BRVIEW_UNLIT` set what a `BRVIEW_SHOT` still draws. The command line and the saved options move to `viewer/brview_run.c`.

## Unreleased: perspective-correct 8-bit parity

- Depends on engine-revival 0.7.0. Its line-by-line ports of `fti8pizp.asm` (`TriangleRender_ZPT_I8_D16_256` and `TriangleRender_ZPTI_I8_D16_256`) and of the `pfpsetup.asm` setup make the period build draw `BR_MATF_PERSPECTIVE` textures into 8-bit buffers. Before it, those kernels were stubs that drew nothing.
- `modern/parity/`: six perspective scenes (the sphere with `earth.pix` and the torus with `rosewood.pix`, unlit and lit through `shade.tab`, and a plane of eight large triangles built in the scene program and turned 60 degrees so it recedes, unlit and lit) and the same plane without perspective. Measured 17 October 2026 against BRender 1.4: coverage IoU 0.9983 or better, 92.6% to 97.9% of pixels on the same palette index, MAD at most 1.71.
- Found: the steep plane scores the same with and without perspective (92.6% and 92.7% identical), so its difference is not in the perspective kernels. The two softrend versions hand the rasteriser screen coordinates that differ by up to 0.03 pixels for the same triangles. Recorded; where in the period geometry it comes from is not yet located.
- Found: the sphere's triangles all take the 1998 setup's linear "cheat" path (w changes too little across them), on both sides, so the perspective sphere draws the same bytes as the linear one. The torus has 28 perspective triangles of 112, the plane all 8.
- CI: the perspective scenes run twice on the period side (identical bytes required, also as their own check) and are gated against BRender 1.4 within the measured bounds. The art card's harness file count was stale (31; the materializer writes 37).

## Unreleased: the period look

- The Keeper's Hour: a Period look option (F2) draws the rooms in 256 colours through BRender's own 8-bit palette path, on the software renderer. The game builds its palette from its own materials: ramps for lit surfaces, the glows and skies as they are, and 128 colours cut from the pictures, which become 8-bit maps lit through a shade table. Saved with the other options; `KEEPERS_PERIOD=1` for one run.
- brview: the 8 key turns on the same look, through the 1998 `std.pal` and the first 37 rows of `shade.tab` (full light keeps a map's colours). Saved; `BRVIEW_PERIOD=1` for one run. brview and the game start on the software renderer when the look is on.
- `modern/display`: `brd_display_render_period` draws into an INDEX_8 buffer at the chosen pixel size and shows it through a palette.
- `display_check.py` checks the look on frames: 256 colours or fewer, the 8-bit path ran (the frame differs from true colour), and the same scene (mean difference at most 30 levels; measured 10.5 for the game and 24.0 for brview). In the game a control must fail: the true-colour frame has more than 256 colours. CI keeps the stills as artifacts.

## Unreleased: 8-bit and lit textured parity

- Depends on engine-revival 0.6.0. Its line-by-line ports of `zb8.asm`, `fti8_piz.asm` and the `fpsetup.asm` float setup make the period build draw into 8-bit buffers through BRender's own palette path.
- `modern/parity/`: nine 8-bit scenes (five untextured, two textured, two lit textured through `shade.tab`) and two 24-bit lit textured scenes. Measured 16 October 2026 against BRender 1.4: the 8-bit scenes reach coverage IoU 0.9983 or better, with 96.4% to 99.9% of pixels on the same palette index and MAD at most 0.43.
- A 1998 defect, recorded: BRender 1.3.2's 24-bit lit textured kernel (`TrapezoidRenderPIZ2TIA_RGB_888` in `t_piza.asm`) reads its 3-byte RGB_888 shade table at a 4-byte stride, so it draws those scenes as stripes (coverage IoU 0.48 and 0.66). With the table laid at the stride the kernel reads (`PARITY_SHADE4=1`, period side only) the scenes match: coverage IoU 0.9998 or better, 97.9% and 99.5% identical. The period build keeps the 1998 behaviour.
- CI: the period scenes also run twice with the table at stride 4 (identical bytes required); the 8-bit classes and the stride 4 lit textured scenes are gated within their measured bounds; the 24-bit lit textured scenes as shipped are reported.

## Unreleased: brview display options

- brview: [ and ] set the pixel size (1 to 6), - and = the field of view (40 to 90 degrees), V vsync; they are saved in the preferences folder and shown in the title line. `BRVIEW_PIXEL`, `BRVIEW_FOV` and `BRVIEW_SHOT=<file.ppm>` (one still of the first model, without spin) serve checks and screenshots.
- The display code moves from the game to `modern/display/brdisplay.{c,h}`, a small library brview and The Keeper's Hour both link. It adds `brd_frame_write_ppm`, which waits for OpenGL to finish before reading back.
- brview's software rasteriser now draws in 24-bit colour unless `--software-bpp` is given, as the game's does. brdemo's 8-bit default had no palette to read stills back through.
- `games/keepers-hour/tools/display_check.py --program brview` runs the eight display checks on brview; CI runs them on Windows (software) and Linux (software and OpenGL). The pixel size 1 control bound rises from 0.80 to 0.95 after measuring brview's mostly flat background (0.83); calibrated.

## Unreleased: textured parity

- Depends on engine-revival 0.5.0. Its port of `t_piza.asm`, under Argonaut's `awtmz.c` setup, makes the period build draw textured scenes, and its renderer rung now requires a textured frame.
- `modern/parity/`: three textured scenes (the sphere with `earth.pix` at two angles, and the torus with `rosewood.pix`). Measured 16 October 2026 against BRender 1.4: coverage IoU 0.9992 or better, 95.7% to 99.7% identical pixels, MAD at most 1.09. Period runs are byte-identical across all nine scenes.
- `parity_compare.py --only` and `--skip` hold one class of scene to its own bounds. CI gates untextured and textured scenes separately.

## Unreleased: the 1998 rasteriser, measured

- Depends on engine-revival 0.4.0. Its C port of BRender's `tt24_piz.asm` kernels makes the period build draw the flat and Gouraud scenes, and deterministically. The renderer rung now fails CTest when its render is invalid.
- `modern/parity/`: the period side clears depth to far, as the 1998 kernels expect. New evidence for 16 October 2026: two period runs are byte-identical, and against BRender 1.4 coverage IoU is 0.9993 or better on all six scenes, with 90.7% to 100% of pixels identical and MAD under 0.2 levels. `parity_compare.py --bounds` takes an optional mean-difference limit.
- CI: the `brender-native` job runs the period scenes twice and requires identical bytes, and the `parity` job compares modern against period within the measured bounds.

## Unreleased: pixel parity instrument

- `modern/parity/`: `parity-scene.c` draws seven untextured scenes on either engine. It is built 64-bit by `modern/CMakeLists.txt` and 32-bit against the period harness by `parity/period/CMakeLists.txt`. `parity_compare.py` reports coverage IoU, identical pixels, MAD and the largest difference per scene, with a control that must fail.
- Measured on 16 October 2026 (`modern/parity/evidence/`):
  - BRender 1.4's software rasteriser is deterministic, and Windows MSVC against Linux GCC gives identical coverage, with at most 0.02% of pixels one level apart.
  - The period 1.3.2 build is not yet a usable reference: its flat paths draw nothing, its Gouraud path saturates and drops faces, and it varies between runs. No parity claim is made.
- CI runs the modern scenes twice on Windows and on Linux (identical bytes required), and a new `parity` job compares Windows against Linux within the measured bounds.
- The winget and Scoop manifests follow The Keeper's Hour 0.4.1 and brview 0.1.3.

## Unreleased: packaging

- `packaging/appimage/build-appimage.sh` builds an AppImage from a staged release folder, with the AppImage type2 runtime (release 20251108) pinned by SHA-256 and checked before use. CI builds both AppImages and runs them headless; `release-keepers.yml` and `release-brview.yml` attach `*-x86_64.AppImage` with a SHA-256 after the same smoke run.
- `packaging/update_manifests.py` writes winget (schema 1.6.0) and Scoop manifests from the SHA-256 a release published. Committed for The Keeper's Hour 0.4.0 and brview 0.1.2; `winget validate` passes. Not submitted.
- `packaging/itch/keepers-hour.md`: an itch.io page draft. Not published.
- `scripts/linux-build-deps.sh` adds `squashfs-tools` and `curl`.

## Unreleased: deterministic OpenGL capture

- The Keeper's Hour finishes the OpenGL frame (`glFinish`) before each captured frame is read back. Under Mesa llvmpipe the readback sometimes returned the previous frame; four 15-frame recordings repeated a frame in every run, and with the fix five 30-frame recordings gave 30 distinct frames, identical across runs. Play is not affected: only captures wait.
- CI records twice on both renderers on Linux, and on Windows, and fails if any frame repeats the one before it (the stale-readback signature) or the two runs differ.

## Unreleased: display options

- The Keeper's Hour: pixel size 1 to 6, field of view 40 to 90 degrees and vsync in the F2 options, saved with the others. Pixel size draws the scene into a smaller offscreen buffer and scales it up with whole pixels (nearest neighbour), then draws the text and panels at full resolution. `kh_display.c` holds it. `KEEPERS_PIXEL` and `KEEPERS_FOV` override the two for one run.
- `tools/display_check.py` checks eight claims on frames, each with a control: whole pixels at size 4, the same scene at sizes 1 and 4, Hor+ at 4:3, 16:9 and 21:9, and that the field of view changes the picture. CI runs it on Windows and on Linux (software and OpenGL). Evidence: `games/keepers-hour/evidence/display-*-2026-10-16.json`.
- The options smoke line is now `keepers options: rebind, display and save ok`: the self-check sets pixel size, field of view and vsync through the menu and reads them back.

## Unreleased: Linux

- brview and The Keeper's Hour build, run and package on 64-bit Linux. No source change was needed; the programs now load SDL3 from their own folder through a `$ORIGIN` run path, and the install step copies it as `libSDL3.so.0`, the name the loader looks for. The Windows programs are unchanged.
- CI job `linux` (ubuntu-24.04, GCC, Ninja) runs the brview and game smoke checks, the frame recorder twice on the software rasteriser with identical bytes, the packaged copies from outside the build tree, and the 21-step ladder (21 of 21).
- `release-brview.yml` and `release-keepers.yml` add `*-linux-x64.tar.gz` with a SHA-256, published only after the packaged copy passes its smoke run. The brview package installs only the viewer's component (`--component Unspecified`), so it cannot pick up the game's files, which the game's install rules added to the default install after brview 0.1.1.
- `scripts/linux-build-deps.sh`: the one Debian and Ubuntu package list CI, the releases and users share.
- `docs/ROADMAP.md`: the measured state on Windows and Linux and the ordered road to a user-ready BRender. `docs/adr/0001`: proposed route for raw-native to read BRender content (convert to glTF first).
- Known: under Mesa llvmpipe the OpenGL frame readback sometimes returns the previous frame, so the Linux recorder check uses the software rasteriser (roadmap item 3).

## 0.3.0 (unreleased)

- The Keeper's Hour: KEEPERS_RECORD writes numbered frames at a fixed step of game time (KEEPERS_FPS, KEEPERS_SECONDS, KEEPERS_CLOCK, KEEPERS_YAW, KEEPERS_YAW_SPEED, KEEPERS_CAPTURE_UI), for the trailer; KEEPERS_CLOCK also sets the lamp angle of a KEEPERS_SHOT still. CI records twice headless and requires identical bytes and a moving picture.
- The Keeper's Hour M4, release: credits on the dawn card and CREDITS.txt in the zip; the release workflow publishes only after the packaged copy passes the full smoke run.
- The Keeper's Hour M3, craft: seven textures drawn by tools/make_art.py (held to the script by a test); a synthesised sound mixer; options and key remapping (F2); the software renderer defaults to 24-bit and draws its text through memory; tools/parity.py compares OpenGL and software stills per room with a wrong-room control (all 5 pass, 20 of 20 controls fail; evidence committed).
- The Keeper's Hour M2, the endings: a decision at the lamp opens three endings, shown or hidden by what the night has found (`(?node)` choices); an end card shows which voices you listened to; the night saves at each room and offers to carry on. CI reaches all three endings by fixed routes and round-trips a save. `release-keepers.yml` packages the game for Windows on `keepers-v*` tags.
- The Keeper's Hour M1, the tower: five rooms built from a room table (lamp room, stairs, radio room, keeper's room, gallery), doors between them, 15 talkers and 75 script nodes. Shapes move to kh_shapes.c; rooms are data in kh_rooms.c. CI enters every room and opens every node; tests check every door leads somewhere and back.
- brview 0.1.1 and the game build as window-only programs (Windows GUI subsystem, SDL3 entry point): no console window opens beside them.
- `games/keepers-hour`: The Keeper's Hour, design and first playable slice (the lamp room). Code MIT; words and art CC BY 4.0 (`LICENSES/CC-BY-4.0.txt`). CI opens every script node headless; tests check every link and that every node is reachable.
- brview hides the frame-time line; the release workflow writes the .sha256 with LF so `sha256sum -c` reads it as is.
- `modern/`: brview, a model viewer for 64-bit Windows built on BRender 1.4 from BlazingRenderer/BRender (MIT, pinned commit `ed5e7a91`) and SDL3 (zlib, `release-3.4.16`), with the 1998 sample models. Released as a Windows zip by `release-brview.yml` on `brview-v*` tags.
- `modern/ladder64`: the 21-step ladder against BRender 1.4, 64-bit; 21 of 21 pass. CI jobs `ladder64` and `brview` run on every change.
- `LICENSES/` adds the BlazingRenderer MIT and SDL3 zlib texts for the binary distribution.
- The `engine_revival` package now lives only in [engine-revival](https://github.com/HarperZ9/engine-revival), pinned here at v0.3.0. `src/`, `schemas/` and `compat/` are removed from this repository, and so are the package tests, which run in engine-revival.
- The project is named `brender-archival` in `pyproject.toml` and installs no package of its own.
- The repository is MIT licensed, matching the terms BRender v1.3.2 was published under. This includes `compat/` and `gallery/`, which were AGPL-3.0-or-later.
- The upstream BRender notice (copyright 1998 Argonaut Software Limited) stays in `LICENSES/MIT-BRender.txt` and is now shipped in the package metadata beside `LICENSE`.
- The two `compat/` C files carry SPDX MIT headers naming both copyright holders.
- 0.2.0 stays FSL-1.1-MIT and 0.1.1 and earlier stay AGPL-3.0-or-later, as released.

## 0.2.0

- From v0.2.0, code is licensed FSL-1.1-MIT. Earlier releases remain under AGPL-3.0-or-later.
- `LICENSE` is the FSL-1.1-MIT text from fsl.software, with licensor Zain Dana Harper and copyright 2026.
- `compat/` and `gallery/` keep their released terms. `compat/` ports routines from BRender v1.3.2, which is MIT, copyright Argonaut Software Limited. Each directory has a `LICENSE-NOTE.md`.
- `LICENSES/` holds the AGPL-3.0-or-later text and the BRender MIT text read at the pinned upstream commit. The BRender MIT notice was missing from the repository before; it is now shipped beside the ports.
- `pyproject.toml` declares `license = "FSL-1.1-MIT"` (PEP 639, setuptools 77 or later) and version 0.2.0. No code behaviour changed.
- v0.1.1 and earlier releases stay AGPL-3.0-or-later.

## 0.1.1

BRender archival release of 27 August 2026, under AGPL-3.0-or-later.
