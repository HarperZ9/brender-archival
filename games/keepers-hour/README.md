# The Keeper's Hour

A short, strange, talkative game about the last night of a lighthouse on a
coast the sea left years ago. Built on BRender, the 1990s Argonaut engine,
running 64-bit on a modern PC. The design is in [DESIGN.md](DESIGN.md).

**Milestone M1, the tower:** five rooms (the lamp room, the stairs, the radio
room, the keeper's room and the gallery outside), 15 things to talk to, and
75 script nodes. Walk between rooms through the doors and stairs, listen to
the four voices in the keeper's head argue, and watch every skill check show
its dice. The endings come in M2.

## Play it

Build it with the modern BRender build (see [../../modern/README.md](../../modern/README.md)):

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
| Fullscreen | Alt+Enter | |
| Quit | Esc outside a conversation | |

For writers: `KEEPERS_OPEN=lamp keepers-hour.exe` starts inside any node of
[data/night.txt](data/night.txt), and `KEEPERS_ROOM=gallery` starts in any room. `KEEPERS_SMOKE=1` opens every node once and
reports problems; CI runs it, and `tests/test_keepers_script.py` checks that
every link resolves and every node can be reached.

## Licence

Code MIT. Words and art CC BY 4.0, with the reasons in
[LICENSE-NOTE.md](LICENSE-NOTE.md).
