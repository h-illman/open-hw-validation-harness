# Architecture

This document describes the structure of the framework as of Phase 4.

---

## Layer diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User Entry Point                     │
│           scripts/run_regression.py                     │
│   --list  /  --project <name>  /  --verbose             │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  Framework Layer                        │
│   framework/project.py       (manifest discovery)      │
│   framework/result_parser.py (JUnit XML parsing)       │
│   framework/tool_check.py    (tool availability)       │
└───────────────────────┬─────────────────────────────────┘
                        │  reads project.yaml from each project
┌───────────────────────▼─────────────────────────────────┐
│                  Project Layer                          │
│   projects/<name>/                                      │
│     project.yaml       <- manifest                      │
│     rtl/               <- HDL sources                   │
│     sim/Makefile       <- drives Verilator + cocotb     │
│     sim/test_<name>.py <- cocotb tests                  │
│     sim/reg_driver.py  <- optional reusable driver      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│               Simulation Backend                        │
│   Verilator   (compiles Verilog → C++ → binary)        │
│   cocotb VPI  (Python ↔ simulator signal bridge)       │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                    DUT (your design)                    │
│   Any Verilog/SystemVerilog RTL module                  │
└─────────────────────────────────────────────────────────┘
```

---

## How project discovery works

The runner calls `framework/project.py:discover_projects()` which:

1. Scans `projects/*/project.yaml`
2. Parses each manifest with PyYAML
3. Returns a list of `ProjectManifest` objects
4. Skips the `template/` folder (not a runnable project)

The runner never has a hardcoded list of projects. Adding a project means
dropping a folder into `projects/` — nothing else changes.

---

## The project.yaml manifest

Each project's manifest tells the framework:

```yaml
name:        reg8           # folder name, used as project ID
dut:
  top_module: reg8          # Verilog module name
  sources: [rtl/reg8.v]    # source files to compile
sim:
  tool: verilator
  test_module: test_reg8    # cocotb test file (no .py)
artifacts:
  results_xml: artifacts/results_reg8.xml
  waves_dir:   artifacts/waves/
```

This manifest is the contract between a project and the framework.

---

## Key design decisions

**Why `projects/` with one folder per DUT?**
Each project is fully self-contained — RTL, tests, Makefile, and manifest
in one place. You can copy, share, or delete a project without touching
anything else. It also makes the discovery model trivial.

**Why a project.yaml manifest?**
The runner needs to know the top module name, source files, and artifact
paths without parsing Verilog or Makefiles. The YAML manifest is the
simplest, most readable way to express that. It also sets up Phase 5:
target-aware fields (e.g. `target_board:`) can be added to the manifest
without changing the framework core.

**Why a `framework/` Python package?**
Extracting discovery, result parsing, and tool checking into a package
means the runner is thin (orchestration only) and the utilities are
testable and reusable. It also means other scripts or tools can import
`framework.project` without copy-pasting code.

**Why keep the Makefile per project?**
cocotb's build system is Makefile-based. Keeping one Makefile per project
means each project can be run standalone (`cd projects/x/sim && make`)
without the runner. This is important for developer iteration speed.

---

## Artifact layout

```
artifacts/
├── waves/                      <- VCD waveforms from all projects
│   └── dump.vcd                <- overwritten on each run
├── sim_build/
│   ├── reg8/                   <- Verilator C++ build for reg8
│   └── periph_ctrl/            <- Verilator C++ build for periph_ctrl
├── results_reg8.xml            <- JUnit XML from reg8
└── results_periph_ctrl.xml     <- JUnit XML from periph_ctrl
```

---

## Phase 5 and 6 extension points

**Phase 5 — Target-aware checks:**
Add `target_board:` and `constraints:` fields to `project.yaml`.
The framework layer gains a `target_checker.py` module that reads these
fields and runs board-specific validation (pin compatibility, clock
requirements, resource estimates). The runner gains a `--target` flag.
No changes to existing project structure.

**Phase 6 — Real hardware backend:**
The driver layer (e.g. `reg_driver.py`) already marks the boundary between
test logic and the simulation backend. Swapping Verilator for a JTAG or
Avalon hardware backend means replacing the driver's implementation, not
the test code above it. The `framework/` package gains a `backends/`
submodule that the runner can select via a `--backend` flag.
