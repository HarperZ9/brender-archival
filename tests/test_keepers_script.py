"""The Keeper's Hour night script: links resolve, every node is reachable, and
the words follow the house style."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "games" / "keepers-hour" / "data" / "night.txt"
WORLD = ROOT / "games" / "keepers-hour" / "src" / "kh_world.c"
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


def _starts():
    starts = set(re.findall(r'add_talker\(w, "[^"]+", "(\w+)"', WORLD.read_text(encoding="utf-8")))
    return starts | {"arrive"}


def test_every_link_leads_to_a_node_or_end():
    nodes = _nodes()
    for node, choices in nodes.items():
        for voice, targets in choices:
            for target in targets:
                assert target == "END" or target in nodes, f"{node} -> {target}"
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
