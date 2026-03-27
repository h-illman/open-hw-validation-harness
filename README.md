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
- Stays lean, readable, and explainable at every layer

## What it does not do (yet)

- Board-specific synthesis or timing analysis (Phase 5)
- Real hardware execution (Phase 6)
- Magical guarantees — it catches behavioral and logic bugs in simulation

---

## Project status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Repo scaffold and structure | ✅ Done |
| 2 | Simulation bring-up (Verilator + cocotb) | ✅ Done |
| 3 | Realistic validation target (periph_ctrl DUT) | ✅ Done |
| 4 | Reusable user-facing framework | ✅ Done |
| 5 | Target-aware board readiness checks | 🔲 Planned |
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

# 4. Run all projects
python scripts/run_regression.py

# 5. Run one project
python scripts/run_regression.py --project periph_ctrl

# 6. View a waveform
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
# Run it
python scripts/run_regression.py --project my_design
```

See **[docs/adding_a_project.md](docs/adding_a_project.md)** for the full walkthrough.

---

## Repository layout

```
open-hw-validation-harness/
│
├── projects/                    <- one folder per DUT/design
│   ├── reg8/                    <- Phase 2 example: 8-bit register
│   │   ├── rtl/reg8.v
│   │   ├── sim/Makefile
│   │   ├── sim/test_reg8.py
│   │   └── project.yaml
│   │
│   ├── periph_ctrl/             <- Phase 3 example: register-mapped peripheral
│   │   ├── rtl/periph_ctrl.v
│   │   ├── sim/Makefile
│   │   ├── sim/reg_driver.py
│   │   ├── sim/test_periph_ctrl.py
│   │   └── project.yaml
│   │
│   └── template/                <- copy this to start your own project
│       ├── rtl/
│       ├── sim/Makefile
│       ├── sim/test_template.py
│       └── project.yaml
│
├── framework/                   <- shared Python utilities
│   ├── project.py               <- manifest loading + auto-discovery
│   ├── result_parser.py         <- JUnit XML parsing
│   └── tool_check.py            <- tool availability checks
│
├── scripts/
│   └── run_regression.py        <- main entry point
│
├── docs/
│   ├── adding_a_project.md      <- how to bring in your own DUT
│   ├── getting_started.md       <- installation and setup
│   └── architecture.md          <- how the framework is structured
│
└── artifacts/
    ├── waves/                   <- VCD waveforms (all projects)
    └── sim_build/               <- Verilator build cache (git-ignored)
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
