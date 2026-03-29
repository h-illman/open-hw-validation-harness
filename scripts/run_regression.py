#!/usr/bin/env python3
# scripts/run_regression.py
#
# open-hw-validation-harness — main regression runner.
#
# This script is the primary user-facing entry point for running validation.
# It auto-discovers all projects under projects/ by reading their project.yaml
# manifests, runs each simulation, parses results, and prints a summary.
#
# Phase 5 adds target-aware board readiness checks alongside simulation.
#
# Usage:
#   python scripts/run_regression.py                               # run all projects
#   python scripts/run_regression.py --project reg8                # run one project
#   python scripts/run_regression.py --list                        # list projects
#   python scripts/run_regression.py --verbose                     # stream output
#
#   # Phase 5 — target-aware validation:
#   python scripts/run_regression.py --target de10_standard
#   python scripts/run_regression.py --project periph_ctrl --target de10_standard
#   python scripts/run_regression.py --target-only --project reg8 --target de0_cv
#
#   # Phase 5 — board info:
#   python scripts/run_regression.py --list-boards
#   python scripts/run_regression.py --board-info de10_standard
#
# Adding your own project:
#   1. Copy projects/template/ to projects/your_project/
#   2. Add your RTL and tests
#   3. Fill in project.yaml  (add a target: block for Phase 5 checks)
#   4. This runner will discover and run it automatically

import argparse
import subprocess
import sys
from pathlib import Path

# Add repo root to path so 'framework' package is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from framework.project       import discover_projects, ProjectManifest
from framework.result_parser import parse_results, SimResults
from framework.tool_check    import all_tools_available

# Phase 5 imports
from framework.boards.registry import list_board_ids, describe_all_boards, get_board
from framework.target_checker  import (
    run_target_checks,
    print_readiness_report,
    save_readiness_report,
    resolve_board_id,
)


# ---------------------------------------------------------------------------
# Simulation helpers (unchanged from Phase 4)
# ---------------------------------------------------------------------------

def run_project(manifest: ProjectManifest, verbose: bool) -> bool:
    """
    Invoke make in the project's sim/ directory.
    Returns True if make exited cleanly.
    """
    result = subprocess.run(
        ["make"],
        cwd=manifest.sim_dir,
        capture_output=(not verbose),
    )

    if result.returncode != 0:
        print(f"  [FAIL] make exited with code {result.returncode}")
        if not verbose and result.stderr:
            print(result.stderr.decode(errors="replace")[-2000:])
        return False

    subprocess.run(
        ["make", "copy-waves"],
        cwd=manifest.sim_dir,
        capture_output=(not verbose),
    )
    return True


def print_project_result(results: SimResults, manifest: ProjectManifest):
    status = "PASS" if results.all_passed else "FAIL"
    print(f"\n  [{status}]  {manifest.name}  "
          f"({results.passed}/{results.total} tests passed)")

    if results.error:
        print(f"    ERROR: {results.error}")

    for f in results.failures:
        print(f"    FAILED: {f.name}")
        if f.message:
            first_line = f.message.split("\n")[0]
            print(f"      {first_line}")


def print_summary(all_results: list, make_failures: list, wave_dir: Path):
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_tests  = total_passed + total_failed

    print(f"\n{'='*62}")
    print("REGRESSION SUMMARY")
    print(f"{'='*62}")
    print(f"  Projects run   : {len(all_results) + len(make_failures)}")
    print(f"  Tests passed   : {total_passed}/{total_tests}")
    print(f"  Tests failed   : {total_failed}")

    if make_failures:
        print(f"  Build failures : {len(make_failures)}")
        for name in make_failures:
            print(f"    - {name}")

    vcd_files = list(wave_dir.glob("*.vcd"))
    if vcd_files:
        print(f"\n  Waveforms ({len(vcd_files)} file(s)): {wave_dir}")
        print("  View with: gtkwave <file.vcd>")

    overall_ok = total_failed == 0 and not make_failures
    verdict = "[REGRESSION PASSED]" if overall_ok else "[REGRESSION FAILED]"
    print(f"\n{verdict}\n")
    return overall_ok


