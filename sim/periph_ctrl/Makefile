# sim/periph_ctrl/Makefile
#
# Drives the cocotb simulation for rtl/example_dut/periph_ctrl.v
# using Verilator.
#
# Usage:
#   make            -> compile + run all tests, produce waveform
#   make clean::    -> remove build artefacts
#   make waves      -> open waveform in GTKWave
#
# Structure mirrors sim/cocotb/Makefile (Phase 2) for consistency.
# Key difference: COCOTB_TEST_MODULES is used instead of the deprecated MODULE.

# ---------------------------------------------------------------------------
# Repo root (two levels up from this Makefile: sim/periph_ctrl/ → repo root)
# ---------------------------------------------------------------------------
REPO_ROOT := $(abspath $(CURDIR)/../..)

# ---------------------------------------------------------------------------
# Simulator settings
# ---------------------------------------------------------------------------
SIM           := verilator
TOPLEVEL_LANG := verilog
TOPLEVEL      := periph_ctrl

# Use the non-deprecated variable (avoids the MODULE warning from Phase 2)
COCOTB_TEST_MODULES := test_periph_ctrl

# ---------------------------------------------------------------------------
# HDL sources
# ---------------------------------------------------------------------------
VERILOG_SOURCES := $(REPO_ROOT)/rtl/example_dut/periph_ctrl.v

# ---------------------------------------------------------------------------
# Waveform and artefact paths
# ---------------------------------------------------------------------------
WAVES     := 1
WAVE_DIR  := $(REPO_ROOT)/artifacts/waves
SIM_BUILD := $(REPO_ROOT)/artifacts/sim_build/periph_ctrl

EXTRA_ARGS := --trace --trace-depth 5

COCOTB_RESULTS_FILE := $(REPO_ROOT)/artifacts/results_periph_ctrl.xml

# ---------------------------------------------------------------------------
# Include cocotb's built-in simulation rules
# ---------------------------------------------------------------------------
include $(shell cocotb-config --makefiles)/Makefile.sim

# ---------------------------------------------------------------------------
# Copy VCD waveform to artifacts/waves/
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
	if [ -z "$$VCD" ]; then \
	    echo "No waveform found. Run 'make' first."; exit 1; \
	fi; \
	gtkwave "$$VCD" &

# ---------------------------------------------------------------------------
# Clean (double-colon to avoid conflict with cocotb's clean:: target)
# ---------------------------------------------------------------------------
.PHONY: clean
clean::
	rm -rf $(SIM_BUILD)
	rm -f $(COCOTB_RESULTS_FILE)
	@echo "Build artefacts cleaned. Waveforms in $(WAVE_DIR) preserved."
