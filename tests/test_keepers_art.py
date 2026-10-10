"""The Keeper's Hour pictures and the renderer parity evidence."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "games" / "keepers-hour"


def test_every_picture_is_exactly_what_the_script_draws():
    result = subprocess.run([sys.executable, str(GAME / "tools" / "make_art.py"), "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout


def test_every_picture_the_rooms_use_exists():
    import re

    rooms = (GAME / "src" / "kh_rooms.c").read_text(encoding="utf-8")
    world = (GAME / "src" / "kh_world.c").read_text(encoding="utf-8")
    used = set(re.findall(r'"(?:the [^"]+|[a-z_]+|@\w+|NULL)", "?[@\w]*"?, "([a-z-]+)"\}', rooms))
    used |= set(re.findall(r'(?:PICTURE|TEX_BOX)\([^"]*"([a-z-]+)"', rooms))
    used |= set(re.findall(r'kh_tex_material\((?:room->walled \? )?"([a-z-]+)"', world))
    assert used, "no pictures found"
    for name in used:
        assert (GAME / "data" / "art" / f"{name}.ppm").is_file(), name


def test_parity_evidence_passes_with_its_control():
    evidence = json.loads((GAME / "evidence" / "parity-2026-10-10.json").read_text(encoding="utf-8"))
    assert evidence["pass"] is True
    assert evidence["wrong_room_control"]["all_fail"] is True
    assert evidence["wrong_room_control"]["max"] < evidence["bounds"]["edge_correlation_min"]
    assert len(evidence["rooms"]) == 5 and all(r["pass"] for r in evidence["rooms"].values())
    assert "after seeing" in evidence["bounds"]["calibrated"]
