"""
Basic smoke tests for the open-hw-validation-harness framework.

Phase 1-4: placeholder smoke test confirming test infrastructure works.
Phase 5:   extends with target-aware layer tests — board registry, checks,
           manifest target field, resolve logic.  Does not require Verilator
           or cocotb — pure Python, always runnable.
"""

from pathlib import Path
import sys

# Make the repo root importable when pytest runs from any directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Phase 1-4: original smoke test (unchanged)
# ---------------------------------------------------------------------------

def test_smoke():
    """
    Placeholder smoke test that always passes.
    """
    assert True


# ---------------------------------------------------------------------------
# Phase 5: board registry
# ---------------------------------------------------------------------------

def test_board_registry_loads():
    """Registry builds without errors and contains expected boards."""
    from framework.boards.registry import list_board_ids, list_boards
    ids = list_board_ids()
    assert "de10_standard" in ids
    assert "de0_cv" in ids


def test_get_known_board():
    """get_board returns the correct profile for a known ID."""
    from framework.boards.registry import get_board
    b = get_board("de10_standard")
    assert b.board_id() == "de10_standard"
    assert "Cyclone V" in b.board_family()
    assert b.fpga_device() == "5CSXFC6D6F31C6"


def test_get_unknown_board_raises():
    """get_board raises KeyError for an unrecognised board ID."""
    from framework.boards.registry import get_board
    try:
        import pytest
        with pytest.raises(KeyError, match="not_a_real_board"):
            get_board("not_a_real_board")
    except ImportError:
        # pytest not installed — use plain try/except
        raised = False
        try:
            get_board("not_a_real_board")
        except KeyError:
            raised = True
        assert raised, "Expected KeyError for unknown board ID"


def test_board_clock_sources_non_empty():
    """Each registered board declares at least one clock source."""
    from framework.boards.registry import list_boards
    for board in list_boards():
        clocks = board.clock_sources()
        assert len(clocks) >= 1, f"{board.board_id()} has no clock sources"
        for c in clocks:
            assert "name" in c
            assert "freq_mhz" in c


def test_board_resource_budget_non_empty():
    """Each registered board declares a non-empty resource budget."""
    from framework.boards.registry import list_boards
    for board in list_boards():
        budget = board.resource_budget()
        assert len(budget) > 0, f"{board.board_id()} has no resource budget"


# ---------------------------------------------------------------------------
# Phase 5: project manifest target field
# ---------------------------------------------------------------------------

def test_manifest_loads_target_block():
    """load_manifest correctly parses an optional target: block."""
    from framework.project import load_manifest
    yaml_path = REPO_ROOT / "projects" / "reg8" / "project.yaml"
    m = load_manifest(yaml_path, REPO_ROOT)
    assert m.target is not None
    assert m.target.get("board") == "de0_cv"
    assert m.target.get("clock_source") == "CLOCK_50"


def test_manifest_target_none_when_absent(tmp_path):
    """load_manifest sets target=None when no target: block exists."""
    from framework.project import load_manifest
    yaml_content = """\
name: bare_project
description: no target block
version: "0.1.0"
phase: 1
dut:
  top_module: bare_mod
  sources:
    - rtl/bare_mod.v
sim:
  tool: verilator
  test_module: test_bare
  timeout_ns: 5000
artifacts:
  results_xml: artifacts/results_bare.xml
  waves_dir:   artifacts/waves/
"""
    p = tmp_path / "project.yaml"
    p.write_text(yaml_content)
    m = load_manifest(p, tmp_path)
    assert m.target is None


# ---------------------------------------------------------------------------
# Phase 5: board_id resolution
# ---------------------------------------------------------------------------

def test_resolve_board_id_cli_takes_precedence():
    """CLI --target overrides the board declared in project.yaml."""
    from framework.project import load_manifest
    from framework.target_checker import resolve_board_id
    yaml_path = REPO_ROOT / "projects" / "reg8" / "project.yaml"
    m = load_manifest(yaml_path, REPO_ROOT)
    # reg8 declares de0_cv; CLI flag says de10_standard
    resolved = resolve_board_id(m, cli_target="de10_standard")
    assert resolved == "de10_standard"


def test_resolve_board_id_from_manifest():
    """resolve_board_id falls back to project.yaml when no CLI target given."""
    from framework.project import load_manifest
    from framework.target_checker import resolve_board_id
    yaml_path = REPO_ROOT / "projects" / "periph_ctrl" / "project.yaml"
    m = load_manifest(yaml_path, REPO_ROOT)
    resolved = resolve_board_id(m, cli_target=None)
    assert resolved == "de10_standard"