# ---------------------------------------------------------------------------
# Phase 5 — board info commands
# ---------------------------------------------------------------------------

def cmd_list_boards() -> None:
    print()
    print(describe_all_boards())


def cmd_board_info(board_id: str) -> None:
    try:
        b = get_board(board_id)
    except KeyError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    print(f"\n{'='*62}")
    print(f"  {b.board_name()}")
    print(f"{'='*62}")
    print(f"  ID        : {b.board_id()}")
    print(f"  Family    : {b.board_family()}")
    print(f"  Device    : {b.fpga_device()}")
    print(f"  Vendor    : {b.vendor()}")
    print(f"  Toolchain : {b.toolchain_hint()}")

    clocks = b.clock_sources()
    if clocks:
        print(f"\n  Clock Sources:")
        for c in clocks:
            pin  = c.get("pin", "N/A")
            note = f"  ({c['note']})" if c.get("note") else ""
            print(f"    {c['name']:<15} {c['freq_mhz']} MHz   pin: {pin}{note}")

    io_stds = b.io_standards()
    if io_stds:
        print(f"\n  Supported I/O Standards:")
        for s in io_stds:
            print(f"    {s}")

    budget = b.resource_budget()
    if budget:
        print(f"\n  Resource Budget (approximate):")
        for k, v in budget.items():
            print(f"    {k:<12} {v:,}")

    # Extended peripheral summary (DE25-Standard and future boards)
    if hasattr(b, "peripheral_summary"):
        periph = b.peripheral_summary()
        print(f"\n  Peripheral Summary:")
        for section, items in periph.items():
            print(f"    [{section.upper().replace('_', ' ')}]")
            for k, v in items.items():
                label = k.replace("_", " ").title()
                print(f"      {label:<26} {v}")

    notes = b.board_notes()
    if notes:
        print(f"\n  Notes:")
        for n in notes:
            print(f"    · {n}")
    print()


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    valid_boards = ", ".join(list_board_ids())

    p = argparse.ArgumentParser(
        description="open-hw-validation-harness — validation runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""\
Examples:
  python scripts/run_regression.py                            run all projects
  python scripts/run_regression.py --project reg8             run one project
  python scripts/run_regression.py --list                     list projects
  python scripts/run_regression.py -v                         verbose output

  # Phase 5 — target-aware checks:
  python scripts/run_regression.py --target de10_standard
  python scripts/run_regression.py --project periph_ctrl --target de10_standard
  python scripts/run_regression.py --target-only --project reg8 --target de0_cv

  # Phase 5 — board info:
  python scripts/run_regression.py --list-boards
  python scripts/run_regression.py --board-info de10_standard

Available board IDs: {valid_boards}
        """,
    )

    # Existing flags
    p.add_argument(
        "--project", "-p",
        help="Run a specific project by name (default: run all)",
    )
    p.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all discovered projects and exit",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Stream simulator output to stdout instead of suppressing it",
    )

    # Phase 5 flags
    p.add_argument(
        "--target", "-t",
        metavar="BOARD_ID",
        help=(
            "Run target-aware checks against this board for all selected projects. "
            "Overrides 'target.board' in project.yaml.  "
            f"Available: {valid_boards}"
        ),
    )
    p.add_argument(
        "--target-only",
        action="store_true",
        default=False,
        help=(
            "Run only target-aware checks — skip simulation entirely. "
            "Requires --target or a target: block in each project.yaml."
        ),
    )
    p.add_argument(
        "--list-boards",
        action="store_true",
        default=False,
        help="List all supported board/target IDs and exit.",
    )
    p.add_argument(
        "--board-info",
        metavar="BOARD_ID",
        help="Show detailed metadata for a board and exit.",
    )

    return p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args   = parser.parse_args()

    # ---- Info-only commands (no project needed) -------------------------
    if args.list_boards:
        cmd_list_boards()
        sys.exit(0)

    if args.board_info:
        cmd_board_info(args.board_info)
        sys.exit(0)

    # ---- Header ---------------------------------------------------------
    print("\n=== open-hw-validation-harness | Validation Runner ===\n")

    # ---- Tool check (skip for target-only) ------------------------------
    if not args.target_only:
        print("Checking required tools...")
        if not all_tools_available(verbose=args.verbose):
            print("\n[ABORT] Install missing tools and re-run.")
            sys.exit(1)
        print("All required tools found.\n")

    # ---- Project discovery ----------------------------------------------
    all_projects = discover_projects(REPO_ROOT)

    if not all_projects:
        print("No projects found under projects/. "
              "Copy projects/template/ to get started.")
        sys.exit(0)

    # --list mode
    if args.list:
        print(f"Discovered {len(all_projects)} project(s):\n")
        for m in all_projects:
            target_hint = ""
            if m.target and m.target.get("board"):
                target_hint = f"  [target: {m.target['board']}]"
            print(f"  {m.name:<20} Phase {m.phase}  --  {m.description}{target_hint}")
        print()
        sys.exit(0)

    # Filter to a single project if requested
    if args.project:
        matched = [m for m in all_projects if m.name == args.project]
        if not matched:
            available = ", ".join(m.name for m in all_projects)
            print(f"[ERROR] Project '{args.project}' not found.")
            print(f"  Available: {available}")
            sys.exit(1)
        projects_to_run = matched
    else:
        projects_to_run = all_projects

    print(f"Running {len(projects_to_run)} project(s)...\n")

    # ---- Per-project loop -----------------------------------------------
    all_sim_results  = []
    make_failures    = []
    target_not_ready = []
    overall_exit     = 0

    for manifest in projects_to_run:
        print(f"{'='*62}")
        print(f"  {manifest.name}  (Phase {manifest.phase})")
        print(f"  {manifest.description}")
        print(f"{'='*62}")

        # ---- Simulation (skipped with --target-only) --------------------
        if not args.target_only:
            make_ok = run_project(manifest, args.verbose)

            if not make_ok:
                make_failures.append(manifest.name)
                overall_exit = 1
                continue

            xml_path = REPO_ROOT / manifest.results_xml
            results  = parse_results(manifest.name, xml_path)
            all_sim_results.append(results)
            print_project_result(results, manifest)

            if not results.all_passed:
                overall_exit = 1

        # ---- Target-aware checks (Phase 5) ------------------------------
        board_id = resolve_board_id(manifest, args.target)

        if board_id:
            try:
                report = run_target_checks(manifest, cli_target=args.target)
            except KeyError as e:
                print(f"\n  [ERROR] Target check failed: {e}")
                overall_exit = 1
                continue

            print_readiness_report(report)

            artifact_dir = REPO_ROOT / "artifacts" / "reports" / manifest.name
            saved_path   = save_readiness_report(report, artifact_dir)
            print(f"  Target report saved: {saved_path.relative_to(REPO_ROOT)}\n")

            if not report.ready:
                target_not_ready.append(manifest.name)
                overall_exit = 1

        elif args.target_only:
            print(
                f"\n  [WARN] --target-only requested but no board resolved "
                f"for '{manifest.name}'.\n"
                f"         Add 'target: {{board: <id>}}' to project.yaml "
                f"or pass --target <board_id>.\n"
            )

    # ---- Final summary --------------------------------------------------
    if not args.target_only:
        wave_dir = REPO_ROOT / "artifacts" / "waves"
        sim_ok   = print_summary(all_sim_results, make_failures, wave_dir)
        if not sim_ok:
            overall_exit = 1

    if target_not_ready:
        print(f"Target readiness failures ({len(target_not_ready)} project(s)):")
        for name in target_not_ready:
            print(f"  - {name}")
        print()

    sys.exit(overall_exit)


if __name__ == "__main__":
    main()
