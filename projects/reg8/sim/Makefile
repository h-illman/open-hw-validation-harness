# projects/reg8/sim/Makefile
#
# Simulation Makefile for the reg8 project.
# Drives Verilator + cocotb for projects/reg8/rtl/reg8.v.
#
# Usage:
#   make            -> compile + run all tests, produce waveform
#   make copy-waves -> copy VCD to artifacts/waves/
#   make clean::    -> remove build artefacts
#   make waves      -> open waveform in GTKWave

# ---------------------------------------------------------------------------
# Repo root: projects/reg8/sim/ -> up 3 levels
# ---------------------------------------------------------------------------
REPO_ROOT := $(abspath $(CURDIR)/../../..)

# ---------------------------------------------------------------------------
# Simulator settings
# ---------------------------------------------------------------------------
SIM                 := verilator
TOPLEVEL_LANG       := verilog
TOPLEVEL            := reg8
COCOTB_TEST_MODULES := test_reg8

# ---------------------------------------------------------------------------
# HDL sources (relative to this project's rtl/ directory)
# ---------------------------------------------------------------------------
VERILOG_SOURCES := $(abspath $(CURDIR)/../rtl/reg8.v)

# ---------------------------------------------------------------------------
# Artifact paths
# ---------------------------------------------------------------------------
WAVES     := 1
WAVE_DIR  := $(REPO_ROOT)/artifacts/waves
SIM_BUILD := $(REPO_ROOT)/artifacts/sim_build/reg8

EXTRA_ARGS := --trace --trace-depth 5

COCOTB_RESULTS_FILE := $(REPO_ROOT)/artifacts/results_reg8.xml

# ---------------------------------------------------------------------------
# cocotb built-in rules
# ---------------------------------------------------------------------------
include $(shell cocotb-config --makefiles)/Makefile.sim

# ---------------------------------------------------------------------------
# Copy waveform (VCD is written to CURDIR at runtime)
# ---------------------------------------------------------------------------
.PHONY: copy-waves
copy-waves:
	@mkdir -p $(WAVE_DIR)
	@if ls $(CURDIR)/*.vcd 1>/dev/null 2>&1; then \
	    cp $(CURDIR)/*.vcd $(WAVE_DIR)/; \
	    echo "Waveform copied to $(WAVE_DIR)/"; \
	else \
	    echo "No VCD file found in $(CURDIR)"; \
	fi

# ---------------------------------------------------------------------------
# Open waveform in GTKWave
# ---------------------------------------------------------------------------
.PHONY: waves
waves:
	@VCD=$$(ls $(WAVE_DIR)/*.vcd 2>/dev/null | head -1); \
	if [ -z "$$VCD" ]; then echo "No waveform. Run 'make' first."; exit 1; fi; \
	gtkwave "$$VCD" &

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------
.PHONY: clean
clean::
	rm -rf $(SIM_BUILD)
	rm -f $(COCOTB_RESULTS_FILE)
	rm -f $(CURDIR)/*.vcd
	@echo "Cleaned."
