# open-hw-validation-harness

An open-source, simulation-first hardware validation harness for FPGA and
board-level digital designs.

---

## Project status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Repo scaffold, docs, placeholder backends | ✅ Done |
| Phase 2 | Verilator + cocotb simulation bring-up (reg8 DUT) | ✅ Done |
| Phase 3 | Register-mapped peripheral MVP (periph_ctrl DUT) | ✅ Done |
| Phase 4 | Hardware backend abstraction (Quartus, JTAG) | 🔲 Planned |

---

## Repository layout

```
open-hw-validation-harness/
├── rtl/
│   └── example_dut/
│       ├── reg8.v              <- Phase 2 DUT: 8-bit register
│       └── periph_ctrl.v       <- Phase 3 DUT: register-mapped peripheral
│
├── sim/
│   ├── cocotb/                 <- Phase 2: reg8 simulation
│   │   ├── Makefile
│   │   └── test_reg8.py
│   └── periph_ctrl/            <- Phase 3: periph_ctrl simulation
│       ├── Makefile
│       ├── reg_driver.py       <- reusable register read/write helper
│       └── test_periph_ctrl.py
│
├── scripts/
│   └── run_regression.py       <- runs all targets, parses results
│
├── docs/
│   ├── getting_started.md
│   └── architecture.md
│
├── artifacts/
│   ├── waves/                  <- VCD waveforms (all DUTs)
│   └── sim_build/              <- Verilator build artefacts (git-ignored)
│
├── requirements.txt
└── pyproject.toml
```

---

## Quick start

```bash
# Activate your venv (every new terminal session)
source ~/hwvenv/bin/activate

# Run Phase 3 simulation
cd sim/periph_ctrl
make

# Run all targets with a summary report
cd ../..
python scripts/run_regression.py

# Run one phase only
python scripts/run_regression.py --target p3

# View waveform
gtkwave artifacts/waves/dump.vcd
```

---

## periph_ctrl register map (Phase 3 DUT)

| Addr | Name       | Access | Reset | Description                     |
|------|------------|--------|-------|---------------------------------|
| 0x0  | REG_ID     | RO     | 0xAB  | Peripheral ID constant          |
| 0x1  | REG_GPIO   | RW     | 0x00  | GPIO output register            |
| 0x2  | REG_CTRL   | RW     | 0x00  | Control register                |
| 0x3  | REG_STATUS | RO     | —     | {6'b0, ctrl\_en, gpio\_nonzero} |
| 0x4+ | —          | —      | —     | Invalid — asserts addr\_err     |

---

## Software requirements

| Tool | Install |
|------|---------|
| Python 3.10+ | python.org |
| cocotb 2.x | `pip install cocotb` (inside venv) |
| Verilator 5.036+ | Build from source — see docs/getting_started.md |
| GNU Make | `sudo apt install make` |
| GTKWave (optional) | `sudo apt install gtkwave` |
