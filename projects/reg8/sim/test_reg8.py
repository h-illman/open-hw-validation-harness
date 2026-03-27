import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, ReadOnly, Timer


def start_clock(dut):
    return cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())


async def sample_after_rising(dut):
    """Wait for a rising edge, then sample after signal updates settle."""
    await RisingEdge(dut.clk)
    await ReadOnly()


async def apply_reset(dut, cycles: int = 3):
    """
    Hold synchronous active-low reset for a few cycles.
    Return in a normal writable phase so the caller can safely drive signals.
    """
    dut.rst_n.value = 0
    dut.en.value = 0
    dut.d.value = 0

    await ClockCycles(dut.clk, cycles)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    # Step out of the current scheduling phase so caller can drive inputs safely
    await Timer(1, unit="ps")


@cocotb.test()
async def test_reset(dut):
    clk_task = start_clock(dut)
    await apply_reset(dut)

    dut.en.value = 1
    dut.d.value = 0xAB
    await sample_after_rising(dut)

    result = int(dut.q.value)
    assert result == 0xAB, (
        f"Pre-reset load failed: expected 0xAB, got 0x{result:02X}"
    )

    await FallingEdge(dut.clk)
    dut.rst_n.value = 0
    await sample_after_rising(dut)

    result = int(dut.q.value)
    assert result == 0x00, (
        f"Reset failed: expected 0x00, got 0x{result:02X}"
    )

    dut._log.info("test_reset PASSED")
    clk_task.cancel()


@cocotb.test()
async def test_load(dut):
    clk_task = start_clock(dut)
    await apply_reset(dut)

    test_vectors = [0x01, 0x7F, 0x80, 0xFF, 0xA5, 0x5A, 0x00]

    dut.en.value = 1
    for val in test_vectors:
        dut.d.value = val
        await sample_after_rising(dut)

        result = int(dut.q.value)
        assert result == val, (
            f"Load failed: drove d=0x{val:02X}, got q=0x{result:02X}"
        )

        await FallingEdge(dut.clk)

    dut._log.info("test_load PASSED")
    clk_task.cancel()


@cocotb.test()
async def test_hold(dut):
    clk_task = start_clock(dut)
    await apply_reset(dut)

    dut.en.value = 1
    dut.d.value = 0x42
    await sample_after_rising(dut)

    result = int(dut.q.value)
    assert result == 0x42, (
        f"Initial load failed: expected 0x42, got 0x{result:02X}"
    )

    await FallingEdge(dut.clk)
    dut.en.value = 0

    for new_d in [0x00, 0xFF, 0x11, 0x99]:
        dut.d.value = new_d
        await sample_after_rising(dut)

        result = int(dut.q.value)
        assert result == 0x42, (
            f"Hold failed: q=0x{result:02X} changed when en=0, d=0x{new_d:02X}"
        )

        await FallingEdge(dut.clk)

    dut._log.info("test_hold PASSED")
    clk_task.cancel()


@cocotb.test()
async def test_reset_overrides_enable(dut):
    clk_task = start_clock(dut)
    await apply_reset(dut)

    await FallingEdge(dut.clk)
    dut.rst_n.value = 0
    dut.en.value = 1
    dut.d.value = 0xFF
    await sample_after_rising(dut)

    result = int(dut.q.value)
    assert result == 0x00, (
        f"Reset-over-enable failed: expected 0x00, got 0x{result:02X}"
    )

    dut._log.info("test_reset_overrides_enable PASSED")
    clk_task.cancel()