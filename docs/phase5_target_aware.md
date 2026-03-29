# Phase 5 — Target-Aware Validation

Phase 5 adds a modular board/target awareness layer to the framework.
You can now tell the framework which FPGA board you intend to use, and it
will run a set of pre-lab readiness checks specific to that board — without
touching the simulation-first validation flow that Phases 1–4 established.

---

## What Phase 5 adds

- A **board profile system** under `framework/boards/`
- Two initial supported boards: **DE10-Standard** and **DE0-CV**
- A **`target:` block** in `project.yaml` to declare your board
- New CLI flags: `--target`, `--target-only`, `--list-boards`, `--board-info`
- JSON readiness reports saved to `artifacts/reports/<project>/`
- An extensible architecture that makes adding new boards a small, isolated task

---

## Quick start

```bash
# See all supported boards
python scripts/run_regression.py --list-boards

# Show details for one board
python scripts/run_regression.py --board-info de10_standard

# Run simulation + target checks together
python scripts/run_regression.py --project periph_ctrl --target de10_standard

# Run target checks only (no simulation needed)
python scripts/run_regression.py --target-only --project reg8 --target de0_cv

# Target board comes from project.yaml — no --target flag needed
python scripts/run_regression.py --project periph_ctrl
```

---

## Declaring a target board in project.yaml

Add a `target:` block to your project's `project.yaml`.  The only required
field inside it is `board:`.  All other fields are optional — they unlock
additional checks when present.

```yaml
# projects/my_design/project.yaml

name: my_design
# ... (existing fields unchanged) ...

target:
  board: de10_standard         # required — which board you plan to use

  clock_source: CLOCK_50       # optional — must match a board clock name
  target_clock_mhz: 50         # optional — your design's intended clock speed

  io_standard: "3.3V LVTTL"    # optional — your I/O voltage standard

  resource_estimate:           # optional — rough pre-lab sanity check
    luts: 500
    ffs:  200
```

If no `target:` block is present, the project behaves exactly as it did in
Phase 4.  Target-aware checks simply won't run unless you pass `--target`
on the CLI.

---

## What checks run

For each project + board combination, the framework runs these checks:

| Check | What it verifies |
|---|---|
| Target Block Present | `target:` block exists and `board:` is declared |
| RTL Sources Exist | All files under `dut.sources` are found on disk |
| Top Module Declared | `dut.top_module` is non-empty |
| Clock Source | `clock_source` (if declared) matches a known board clock |
| Clock Frequency | `target_clock_mhz` (if declared) is within board range |
| I/O Standard | `io_standard` (if declared) is supported on the board |
| Resource Estimate | `resource_estimate` (if declared) fits within board budget |

Each check reports one of three levels:

- **INFO** — informational, always passes
- **WARN** — potential issue, does not block lab readiness
- **ERROR** — blocks lab readiness; fix before going to hardware

A project is marked **READY FOR LAB** when no ERROR-level check fails.

---

## Supported boards

### `de10_standard` — DE10-Standard (Terasic)

| Field | Value |
|---|---|
| Family | Cyclone V SX SoC |
| Device | 5CSXFC6D6F31C6 |
| Vendor | Terasic / Intel |
| Toolchain | Quartus Prime Lite or Standard |
| Primary clock | CLOCK_50 (50 MHz, pin AF14) |
| LUT budget | ~41,910 |
| FF budget | ~83,820 |

Notes: includes ARM Cortex-A9 HPS subsystem.  This profile covers FPGA
fabric only.  HPS validation is out of scope for this harness.

---

### `de0_cv` — DE0-CV (Terasic)

| Field | Value |
|---|---|
| Family | Cyclone V E |
| Device | 5CEBA4F23C7 |
| Vendor | Terasic / Intel |
| Toolchain | Quartus Prime Lite |
| Primary clock | CLOCK_50 (50 MHz, pin M9) |
| LUT budget | ~18,480 |
| FF budget | ~36,960 |

Notes: no HPS.  Fewer resources than DE10-Standard — watch LUT/FF budgets
for larger designs.

---

## How the runner behaves

### Simulation + target checks (most common)

```bash
python scripts/run_regression.py --project periph_ctrl --target de10_standard
```

1. Runs simulation via `make` (existing Phase 4 flow)
2. Parses JUnit XML results
3. Runs target-aware board checks
4. Prints both results and a readiness verdict
5. Saves `artifacts/reports/periph_ctrl/target_readiness.json`

