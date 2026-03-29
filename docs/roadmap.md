# Project Roadmap

The development of the Open Hardware Validation Harness is broken into 6 phases.

## 1. Project scaffold and toolchain  ✅
Setup of the basic repository structure, Python environments, and foundational
documentation.  Establishes conventions before complex logic is added.

## 2. Simulation bring-up  ✅
Integration of Verilator and cocotb.  Implements the simulation backend and
enables initial HDL testing with an 8-bit register DUT (reg8).

## 3. MVP validation target  ✅
Development of a more realistic DUT (periph_ctrl — a register-mapped peripheral
controller) and standard verification components.  Real tests execute against
the simulated target and produce waveforms and JUnit XML results.

## 4. Framework polish and reuse  ✅
Refines the project manifest system, auto-discovery, result parsing, and
tool-checking into a clean `framework/` package.  Makes adding a new project
a 10-minute task with no framework changes required.

## 5. Target-aware board readiness checks  ✅
Adds a modular `framework/boards/` layer.  Users can declare a target board
in `project.yaml` or via `--target` on the CLI.  The framework runs pre-lab
readiness checks (clock compatibility, I/O standards, resource estimates,
structural checks) and produces a readiness report.  Initial supported boards:
DE10-Standard and DE0-CV.  Architecture is designed for easy expansion.

## 6. Real hardware validation backend  🔲 Planned
Adds a hardware execution backend.  After simulation passes and target checks
pass, the framework will be able to dispatch to real FPGA hardware via a
selected backend (JTAG, UART, etc.).  The `BoardProfile` class already has
the correct extension points for this.  The `--target` flag and readiness
report from Phase 5 feed naturally into a Phase 6 `--backend hw` dispatch step.
