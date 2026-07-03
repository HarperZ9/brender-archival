from __future__ import annotations

from pathlib import Path

from engine_revival.records import RECORD_DIRS, load_records


RESTRICTED_LABELS = {
    "restricted",
    "unknown",
    "rights-holder-needed",
    "do-not-redistribute",
}
PUBLISHABLE_LEVELS = {"public", "publishable", "downloadable"}
UNSAFE_WORDS = {"upload included", "download the sdk", "leaked source", "private contact"}
ACCESSION_RESTRICTED_REVIEWS = {
    "restricted",
    "unknown",
    "rights-holder-needed",
    "do-not-redistribute",
}


def audit_public_workspace(root: Path) -> list[str]:
    messages: list[str] = []
    if (root / "artifacts").exists():
        for record in load_records(root, "artifact"):
            redistribution = str(record.payload.get("redistribution_status", ""))
            access = str(record.payload.get("access_level", ""))
            text = _record_text(record.payload)
            if redistribution in RESTRICTED_LABELS and access in PUBLISHABLE_LEVELS:
                messages.append(f"{record.path}: restricted material cannot be publishable")
            messages.extend(_unsafe_wording_messages(record.path, text))
    if (root / "accessions").exists():
        for record in load_records(root, "accession"):
            rights_review = str(record.payload.get("rights_review", ""))
            storage_class = str(record.payload.get("storage_class", ""))
            text = _record_text(record.payload)
            if rights_review in ACCESSION_RESTRICTED_REVIEWS and storage_class == "local-public":
                messages.append(f"{record.path}: restricted accession cannot use public storage")
            messages.extend(_unsafe_wording_messages(record.path, text))
    for kind in (
        "build",
        "harness",
        "attempt",
        "readiness",
        "reproduction",
        "task",
        "milestone",
    ):
        if (root / RECORD_DIRS[kind]).exists():
            for record in load_records(root, kind):
                messages.extend(_unsafe_wording_messages(record.path, _record_text(record.payload)))
    return messages


def _record_text(payload: dict[str, object]) -> str:
    return " ".join(str(value).lower() for value in payload.values())


def _unsafe_wording_messages(path: Path, text: str) -> list[str]:
    return [
        f"{path}: unsafe public wording: {word}"
        for word in UNSAFE_WORDS
        if word in text
    ]
