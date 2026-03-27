# sim/periph_ctrl/test_periph_ctrl.py
#
# cocotb test suite for rtl/example_dut/periph_ctrl.v
#
# Register map under test:
#   0x0  REG_ID     [RO] = 0xAB
#   0x1  REG_GPIO   [RW] = 0x00 on reset  →  drives gpio_out[7:0]
#   0x2  REG_CTRL   [RW] = 0x00 on reset
#   0x3  REG_STATUS [RO] = {6'b0, ctrl_en, gpio_nonzero}
#   0x4+ invalid    →  addr_err=1
#
# Test list:
#   test_reset_defaults          - all registers at reset values
#   test_write_readback          - write then read back RW registers
#   test_gpio_output             - gpio_out reflects REG_GPIO
#   test_read_only_id            - writes to REG_ID are silently ignored
#   test_status_register         - REG_STATUS reflects live register state
#   test_invalid_address         - addr_err on out-of-range address
#   test_regression_sequence     - multi-step sequence covering all behaviors

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge
from reg_driver import RegDriver

# Register address constants (matches periph_ctrl.v localparams)
ADDR_ID     = 0x0
ADDR_GPIO   = 0x1
ADDR_CTRL   = 0x2
ADDR_STATUS = 0x3
ADDR_INVALID = 0x5   # anything 4-7 is invalid

PERIPHERAL_ID = 0xAB


# ---------------------------------------------------------------------------
# Test 1: Reset / default values
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_reset_defaults(dut):
    """
    After reset:
      REG_ID     should read 0xAB
      REG_GPIO   should read 0x00
      REG_CTRL   should read 0x00
      REG_STATUS should read 0x00 (gpio_nonzero=0, ctrl_en=0)
      gpio_out   should be 0x00
    """
    drv = RegDriver(dut)
    drv.start_clock()
    await drv.reset()

    for addr, expected, name in [
        (ADDR_ID,     PERIPHERAL_ID, "REG_ID"),
        (ADDR_GPIO,   0x00,          "REG_GPIO"),
        (ADDR_CTRL,   0x00,          "REG_CTRL"),
        (ADDR_STATUS, 0x00,          "REG_STATUS"),
    ]:
        data, valid, err = await drv.read(addr)
        assert valid == 1, f"{name}: rd_valid not set"
        assert err   == 0, f"{name}: unexpected addr_err"
        assert data == expected, \
            f"{name} reset default wrong: expected 0x{expected:02X}, got 0x{data:02X}"

    assert int(dut.gpio_out.value) == 0x00, \
        f"gpio_out after reset: expected 0x00, got 0x{int(dut.gpio_out.value):02X}"

    dut._log.info("test_reset_defaults PASSED")
    drv.stop_clock()


# ---------------------------------------------------------------------------
# Test 2: Write / readback of RW registers
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_write_readback(dut):
    """
    Write distinct values to REG_GPIO and REG_CTRL, then read them back.
    Verifies that write data is actually stored and returned correctly.
    """
    drv = RegDriver(dut)
    drv.start_clock()
    await drv.reset()

    test_cases = [
        (ADDR_GPIO, 0x55, "REG_GPIO"),
        (ADDR_GPIO, 0xFF, "REG_GPIO"),
        (ADDR_GPIO, 0x00, "REG_GPIO"),
        (ADDR_CTRL, 0x01, "REG_CTRL"),
        (ADDR_CTRL, 0xA5, "REG_CTRL"),
        (ADDR_CTRL, 0x00, "REG_CTRL"),
    ]

    for addr, wr_val, name in test_cases:
        await drv.write(addr, wr_val)
        data, valid, err = await drv.read(addr)
        assert valid == 1, f"{name}: rd_valid not set after write"
        assert err   == 0, f"{name}: unexpected addr_err"
        assert data == wr_val, \
            f"{name} readback failed: wrote 0x{wr_val:02X}, got 0x{data:02X}"

    dut._log.info("test_write_readback PASSED")
    drv.stop_clock()