Exit code is non-zero if either simulation fails **or** target checks find
ERROR-level issues.

---

### Target checks only (before writing tests)

```bash
python scripts/run_regression.py --target-only --project my_design --target de10_standard
```

Skips simulation entirely.  Useful when:
- You want to check structural/config issues before your testbench is ready
- You already know simulation passes and just want the board check

---

### Board declared in project.yaml (no CLI flag needed)

If your `project.yaml` has a `target: {board: de10_standard}` block, you
can just run:

```bash
python scripts/run_regression.py --project periph_ctrl
```

The framework reads the board from the manifest and runs target checks
automatically.  The `--target` CLI flag overrides the manifest if both
are present.

---

## Adding a new board

1. Create `framework/boards/your_board.py` implementing `BoardProfile`:

```python
from framework.boards.base_board    import BoardProfile, BoardReadinessReport
from framework.boards.common_checks import (
    check_target_block_present,
    check_sources_exist,
    check_top_module_declared,
    check_clock_source,
    check_clock_frequency,
    check_io_standard,
    check_resource_estimate,
)

class MyBoard(BoardProfile):
    def board_id(self)     -> str: return "my_board"
    def board_name(self)   -> str: return "My Board (Manufacturer)"
    def board_family(self) -> str: return "Device Family"
    def fpga_device(self)  -> str: return "DEVICE_PART"
    def vendor(self)       -> str: return "Vendor Name"
    def toolchain_hint(self) -> str: return "Toolchain Name"

    def clock_sources(self):
        return [{"name": "CLK_50", "freq_mhz": 50.0, "pin": "A1"}]

    def resource_budget(self):
        return {"luts": 10000, "ffs": 20000}

    def check_project(self, manifest) -> BoardReadinessReport:
        report = BoardReadinessReport(
            board_id=self.board_id(), board_name=self.board_name(),
            board_family=self.board_family(), fpga_device=self.fpga_device(),
            project_name=manifest.name,
        )
        report.checks.append(check_target_block_present(manifest))
        report.checks.append(check_sources_exist(manifest))
        report.checks.append(check_top_module_declared(manifest))
        report.checks.append(check_clock_source(manifest, self.clock_sources()))
        report.checks.append(check_clock_frequency(manifest, self.clock_sources(), 200.0))
        report.checks.append(check_io_standard(manifest, self.io_standards()))
        report.checks.append(check_resource_estimate(manifest, self.resource_budget()))
        return report
```

2. Register it in `framework/boards/registry.py`:

```python
def _build() -> Dict[str, BoardProfile]:
    from framework.boards.de10_standard import DE10Standard
    from framework.boards.de0_cv        import DE0CV
    from framework.boards.my_board      import MyBoard   # add this

    boards = [DE10Standard(), DE0CV(), MyBoard()]        # add to list
    ...
```

That's it.  `--list-boards`, `--board-info`, and `--target` pick it up
automatically.

---

## Artifact output

Target checks produce a JSON file at:

```
artifacts/reports/<project_name>/target_readiness.json
```

Example contents:

```json
{
  "board_id": "de10_standard",
  "board_name": "DE10-Standard (Terasic)",
  "project_name": "periph_ctrl",
  "ready": true,
  "checks": [
    {
      "check_id": "clock_source",
      "check_name": "Clock Source",
      "passed": true,
      "level": "INFO",
      "message": "clock_source 'CLOCK_50' found on board (50.0 MHz)."
    }
  ],
  "summary": {
    "total": 7,
    "passed": 7,
    "errors": 0,
    "warnings": 0
  }
}
```

---

## What Phase 5 does NOT do

- Does not program or execute on real hardware (Phase 6)
- Does not run synthesis or place-and-route
- Does not replace Quartus/Vivado timing reports
- Does not lock the framework to any specific board
- Does not change the existing simulation flow in any way

---

## How this sets up Phase 6

Phase 6 will add a real hardware execution backend.  Phase 5 prepares for
this cleanly:

- `BoardProfile` already has a natural extension point for `program()` and
  `capture_output()` methods without touching check logic
- `framework/target_checker.py` is the right place to dispatch to a hardware
  backend after simulation passes and target checks pass
- The `--target` flag already selects a board — Phase 6 only needs to add a
  `--backend hw` flag alongside it
- The readiness report JSON provides a machine-readable go/no-go signal that
  a Phase 6 hardware dispatcher can consume before attempting board programming
