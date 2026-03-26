# Architecture

This document describes the structure of the validation harness as of Phase 3.

---

## Layer diagram

```
┌─────────────────────────────────────────────────────┐
│                   Test Layer                        │
│  sim/cocotb/test_reg8.py                            │
│  sim/periph_ctrl/test_periph_ctrl.py                │
│  (cocotb @cocotb.test() coroutines)                 │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                  Driver Layer                        │
│  sim/periph_ctrl/reg_driver.py  (Phase 3)           │
│  (encapsulates bus timing, reset sequencing)        │
│                                                     │
│  Phase 4: this layer will also contain a JTAG/      │
│  Avalon hardware backend driver with the same API   │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│               Simulation Backend                    │
│  Verilator (compiles Verilog → C++ → executable)   │
│  cocotb VPI bridge (Python ↔ simulator signals)    │
│                                                     │
│  Phase 4: real FPGA hardware replaces this layer   │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                   DUT Layer                         │
│  rtl/example_dut/reg8.v         (Phase 2)           │
│  rtl/example_dut/periph_ctrl.v  (Phase 3)           │
└─────────────────────────────────────────────────────┘
```

---

## Key design decisions

**Why separate sim/cocotb/ and sim/periph_ctrl/ directories?**
Each DUT gets its own simulation directory with its own Makefile. This keeps
the build system for each target self-contained. Adding a Phase 4 DUT means
adding `sim/new_dut/` without touching existing targets.

**Why a RegDriver class?**
It puts all timing knowledge in one place. The falling-edge drive / rising-edge
sample pattern is critical for correctness (see Phase 2 debugging) and would be
error-prone if repeated across every test. The class also marks the exact
boundary where simulation will be replaced by hardware access in Phase 4.

**Why synchronous registered outputs on periph_ctrl?**
`rd_data`, `rd_valid`, and `addr_err` are all registered (update on the clock
edge). This is how real bus peripherals work — it avoids combinational paths
on the output bus and makes timing closure easier on real FPGAs.

**Why is REG_STATUS computed rather than stored?**
Status registers in real peripherals are typically derived from internal state
rather than written by software. Computing it combinationally from reg_gpio
and reg_ctrl means it is always consistent with the actual hardware state.

---

## Artifact layout

```
artifacts/
├── waves/                  <- VCD waveforms from all simulation runs
│   └── dump.vcd            <- latest waveform (overwritten each run)
├── sim_build/
│   ├── reg8/               <- Verilator C++ build for reg8
│   └── periph_ctrl/        <- Verilator C++ build for periph_ctrl
├── results_reg8.xml         <- JUnit XML from Phase 2 run
└── results_periph_ctrl.xml  <- JUnit XML from Phase 3 run
```

---

## Future phases

**Phase 4** will add:
- A hardware backend in `backends/` implementing the same read/write API
  as `RegDriver`
- Quartus compilation integration
- JTAG or Avalon-based register access to a real FPGA board
- The test files in `sim/` will not need to change
