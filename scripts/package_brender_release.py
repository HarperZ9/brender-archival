"""Package a distributable BRender revival-release staging directory.

Stages the materialized harness, README, captured CTest transcripts, current
release media, and provenance into one directory, then writes a canonical
SHA256SUMS file and a packaging receipt. No proprietary source or assets are
copied: the staged harness references the public checkout by path only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGED_NAME = "brender-revival-release"
STAGED_FILES = (
    ("harness", None),
    ("README.md", "README.md"),
    ("builds/brender-v132-ctest-nineteen-rungs.log", "evidence/ctest-nineteen-rungs.log"),
    ("builds/brender-v132-ctest-twenty-rungs.log", "evidence/ctest-twenty-rungs.log"),
    ("builds/brender-v132-ctest-twentyone-targets.log", "evidence/ctest-twentyone-targets.log"),
    ("gallery/release-20260827/period-pipeline-orbit-00.png", "media/period-pipeline-orbit-00.png"),
    ("gallery/release-20260827/period-pipeline-orbit-01.png", "media/period-pipeline-orbit-01.png"),
    ("gallery/release-20260827/period-pipeline-orbit-02.png", "media/period-pipeline-orbit-02.png"),
    ("gallery/release-20260827/period-pipeline-orbit-03.png", "media/period-pipeline-orbit-03.png"),
    ("gallery/release-20260827/period-pipeline-orbit-04.png", "media/period-pipeline-orbit-04.png"),
    ("gallery/release-20260827/period-pipeline-orbit-05.png", "media/period-pipeline-orbit-05.png"),
    ("gallery/release-20260827/period-pipeline-orbit-06.png", "media/period-pipeline-orbit-06.png"),
    ("gallery/release-20260827/period-pipeline-orbit-07.png", "media/period-pipeline-orbit-07.png"),
    ("gallery/release-20260827/period-pipeline-still.png", "media/period-pipeline-still.png"),
    (
        "gallery/release-20260827/period-pipeline-orbit-contact-sheet.png",
        "media/period-pipeline-orbit-contact-sheet.png",
    ),
    ("gallery/release-20260827/period-pipeline-poster.png", "media/period-pipeline-poster.png"),
    ("gallery/release-20260827/progress-sequence.png", "media/progress-sequence.png"),
    ("gallery/release-20260827/pipeline-diagram.png", "media/pipeline-diagram.png"),
    ("gallery/release-20260827/evidence-card.png", "media/evidence-card.png"),
    ("gallery/release-20260827/social-card-1200x630.png", "media/social-card-1200x630.png"),
    ("gallery/release-20260827/provenance-manifest.json", "media/provenance-manifest.json"),
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def package_release(source_root: Path, output_root: Path) -> list[Path]:
    from engine_revival.brender_harness import materialize_brender_core_harness

    output = output_root / STAGED_NAME
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    written = [output / "harness"]
    materialize_brender_core_harness(source_root, output / "harness")

    for repo_relative, staged_relative in STAGED_FILES[1:]:
        src = ROOT / repo_relative
        dst = output / staged_relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        written.append(dst)

    digests = {}
    for path in sorted(output.rglob("*")):
        if path.is_file():
            key = path.relative_to(output).as_posix()
            digests[key] = _sha256(path.read_bytes())

    sums = output / "SHA256SUMS.txt"
    sums.write_text(
        "".join(f"{digest}  {key}\n" for key, digest in sorted(digests.items())),
        encoding="utf-8",
    )
    written.append(sums)

    receipt = {
        "schema": "brender-archival.release-package/v1",
        "packaged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "staged_files": sorted(digests),
        "sha256": digests,
    }
    receipt_path = output / "package-receipt.json"
    receipt_path.write_bytes(
        json.dumps(receipt, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8") + b"\n"
    )
    written.append(receipt_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True,
                        help="Public BRender v1.3.2 checkout (pinned at d88d0ed4).")
    parser.add_argument("--output-root", type=Path, required=True,
                        help="Directory to stage the release package under.")
    args = parser.parse_args()
    written = package_release(args.source_root, args.output_root)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
