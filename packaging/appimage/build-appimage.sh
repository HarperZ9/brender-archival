#!/usr/bin/env bash
# Build an AppImage from a staged release folder.
#
#   bash packaging/appimage/build-appimage.sh <stage-dir> <exe-name> <title> <icon.png> <out.AppImage>
#
# The stage folder is what `cmake --install` writes for one product (the
# program, libSDL3.so.0 and its data). It becomes the AppImage's root, and
# AppRun starts the program there, so the program finds its data and SDL3
# exactly as it does when run from the unpacked tarball.
#
# The AppImage runtime comes from AppImage/type2-runtime, release 20251108,
# pinned by SHA-256 below and checked before use. mksquashfs comes from the
# distribution (squashfs-tools). Nothing else is downloaded.
set -euo pipefail

RUNTIME_URL=https://github.com/AppImage/type2-runtime/releases/download/20251108/runtime-x86_64
RUNTIME_SHA256=2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d

stage=$1 exe=$2 title=$3 icon=$4 out=$5
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
app="$work/AppDir"

cp -a "$stage" "$app"
test -x "$app/$exe" || { echo "no program $exe in $stage" >&2; exit 1; }

cat > "$app/AppRun" <<EOF
#!/bin/sh
here=\$(dirname "\$(readlink -f "\$0")")
exec "\$here/$exe" "\$@"
EOF
chmod +x "$app/AppRun"

cat > "$app/$exe.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$title
Exec=$exe
Icon=$exe
Categories=Game;
Terminal=false
EOF
cp "$icon" "$app/$exe.png"
ln -s "$exe.png" "$app/.DirIcon"

curl -sSL -o "$work/runtime" "$RUNTIME_URL"
echo "$RUNTIME_SHA256  $work/runtime" | sha256sum -c --quiet -

mksquashfs "$app" "$work/fs.squashfs" -root-owned -noappend -comp gzip -quiet
cat "$work/runtime" "$work/fs.squashfs" > "$out"
chmod +x "$out"
echo "built $out ($(stat -c %s "$out") bytes)"
