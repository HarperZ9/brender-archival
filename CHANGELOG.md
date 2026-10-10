# Changelog

## 0.3.0 (unreleased)

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
