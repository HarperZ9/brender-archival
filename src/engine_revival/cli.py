from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="engine-revival",
        description="Validate and publish public-safe engine revival records.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("seed", "validate", "audit-public", "index", "report"):
        command = subparsers.add_parser(name)
        command.add_argument("--root", default=".", help="workspace root")
    materialize = subparsers.add_parser("materialize-brender-harness")
    materialize.add_argument("--source-root", required=True, help="public BRender checkout")
    materialize.add_argument("--output-root", required=True, help="out-of-tree harness output")
    return parser


def _run_seed(root: Path) -> int:
    from engine_revival.seed import seed_workspace

    for path in seed_workspace(root):
        print(path)
    return 0


def _run_validate(root: Path) -> int:
    from engine_revival.validate import validate_workspace

    messages = validate_workspace(root)
    for message in messages:
        print(message)
    return 1 if messages else 0


def _run_audit(root: Path) -> int:
    from engine_revival.audit import audit_public_workspace

    messages = audit_public_workspace(root)
    for message in messages:
        print(message)
    return 1 if messages else 0


def _run_index(root: Path) -> int:
    from engine_revival.indexer import build_target_index, render_target_table

    print(render_target_table(build_target_index(root)), end="")
    return 0


def _run_report(root: Path) -> int:
    from engine_revival.report import write_reports

    for path in write_reports(root):
        print(path)
    return 0


def _run_materialize_brender_harness(source_root: Path, output_root: Path) -> int:
    from engine_revival.brender_harness import (
        HarnessMaterializationError,
        materialize_brender_core_harness,
    )

    try:
        written = materialize_brender_core_harness(source_root, output_root)
    except HarnessMaterializationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for path in written:
        print(path)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if args.command == "validate":
        return _run_validate(Path(args.root))
    if args.command == "seed":
        return _run_seed(Path(args.root))
    if args.command == "audit-public":
        return _run_audit(Path(args.root))
    if args.command == "index":
        return _run_index(Path(args.root))
    if args.command == "report":
        return _run_report(Path(args.root))
    if args.command == "materialize-brender-harness":
        return _run_materialize_brender_harness(
            Path(args.source_root),
            Path(args.output_root),
        )
    return 0
