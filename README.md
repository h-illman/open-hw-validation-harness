# open-hw-validation-harness

A lean, open-source, simulation-first validation framework for FPGA and
digital hardware designs.

**The core idea:** bring in your own RTL design, run automated simulation
tests, see what passes and what fails, fix issues, and go into the lab with
much higher confidence.

---

## What this framework does

- Runs your HDL design through automated cocotb + Verilator simulation
- Reports pass/fail results for every test
- Generates VCD waveforms for debugging
- Auto-discovers projects — add your DUT, run the runner, done
- **Phase 5:** checks your design against a target board before you go to lab
- Stays lean, readable, and explainable at every layer

---

## Project status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Repo scaffold and structure | ✅ Done |
| 2 | Simulation bring-up (Verilator + cocotb) | ✅ Done |
| 3 | Realistic validation target (periph_ctrl DUT) | ✅ Done |
| 4 | Reusable user-facing framework | ✅ Done |
| 5 | Target-aware board readiness checks | ✅ Done |
| 6 | Real hardware validation backend | 🔲 Planned |

---

## Quick start

```bash
# 1. Activate your Python venv
source ~/hwvenv/bin/activate

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. See what projects are available
python scripts/run_regression.py --list

# 4. Run all projects (simulation only)
python scripts/run_regression.py

# 5. Run one project
python scripts/run_regression.py --project periph_ctrl

# 6. Run simulation + target board checks
python scripts/run_regression.py --project periph_ctrl --target de10_standard

# 7. Run target checks only (no simulation)
python scripts/run_regression.py --target-only --project reg8 --target de0_cv

# 8. See supported boards
python scripts/run_regression.py --list-boards

# 9. View waveform
gtkwave artifacts/waves/dump.vcd
```

---

## Adding your own design

```bash
# Copy the template
cp -r projects/template projects/my_design

# Add your RTL to projects/my_design/rtl/
# Write your tests in projects/my_design/sim/
# Fill in projects/my_design/project.yaml
# Optionally add a target: block for Phase 5 checks
# Run it
python scripts/run_regression.py --project my_design
```

See **[docs/adding_a_project.md](docs/adding_a_project.md)** for the full walkthrough.
See **[docs/phase5_target_aware.md](docs/phase5_target_aware.md)** for target-aware checks.

---

## Repository layout

```
open-hw-validation-harness/
│
├── projects/                    <- one folder per DUT/design
│   ├── reg8/                    <- Phase 2 example: 8-bit register
│   ├── periph_ctrl/             <- Phase 3 example: register-mapped peripheral
│   └── template/                <- copy this to start your own project
│
├── framework/                   <- shared Python utilities
│   ├── project.py               <- manifest loading + auto-discovery
│   ├── result_parser.py         <- JUnit XML parsing
│   ├── tool_check.py            <- tool availability checks
│   ├── target_checker.py        <- Phase 5: target check orchestrator
│   └── boards/                  <- Phase 5: board profile system
│       ├── base_board.py        <- BoardProfile ABC
│       ├── common_checks.py     <- reusable check functions
│       ├── registry.py          <- board_id -> profile registry
│       ├── de10_standard.py     <- DE10-Standard (Terasic / Cyclone V SX)
│       └── de0_cv.py            <- DE0-CV (Terasic / Cyclone V E)
│
├── scripts/
│   └── run_regression.py        <- main entry point
│
├── docs/
│   ├── adding_a_project.md      <- how to bring in your own DUT
│   ├── getting_started.md       <- installation and setup
│   ├── architecture.md          <- how the framework is structured
│   └── phase5_target_aware.md   <- Phase 5: target-aware checks guide
│
└── artifacts/
    ├── waves/                   <- VCD waveforms
    ├── sim_build/               <- Verilator build cache (git-ignored)
    └── reports/                 <- Phase 5: target readiness JSON reports
```

---

## Software requirements

| Tool | Version | Install |
|------|---------|---------| 
| Python | 3.10+ | python.org |
| cocotb | 2.x | `pip install cocotb` |
| PyYAML | 6.x | `pip install pyyaml` |
| Verilator | 5.036+ | Build from source — see docs/getting_started.md |
| GNU Make | 4.x | `sudo apt install make` |
| GTKWave | any | `sudo apt install gtkwave` (optional) |

> **Windows users:** Verilator requires WSL2. Run everything from inside
> Ubuntu. Your project files are accessible at `/mnt/d/...`.
