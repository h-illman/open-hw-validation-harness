# projects/template/sim/Makefile
#
# Template simulation Makefile.
# Copy this into your own project's sim/ directory.
# Update the three variables marked with <-- EDIT THIS.

# ---------------------------------------------------------------------------
# Repo root (do not change — this works for any project under projects/)
# ---------------------------------------------------------------------------
REPO_ROOT := $(abspath $(CURDIR)/../../..)

# ---------------------------------------------------------------------------
# <-- EDIT THIS: set these three variables for your project
# ---------------------------------------------------------------------------
TOPLEVEL            := your_top_module        # Verilog module name
COCOTB_TEST_MODULES := test_your_module       # Python test file (no .py)
VERILOG_SOURCES     := $(abspath $(CURDIR)/../rtl/your_top_module.v)

# ---------------------------------------------------------------------------
# Simulator settings (no changes needed for Verilator)
# ---------------------------------------------------------------------------
SIM           := verilator
TOPLEVEL_LANG := verilog

# ---------------------------------------------------------------------------
# Artifact paths (update results XML name to match your project)
# ---------------------------------------------------------------------------
WAVES     := 1
WAVE_DIR  := $(REPO_ROOT)/artifacts/waves
SIM_BUILD := $(REPO_ROOT)/artifacts/sim_build/$(TOPLEVEL)

EXTRA_ARGS := --trace --trace-depth 5

# <-- EDIT THIS: rename results XML to match your project name
COCOTB_RESULTS_FILE := $(REPO_ROOT)/artifacts/results_$(TOPLEVEL).xml

# ---------------------------------------------------------------------------
# cocotb built-in rules (do not change)
# ---------------------------------------------------------------------------
include $(shell cocotb-config --makefiles)/Makefile.sim

# ---------------------------------------------------------------------------
# Copy waveform to artifacts/waves/ after simulation
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

.PHONY: waves
waves:
	@VCD=$$(ls $(WAVE_DIR)/*.vcd 2>/dev/null | head -1); \
	if [ -z "$$VCD" ]; then echo "No waveform. Run 'make' first."; exit 1; fi; \
	gtkwave "$$VCD" &

.PHONY: clean
clean::
	rm -rf $(SIM_BUILD)
	rm -f $(COCOTB_RESULTS_FILE)
	rm -f $(CURDIR)/*.vcd
	@echo "Cleaned."
