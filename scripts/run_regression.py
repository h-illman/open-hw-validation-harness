#!/usr/bin/env python3
# scripts/run_regression.py
#
# Regression runner for open-hw-validation-harness.
# Runs all registered simulation targets, parses JUnit XML results,
# and prints a clear pass/fail summary.
#
# Usage:
#   python scripts/run_regression.py               # run all targets
#   python scripts/run_regression.py --target p2   # Phase 2 only
#   python scripts/run_regression.py --target p3   # Phase 3 only
#   python scripts/run_regression.py --verbose      # stream simulator output

import argparse
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WAVE_DIR  = REPO_ROOT / "artifacts" / "waves"

# ---------------------------------------------------------------------------
# Registered simulation targets.
# Add new DUTs here as the project grows.
# ---------------------------------------------------------------------------
SIMULATION_TARGETS = {
    "p2": {
        "name":     "Phase 2 — reg8 (8-bit register, Verilator)",
        "makefile": REPO_ROOT / "sim" / "cocotb",
        "results":  REPO_ROOT / "artifacts" / "results_reg8.xml",
    },
    "p3": {
        "name":     "Phase 3 — periph_ctrl (register-mapped peripheral, Verilator)",
        "makefile": REPO_ROOT / "sim" / "periph_ctrl",
        "results":  REPO_ROOT / "artifacts" / "results_periph_ctrl.xml",
    },
}

# ---------------------------------------------------------------------------
# Tool check
# ---------------------------------------------------------------------------
REQUIRED_TOOLS = ["verilator", "make"]

def check_tools(verbose: bool) -> bool:
    all_ok = True
    for tool in REQUIRED_TOOLS:
        path = shutil.which(tool)
        if path:
            if verbose:
                print(f"  [OK]  {tool} -> {path}")
        else:
            print(f"  [MISSING]  '{tool}' not found on PATH")
            all_ok = False

    try:
        import importlib.util
        if importlib.util.find_spec("cocotb") is None:
            raise ImportError
        if verbose:
            print("  [OK]  cocotb (Python package)")
    except ImportError:
        print("  [MISSING]  'cocotb' Python package not installed")
        all_ok = False

    return all_ok

# ---------------------------------------------------------------------------
# Run one simulation target
# ---------------------------------------------------------------------------
def run_target(target: dict, verbose: bool) -> bool:
    print(f"\n{'='*62}")
    print(f"  {target['name']}")
    print(f"{'='*62}")

    result = subprocess.run(
        ["make"],
        cwd=target["makefile"],
        capture_output=(not verbose),
    )

    if result.returncode != 0:
        print(f"[FAIL] make exited with code {result.returncode}")
        if not verbose and result.stderr:
            print(result.stderr.decode(errors="replace")[-2000:])
        return False

    subprocess.run(
        ["make", "copy-waves"],
        cwd=target["makefile"],
        capture_output=(not verbose),
    )
    return True

# ---------------------------------------------------------------------------
# Parse JUnit XML written by cocotb
# ---------------------------------------------------------------------------
def parse_results(xml_path: Path) -> dict:
    if not xml_path.exists():
        return {"passed": 0, "failed": 0,
                "failures": [f"Results file not found: {xml_path}"]}

    tree = ET.parse(xml_path)
    root = tree.getroot()
    passed, failed, failures = 0, 0, []

    for testcase in root.iter("testcase"):
        failure_elem = testcase.find("failure")
        if failure_elem is not None:
            failed += 1
            failures.append(
                f"{testcase.get('name', 'unknown')}: "
                f"{failure_elem.get('message', '')}"
            )
        else:
            passed += 1

    return {"passed": passed, "failed": failed, "failures": failures}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="open-hw-validation-harness regression runner"
    )
    parser.add_argument(
        "--target", "-t",
        choices=list(SIMULATION_TARGETS.keys()) + ["all"],
        default="all",
        help="Which target(s) to run: p2, p3, or all (default: all)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Stream simulator output to stdout",
    )
    args = parser.parse_args()

    print("\n=== open-hw-validation-harness | Regression Runner ===\n")

    print("Checking required tools...")
    if not check_tools(args.verbose):
        print("\n[ABORT] Install missing tools and re-run.")
        sys.exit(1)
    print("All required tools found.\n")

    # Select targets
    if args.target == "all":
        targets = list(SIMULATION_TARGETS.values())
    else:
        targets = [SIMULATION_TARGETS[args.target]]

    total_passed  = 0
    total_failed  = 0
    all_failures  = []
    make_failures = []

    for target in targets:
        make_ok = run_target(target, args.verbose)
        if not make_ok:
            make_failures.append(target["name"])
            continue

        summary = parse_results(target["results"])
        total_passed += summary["passed"]
        total_failed += summary["failed"]
        all_failures += summary["failures"]

        status = "PASS" if summary["failed"] == 0 else "FAIL"
        print(f"\n  Result: [{status}]  "
              f"{summary['passed']} passed, {summary['failed']} failed")
        for f in summary["failures"]:
            print(f"    FAILED: {f}")

    # Final summary
    print(f"\n{'='*62}")
    print("REGRESSION SUMMARY")
    print(f"{'='*62}")
    print(f"  Tests passed : {total_passed}")
    print(f"  Tests failed : {total_failed}")
    if make_failures:
        print(f"  Make errors  : {len(make_failures)}")
        for mf in make_failures:
            print(f"    - {mf}")

    vcd_files = list(WAVE_DIR.glob("*.vcd"))
    if vcd_files:
        print(f"\n  Waveforms: {WAVE_DIR}")
        for vcd in vcd_files:
            print(f"    {vcd.name}")
        print("  View with: gtkwave <file.vcd>")

    overall_ok = (total_failed == 0) and not make_failures
    print(f"\n{'[REGRESSION PASSED]' if overall_ok else '[REGRESSION FAILED]'}\n")
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
