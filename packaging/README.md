# Packaging

How The Keeper's Hour and brview reach players beyond the GitHub releases.

| Channel | What is here | State |
|---|---|---|
| GitHub releases | Windows zip and Linux tarball, built by the release workflows | published |
| AppImage (Linux) | `appimage/build-appimage.sh`, run by CI and by the release workflows | built and smoke-run in CI. The first release that carries one is the next tag. |
| winget (Windows) | `winget/<Identifier>/<version>/`, three manifests, schema 1.6.0 | prepared, `winget validate` passes. Not submitted. |
| Scoop (Windows) | `scoop/<product>.json`, with `checkver` and `autoupdate` | prepared. Not submitted. |
| itch.io | `itch/keepers-hour.md`, page text and fields | draft. Not published. |

Submitting to winget-pkgs, adding a Scoop bucket or creating the itch.io page
puts the project on a third-party service. That is the author's decision.
Everything here is ready for it, and nothing here is submitted.

## AppImage

`build-appimage.sh` turns a staged release folder (what `cmake --install`
writes) into an AppImage. The folder becomes the image's root, AppRun starts
the program there, and the program finds its data and `libSDL3.so.0` as it
does from the tarball. The runtime is AppImage/type2-runtime release
20251108, fetched at build time and checked against its SHA-256 before use;
`mksquashfs` comes from the distribution.

CI builds both AppImages from the packaged copies and runs them with
`--appimage-extract-and-run`, which needs no FUSE, from outside the build
tree. The release workflows do the same before uploading. On a desktop with
FUSE, the AppImage runs directly: `chmod +x` it, then start it.

## winget and Scoop

`update_manifests.py <product> <version>` writes both from the release: it
reads the `.sha256` file the release workflow published beside the Windows
zip. A manifest can therefore only carry a hash CI produced after the
packaged smoke run.

```
python packaging/update_manifests.py keepers-hour 0.4.0
python packaging/update_manifests.py brview 0.1.2
winget validate --manifest packaging/winget/HarperZ9.TheKeepersHour/0.4.0
```

Not yet checked:

- **winget install.** It needs local manifests enabled, which is a machine
  setting, or a submission. The zip is installed as a portable package with
  an alias to the program inside its folder, and SDL3.dll sits beside it.
  Whether the alias finds SDL3.dll is the first thing to check in the
  winget-pkgs validation run.
- **Scoop install.** Scoop is not installed here. Scoop launches through a
  shim that starts the real program in its folder, so SDL3.dll and the data
  are found, but this has not been run.

To submit: copy `winget/<Identifier>/<version>/` to
`manifests/h/HarperZ9/<Identifier>/<version>/` in a fork of
microsoft/winget-pkgs and open a pull request. For Scoop, add `scoop/*.json`
to a bucket repository, or propose them to the Games or Extras bucket.
