# sim/periph_ctrl/reg_driver.py
#
# RegDriver: a lightweight cocotb helper for the periph_ctrl register bus.
#
# Why this exists:
#   Every test needs to do the same timing dance: drive signals on the falling
#   edge (setup time), then await the rising edge (capture), then read outputs.
#   Putting that logic in one place keeps the tests clean and readable.
#
# How it maps to real hardware:
#   In a real system this driver would be replaced by:
#   - a JTAG/Avalon read-write backend (Phase 4)
#   - or a software register access layer
#   The test code above this driver stays the same either way.
#
# Usage:
#   driver = RegDriver(dut)
#   await driver.reset()
#   await driver.write(0x1, 0xFF)
#   data, valid = await driver.read(0x1)

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
import cocotb


class RegDriver:
    """
    Encapsulates clock generation, reset sequencing, and register
    read/write timing for the periph_ctrl DUT.
    """

    CLK_PERIOD_NS = 10  # 100 MHz

    def __init__(self, dut):
        self.dut = dut
        self._clk_task = None

    # -----------------------------------------------------------------------
    # Clock
    # -----------------------------------------------------------------------
    def start_clock(self):
        """Start the clock. Call once at the top of each test."""
        self._clk_task = cocotb.start_soon(
            Clock(self.dut.clk, self.CLK_PERIOD_NS, unit="ns").start()
        )

    def stop_clock(self):
        """Cancel the clock at the end of each test."""
        if self._clk_task:
            self._clk_task.cancel()
            self._clk_task = None

    # -----------------------------------------------------------------------
    # Reset
    # -----------------------------------------------------------------------
    async def reset(self, cycles: int = 3):
        """
        Assert active-low reset for `cycles` clock cycles, then release.
        Idles all bus signals during reset.
        Returns on the FallingEdge that follows reset release, so callers
        are safely between clock edges before they start driving signals.
        """
        dut = self.dut
        dut.rst_n.value  = 0
        dut.wr_en.value  = 0
        dut.rd_en.value  = 0
        dut.wr_data.value = 0
        dut.addr.value   = 0

        await ClockCycles(dut.clk, cycles)
        await FallingEdge(dut.clk)   # step to falling edge mid-cycle
        dut.rst_n.value = 1          # release reset with half-period setup time
        # Caller resumes on a FallingEdge — next RisingEdge is always a future event

    # -----------------------------------------------------------------------
    # Write
    # -----------------------------------------------------------------------
    async def write(self, addr: int, data: int):
        """
        Write `data` to register `addr`.
        Drives the bus on the FallingEdge (setup), captures on the RisingEdge.
        Steps to the next FallingEdge before returning so callers are always
        safely between edges and registered outputs (like addr_err) have settled.
        """
        dut = self.dut
        dut.addr.value    = addr
        dut.wr_data.value = data
        dut.wr_en.value   = 1
        dut.rd_en.value   = 0

        await RisingEdge(dut.clk)   # DUT latches write on this edge
        await FallingEdge(dut.clk)  # outputs settled; return here

        dut.wr_en.value = 0

    # -----------------------------------------------------------------------
    # Read
    # -----------------------------------------------------------------------
    async def read(self, addr: int) -> tuple[int, int, int]:
        """
        Read from register `addr`.
        Returns (rd_data, rd_valid, addr_err) as integers.

        Timing:
          We are called on a FallingEdge (from reset() or a previous op).
          Drive rd_en=1 here → half-period of stable setup time before the edge.
          await RisingEdge → DUT latches rd_en and updates registered outputs.
          await FallingEdge → outputs are fully settled; safe to sample.
          De-assert rd_en and return on FallingEdge for the next operation.

        Why sample on FallingEdge, not immediately after RisingEdge?
          rd_data, rd_valid, and addr_err are registered — they change ON the
          rising edge.  Cocotb wakes up from RisingEdge inside the same
          evaluation step, so Verilator may not have propagated the new register
          values yet.  Stepping to the FallingEdge guarantees we read settled,
          post-evaluation values.  This is the same fix used to resolve the
          Phase 2 timing bug.
        """
        dut = self.dut
        dut.addr.value    = addr
        dut.rd_en.value   = 1
        dut.wr_en.value   = 0
        dut.wr_data.value = 0

        await RisingEdge(dut.clk)   # DUT latches rd_en on this edge
        await FallingEdge(dut.clk)  # outputs are settled — safe to sample now

        data  = int(dut.rd_data.value)
        valid = int(dut.rd_valid.value)
        err   = int(dut.addr_err.value)

        dut.rd_en.value = 0
        # Return on FallingEdge — caller is safely between edges

        return data, valid, err

    # -----------------------------------------------------------------------
    # Convenience: idle one full cycle
    # -----------------------------------------------------------------------
    async def idle(self, cycles: int = 1):
        """Hold the bus idle for `cycles` clock cycles."""
        self.dut.wr_en.value = 0
        self.dut.rd_en.value = 0
        await ClockCycles(self.dut.clk, cycles)
        await FallingEdge(self.dut.clk)
