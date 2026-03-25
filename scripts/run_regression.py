#!/usr/bin/env python3
# scripts/run_regression.py
#
# Phase 2 regression runner for open-hw-validation-harness.
#
# What this script does:
#   1. Checks that required tools (verilator, cocotb) are available.
#   2. Runs the cocotb simulation for rtl/example_dut/reg8.v via its Makefile.
#   3. Parses the JUnit XML results file that cocotb produces.
#   4. Prints a human-readable pass/fail summary.
#   5. Tells you where the waveform file landed.
#   6. Exits with code 0 on full pass, 1 on any failure.
#
# Usage:
#   python scripts/run_regression.py
#   python scripts/run_regression.py --verbose
#
# Phase 3 note:
#   When additional DUTs or backends are added, register their Makefiles
#   in SIMULATION_TARGETS below.  The run loop and result parsing stay the same.

import argparse
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------------------
# Repository layout (everything relative to this file's parent directory)
# ---------------------------------------------------------------------------
REPO_ROOT  = Path(__file__).resolve().parent.parent
WAVE_DIR   = REPO_ROOT / "artifacts" / "waves"
RESULTS_DIR = REPO_ROOT / "artifacts"

# ---------------------------------------------------------------------------
# Simulation targets for Phase 2.
# Each entry is a dict with:
#   name     - human-readable label
#   makefile - directory containing the Makefile to invoke
#   results  - path to the JUnit XML file that cocotb writes
# ---------------------------------------------------------------------------
SIMULATION_TARGETS = [
    {
        "name":     "reg8 (8-bit register, Verilator)",
        "makefile": REPO_ROOT / "sim" / "cocotb",
        "results":  REPO_ROOT / "artifacts" / "results_reg8.xml",
    },
]


# ---------------------------------------------------------------------------
# Tool availability check
# ---------------------------------------------------------------------------
REQUIRED_TOOLS = ["verilator", "make"]

def check_tools(verbose: bool) -> bool:
    """Return True if all required tools are on PATH."""
    all_ok = True
    for tool in REQUIRED_TOOLS:
        path = shutil.which(tool)
        if path:
            if verbose:
                print(f"  [OK]  {tool} -> {path}")
        else:
            print(f"  [MISSING]  '{tool}' not found on PATH")
            all_ok = False

    # cocotb is a Python package; check with importlib
    try:
        import importlib.util
        spec = importlib.util.find_spec("cocotb")
        if spec is None:
            raise ImportError
        if verbose:
            print(f"  [OK]  cocotb (Python package)")
    except ImportError:
        print("  [MISSING]  'cocotb' Python package not installed")
        all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Run a single simulation target
# ---------------------------------------------------------------------------
def run_target(target: dict, verbose: bool) -> bool:
    """
    Invoke 'make' in the target's directory, then 'make copy-waves'.
    Returns True if make exited 0.
    """
    name     = target["name"]
    make_dir = target["makefile"]

    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print(f"{'='*60}")

    # Run the simulation
    result = subprocess.run(
        ["make"],
        cwd=make_dir,
        capture_output=(not verbose),
    )

    if result.returncode != 0:
        print(f"[FAIL] Simulation make failed (exit {result.returncode})")
        if not verbose and result.stderr:
            print(result.stderr.decode(errors="replace")[-2000:])  # tail of stderr
        return False

    # Copy waveforms to artifacts/waves/
    subprocess.run(
        ["make", "copy-waves"],
        cwd=make_dir,
        capture_output=(not verbose),
    )
    return True


# ---------------------------------------------------------------------------
# Parse cocotb JUnit XML results
# ---------------------------------------------------------------------------
def parse_results(xml_path: Path) -> dict:
    """
    cocotb writes a JUnit-compatible XML file.
    Returns a dict: { "passed": int, "failed": int, "failures": [str] }
    """
    if not xml_path.exists():
        return {"passed": 0, "failed": 0, "failures": [f"Results file not found: {xml_path}"]}

    tree = ET.parse(xml_path)
    root = tree.getroot()

    passed   = 0
    failed   = 0
    failures = []

    # JUnit XML: <testsuite> contains <testcase> elements;
    # failures have a <failure> child.
    for testcase in root.iter("testcase"):
        failure_elem = testcase.find("failure")
        if failure_elem is not None:
            failed += 1
            test_name = testcase.get("name", "unknown")
            message   = failure_elem.get("message", "")
            failures.append(f"{test_name}: {message}")
        else:
            passed += 1

    return {"passed": passed, "failed": failed, "failures": failures}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Phase 2 regression runner — open-hw-validation-harness"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Stream simulator output to stdout instead of suppressing it",
    )
    args = parser.parse_args()

    print("\n=== open-hw-validation-harness | Phase 2 Regression Runner ===\n")

    # 1. Tool check
    print("Checking required tools...")
    if not check_tools(args.verbose):
        print("\n[ABORT] Install missing tools and re-run.")
        sys.exit(1)
    print("All required tools found.\n")

    # 2. Run each simulation target
    total_passed  = 0
    total_failed  = 0
    all_failures  = []
    make_failures = []

    for target in SIMULATION_TARGETS:
        make_ok = run_target(target, args.verbose)

        if not make_ok:
            make_failures.append(target["name"])
            continue

        # 3. Parse results
        summary = parse_results(target["results"])
        total_passed += summary["passed"]
        total_failed += summary["failed"]
        all_failures += summary["failures"]

        # Per-target summary
        status = "PASS" if summary["failed"] == 0 else "FAIL"
        print(f"\nResult: [{status}]  "
              f"{summary['passed']} passed, {summary['failed']} failed")

        for f in summary["failures"]:
            print(f"  FAILED: {f}")

    # 4. Final summary
    print(f"\n{'='*60}")
    print("REGRESSION SUMMARY")
    print(f"{'='*60}")
    print(f"  Tests passed : {total_passed}")
    print(f"  Tests failed : {total_failed}")
    if make_failures:
        print(f"  Make errors  : {len(make_failures)}")
        for mf in make_failures:
            print(f"    - {mf}")

    # 5. Waveform location
    vcd_files = list(WAVE_DIR.glob("*.vcd"))
    if vcd_files:
        print(f"\nWaveforms in: {WAVE_DIR}")
        for vcd in vcd_files:
            print(f"    {vcd.name}")
        print("  Open with: gtkwave <file.vcd>")
    else:
        print(f"\nNo waveforms found in {WAVE_DIR} (run simulation first).")

    # 6. Exit code
    overall_ok = (total_failed == 0) and (not make_failures)
    if overall_ok:
        print("\n[REGRESSION PASSED]\n")
        sys.exit(0)
    else:
        print("\n[REGRESSION FAILED]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
