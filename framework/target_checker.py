# framework/target_checker.py
#
# Phase 5: target-aware validation orchestrator.
#
# This module bridges the project manifest layer and the board profile layer.
# Given a ProjectManifest and a board_id, it resolves the board profile,
# runs the board's check_project() method, and returns a BoardReadinessReport.
#
# It also handles board_id resolution (CLI --target flag takes precedence
# over the project.yaml target.board field) and report rendering/saving.
#
# Separation of concerns:
#   framework/target_checker.py  — orchestration, resolution, reporting
#   framework/boards/             — board profiles and check logic
#   framework/project.py          — manifest loading (unchanged simulation path)
#   scripts/run_regression.py     — CLI entry point (calls this module)
#
# Phase 6 note:
#   When a hardware backend is added, this module is the right insertion
#   point: after simulation passes and target checks pass, dispatch to the
#   hardware backend selected via --backend.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from framework.boards.base_board import BoardReadinessReport, BoardCheckResult
from framework.boards.registry   import get_board, list_board_ids, describe_all_boards
from framework.project           import ProjectManifest


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def resolve_board_id(
    manifest: ProjectManifest,
    cli_target: Optional[str] = None,
) -> Optional[str]:
    """
    Determine the board_id to use, with CLI flag taking precedence over
    the project.yaml target block.

    Returns the resolved board_id string, or None if neither source
    provides one.
    """
    if cli_target and cli_target.strip():
        return cli_target.strip()

    if manifest.target and manifest.target.get("board"):
        return manifest.target["board"].strip()

    return None


# ---------------------------------------------------------------------------
# Main check entry point
# ---------------------------------------------------------------------------

def run_target_checks(
    manifest: ProjectManifest,
    cli_target: Optional[str] = None,
) -> BoardReadinessReport:
    """
    Resolve the target board and run all target-aware checks.

    Raises:
        ValueError  if no board_id can be resolved from either source.
        KeyError    if the board_id is not in the registry.
    """
    board_id = resolve_board_id(manifest, cli_target)

    if not board_id:
        valid = ", ".join(list_board_ids())
        raise ValueError(
            f"No target board specified for project '{manifest.name}'.\n"
            f"Use --target <board_id> on the CLI, or add:\n"
            f"  target:\n"
            f"    board: <board_id>\n"
            f"to your project.yaml.\n"
            f"Available boards: {valid}"
        )

    board = get_board(board_id)  # raises KeyError if not found
    return board.check_project(manifest)


# ---------------------------------------------------------------------------
# Console reporter
# ---------------------------------------------------------------------------

_DIV  = "=" * 62
_SDIV = "-" * 62


def print_readiness_report(report: BoardReadinessReport) -> None:
    """Render a BoardReadinessReport to stdout."""
    print(f"\n{_DIV}")
    print(f"  TARGET-AWARE CHECKS")
    print(f"  Project : {report.project_name}")
    print(f"  Board   : {report.board_name}")
    print(f"  Family  : {report.board_family}")
    print(f"  Device  : {report.fpga_device}")
    print(f"{_DIV}")
    print()

    for check in report.checks:
        _print_check(check)

    if report.board_notes:
        print(_SDIV)
        print("  Board notes:")
        for note in report.board_notes:
            print(f"    · {note}")
        print()

    print(_SDIV)
    _print_readiness_summary(report)
    print(_SDIV)
    print()


def _print_check(c: BoardCheckResult) -> None:
    sym = "✓" if c.passed else "✗"
    print(f"  {sym} [{c.level:<5}] {c.check_name}")
    print(f"          {c.message}")
    if c.detail:
        for line in c.detail.strip().splitlines():
            print(f"            {line}")
    if c.suggestion:
        print(f"          -> {c.suggestion}")
    print()


def _print_readiness_summary(report: BoardReadinessReport) -> None:
    total   = len(report.checks)
    passed  = len(report.passed_checks())
    errors  = len(report.errors())
    warns   = len(report.warnings())

    if report.ready:
        verdict = "READY FOR LAB  (no ERROR-level issues found)"
    else:
        verdict = "NOT READY      (fix ERROR-level issues before going to lab)"

    print(f"  {verdict}")
    print(f"  Checks: {total}   Passed: {passed}   "
          f"Errors: {errors}   Warnings: {warns}")


# ---------------------------------------------------------------------------
# Artifact saver
# ---------------------------------------------------------------------------

def save_readiness_report(
    report: BoardReadinessReport,
    artifact_dir: Path,
) -> Path:
    """
    Save the BoardReadinessReport as a JSON file in artifact_dir.
    Returns the path of the written file.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifact_dir / "target_readiness.json"

    data = {
        "board_id":     report.board_id,
        "board_name":   report.board_name,
        "board_family": report.board_family,
        "fpga_device":  report.fpga_device,
        "project_name": report.project_name,
        "ready":        report.ready,
        "board_notes":  report.board_notes,
        "checks": [
            {
                "check_id":   c.check_id,
                "check_name": c.check_name,
                "passed":     c.passed,
                "level":      c.level,
                "message":    c.message,
                "detail":     c.detail,
                "suggestion": c.suggestion,
            }
            for c in report.checks
        ],
        "summary": {
            "total":    len(report.checks),
            "passed":   len(report.passed_checks()),
            "errors":   len(report.errors()),
            "warnings": len(report.warnings()),
            "infos":    len(report.infos()),
        },
    }

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    return out_path
