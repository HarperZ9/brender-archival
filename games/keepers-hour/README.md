# The Keeper's Hour

A short, strange, talkative game about the last night of a lighthouse on a
coast the sea left years ago. Built on BRender, the 1990s Argonaut engine,
running 64-bit on a modern PC. The design is in [DESIGN.md](DESIGN.md).

**Milestone M4: released.** Credits on the dawn card and in CREDITS.txt; the
release workflow publishes a build only after the packaged copy passes the
full smoke run. All four milestones in DESIGN.md are done.

**Milestone M3: craft.** Textured stone, boards and pictures; sound made in
code; an options screen with volume, look speed and key remapping (F2); and
the same scene on OpenGL and on BRender's software rasteriser
(`--force-software`), checked room by room.

**Milestone M2: a complete short game.** Five rooms (the lamp room, the stairs,
the radio room, the keeper's room and the gallery outside), 15 things to talk
to, 80 script nodes, and three endings at dawn, opened by what you found in the
night. The night saves every time you change room, and the next start offers
to carry on. Every skill check shows its sums.

**Download for Windows:** `keepers-hour-<version>-windows-x64.zip` on the
[releases page](https://github.com/HarperZ9/brender-archival/releases). Unzip
and run `keepers-hour.exe`; the SHA-256 is beside the zip.

## Build it

Or build it with the modern BRender build (see [../../modern/README.md](../../modern/README.md)):

```
cmake -S modern -B build -A x64
cmake --build build --config Release
build\keepers-hour\Release\keepers-hour.exe
```

| Action | Keyboard and mouse | Gamepad |
|---|---|---|
| Walk | WASD or arrows | left stick |
| Turn the view | hold right mouse and move | right stick |
| Talk, continue, choose | E, Space, Enter or left click | A |
| Pick a reply | 1 to 4, or Up and Down then E | D-pad, then A |
| Leave a conversation | Esc | B |
| Options and key remapping | F2 | Back |
| Fullscreen | Alt+Enter | |
| Quit | Esc outside a conversation | |

For writers: `KEEPERS_OPEN=lamp keepers-hour.exe` starts inside any node of
[data/night.txt](data/night.txt), and `KEEPERS_ROOM=gallery` starts in any room. `KEEPERS_SMOKE=1` opens every node once and
reports problems; CI runs it, and `tests/test_keepers_script.py` checks that
every link resolves and every node can be reached.

## Licence

Code MIT. Words and art CC BY 4.0, with the reasons in
[LICENSE-NOTE.md](LICENSE-NOTE.md).