# ---------------------------------------------------------------------------
# Test 3: GPIO output register drives gpio_out
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_gpio_output(dut):
    """
    Write values to REG_GPIO and verify gpio_out reflects them immediately
    (gpio_out is a continuous assign from the register, no extra latency).
    """
    drv = RegDriver(dut)
    drv.start_clock()
    await drv.reset()

    gpio_vectors = [0x01, 0x80, 0xFF, 0xA5, 0x5A, 0x00]

    for val in gpio_vectors:
        await drv.write(ADDR_GPIO, val)
        gpio = int(dut.gpio_out.value)
        assert gpio == val, \
            f"gpio_out mismatch: wrote 0x{val:02X}, gpio_out=0x{gpio:02X}"

    dut._log.info("test_gpio_output PASSED")
    drv.stop_clock()


# ---------------------------------------------------------------------------
# Test 4: REG_ID is read-only (writes silently ignored)
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_read_only_id(dut):
    """
    Attempt to write to REG_ID (a read-only register).
    The write should be silently ignored — REG_ID must still return 0xAB.
    This tests that RO protection is working in the address decode logic.
    """
    drv = RegDriver(dut)
    drv.start_clock()
    await drv.reset()

    # Attempt to overwrite the ID register with a junk value
    await drv.write(ADDR_ID, 0x00)

    # REG_ID must still return the original constant
    data, valid, err = await drv.read(ADDR_ID)
    assert valid == 1, "REG_ID: rd_valid not set"
    assert err   == 0, "REG_ID: unexpected addr_err"
    assert data == PERIPHERAL_ID, \
        f"REG_ID was overwritten! expected 0x{PERIPHERAL_ID:02X}, got 0x{data:02X}"

    dut._log.info("test_read_only_id PASSED")
    drv.stop_clock()


# ---------------------------------------------------------------------------
# Test 5: REG_STATUS reflects live register state
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_status_register(dut):
    """
    REG_STATUS = {6'b0, ctrl_en, gpio_nonzero}
      ctrl_en      = REG_CTRL[0]
      gpio_nonzero = (REG_GPIO != 0)

    Verify STATUS updates correctly as GPIO and CTRL change.
    """
    drv = RegDriver(dut)
    drv.start_clock()
    await drv.reset()

    async def check_status(expected, label):
        data, valid, err = await drv.read(ADDR_STATUS)
        assert valid == 1, f"{label}: rd_valid not set"
        assert data == expected, \
            f"{label}: REG_STATUS expected 0x{expected:02X}, got 0x{data:02X}"

    # After reset: both bits 0
    await check_status(0x00, "after reset")

    # Set GPIO to non-zero → gpio_nonzero bit should be 1
    await drv.write(ADDR_GPIO, 0x01)
    await check_status(0x01, "after GPIO=0x01")

    # Set CTRL bit 0 → ctrl_en should be 1
    await drv.write(ADDR_CTRL, 0x01)
    await check_status(0x03, "after GPIO=0x01 CTRL=0x01")

    # Clear CTRL bit 0 → ctrl_en back to 0
    await drv.write(ADDR_CTRL, 0x00)
    await check_status(0x01, "after CTRL=0x00")

    # Clear GPIO → both bits back to 0
    await drv.write(ADDR_GPIO, 0x00)
    await check_status(0x00, "after GPIO=0x00")

    dut._log.info("test_status_register PASSED")
    drv.stop_clock()


