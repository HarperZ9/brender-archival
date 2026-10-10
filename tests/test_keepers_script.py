"""The Keeper's Hour night script: links resolve, every node is reachable, and
the words follow the house style."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "games" / "keepers-hour" / "data" / "night.txt"
ROOMS = ROOT / "games" / "keepers-hour" / "src" / "kh_rooms.c"
VOICES = {"LENS", "LEDGER", "TIDE", "STATIC"}


def _nodes():
    nodes, current = {}, None
    for line in SCRIPT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("=="):
            current = line[2:].strip()
            nodes[current] = []
        elif line.startswith("*"):
            check = re.match(r"\*\s*\[(\w+) (\d+)\]", line)
            targets = [t.strip() for t in line.split("->", 1)[1].split("|")]
            nodes[current].append((check.group(1) if check else None, targets))
    return nodes


def _rooms():
    text = ROOMS.read_text(encoding="utf-8")
    return re.findall(r'ROOM\("(\w+)"', text)


def _talkers():
    """(room, talker name, node) for every talker in the room table."""
    text = ROOMS.read_text(encoding="utf-8")
    found, room = [], None
    tables = dict(re.findall(r'ROOM\("(\w+)", "[^"]*", \d, [\d.f]+, [\d.f]+, (\w+)', text))
    for table in re.split(r"static const kh_prop ", text)[1:]:
        name = table.split("[", 1)[0]
        room = next(r for r, t in tables.items() if t == name)
        for who, node in re.findall(r'"(the [^"]+)", "([@\w]+)"', table):
            found.append((room, who, node))
    return found


def _starts():
    return {node for _, _, node in _talkers() if not node.startswith("@")} | {"arrive"}


def test_every_link_leads_to_a_node_or_end():
    nodes = _nodes()
    for node, choices in nodes.items():
        for voice, targets in choices:
            for target in targets:
                ok = target == "END" or target in nodes or (target.startswith("@") and target[1:] in _rooms())
                assert ok, f"{node} -> {target}"
            if voice is not None:
                assert voice in VOICES, voice
                assert len(targets) == 2, f"{node}: a checked choice needs a success and a failure"


def test_every_node_is_reachable_from_a_talker():
    nodes, seen = _nodes(), set()
    stack = list(_starts())
    assert set(stack) <= set(nodes), set(stack) - set(nodes)
    while stack:
        node = stack.pop()
        if node in seen or node == "END":
            continue
        seen.add(node)
        stack.extend(t for _, targets in nodes[node] for t in targets)
    assert seen == set(nodes), set(nodes) - seen


def test_every_node_ends_somewhere():
    for node, choices in _nodes().items():
        assert choices, f"{node} has no way out"


def test_words_have_no_long_dashes():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "\u2014" not in text and "\u2013" not in text


def test_every_room_is_reachable_from_the_lamp_room_and_back():
    rooms = _rooms()
    assert set(rooms) == {"lamp", "stairs", "radio", "keeper", "gallery"}
    doors = {}
    for room, _, node in _talkers():
        if node.startswith("@"):
            assert node[1:] in rooms, node
            doors.setdefault(room, set()).add(node[1:])
    seen, stack = set(), ["lamp"]
    while stack:
        room = stack.pop()
        if room not in seen:
            seen.add(room)
            stack.extend(doors.get(room, ()))
    assert seen == set(rooms), set(rooms) - seen
    for room, targets in doors.items():
        for target in targets:
            assert room in doors.get(target, set()), f"no way back from {target} to {room}"


def test_every_talker_starts_a_node_that_exists():
    nodes = _nodes()
    talkers = [t for t in _talkers() if not t[2].startswith("@")]
    assert len(talkers) >= 15
    for room, who, node in talkers:
        assert node in nodes, f"{room}: {who} -> {node}"
