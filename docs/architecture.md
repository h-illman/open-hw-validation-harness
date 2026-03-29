# Architecture

This document describes the structure of the framework as of Phase 5.

---

## Layer diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Entry Point                       │
│              scripts/run_regression.py                      │
│  --list / --project / --verbose                             │
│  --target / --target-only / --list-boards / --board-info    │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┴──────────────────┐
          │                                   │
┌─────────▼──────────────────┐   ┌────────────▼───────────────┐
│     Framework Layer        │   │  Target-Aware Layer (P5)   │
│  framework/project.py      │   │  framework/target_checker.py│
│  framework/result_parser.py│   │  framework/boards/          │
│  framework/tool_check.py   │   │    base_board.py            │
└─────────┬──────────────────┘   │    common_checks.py         │
          │                      │    de10_standard.py         │
          │ reads project.yaml   │    de0_cv.py                │
          │ (incl. target: block)│    registry.py              │
          │                      └────────────────────────────┘
┌─────────▼──────────────────────────────────────────────────┐
│                      Project Layer                          │
│  projects/<name>/                                           │
│    project.yaml        <- manifest (+ optional target: P5) │
│    rtl/                <- HDL sources                       │
│    sim/Makefile        <- drives Verilator + cocotb         │
│    sim/test_<n>.py     <- cocotb tests                      │
└─────────┬──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│                   Simulation Backend                        │
│  Verilator   (compiles Verilog -> C++ -> binary)           │
│  cocotb VPI  (Python <-> simulator signal bridge)          │
└─────────┬──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│                     DUT (your design)                       │
│  Any Verilog/SystemVerilog RTL module                       │
└─────────────────────────────────────────────────────────────┘
```

---

## How project discovery works

The runner calls `framework/project.py:discover_projects()` which:

1. Scans `projects/*/project.yaml`
2. Parses each manifest with PyYAML
3. Returns a list of `ProjectManifest` objects
4. Skips the `template/` folder (not a runnable project)

The runner never has a hardcoded list of projects.

---

## The project.yaml manifest (Phase 5 additions)

The existing manifest schema is unchanged.  Phase 5 adds an optional
`target:` block that the existing simulation path ignores completely.

```yaml
name:        my_design
dut:
  top_module: my_top_module
  sources: [rtl/my_top_module.v]
sim:
  tool: verilator
  test_module: test_my_design
  timeout_ns: 10000
artifacts:
  results_xml: artifacts/results_my_design.xml
  waves_dir:   artifacts/waves/

# Phase 5 — optional target block
target:
  board: de10_standard          # required for target-aware checks
  clock_source: CLOCK_50        # optional
  target_clock_mhz: 50         # optional
  resource_estimate:            # optional
    luts: 500
    ffs:  200
```

---

## Board profile system (Phase 5)

```
framework/boards/
  __init__.py
  base_board.py        <- BoardProfile ABC + BoardReadinessReport dataclass
  common_checks.py     <- reusable check functions (shared by all boards)
  registry.py          <- central registry: board_id -> BoardProfile instance
  de10_standard.py     <- DE10-Standard profile
  de0_cv.py            <- DE0-CV profile
```

`BoardProfile` is the contract every supported board must implement.  It
declares board metadata (clocks, I/O standards, resource budgets) and
a `check_project(manifest)` method that runs the board's checks and returns
a `BoardReadinessReport`.

`common_checks.py` contains the actual check logic.  Board profiles call
these functions rather than re-implementing checks per board.  Adding a new
board means writing ~40 lines to declare metadata and call the check functions.

---

## Artifact layout (Phase 5 additions)

```
artifacts/
├── waves/                       <- VCD waveforms (unchanged)
├── sim_build/                   <- Verilator build cache (unchanged)
├── results_reg8.xml             <- JUnit XML from reg8 (unchanged)
├── results_periph_ctrl.xml      <- JUnit XML from periph_ctrl (unchanged)
└── reports/                     <- NEW: Phase 5 target readiness reports
    ├── reg8/
    │   └── target_readiness.json
    └── periph_ctrl/
        └── target_readiness.json
```

---

## Phase 6 extension points

**Phase 5 already prepared these hooks:**

`BoardProfile.check_project()` runs pre-lab checks.  Phase 6 can add
`BoardProfile.program()` and `BoardProfile.capture_output()` alongside it
without touching Phase 5 check logic.

`framework/target_checker.py` is the orchestration point.  After simulation
and target checks both pass, it is the natural place to dispatch to a hardware
backend.  A `--backend hw` flag alongside `--target` would be sufficient to
activate it.

The readiness report JSON (`artifacts/reports/.../target_readiness.json`)
provides a machine-readable go/no-go signal for a Phase 6 dispatch step.
