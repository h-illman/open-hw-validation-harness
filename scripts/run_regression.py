#!/usr/bin/env python3
# scripts/run_regression.py
#
# open-hw-validation-harness — main regression runner.
#
# This script is the primary user-facing entry point for running validation.
# It auto-discovers all projects under projects/ by reading their project.yaml
# manifests, runs each simulation, parses results, and prints a summary.
#
# Usage:
#   python scripts/run_regression.py                  # run all projects
#   python scripts/run_regression.py --project reg8   # run one project
#   python scripts/run_regression.py --list           # list discovered projects
#   python scripts/run_regression.py --verbose        # stream simulator output
#
# Adding your own project:
#   1. Copy projects/template/ to projects/your_project/
#   2. Add your RTL and tests
#   3. Fill in project.yaml
#   4. This runner will discover and run it automatically

import argparse
import subprocess
import sys
from pathlib import Path

# Add repo root to path so 'framework' package is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from framework.project      import discover_projects, ProjectManifest
from framework.result_parser import parse_results, SimResults
from framework.tool_check   import all_tools_available


# ---------------------------------------------------------------------------
# Run one project's simulation via its Makefile
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
            # Show the last 2000 chars of stderr so the user can diagnose
            print(result.stderr.decode(errors="replace")[-2000:])
        return False

    # Copy waveform to artifacts/waves/
    subprocess.run(
        ["make", "copy-waves"],
        cwd=manifest.sim_dir,
        capture_output=(not verbose),
    )
    return True


# ---------------------------------------------------------------------------
# Print results for one project
# ---------------------------------------------------------------------------
def print_project_result(results: SimResults, manifest: ProjectManifest):
    status = "PASS" if results.all_passed else "FAIL"
    print(f"\n  [{status}]  {manifest.name}  "
          f"({results.passed}/{results.total} tests passed)")

    if results.error:
        print(f"    ERROR: {results.error}")

    for f in results.failures:
        print(f"    FAILED: {f.name}")
        if f.message:
            # Print the first line of the message only (keeps output clean)
            first_line = f.message.split("\n")[0]
            print(f"      {first_line}")


# ---------------------------------------------------------------------------
# Print final summary
# ---------------------------------------------------------------------------
def print_summary(all_results: list[SimResults], make_failures: list[str],
                  wave_dir: Path):
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

    # Report waveform location
    vcd_files = list(wave_dir.glob("*.vcd"))
    if vcd_files:
        print(f"\n  Waveforms ({len(vcd_files)} file(s)): {wave_dir}")
        print("  View with: gtkwave <file.vcd>")

    overall_ok = total_failed == 0 and not make_failures
    verdict = "[REGRESSION PASSED]" if overall_ok else "[REGRESSION FAILED]"
    print(f"\n{verdict}\n")
    return overall_ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="open-hw-validation-harness — validation runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_regression.py                  # run all projects
  python scripts/run_regression.py --project reg8   # run one project
  python scripts/run_regression.py --list           # list available projects
  python scripts/run_regression.py -v               # verbose output
        """,
    )
    parser.add_argument(
        "--project", "-p",
        help="Run a specific project by name (default: run all)",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all discovered projects and exit",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Stream simulator output to stdout instead of suppressing it",
    )
    args = parser.parse_args()

    print("\n=== open-hw-validation-harness | Validation Runner ===\n")

    # Tool check
    print("Checking required tools...")
    if not all_tools_available(verbose=args.verbose):
        print("\n[ABORT] Install missing tools and re-run.")
        sys.exit(1)
    print("All required tools found.\n")

    # Discover projects
    all_projects = discover_projects(REPO_ROOT)

    if not all_projects:
        print("No projects found under projects/. "
              "Copy projects/template/ to get started.")
        sys.exit(0)

    # --list mode: just print what was found
    if args.list:
        print(f"Discovered {len(all_projects)} project(s):\n")
        for m in all_projects:
            print(f"  {m.name:<20} Phase {m.phase}  —  {m.description}")
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

    # Run each project
    all_results   = []
    make_failures = []

    for manifest in projects_to_run:
        print(f"{'='*62}")
        print(f"  {manifest.name}  (Phase {manifest.phase})")
        print(f"  {manifest.description}")
        print(f"{'='*62}")

        make_ok = run_project(manifest, args.verbose)

        if not make_ok:
            make_failures.append(manifest.name)
            continue

        # Parse JUnit XML results
        xml_path = REPO_ROOT / manifest.results_xml
        results  = parse_results(manifest.name, xml_path)
        all_results.append(results)
        print_project_result(results, manifest)

    # Final summary
    wave_dir = REPO_ROOT / "artifacts" / "waves"
    overall_ok = print_summary(all_results, make_failures, wave_dir)
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