def test_resolve_board_id_none_when_no_target(tmp_path):
    """resolve_board_id returns None when neither CLI nor manifest specifies a board."""
    from framework.project import load_manifest
    from framework.target_checker import resolve_board_id
    yaml_content = """\
name: no_target
description: no target
version: "0.1.0"
phase: 1
dut:
  top_module: mod
  sources: [rtl/mod.v]
sim:
  tool: verilator
  test_module: test_mod
  timeout_ns: 5000
artifacts:
  results_xml: artifacts/results_no_target.xml
  waves_dir:   artifacts/waves/
"""
    p = tmp_path / "project.yaml"
    p.write_text(yaml_content)
    m = load_manifest(p, tmp_path)
    assert resolve_board_id(m, cli_target=None) is None


# ---------------------------------------------------------------------------
# Phase 5: common checks
# ---------------------------------------------------------------------------

def test_check_sources_exist_pass():
    """check_sources_exist passes when all declared sources are on disk."""
    from framework.project import load_manifest
    from framework.boards.common_checks import check_sources_exist
    yaml_path = REPO_ROOT / "projects" / "reg8" / "project.yaml"
    m = load_manifest(yaml_path, REPO_ROOT)
    result = check_sources_exist(m)
    assert result.passed
    assert result.level == "INFO"


def test_check_sources_exist_fail(tmp_path):
    """check_sources_exist fails when a declared source is missing."""
    from framework.project import load_manifest
    from framework.boards.common_checks import check_sources_exist
    yaml_content = """\
name: missing_src
description: missing source
version: "0.1.0"
phase: 1
dut:
  top_module: mod
  sources:
    - rtl/does_not_exist.v
sim:
  tool: verilator
  test_module: test_mod
  timeout_ns: 5000
artifacts:
  results_xml: artifacts/results_missing.xml
  waves_dir:   artifacts/waves/
"""
    p = tmp_path / "project.yaml"
    p.write_text(yaml_content)
    m = load_manifest(p, tmp_path)
    result = check_sources_exist(m)
    assert not result.passed
    assert result.level == "ERROR"


def test_check_clock_source_match():
    """check_clock_source passes when declared clock matches a board clock."""
    from framework.project import load_manifest
    from framework.boards.common_checks import check_clock_source
    from framework.boards.registry import get_board
    yaml_path = REPO_ROOT / "projects" / "reg8" / "project.yaml"
    m = load_manifest(yaml_path, REPO_ROOT)
    board = get_board("de0_cv")
    result = check_clock_source(m, board.clock_sources())
    assert result.passed


def test_check_clock_source_mismatch(tmp_path):
    """check_clock_source errors when declared clock is not on the board."""
    from framework.project import load_manifest
    from framework.boards.common_checks import check_clock_source
    from framework.boards.registry import get_board
    yaml_content = """\
name: bad_clk
description: bad clock
version: "0.1.0"
phase: 1
dut:
  top_module: mod
  sources: [rtl/mod.v]
sim:
  tool: verilator
  test_module: test_mod
  timeout_ns: 5000
artifacts:
  results_xml: artifacts/results_bad_clk.xml
  waves_dir:   artifacts/waves/
target:
  board: de0_cv
  clock_source: FAKE_CLK_999
"""
    p = tmp_path / "project.yaml"
    p.write_text(yaml_content)
    m = load_manifest(p, tmp_path)
    board = get_board("de0_cv")
    result = check_clock_source(m, board.clock_sources())
    assert not result.passed
    assert result.level == "ERROR"


def test_check_resource_estimate_over_budget(tmp_path):
    """check_resource_estimate warns when estimate exceeds board budget."""
    from framework.project import load_manifest
    from framework.boards.common_checks import check_resource_estimate
    from framework.boards.registry import get_board
    yaml_content = """\
name: over_budget
description: over budget
version: "0.1.0"
phase: 1
dut:
  top_module: mod
  sources: [rtl/mod.v]
sim:
  tool: verilator
  test_module: test_mod
  timeout_ns: 5000
artifacts:
  results_xml: artifacts/results_over.xml
  waves_dir:   artifacts/waves/
target:
  board: de0_cv
  resource_estimate:
    luts: 999999
    ffs:  999999
"""
    p = tmp_path / "project.yaml"
    p.write_text(yaml_content)
    m = load_manifest(p, tmp_path)
    board = get_board("de0_cv")
    result = check_resource_estimate(m, board.resource_budget())
    assert not result.passed
    assert result.level == "WARN"


