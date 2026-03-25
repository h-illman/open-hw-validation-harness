# Open Hardware Validation Harness

An open-source, simulation-first hardware validation harness for FPGA and board-level digital designs.

## Project goal
This project aims to build a reusable validation framework that can:
- run simulation-based regression tests on hardware designs
- apply stimuli and check responses automatically
- generate logs, waveforms, and reports
- support a future transition from simulation to real hardware targets

## Target
A board-agnostic validation framework for FPGA hardware such as the DE25-Standard Development and Education Kit.

## Current status
Phase 2 adds a basic cocotb-based simulation flow for validating simple RTL modules and viewing waveform output.

## Requirements
- Python 3.10+
- pip
- Icarus Verilog
- GNU Make
- GTKWave (optional, for viewing waveforms)

## Install
Clone the repo and set up a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
