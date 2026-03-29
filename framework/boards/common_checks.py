# framework/boards/common_checks.py
#
# Reusable target-aware check functions shared across board profiles.
#
# Each function takes a ProjectManifest and board-specific parameters,
# and returns a BoardCheckResult.  Board profiles call these from their
# check_project() implementation so check logic isn't duplicated per board.
#
# Manifest fields used by these checks come from the optional `target:` block
# in project.yaml.  All checks degrade gracefully if the block is absent.

from __future__ import annotations
import os
from typing import List
from framework.boards.base_board import BoardCheckResult


# ---------------------------------------------------------------------------
# Target block presence
# ---------------------------------------------------------------------------

def check_target_block_present(manifest) -> BoardCheckResult:
    """
    Verify the project has a non-empty target block with a board declared.
    Absence is a WARN — not an ERROR — since simulation still works.
    """
    tb = manifest.target or {}

    if not tb:
        return BoardCheckResult(
            check_id="target_block_present",
            check_name="Target Block Present",
            passed=False,
            level="WARN",
            message="No 'target:' block found in project.yaml.",
            suggestion=(
                "Add a 'target:' block to project.yaml to unlock full "
                "target-aware validation. See docs/phase5_target_aware.md."
            ),
        )

    board = tb.get("board", None)
    if not board:
        return BoardCheckResult(
            check_id="target_block_present",
            check_name="Target Block Present",
            passed=False,
            level="WARN",
            message="'target:' block present but 'board' key is missing.",
            suggestion="Add 'board: <board_id>' inside the target: block.",
        )

    return BoardCheckResult(
        check_id="target_block_present",
        check_name="Target Block Present",
        passed=True,
        level="INFO",
        message=f"Target block present — board declared as '{board}'.",
    )


# ---------------------------------------------------------------------------
# RTL source file existence
# ---------------------------------------------------------------------------

def check_sources_exist(manifest) -> BoardCheckResult:
    """
    Check that all sources listed in project.yaml actually exist on disk.
    Paths are relative to the project's project_dir.
    """
    project_dir = manifest.project_dir
    sources     = manifest.sources or []
    missing     = []

    for src in sources:
        full_path = project_dir / src
        if not full_path.is_file():
            missing.append(str(full_path))

    if missing:
        return BoardCheckResult(
            check_id="sources_exist",
            check_name="RTL Sources Exist",
            passed=False,
            level="ERROR",
            message=f"{len(missing)} source file(s) declared in project.yaml not found on disk.",
            detail="\n".join(f"  {p}" for p in missing),
            suggestion=(
                "Check that paths under 'dut.sources' are correct "
                "relative to the project folder."
            ),
        )

    return BoardCheckResult(
        check_id="sources_exist",
        check_name="RTL Sources Exist",
        passed=True,
        level="INFO",
        message=f"All {len(sources)} declared source file(s) found.",
    )


# ---------------------------------------------------------------------------
# Top module declared
# ---------------------------------------------------------------------------

def check_top_module_declared(manifest) -> BoardCheckResult:
    """Verify the project declares a non-empty top_module."""
    top = manifest.top_module or ""
    if not top.strip():
        return BoardCheckResult(
            check_id="top_module_declared",
            check_name="Top Module Declared",
            passed=False,
            level="ERROR",
            message="No 'top_module' declared under dut: in project.yaml.",
            suggestion="Add 'top_module: <your_module_name>' under dut:.",
        )

    return BoardCheckResult(
        check_id="top_module_declared",
        check_name="Top Module Declared",
        passed=True,
        level="INFO",
        message=f"top_module declared as '{top}'.",
    )


# ---------------------------------------------------------------------------
# Clock source
# ---------------------------------------------------------------------------

