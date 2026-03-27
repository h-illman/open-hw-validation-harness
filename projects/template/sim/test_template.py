# projects/template/sim/test_template.py
#
# Template cocotb test file.
# Rename this to test_<your_module>.py and fill in your test logic.
#
# Quick cocotb reference:
#   dut.<port_name>.value = x    -> drive a signal
#   int(dut.<port_name>.value)   -> read a signal
#   await RisingEdge(dut.clk)    -> wait for the next rising clock edge
#   await FallingEdge(dut.clk)   -> wait for the next falling clock edge
#   await ClockCycles(dut.clk,n) -> wait for n complete clock cycles
#   assert <condition>, "message" -> fail the test if condition is False

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles


# ---------------------------------------------------------------------------
# Helper: start a clock (call once at the top of each test)
# ---------------------------------------------------------------------------
def start_clock(dut, period_ns=10):
    return cocotb.start_soon(Clock(dut.clk, period_ns, unit="ns").start())


# ---------------------------------------------------------------------------
# Helper: apply reset (customize signal names to match your DUT)
# ---------------------------------------------------------------------------
async def apply_reset(dut, cycles=3):
    dut.rst_n.value = 0           # assert active-low reset
    await ClockCycles(dut.clk, cycles)
    await FallingEdge(dut.clk)    # return on falling edge (safe to drive after)
    dut.rst_n.value = 1           # release reset


# ---------------------------------------------------------------------------
# Test 1: Reset / default values
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_reset(dut):
    """Verify that all outputs are at their expected reset values."""
    clk_task = start_clock(dut)
    await apply_reset(dut)

    # TODO: replace with your DUT's reset expectations
    # Example:
    #   assert int(dut.q.value) == 0, f"Expected 0, got {int(dut.q.value)}"

    dut._log.info("test_reset PASSED")
    clk_task.cancel()


# ---------------------------------------------------------------------------
# Test 2: Basic functional test
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_basic_function(dut):
    """Verify basic DUT behavior."""
    clk_task = start_clock(dut)
    await apply_reset(dut)

    # TODO: drive inputs and check outputs
    # Example:
    #   dut.en.value = 1
    #   dut.d.value  = 0xAB
    #   await RisingEdge(dut.clk)
    #   assert int(dut.q.value) == 0xAB

    dut._log.info("test_basic_function PASSED")
    clk_task.cancel()
