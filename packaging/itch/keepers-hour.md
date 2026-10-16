# The Keeper's Hour: itch.io page draft

Draft text for an itch.io page. Nothing here is published. Creating the page
and uploading builds is the author's decision. Fields follow itch.io's
"Create a new project" form.

## Fields

| Field | Value |
|---|---|
| Title | The Keeper's Hour |
| Project URL | harperz9.itch.io/the-keepers-hour |
| Short description | The last night of a lighthouse on a coast the sea left behind. |
| Classification | Games |
| Kind of project | Downloadable |
| Release status | Released |
| Pricing | No payments (free) |
| Uploads | `keepers-hour-<version>-windows-x64.zip` (Windows), `keepers-hour-<version>-x86_64.AppImage` and `keepers-hour-<version>-linux-x64.tar.gz` (Linux), from the GitHub release |
| Genre | Adventure |
| Tags | narrative, lighthouse, short, retro, 3d, dialogue, choices-matter, open-source |
| Average session | About half an hour |
| Languages | English |
| Inputs | Keyboard, Mouse, Xbox controller, Playstation controller |
| Accessibility | Configurable controls |
| Source code | https://github.com/HarperZ9/brender-archival (games/keepers-hour) |
| Licence | Code MIT; words and art CC BY 4.0 |

## Description

The sea left this coast years ago. The light still turns.

Tonight is the last night of the lighthouse at Relay Nine. A letter says the
lamp goes out at dawn. You are the keeper, and you have until then: five rooms,
fifteen things that will talk to you if you let them, and four voices in your
own head that do not agree about anything.

- **About 25 minutes**, three endings, and the night saves every time you
  change room.
- **Every check shows its sums.** A voice's rating plus two dice against a
  target, on screen. Failing a check opens a different line, never a dead end.
- **Built on BRender**, Argonaut Software's 3D engine from the 1990s, revived
  as a 64-bit engine. Run it on OpenGL or on BRender's own software rasteriser
  (`--force-software`).
- **Pixel size 1 to 6** in the options for a coarser, period look, with the
  text kept sharp. Field of view and vsync are there too.
- **Keyboard, mouse and gamepad**, with every key remappable (F2).

## Controls

| Action | Keyboard and mouse | Gamepad |
|---|---|---|
| Walk | WASD or arrows | left stick |
| Turn the view | hold right mouse and move | right stick |
| Talk, continue, choose | E, Space, Enter or left click | A |
| Pick a reply | 1 to 4, or Up and Down then E | D-pad, then A |
| Leave a conversation | Esc | B |
| Options | F2 | Back |
| Fullscreen | Alt+Enter | |

## System requirements

- Windows 10 or 11, 64-bit. Unzip and run `keepers-hour.exe`.
- Linux, 64-bit, with glibc 2.38 or newer (Ubuntu 24.04, Debian 13, Fedora 39
  or later) and an X11 or Wayland desktop. Run the AppImage, or unpack the
  tarball and run `./keepers-hour`.
- OpenGL 3.3 for the default renderer. Without it, the game uses BRender's
  software rasteriser.

## Credits

Written, designed and built by Zain Dana Harper. Engine: BRender 1.4 from
BlazingRenderer/BRender (MIT), on BRender by Argonaut Software (1998, MIT).
SDL3 (zlib licence). Full credits are in `CREDITS.txt` inside every download.

## Screenshots

From `games/keepers-hour/media/` in the repository:

- `lamp-room-pixel-1.png`: the lamp room at pixel size 1.
- `lamp-room-pixel-4.png`: the same scene at pixel size 4.

A cover image (630 x 500) is still to be made. Make it from the game's own
frames with `KEEPERS_SHOT`, not from generated art.
