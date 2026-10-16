# Changelog

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