# ---------------------------------------------------------------------------
# Phase 5: full check_project round-trip
# ---------------------------------------------------------------------------

def test_run_target_checks_end_to_end():
    """run_target_checks produces a BoardReadinessReport for a real project."""
    from framework.project import load_manifest
    from framework.target_checker import run_target_checks
    yaml_path = REPO_ROOT / "projects" / "periph_ctrl" / "project.yaml"
    m = load_manifest(yaml_path, REPO_ROOT)
    report = run_target_checks(m)
    assert report.project_name == "periph_ctrl"
    assert report.board_id == "de10_standard"
    assert len(report.checks) > 0
    # periph_ctrl with valid config should be READY
    assert report.ready


def test_run_target_checks_cli_override():
    """CLI board_id correctly overrides the manifest board."""
    from framework.project import load_manifest
    from framework.target_checker import run_target_checks
    # reg8 declares de0_cv in its yaml; override to de10_standard via CLI
    yaml_path = REPO_ROOT / "projects" / "reg8" / "project.yaml"
    m = load_manifest(yaml_path, REPO_ROOT)
    report = run_target_checks(m, cli_target="de10_standard")
    assert report.board_id == "de10_standard"
    assert report.ready


# ---------------------------------------------------------------------------
# DE25-Standard board profile tests
# ---------------------------------------------------------------------------

def test_de25_standard_in_registry():
    """DE25-Standard is registered and accessible by ID."""
    from framework.boards.registry import get_board, list_board_ids
    assert "de25_standard" in list_board_ids()
    b = get_board("de25_standard")
    assert b.board_id() == "de25_standard"


def test_de25_standard_device_string():
    """DE25-Standard reports the correct Agilex 5 device part number."""
    from framework.boards.registry import get_board
    b = get_board("de25_standard")
    assert b.fpga_device() == "A5ED013BB32AE4S"
    assert "Agilex" in b.board_family()


def test_de25_standard_has_four_clocks():
    """DE25-Standard declares exactly 4 clock sources (3x50MHz + 1x150MHz)."""
    from framework.boards.registry import get_board
    b = get_board("de25_standard")
    clocks = b.clock_sources()
    assert len(clocks) == 4
    names = [c["name"] for c in clocks]
    assert "CLOCK_50"  in names
    assert "CLOCK_150" in names
    freqs = sorted(set(c["freq_mhz"] for c in clocks))
    assert 50.0  in freqs
    assert 150.0 in freqs


def test_de25_standard_resource_budget_larger_than_cyclone_v():
    """DE25-Standard budget exceeds DE10-Standard and DE0-CV (it is a bigger device)."""
    from framework.boards.registry import get_board
    de25  = get_board("de25_standard")
    de10  = get_board("de10_standard")
    de0   = get_board("de0_cv")
    assert de25.resource_budget()["luts"] > de10.resource_budget()["luts"]
    assert de25.resource_budget()["luts"] > de0.resource_budget()["luts"]


def test_de25_standard_quartus_pro_check():
    """Toolchain check surfaces the Quartus Pro requirement."""
    from framework.boards.registry import get_board
    from framework.project import load_manifest
    from pathlib import Path
    root = Path(REPO_ROOT)
    m = load_manifest(root / "projects" / "reg8" / "project.yaml", root)
    b = get_board("de25_standard")
    report = b.check_project(m)
    toolchain_check = next(
        (c for c in report.checks if c.check_id == "toolchain_required"), None
    )
    assert toolchain_check is not None
    assert "Pro" in toolchain_check.message
    assert toolchain_check.level == "INFO"   # never blocks — informational only


def test_de25_standard_hsmc_differential_check_pass():
    """HSMC differential check passes (INFO) when hsmc_differential not declared."""
    from framework.boards.registry import get_board
    from framework.project import load_manifest
    from pathlib import Path
    root = Path(REPO_ROOT)
    m = load_manifest(root / "projects" / "periph_ctrl" / "project.yaml", root)
    b = get_board("de25_standard")
    report = b.check_project(m)
    hsmc_check = next(
        (c for c in report.checks if c.check_id == "hsmc_differential"), None
    )
    assert hsmc_check is not None
    assert hsmc_check.passed is True


