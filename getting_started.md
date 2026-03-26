# Getting Started

This guide covers setup and running for all completed phases.

---

## Prerequisites

All the same tools from Phase 2 are still required. If you've already done
Phase 2 setup, skip straight to **Running Phase 3**.

| Tool | Install |
|------|---------|
| WSL2 + Ubuntu | Microsoft Store |
| Python 3.10+ | `sudo apt install python3` |
| python3-venv | `sudo apt install python3-venv python3-full` |
| Verilator 5.036+ | Build from source (see below) |
| GNU Make | `sudo apt install make` |
| GTKWave (optional) | `sudo apt install gtkwave` |

### Virtual environment (one-time)

```bash
python3 -m venv ~/hwvenv
source ~/hwvenv/bin/activate
pip install -r requirements.txt
```

Add to `~/.bashrc` to activate automatically:
```bash
echo 'source ~/hwvenv/bin/activate' >> ~/.bashrc
```

### Verilator 5.036 from source

```bash
sudo apt install -y git perl make autoconf g++ flex bison ccache help2man \
    libgoogle-perftools-dev numactl libfl2 libfl-dev zlib1g zlib1g-dev
git clone https://github.com/verilator/verilator
cd verilator && git checkout v5.036
autoconf && ./configure
make -j$(nproc)
sudo make install
cd .. && rm -rf verilator
verilator --version   # should print 5.036
```

---

## Running Phase 2 (reg8)

```bash
source ~/hwvenv/bin/activate
cd "/mnt/d/.../open-hw-validation-harness/sim/cocotb"
make
```

Expected: 4 tests PASS (reset, load, hold, reset_overrides_enable).

---

## Running Phase 3 (periph_ctrl)

```bash
source ~/hwvenv/bin/activate
cd "/mnt/d/.../open-hw-validation-harness/sim/periph_ctrl"
make
```

Expected: 7 tests PASS — see test list below.

---

## Phase 3 DUT: periph_ctrl

`periph_ctrl.v` is a simple register-mapped peripheral controller.
It is representative of real FPGA peripheral blocks: a small address-decoded
register file with RO, RW, and computed-status registers, a GPIO output,
and clean error signaling for out-of-range addresses.

### Register map

| Addr | Name       | Access | Reset | Description                     |
|------|------------|--------|-------|---------------------------------|
| 0x0  | REG_ID     | RO     | 0xAB  | Peripheral ID constant          |
| 0x1  | REG_GPIO   | RW     | 0x00  | GPIO output (drives gpio_out)   |
| 0x2  | REG_CTRL   | RW     | 0x00  | General control register        |
| 0x3  | REG_STATUS | RO     | —     | {6'b0, ctrl_en, gpio_nonzero}  |
| 0x4+ | —          | —      | —     | Invalid — addr_err pulses high  |

REG_STATUS is computed live from internal state (not stored).

### Ports

| Port | Dir | Width | Description |
|------|-----|-------|-------------|
| clk | in | 1 | Clock |
| rst_n | in | 1 | Active-low reset |
| addr | in | 3 | Register address |
| wr_en | in | 1 | Write enable (pulse) |
| rd_en | in | 1 | Read enable (pulse) |
| wr_data | in | 8 | Write data |
| rd_data | out | 8 | Read data (registered) |
| rd_valid | out | 1 | High for one cycle after valid read |
| addr_err | out | 1 | High for one cycle after invalid address |
| gpio_out | out | 8 | Live value of REG_GPIO |

---

## Phase 3 test list

| Test | What it validates |
|------|------------------|
| test_reset_defaults | All registers at correct reset values |
| test_write_readback | Write then read back RW registers |
| test_gpio_output | gpio_out tracks REG_GPIO |
| test_read_only_id | Writes to REG_ID are silently ignored |
| test_status_register | REG_STATUS reflects live ctrl_en and gpio_nonzero |
| test_invalid_address | addr_err pulses on addresses 0x4-0x7 |
| test_regression_sequence | Multi-step sequence covering all behaviors |

---

## RegDriver (reusable helper)

`sim/periph_ctrl/reg_driver.py` encapsulates the timing for every register
access so tests stay clean and readable.

```python
drv = RegDriver(dut)
drv.start_clock()
await drv.reset()

await drv.write(0x1, 0xFF)          # write 0xFF to REG_GPIO
data, valid, err = await drv.read(0x1)   # read it back
```

The driver handles the "drive on falling edge, sample on rising edge" pattern
internally. In Phase 4, this driver will be replaced or extended with a
hardware-backend adapter — the test code above it stays unchanged.

---

## Running the full regression

From the repo root:

```bash
python scripts/run_regression.py           # all targets
python scripts/run_regression.py -t p3    # Phase 3 only
python scripts/run_regression.py -v       # verbose (stream simulator output)
```

---

## Waveforms

After any `make` run, waveforms land in `artifacts/waves/`.

```bash
gtkwave artifacts/waves/dump.vcd
```

Signals to add in GTKWave: `clk`, `rst_n`, `addr`, `wr_en`, `rd_en`,
`wr_data`, `rd_data`, `rd_valid`, `addr_err`, `gpio_out`.

---

## What success looks like

✅ `make` in `sim/periph_ctrl/` exits with code 0  
✅ Terminal shows PASS for all 7 tests  
✅ `artifacts/results_periph_ctrl.xml` exists  
✅ `artifacts/waves/` contains a `.vcd` file  
✅ `python scripts/run_regression.py` prints `[REGRESSION PASSED]`  

---

## How Phase 3 connects to Phase 4

Phase 4 will add a hardware backend. The plan:

```
Phase 3 (now):          Phase 4 (future):
┌─────────────┐         ┌─────────────┐
│ Test code   │         │ Test code   │  ← same Python tests, unchanged
│ (Python)    │         │ (Python)    │
└──────┬──────┘         └──────┬──────┘
       │                       │
┌──────▼──────┐         ┌──────▼──────┐
│  RegDriver  │         │  RegDriver  │  ← thin abstraction layer
│ (cocotb/sim)│         │ (JTAG/HW)  │  ← swap this out for real HW
└──────┬──────┘         └──────┬──────┘
       │                       │
┌──────▼──────┐         ┌──────▼──────┐
│  Verilator  │         │  Real FPGA  │
│ simulation  │         │  on board   │
└─────────────┘         └─────────────┘
```

The `RegDriver` abstraction boundary is exactly where the simulation-to-hardware
transition will happen. The tests above it don't need to change.
