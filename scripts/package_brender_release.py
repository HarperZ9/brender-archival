"""Package a distributable BRender revival-release staging directory.

Stages the materialized harness, README, captured CTest transcripts, and the
harness manifest into one directory, then writes a canonical SHA256SUMS file
and a packaging receipt. No proprietary source or assets are copied: the
staged harness references the public checkout by path only.
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
