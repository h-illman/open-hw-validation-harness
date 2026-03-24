# Architecture

## Framework Concept
The Open Hardware Validation Harness is designed to be an abstraction engine for digital hardware validation. 

The core idea is the **backend abstraction**. By defining abstract interfaces for connecting to, resetting, and driving a Device Under Test (DUT), we can use the *exact same tests* and *exact same drivers* whether the backend is a software timing or open-source simulator (Simulation Backend) or a physical hardware device like an FPGA via PCIe or UART (Hardware Backend).

## Phase 1 vs Future Phases
Currently (Phase 1), we are only establishing the repository scaffold and foundational Python environment. We will introduce the **Simulation Backend** in future phases (e.g. using Verilator and cocotb) before eventually supporting a **Hardware Backend**.

## Structural Separation
The framework ensures a clean separation of concerns:
- **RTL (`rtl/`)**: Contains the hardware descriptions (Verilog/SystemVerilog/VHDL) representing the Device Under Test.
- **Infrastructure (`tb/`)**: The validation infrastructure, consisting of drivers, utilities, backend definitions, and configuration parsers.
- **Tests (`tests/`)**: High-level test scenarios written in Python, interacting only with the generic interfaces provided by `tb/` rather than specific simulation features.
- **Artifacts (`artifacts/`)**: Ephemeral outputs like simulation waves (VCD/FST), test reports, and logs. This directory is omitted from source control.
