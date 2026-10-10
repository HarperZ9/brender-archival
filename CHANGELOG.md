# Changelog

## 0.3.0 (unreleased)

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
