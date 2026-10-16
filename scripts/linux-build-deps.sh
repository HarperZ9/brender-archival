#!/usr/bin/env bash
# Packages a Debian or Ubuntu machine needs to build brview and The Keeper's
# Hour from modern/, and to run their headless smoke checks. CI and the Linux
# release jobs run this script, so the build a user reproduces is the one CI
# checks.
#
# SDL3 is built from source by modern/CMakeLists.txt. It enables a video or
# audio backend only when that backend's headers are present, so the X11,
# Wayland, ALSA, PulseAudio and PipeWire headers below decide what the
# shipped libSDL3.so.0 can open on a player's desktop.
set -euo pipefail
sudo apt-get update -q
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends \
  build-essential cmake ninja-build pkg-config git \
  glslang-tools spirv-cross \
  libx11-dev libxext-dev libxrandr-dev libxcursor-dev libxi-dev libxss-dev \
  libxtst-dev libxfixes-dev libxinerama-dev libxkbcommon-dev \
  libwayland-dev wayland-protocols libdecor-0-dev \
  libegl-dev libgl-dev libgles-dev libdrm-dev libgbm-dev \
  libasound2-dev libpulse-dev libpipewire-0.3-dev \
  libdbus-1-dev libudev-dev \
  libegl-mesa0 libgl1-mesa-dri
