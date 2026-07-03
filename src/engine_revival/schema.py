from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SchemaSpec:
    kind: str
    required: tuple[str, ...]
    properties: dict[str, str]


def load_schema(root: Path, kind: str) -> SchemaSpec:
    path = root / "schemas" / f"{kind}.schema.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SchemaSpec(
        kind=str(payload["kind"]),
        required=tuple(str(item) for item in payload["required"]),
        properties={str(key): str(value) for key, value in payload["properties"].items()},
    )


def validate_required_fields(record: dict[str, object], schema: SchemaSpec) -> list[str]:
    messages: list[str] = []
    for field in schema.required:
        if field not in record:
            messages.append(f"{schema.kind} missing required field: {field}")
    return messages