def check_clock_source(
    manifest,
    board_clock_sources: List[dict],
) -> BoardCheckResult:
    """
    If the project declares target.clock_source, verify it matches a
    known board clock.  If no clock_source is declared, emit an INFO
    suggesting the user pick one.
    """
    tb            = manifest.target or {}
    declared_clk  = tb.get("clock_source", None)
    board_clk_names = [c["name"] for c in board_clock_sources]
    board_clk_hint  = ", ".join(board_clk_names)

    if declared_clk is None:
        return BoardCheckResult(
            check_id="clock_source",
            check_name="Clock Source",
            passed=True,
            level="INFO",
            message="No clock_source declared — board default will be assumed.",
            suggestion=(
                f"Add 'clock_source: CLOCK_50' (or similar) under target: "
                f"in project.yaml.  Available: {board_clk_hint}"
            ) if board_clk_names else None,
        )

    if declared_clk in board_clk_names:
        match = next(c for c in board_clock_sources if c["name"] == declared_clk)
        return BoardCheckResult(
            check_id="clock_source",
            check_name="Clock Source",
            passed=True,
            level="INFO",
            message=(
                f"clock_source '{declared_clk}' found on board "
                f"({match['freq_mhz']} MHz)."
            ),
        )

    return BoardCheckResult(
        check_id="clock_source",
        check_name="Clock Source",
        passed=False,
        level="ERROR",
        message=f"clock_source '{declared_clk}' is not a known clock on this board.",
        detail=f"Board clocks: {board_clk_hint}",
        suggestion=f"Use one of: {board_clk_hint}",
    )


# ---------------------------------------------------------------------------
# Clock frequency sanity
# ---------------------------------------------------------------------------

def check_clock_frequency(
    manifest,
    board_clock_sources: List[dict],
    max_reasonable_mhz: float = 500.0,
) -> BoardCheckResult:
    """
    If the project declares target.target_clock_mhz, flag it if it is
    unreasonably high for this device family.
    """
    tb          = manifest.target or {}
    target_mhz  = tb.get("target_clock_mhz", None)

    if target_mhz is None:
        return BoardCheckResult(
            check_id="clock_frequency",
            check_name="Clock Frequency",
            passed=True,
            level="INFO",
            message="No target_clock_mhz declared — skipping frequency check.",
        )

    try:
        mhz = float(target_mhz)
    except (TypeError, ValueError):
        return BoardCheckResult(
            check_id="clock_frequency",
            check_name="Clock Frequency",
            passed=False,
            level="WARN",
            message=f"target_clock_mhz value '{target_mhz}' is not a valid number.",
        )

    if mhz > max_reasonable_mhz:
        return BoardCheckResult(
            check_id="clock_frequency",
            check_name="Clock Frequency",
            passed=False,
            level="WARN",
            message=(
                f"target_clock_mhz={mhz} MHz appears very high for this "
                f"board family (max reasonable: {max_reasonable_mhz} MHz)."
            ),
            suggestion=(
                "Verify your timing constraints. Run synthesis to get a "
                "proper Fmax estimate for this device."
            ),
        )

    return BoardCheckResult(
        check_id="clock_frequency",
        check_name="Clock Frequency",
        passed=True,
        level="INFO",
        message=f"target_clock_mhz={mhz} MHz is within a reasonable range.",
    )


# ---------------------------------------------------------------------------
# I/O standard
# ---------------------------------------------------------------------------

def check_io_standard(
    manifest,
    supported_io_standards: List[str],
) -> BoardCheckResult:
    """
    If the project declares target.io_standard, verify it is supported
    on this board.
    """
    tb          = manifest.target or {}
    declared_io = tb.get("io_standard", None)

    if declared_io is None:
        return BoardCheckResult(
            check_id="io_standard",
            check_name="I/O Standard",
            passed=True,
            level="INFO",
            message="No io_standard declared — skipping I/O check.",
            suggestion=(
                f"Supported on this board: {', '.join(supported_io_standards)}"
            ) if supported_io_standards else None,
        )

    if declared_io in supported_io_standards:
        return BoardCheckResult(
            check_id="io_standard",
            check_name="I/O Standard",
            passed=True,
            level="INFO",
            message=f"I/O standard '{declared_io}' is supported on this board.",
        )

    return BoardCheckResult(
        check_id="io_standard",
        check_name="I/O Standard",
        passed=False,
        level="WARN",
        message=f"I/O standard '{declared_io}' is not in this board's supported list.",
        detail=f"Supported: {', '.join(supported_io_standards)}",
        suggestion="Verify you are using the correct I/O voltage standard.",
    )