def test_de25_standard_hsmc_differential_check_warn(tmp_path):
    """HSMC differential check warns when hsmc_differential: true is declared."""
    from framework.boards.registry import get_board
    from framework.project import load_manifest
    yaml_content = """\
name: diff_design
description: uses HSMC differential
version: "0.1.0"
phase: 1
dut:
  top_module: diff_mod
  sources: [rtl/diff_mod.v]
sim:
  tool: verilator
  test_module: test_diff
  timeout_ns: 5000
artifacts:
  results_xml: artifacts/results_diff.xml
  waves_dir:   artifacts/waves/
target:
  board: de25_standard
  hsmc_differential: true
"""
    p = tmp_path / "project.yaml"
    p.write_text(yaml_content)
    m = load_manifest(p, tmp_path)
    b = get_board("de25_standard")
    report = b.check_project(m)
    hsmc_check = next(
        (c for c in report.checks if c.check_id == "hsmc_differential"), None
    )
    assert hsmc_check is not None
    assert hsmc_check.passed is False
    assert hsmc_check.level == "WARN"


def test_de25_standard_memory_interface_sdram(tmp_path):
    """Memory interface check identifies sdram as a valid interface."""
    from framework.boards.registry import get_board
    from framework.project import load_manifest
    yaml_content = """\
name: mem_design
description: uses SDRAM
version: "0.1.0"
phase: 1
dut:
  top_module: mem_mod
  sources: [rtl/mem_mod.v]
sim:
  tool: verilator
  test_module: test_mem
  timeout_ns: 5000
artifacts:
  results_xml: artifacts/results_mem.xml
  waves_dir:   artifacts/waves/
target:
  board: de25_standard
  memory_interface: sdram
"""
    p = tmp_path / "project.yaml"
    p.write_text(yaml_content)
    m = load_manifest(p, tmp_path)
    b = get_board("de25_standard")
    report = b.check_project(m)
    mem_check = next(
        (c for c in report.checks if c.check_id == "memory_interface"), None
    )
    assert mem_check is not None
    assert mem_check.passed is True
    assert "64 MB" in mem_check.detail


def test_de25_standard_memory_interface_invalid(tmp_path):
    """Memory interface check warns on an unrecognised interface name."""
    from framework.boards.registry import get_board
    from framework.project import load_manifest
    yaml_content = """\
name: bad_mem
description: bad memory interface
version: "0.1.0"
phase: 1
dut:
  top_module: mod
  sources: [rtl/mod.v]
sim:
  tool: verilator
  test_module: test_mod
  timeout_ns: 5000
artifacts:
  results_xml: artifacts/results_bad_mem.xml
  waves_dir:   artifacts/waves/
target:
  board: de25_standard
  memory_interface: sram
"""
    p = tmp_path / "project.yaml"
    p.write_text(yaml_content)
    m = load_manifest(p, tmp_path)
    b = get_board("de25_standard")
    report = b.check_project(m)
    mem_check = next(
        (c for c in report.checks if c.check_id == "memory_interface"), None
    )
    assert mem_check is not None
    assert mem_check.passed is False
    assert mem_check.level == "WARN"


def test_de25_standard_full_check_count():
    """DE25-Standard runs exactly 10 checks (more than Cyclone V boards)."""
    from framework.boards.registry import get_board
    from framework.project import load_manifest
    from pathlib import Path
    root = Path(REPO_ROOT)
    m = load_manifest(root / "projects" / "periph_ctrl" / "project.yaml", root)
    b = get_board("de25_standard")
    report = b.check_project(m)
    # DE25 runs 10 checks: 7 common + toolchain + HSMC + memory
    assert len(report.checks) == 10


def test_de25_standard_peripheral_summary():
    """DE25-Standard exposes a peripheral_summary with expected sections."""
    from framework.boards.registry import get_board
    b = get_board("de25_standard")
    assert hasattr(b, "peripheral_summary")
    periph = b.peripheral_summary()
    assert "fpga_side"        in periph
    assert "hps_side"         in periph
    assert "memory"           in periph
    assert "board_management" in periph
    # Spot-check key peripherals are documented
    assert "hdmi_out"         in periph["fpga_side"]
    assert "audio_codec"      in periph["fpga_side"]
    assert "ai_tensor_block"  in periph["fpga_side"]
    assert "ethernet"         in periph["hps_side"]
    assert "ddr4_shared"      in periph["memory"]
