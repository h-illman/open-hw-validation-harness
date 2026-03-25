# sim/cocotb/Makefile
#
# Drives the cocotb simulation for rtl/example_dut/reg8.v using Verilator.
#
# Usage:
#   make            -> compile + run all tests, produce waveform
#   make clean      -> remove build artefacts (not waves)
#   make waves      -> open waveform in GTKWave (requires GTKWave installed)
#
# How this works:
#   cocotb ships a set of Makefiles that know how to link your Python tests
#   with a simulator.  We set the required variables and include their rules.
#   Verilator translates the Verilog to C++, compiles it, and runs the
#   simulation.  cocotb hooks into Verilator via the VPI/DPI interface.
#
# Variables:
#   SIM          - which simulator backend cocotb uses
#   TOPLEVEL_LANG - HDL language of the top module
#   TOPLEVEL     - name of the Verilog top module (must match module name)
#   MODULE       - Python test file (without .py extension)
#   VERILOG_SOURCES - path(s) to the HDL source(s)
#   WAVES        - set to 1 to enable VCD waveform dump
#   SIM_BUILD    - where Verilator build artefacts go
#   COCOTB_RESULTS_FILE - path for the JUnit-style XML results file

# ---------------------------------------------------------------------------
# Repo root (two levels up from this Makefile)
# ---------------------------------------------------------------------------
REPO_ROOT := $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/../..)

# ---------------------------------------------------------------------------
# Simulator settings
# ---------------------------------------------------------------------------
SIM           := verilator
TOPLEVEL_LANG := verilog
TOPLEVEL      := reg8
MODULE        := test_reg8

# ---------------------------------------------------------------------------
# HDL sources
# ---------------------------------------------------------------------------
VERILOG_SOURCES := $(REPO_ROOT)/rtl/example_dut/reg8.v

# ---------------------------------------------------------------------------
# Waveform and artefact paths
# ---------------------------------------------------------------------------
WAVES     := 1
WAVE_DIR  := $(REPO_ROOT)/artifacts/waves
SIM_BUILD := $(REPO_ROOT)/artifacts/sim_build/reg8

# Extra Verilator flags: generate VCD, trace depth
EXTRA_ARGS := --trace --trace-depth 5

# Where cocotb writes the JUnit XML results file
COCOTB_RESULTS_FILE := $(REPO_ROOT)/artifacts/results_reg8.xml

# ---------------------------------------------------------------------------
# Include cocotb's built-in Makefile rules
# (cocotb installs these; the path is resolved via cocotb-config)
# ---------------------------------------------------------------------------
include $(shell cocotb-config --makefiles)/Makefile.sim

# ---------------------------------------------------------------------------
# Post-run: copy the VCD into the waves directory
# ---------------------------------------------------------------------------
.PHONY: copy-waves
.PHONY: copy-waves
copy-waves:
	@mkdir -p $(WAVE_DIR)
	@if [ -f dump.vcd ]; then \
	    cp dump.vcd $(WAVE_DIR)/reg8_dump.vcd; \
	    echo "Waveform copied to $(WAVE_DIR)/reg8_dump.vcd"; \
	elif ls $(SIM_BUILD)/*.vcd 1>/dev/null 2>&1; then \
	    cp $(SIM_BUILD)/*.vcd $(WAVE_DIR)/; \
	    echo "Waveform copied from $(SIM_BUILD) to $(WAVE_DIR)/"; \
	else \
	    echo "No VCD file found in current directory or $(SIM_BUILD)"; \
	fi

# ---------------------------------------------------------------------------
# Open waveform in GTKWave (optional convenience target)
# ---------------------------------------------------------------------------
.PHONY: waves
waves:
	@VCD=$$(ls $(WAVE_DIR)/*.vcd 2>/dev/null | head -1); \
	if [ -z "$$VCD" ]; then \
	    echo "No waveform found. Run 'make' first."; \
	    exit 1; \
	fi; \
	echo "Opening $$VCD in GTKWave..."; \
	gtkwave "$$VCD" &

# ---------------------------------------------------------------------------
# Clean build artefacts (keep waves)
# ---------------------------------------------------------------------------
.PHONY: clean
clean::
	rm -rf $(SIM_BUILD)
	rm -f $(COCOTB_RESULTS_FILE)
	@echo "Build artefacts cleaned. Waveforms in $(WAVE_DIR) are preserved."