# ---------------------------------------------------------------------------
# Resource estimate
# ---------------------------------------------------------------------------

def check_resource_estimate(
    manifest,
    resource_budget: dict,
) -> BoardCheckResult:
    """
    If the project declares target.resource_estimate, compare against the
    board's resource_budget for a rough pre-lab sanity check.

    Example project.yaml snippet:
        target:
          resource_estimate:
            luts: 500
            ffs:  200
    """
    tb       = manifest.target or {}
    estimate = tb.get("resource_estimate", None)

    if not estimate or not resource_budget:
        return BoardCheckResult(
            check_id="resource_estimate",
            check_name="Resource Estimate",
            passed=True,
            level="INFO",
            message="No resource_estimate declared — skipping resource check.",
            suggestion=(
                "Add 'resource_estimate: {luts: N, ffs: N}' under target: "
                "for a rough pre-lab sanity check."
            ),
        )

    overages = []
    rows     = []

    for resource, requested in estimate.items():
        budget = resource_budget.get(resource)
        if budget is None:
            rows.append(f"  {resource}: requested={requested}  (no budget data for this resource)")
            continue
        pct  = (requested / budget * 100) if budget > 0 else 0
        flag = "  *** OVER BUDGET ***" if requested > budget else ""
        rows.append(
            f"  {resource}: requested={requested}  budget={budget}  "
            f"({pct:.1f}%){flag}"
        )
        if requested > budget:
            overages.append(resource)

    if overages:
        return BoardCheckResult(
            check_id="resource_estimate",
            check_name="Resource Estimate",
            passed=False,
            level="WARN",
            message=f"Resource estimate exceeds board budget for: {', '.join(overages)}.",
            detail="\n".join(rows),
            suggestion=(
                "These are rough estimates — run synthesis for exact numbers.  "
                "Optimize if estimates are significantly over budget."
            ),
        )

    return BoardCheckResult(
        check_id="resource_estimate",
        check_name="Resource Estimate",
        passed=True,
        level="INFO",
        message="Resource estimate is within board budget (rough check only).",
        detail="\n".join(rows),
    )


# ---------------------------------------------------------------------------
# Toolchain requirement
# ---------------------------------------------------------------------------

def check_toolchain_declared(
    manifest,
    required_toolchain: str,
    required_edition: str,
    free_license_available: bool = False,
) -> BoardCheckResult:
    """
    Inform the user which synthesis toolchain edition this board requires.

    This is always INFO-level — it never blocks simulation-first validation.
    It surfaces the toolchain requirement early so users aren't surprised
    when they move toward lab.

    Used by boards that require a specific edition not covered by Quartus Lite
    (e.g. Agilex 5 requires Quartus Prime Pro).

    Args:
        required_toolchain     : e.g. "Quartus Prime Pro"
        required_edition       : e.g. "Pro Edition"
        free_license_available : True if the board ships with a free Pro license
    """
    license_note = (
        "A free Quartus Pro license is included with the DE25-Standard kit."
        if free_license_available
        else f"{required_edition} license required — check Altera/Intel licensing."
    )

    tb = manifest.target or {}
    declared_tool = tb.get("toolchain", None)

    if declared_tool and declared_tool.strip().lower() not in required_toolchain.lower():
        return BoardCheckResult(
            check_id="toolchain_required",
            check_name="Toolchain Requirement",
            passed=False,
            level="WARN",
            message=(
                f"Project declares toolchain '{declared_tool}' but this board "
                f"requires {required_toolchain}."
            ),
            detail=license_note,
            suggestion=f"Update 'toolchain:' in your project.yaml target block to '{required_toolchain}'.",
        )

    return BoardCheckResult(
        check_id="toolchain_required",
        check_name="Toolchain Requirement",
        passed=True,
        level="INFO",
        message=f"This board requires {required_toolchain} ({required_edition}).",
        detail=license_note,
    )
