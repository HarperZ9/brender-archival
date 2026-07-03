from engine_revival.audit import audit_public_workspace
from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace
from engine_revival.validate import validate_workspace


def test_seeded_public_archive_contract(tmp_path):
    seed_workspace(tmp_path)
    assert validate_workspace(tmp_path) == []
    assert audit_public_workspace(tmp_path) == []
    reports = write_reports(tmp_path)
    assert tmp_path / "docs" / "generated" / "index.md" in reports
    assert tmp_path / "docs" / "generated" / "sources.md" in reports
    assert tmp_path / "docs" / "generated" / "accessions.md" in reports
    assert tmp_path / "docs" / "generated" / "tasks.md" in reports
    assert tmp_path / "docs" / "generated" / "milestones.md" in reports
    assert tmp_path / "docs" / "generated" / "packets.md" in reports
    assert tmp_path / "docs" / "generated" / "reproductions.md" in reports
    assert tmp_path / "docs" / "generated" / "snapshots.md" in reports
    assert tmp_path / "docs" / "generated" / "database.json" in reports
    assert tmp_path / "docs" / "generated" / "coverage.md" in reports
