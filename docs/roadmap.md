# Project Roadmap

The development of the Open Hardware Validation Harness is broken down into 5 phases:

## 1. Project scaffold and toolchain
Setup of the basic repository structure, Python environments, and foundational documentation. This establishes conventions before complex logic is added.

## 2. Simulation bring-up
Integration of open-source simulation tools (e.g. Verilator, cocotb). This stage implements the Simulation Backend and enables initial HDL testing.

## 3. MVP validation target
Development of a minimal Device Under Test (DUT) and standard verification components. Real tests will be executed against the simulated target.

## 4. Framework polish and reuse
Refining APIs, standardizing the logging/reporting flows, and ensuring the architecture successfully abstracts the underlying complexities to make test writing effortless.

## 5. Hardware-ready transition
Implementation of the Hardware Backend (e.g., PCIe, UART, JTAG wrappers). At this point, the framework will be able to target both full simulation and physical FPGA/board-level hardware using the same top-level test sequences.
