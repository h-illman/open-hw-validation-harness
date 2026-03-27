# projects/periph_ctrl/sim/Makefile
#
# Simulation Makefile for the periph_ctrl project.
# Drives Verilator + cocotb for projects/periph_ctrl/rtl/periph_ctrl.v.
#
# Usage:
#   make            -> compile + run all tests, produce waveform
#   make copy-waves -> copy VCD to artifacts/waves/
#   make clean::    -> remove build artefacts
#   make waves      -> open waveform in GTKWave

# ---------------------------------------------------------------------------
# Repo root: projects/periph_ctrl/sim/ -> up 3 levels
# ---------------------------------------------------------------------------
REPO_ROOT := $(abspath $(CURDIR)/../../..)

# ---------------------------------------------------------------------------
# Simulator settings
# ---------------------------------------------------------------------------
SIM                 := verilator
TOPLEVEL_LANG       := verilog
TOPLEVEL            := periph_ctrl
COCOTB_TEST_MODULES := test_periph_ctrl

# ---------------------------------------------------------------------------
# HDL sources
# ---------------------------------------------------------------------------
VERILOG_SOURCES := $(abspath $(CURDIR)/../rtl/periph_ctrl.v)

# ---------------------------------------------------------------------------
# Artifact paths
# ---------------------------------------------------------------------------
WAVES     := 1
WAVE_DIR  := $(REPO_ROOT)/artifacts/waves
SIM_BUILD := $(REPO_ROOT)/artifacts/sim_build/periph_ctrl

EXTRA_ARGS := --trace --trace-depth 5

COCOTB_RESULTS_FILE := $(REPO_ROOT)/artifacts/results_periph_ctrl.xml

# ---------------------------------------------------------------------------
# cocotb built-in rules
# ---------------------------------------------------------------------------
include $(shell cocotb-config --makefiles)/Makefile.sim

# ---------------------------------------------------------------------------
# Copy waveform
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
