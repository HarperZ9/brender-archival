import json
from pathlib import Path

from engine_revival.audit import audit_public_workspace

ROOT = Path(__file__).resolve().parents[1]


def _write_accession(path, rights_review, storage_class, fixity_status="not-started"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "id": path.stem,
                "artifact_id": "restricted-sdk",
                "package_type": "external-custody",
                "capture_status": "blocked",
                "storage_class": storage_class,
                "fixity_status": fixity_status,
                "rights_review": rights_review,
                "public_notes": "Public-safe accession.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_valid_fixture_passes_public_audit():
    assert audit_public_workspace(ROOT / "tests" / "fixtures" / "valid-mini") == []


def test_restricted_publishable_artifact_fails_public_audit():
    messages = audit_public_workspace(ROOT / "tests" / "fixtures" / "unsafe-records")
    assert any("restricted material cannot be publishable" in message for message in messages)


def test_restricted_accession_with_public_storage_fails_public_audit(tmp_path):
    (tmp_path / "artifacts").mkdir()
    _write_accession(tmp_path / "accessions" / "restricted-public.json", "restricted", "local-public")
    messages = audit_public_workspace(tmp_path)
    assert any("restricted accession cannot use public storage" in message for message in messages)


def test_do_not_redistribute_accession_with_public_storage_fails_public_audit(tmp_path):
    (tmp_path / "artifacts").mkdir()
    _write_accession(
        tmp_path / "accessions" / "do-not-redistribute-public.json",
        "do-not-redistribute",
        "local-public",
    )
    messages = audit_public_workspace(tmp_path)
    assert any("restricted accession cannot use public storage" in message for message in messages)


def test_metadata_only_restricted_accession_not_held_passes_public_audit(tmp_path):
    (tmp_path / "artifacts").mkdir()
    _write_accession(
        tmp_path / "accessions" / "metadata-only.json",
        "restricted",
        "not-held",
        "not-applicable",
    )
    assert audit_public_workspace(tmp_path) == []


def test_harness_with_unsafe_public_wording_fails_public_audit(tmp_path):
    (tmp_path / "harnesses").mkdir()
    (tmp_path / "harnesses" / "unsafe-harness.json").write_text(
        json.dumps(
            {
                "id": "unsafe-harness",
                "public_notes": "download the sdk before building",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    messages = audit_public_workspace(tmp_path)

    assert any("unsafe public wording: download the sdk" in message for message in messages)
