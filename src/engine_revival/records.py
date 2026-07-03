from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecordFile:
    kind: str
    path: Path
    payload: dict[str, object]


RECORD_DIRS = {
    "target": "targets",
    "artifact": "artifacts",
    "source": "sources",
    "task": "tasks",
    "milestone": "milestones",
    "accession": "accessions",
    "reproduction": "reproductions",
    "snapshot": "snapshots",
    "readiness": "readiness",
    "build": "builds",
    "harness": "harnesses",
    "attempt": "attempts",
}


def load_records(root: Path, kind: str) -> list[RecordFile]:
    directory = root / RECORD_DIRS[kind]
    records: list[RecordFile] = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        records.append(RecordFile(kind=kind, path=path, payload=payload))
    return records
