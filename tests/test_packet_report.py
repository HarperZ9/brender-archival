from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def test_packet_page_resolves_evidence_source_details(tmp_path):
    seed_workspace(tmp_path)
    packet_task = tmp_path / "tasks" / "brender-critical-edition-packet.json"
    packet_task.write_text(
        """{
  "id": "brender-critical-edition-packet",
  "target_id": "brender",
  "task_type": "build-archive-packet",
  "status": "planned",
  "public_notes": "Build the BRender critical-edition packet.",
  "inputs": ["public source branches", "BRender accessions"],
  "outputs": ["standalone archival packet", "version graph"],
  "blocked_by": ["brender-triage"],
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
    page = tmp_path / "docs" / "generated" / "packets" / "brender-critical-edition-packet.md"
    assert page in write_reports(tmp_path)
    text = page.read_text(encoding="utf-8")
    assert "| Source | Type | Confidence | Scope | URL |" in text
    assert (
        "| Initial engine revival research reports | local-research-summary | "
        "moderate | initial target selection |  |"
    ) in text
