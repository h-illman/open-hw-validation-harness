# Adding Your Own Project

This guide explains how to bring your own RTL design into the validation
framework.  The whole process takes about 10 minutes for a simple DUT.

---

## How the framework is structured

Every DUT lives in its own self-contained folder under `projects/`:

```
projects/
  your_project/
    rtl/              <- your Verilog/SystemVerilog source files
    sim/
      Makefile        <- drives Verilator + cocotb
      test_<dut>.py   <- your cocotb tests
    project.yaml      <- manifest: tells the runner what this project is
```

The runner (`scripts/run_regression.py`) automatically discovers any folder
under `projects/` that contains a `project.yaml`.  You never have to register
your project anywhere — just drop it in and run.

---

## Step-by-step

### Step 1 — Copy the template

```bash
cp -r projects/template projects/my_design
```

You now have a working skeleton.  All further changes happen inside
`projects/my_design/`.

---

### Step 2 — Add your RTL

Put your Verilog or SystemVerilog source files in `projects/my_design/rtl/`.

```
projects/my_design/
  rtl/
    my_top_module.v       <- your design
    submodule_a.v         <- any sub-modules it instantiates
```

Keep all synthesizable RTL here.  Test bench code goes in `sim/`.

---

### Step 3 — Edit project.yaml

Open `projects/my_design/project.yaml` and fill in the fields:

```yaml
name: my_design                          # must match the folder name
description: "What this design does"
version: "0.1.0"

dut:
  top_module: my_top_module              # Verilog module name (exact match)
  sources:
    - rtl/my_top_module.v               # all source files needed to compile
    - rtl/submodule_a.v

sim:
  tool: verilator
  test_module: test_my_design           # your test file name (no .py)
  timeout_ns: 10000

artifacts:
  results_xml: artifacts/results_my_design.xml
  waves_dir:   artifacts/waves/
```

---

### Step 4 — Edit the Makefile

Open `projects/my_design/sim/Makefile` and update the three marked variables:

```makefile
TOPLEVEL            := my_top_module       # must match DUT module name
COCOTB_TEST_MODULES := test_my_design      # your test file (no .py)
VERILOG_SOURCES     := $(abspath $(CURDIR)/../rtl/my_top_module.v)
```

If your design has multiple source files, list them all in `VERILOG_SOURCES`:

```makefile
VERILOG_SOURCES := \
    $(abspath $(CURDIR)/../rtl/my_top_module.v) \
    $(abspath $(CURDIR)/../rtl/submodule_a.v)
```

Also update the results XML name:

```makefile
COCOTB_RESULTS_FILE := $(REPO_ROOT)/artifacts/results_my_design.xml
```

---

### Step 5 — Write your tests

Rename `sim/test_template.py` to `sim/test_my_design.py` and write your
cocotb tests.  The template file has comments explaining the basic patterns.

A minimal test looks like this:

```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

@cocotb.test()
async def test_reset(dut):
    clk = cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    await RisingEdge(dut.clk)
    assert int(dut.q.value) == 0, f"Expected 0, got {int(dut.q.value)}"

    clk.cancel()
```

See `projects/periph_ctrl/sim/test_periph_ctrl.py` for a more complete
example, including a reusable driver class.

---

### Step 6 — Run your simulation

```bash
# From inside WSL/Linux, with your venv active:
source ~/hwvenv/bin/activate

# Run just your project
cd projects/my_design/sim
make

# Or use the runner from the repo root
cd /path/to/open-hw-validation-harness
python scripts/run_regression.py --project my_design
```

---

### Step 7 — Check results and waveform

```bash
# Runner summary from repo root
python scripts/run_regression.py --project my_design

# Open waveform
gtkwave artifacts/waves/dump.vcd
```

---

## Tips

**Clock period:** The template uses 10 ns (100 MHz). Change the period in
`Clock(dut.clk, 10, unit="ns")` to match your design's clock.

**Reset polarity:** If your design uses active-high reset, change
`dut.rst_n.value = 0` → `dut.rst_en.value = 1` and invert accordingly.

**Multiple source files:** List every `.v` or `.sv` file that Verilator needs
to compile your design in both `VERILOG_SOURCES` (Makefile) and `sources:`
(project.yaml).

**Timing rule:** Always drive signals on a `FallingEdge` and sample registered
outputs after a `FallingEdge` that follows a `RisingEdge`. See Phase 2/3
debugging notes in `docs/getting_started.md` for a full explanation.

**Reusable driver:** If your DUT has a bus or register interface, consider
writing a small driver class like `projects/periph_ctrl/sim/reg_driver.py`.
It keeps test logic clean and marks the boundary where a future hardware
backend would plug in.

---

## What the runner discovers

```bash
python scripts/run_regression.py --list
```

Lists every project the runner found.  If your project doesn't appear, check
that `projects/my_design/project.yaml` exists and has a valid `name:` field.