# ---------------------------------------------------------------------------
# Test 6: Invalid address → addr_err asserted
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_invalid_address(dut):
    """
    Accesses to addresses 0x4-0x7 are invalid.
    addr_err should pulse high for exactly one cycle.
    rd_valid must NOT be set on an invalid access.
    """
    drv = RegDriver(dut)
    drv.start_clock()
    await drv.reset()

    invalid_addrs = [0x4, 0x5, 0x6, 0x7]

    for bad_addr in invalid_addrs:
        # Invalid read
        data, valid, err = await drv.read(bad_addr)
        assert err   == 1, f"addr=0x{bad_addr:X}: addr_err expected 1, got {err}"
        assert valid == 0, f"addr=0x{bad_addr:X}: rd_valid should be 0 on error"

        # Invalid write (wr_en with bad address)
        dut.addr.value    = bad_addr
        dut.wr_data.value = 0xFF
        dut.wr_en.value   = 1
        dut.rd_en.value   = 0
        await RisingEdge(dut.clk)   # DUT latches, addr_err registered here
        await FallingEdge(dut.clk)  # outputs settled — safe to sample
        dut.wr_en.value = 0
        err = int(dut.addr_err.value)
        assert err == 1, \
            f"addr=0x{bad_addr:X}: addr_err expected 1 on invalid write, got {err}"

    dut._log.info("test_invalid_address PASSED")
    drv.stop_clock()


# ---------------------------------------------------------------------------
# Test 7: Regression sequence
# ---------------------------------------------------------------------------
@cocotb.test()
async def test_regression_sequence(dut):
    """
    A realistic multi-step validation sequence that exercises all behaviors
    in a natural order — the kind of sequence a real validation engineer
    would run against a new peripheral block.

    Steps:
      1. Confirm ID register after reset
      2. Write and verify GPIO outputs
      3. Write CTRL and verify STATUS changes
      4. Confirm RO protection on ID and STATUS
      5. Run several back-to-back writes then reads
      6. Test invalid address in the middle of a sequence
      7. Confirm peripheral recovers cleanly after the error
    """
    drv = RegDriver(dut)
    drv.start_clock()
    await drv.reset()

    # 1. ID check
    data, valid, _ = await drv.read(ADDR_ID)
    assert data == PERIPHERAL_ID, f"Step 1: ID={hex(data)}"

    # 2. GPIO walk — each bit individually
    for bit in range(8):
        val = 1 << bit
        await drv.write(ADDR_GPIO, val)
        gpio = int(dut.gpio_out.value)
        assert gpio == val, f"Step 2: GPIO bit {bit} failed"

    # 3. CTRL → STATUS interaction
    await drv.write(ADDR_CTRL, 0x01)
    await drv.write(ADDR_GPIO, 0xF0)
    data, _, _ = await drv.read(ADDR_STATUS)
    assert data == 0x03, f"Step 3: STATUS expected 0x03, got 0x{data:02X}"

    # 4. RO protection: try to corrupt ID, read it back
    await drv.write(ADDR_ID,     0xDE)
    await drv.write(ADDR_STATUS, 0xAD)  # STATUS is also RO
    data_id, _, _ = await drv.read(ADDR_ID)
    assert data_id == PERIPHERAL_ID, "Step 4: ID was overwritten (RO protection failed)"

    # 5. Back-to-back write sequence then bulk readback
    await drv.write(ADDR_GPIO, 0x42)
    await drv.write(ADDR_CTRL, 0x00)
    gpio_rb, _, _ = await drv.read(ADDR_GPIO)
    ctrl_rb, _, _ = await drv.read(ADDR_CTRL)
    assert gpio_rb == 0x42, f"Step 5: GPIO readback {hex(gpio_rb)}"
    assert ctrl_rb == 0x00, f"Step 5: CTRL readback {hex(ctrl_rb)}"

    # 6. Invalid access in the middle of a sequence
    _, _, err = await drv.read(ADDR_INVALID)
    assert err == 1, "Step 6: addr_err not set for invalid access"

    # 7. Recovery: valid access immediately after the error
    data, valid, err = await drv.read(ADDR_GPIO)
    assert valid == 1 and err == 0 and data == 0x42, \
        f"Step 7: recovery read failed: data={hex(data)} valid={valid} err={err}"

    dut._log.info("test_regression_sequence PASSED")
    drv.stop_clock()
