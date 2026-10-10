# The Keeper's Hour

A short, strange, talkative game about the last night of a lighthouse. Built on
BRender, the 1990s Argonaut engine, running on a modern PC.

## The pitch

You keep a lighthouse on a coast the sea left years ago. The lamp still turns.
Nobody remembers why it should. Tonight a letter says the light goes off at
dawn, and you have one night to decide what that means.

Nothing attacks you. The tension is in the room: a logbook that has opinions,
a kettle that has given up, a radio that picks up ships that are not there, and
four voices in your own head that disagree about all of it. You walk, you look,
you talk, and the lamp sweeps the walls every few seconds like an eye opening.

It is closer to Disco Elysium than to horror: humane, funny, a little sad,
built from conversation and noticing rather than threat.

## What makes it this author's game

- **The aperture.** The lamp is the central object, a faceted lens around a
  bright core, and its beam is the rhythm of every scene. Light from darkness,
  the lone figure against the vast, the tower: the recurring forms of the
  author's art, used as the stage rather than as decoration.
- **Reveal the process.** Every skill check shows its numbers: the voice, its
  rating, the two dice, the target. Nothing is hidden behind a curtain.
- **Secure, not anxious.** No timers that punish, no fail states that waste
  your evening. The night ends when you choose to end it. The game is about
  25 minutes and then it lets you go.
- **Period honest.** Every frame is drawn by BRender. The look is what a 1998
  engine does well: flat and Gouraud shading, a few textures, hard
  silhouettes, a palette that knows its limits.

## The four voices

Your skills are people in your head. Each has a rating from 1 to 6 and a way of
talking.

| Voice | What it notices | How it talks |
|---|---|---|
| The Lens | detail, light, what is actually there | precise, a little cold |
| The Ledger | rules, habits, what was written down | dry, bureaucratic, often right |
| The Tide | feeling, other people, what is owed | warm, overwhelming |
| The Static | the radio, chance, the half-heard world | fragmentary, sometimes prophetic |

A check rolls two six-sided dice plus the voice's rating against a target. The
dice come from a seeded generator, so a given night replays the same way, and
the roll is shown in full. Failing a check opens a different line, never a dead
end.

## The night

Five rooms on one tower, climbed in any order, each with three or four things
to talk to:

1. **The lamp room** (the slice): the lens, the logbook, the kettle.
2. **The radio room**: a set that hears ships that are not there.
3. **The stairs**: 112 steps, and the paintings someone hung on them.
4. **The keeper's room**: the bed, the letter, a photograph.
5. **The gallery**: outside, the dry seabed, the town lights far off.

Three endings follow from what you learned and who you listened to: keep the
light on in defiance, turn it off with ceremony, or point it at the town.

## Controls

| Action | Keyboard and mouse | Gamepad |
|---|---|---|
| Walk | WASD or arrows | left stick |
| Look around | hold right mouse and move | right stick |
| Talk to what is in front of you | E or left click | A |
| Choose a reply | 1 to 4, or click | D-pad and A |
| Skip a line | Space | A |
| Leave a conversation | Esc | B |
| Fullscreen | Alt+Enter | |

Every action is remappable in a later milestone; the slice ships the defaults.

## How it is built

- Engine: BRender 1.4 from BlazingRenderer/BRender (MIT), 64-bit, through
  this repository's `modern/` build. OpenGL by default, BRender's software
  rasteriser with `--force-software`.
- Window, input and gamepad: SDL3 (zlib).
- Geometry: built in code from BRender model primitives, so the slice needs no
  art files yet. Later rooms add hand-made `.dat` models and `.pix` textures.
- Dialogue: a plain text script (`night.txt`), one node per block, read at
  start-up. Writers edit text, not C.
- UI: BRender's own pixelmap text, drawn over the 3D frame.

## Licence

- **Code: MIT**, the same as the rest of this repository and as BRender.
- **Words and art: CC BY 4.0** (the dialogue script, and every model, texture
  and image made for the game). Why: anyone may reuse, remix and sell them,
  including in commercial games, with credit. Credit keeps the work traceable
  to its author, which matters to this project's provenance practice, and CC BY
  is already the licence the author uses for written work. CC0 was the
  alternative; it was not chosen because it drops the credit.
- Fonts: BRender's built-in bitmap fonts (MIT) only.

## Scope and milestones

| Milestone | What ships | Exit check a test can run |
|---|---|---|
| M0 Slice (done) | lamp room, three talkers, four voices, checks, walk and look | `KEEPERS_SMOKE=1` walks a scripted route, opens every node in the lamp room and exits 0; the script parser rejects a node that links to a missing node |
| M1 Tower (done) | all five rooms and their talkers | every node reachable from the start, checked by a graph test over `night.txt` |
| M2 Endings (done) | the letter, three endings, a save at each room | each ending reached by a scripted route in CI |
| M3 Craft (done, see notes) | textures, sound, remapping, an options screen | software and OpenGL runs show the same scene: edge correlation >= 0.76 per room, with a wrong-room control that must fail |
| M4 Release | Windows zip on GitHub releases with credits and licences | the packaged copy passes the smoke run in CI |

The game stays small on purpose: one tower, one night, about 25 minutes.

### Notes on M3, as built

- **Pictures:** seven 128 x 128 textures (floorboards, stone, the sea chart,
  the tower painting, Agnes's portrait, the photograph, the letter) are drawn
  stroke by stroke by `tools/make_art.py` from fixed seeds. A test holds the
  committed files to the script. The furniture is still built in code from
  BRender primitives; hand-modelled `.dat` furniture is not done and moves to
  a later milestone.
- **Sound:** a small mixer synthesises everything (wind, the clockwork tick
  once a sweep, radio crackle, a note per voice, dice, doors, a chord at dawn).
  raw-native's sound engine was not used: it is web-side, and this is a native
  C build. There are no sound files.
- **Options:** F2 or the gamepad's Back button: volume, look speed and six
  rebindable actions, saved in the player's preferences folder.
- **Renderer parity:** `tools/parity.py` draws a still of every room on
  OpenGL and on the software rasteriser and compares them. The first bounds,
  set before measuring, also passed a wrong-room comparison, so they could not
  tell rooms apart. The verdict now rests on edge correlation (>= 0.76), a
  bound chosen after seeing the numbers (same room 0.78 to 0.86, wrong rooms
  up to 0.73: a thin margin). Each run repeats the wrong-room control. Result
  on 10 October 2026: all five rooms pass and all 20 wrong-room pairs fail
  (`evidence/parity-2026-10-10.json`). CI has no OpenGL, so this runs locally.
