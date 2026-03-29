# framework/boards/de25_standard.py
#
# Board profile for the Terasic DE25-Standard.
#
# FPGA    : Altera Agilex 5 SoC E-Series — A5ED013BB32AE4S
# Family  : Agilex 5 SoC E-Series
# LEs     : 138,000
# HPS     : Quad-core ARM (2× Cortex-A55 + 2× Cortex-A76)
# Vendor  : Terasic / Altera (Intel)
# Toolchain: Quartus Prime Pro Edition (free license included with board)
#
# The DE25-Standard is the next-generation successor to the DE10-Standard,
# featuring the Agilex 5 SoC FPGA with DDR4 memory, HDMI 1080p output,
# AI Tensor Blocks, MIPI CSI/DSI, and a full multimedia peripheral set.
#
# Key differences from DE10-Standard / DE0-CV that affect validation:
#   - Requires Quartus Prime Pro (not Lite) — free license included
#   - Agilex 5 uses a different I/O bank architecture than Cyclone V
#   - HSMC I/O must be single-ended (no differential pairs via HSMC on Agilex 5)
#   - Three 50 MHz + one 150 MHz clock sources on FPGA fabric
#   - HPS is quad-core (A55+A76) vs dual A9 on DE10-Standard
#   - Nios V soft processor (RISC-V ISA) replaces Nios II
#
# Reference:
#   https://www.terasic.com.tw/cgi-bin/page/archive.pl?Language=English&No=1354
#   User Manual: https://DE25-standard.terasic.com/cd/
#   ManualsLib: https://www.manualslib.com/manual/3615239/Terasic-De25-Standard.html

from __future__ import annotations
from framework.boards.base_board    import BoardProfile, BoardReadinessReport, BoardCheckResult
from framework.boards.common_checks import (
    check_target_block_present,
    check_sources_exist,
    check_top_module_declared,
    check_clock_source,
    check_clock_frequency,
    check_io_standard,
    check_resource_estimate,
    check_toolchain_declared,
)


class DE25Standard(BoardProfile):

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------

    def board_id(self)     -> str: return "de25_standard"
    def board_name(self)   -> str: return "DE25-Standard (Terasic)"
    def board_family(self) -> str: return "Agilex 5 SoC E-Series"
    def fpga_device(self)  -> str: return "A5ED013BB32AE4S"
    def vendor(self)       -> str: return "Terasic / Altera"
    def toolchain_hint(self) -> str: return "Quartus Prime Pro Edition (free license included)"

    # -------------------------------------------------------------------------
    # Clock sources
    #
    # From the DE25-Standard user manual (June 2024):
    #   "The three 50 MHz clock signals connected to the FPGA are used as
    #    clock sources for user logic."
    #   Additionally one 150 MHz differential clock input is provided.
    # -------------------------------------------------------------------------

    def clock_sources(self):
        return [
            {"name": "CLOCK_50",   "freq_mhz": 50.0,  "pin": "PIN_N14"},
            {"name": "CLOCK2_50",  "freq_mhz": 50.0,  "pin": "PIN_H13"},
            {"name": "CLOCK3_50",  "freq_mhz": 50.0,  "pin": "PIN_E11"},
            {"name": "CLOCK_150",  "freq_mhz": 150.0, "pin": "differential", "note": "150 MHz differential input"},
        ]

    # -------------------------------------------------------------------------
    # I/O standards
    #
    # Agilex 5 supports a broader range than Cyclone V.
    # Note: HSMC I/O must be single-ended on Agilex 5 (no differential pairs
    # via HSMC) — this is flagged separately in board notes.
    # -------------------------------------------------------------------------

    def io_standards(self):
        return [
            "3.3V LVCMOS",
            "2.5V LVCMOS",
            "1.8V LVCMOS",
            "1.2V LVCMOS",
            "LVDS",
            "True Differential Signaling",
            "HCSL",
            "MIPI D-PHY",
        ]

    # -------------------------------------------------------------------------
    # Resource budget
    #
    # Agilex 5 A5ED013BB32AE4S approximate resources.
    # Intel publishes resources in ALMs (Adaptive Logic Modules).
    # "138K LEs" is the marketing figure; 1 ALM ≈ 2.5 LEs for comparison.
    # Embedded memory and DSP figures from Agilex 5 E-series datasheet.
    # -------------------------------------------------------------------------

    def resource_budget(self):
        return {
            # Marketing "logic elements" figure — comparable to other DE boards
            "luts":         138000,   # 138K LEs (Agilex 5 E-series marketing figure)
            # Underlying ALMs for users who work at that level
            "alms":          55200,   # ~55,200 ALMs (138K LEs / 2.5)
            # Flip-flops: 2 per ALM × 2 registers each = ~4 per ALM
            "ffs":          220800,   # ~220,800 registers
            # Embedded memory
            "bram_kb":       8420,    # 8,420 Kbits (~8.42 Mbits) of embedded RAM
            # DSP blocks (18×19 multipliers)
            "dsps":           294,    # ~294 DSP blocks
            # Fractional PLLs
            "plls":             8,    # 8 fractional PLLs
            # Transceivers (via HSMC)
            "xcvrs":            4,    # 4 transceivers on HSMC connector
        }

    # -------------------------------------------------------------------------
    # Board notes shown in the readiness report
    # -------------------------------------------------------------------------

    def board_notes(self):
        return [
            # Toolchain — the most important difference from Cyclone V boards
            "CRITICAL: Requires Quartus Prime Pro Edition (NOT Lite/Standard).",
            "A free Quartus Pro license is included with the DE25-Standard kit.",

            # FPGA fabric
            "Agilex 5 SoC — 138K LEs, AI Tensor Block, Nios V (RISC-V) soft processor.",
            "Use CLOCK_50 (50 MHz) as primary clock for simple FPGA designs.",
            "150 MHz differential clock also available for higher-speed designs.",

            # HPS
            "HPS: Quad-core ARM (2× Cortex-A55 + 2× Cortex-A76). "
            "This profile covers FPGA fabric only.",
            "Linux BSP provided — supports Yocto and Debian on the HPS.",

            # Memory
            "FPGA side: 1 GB DDR4 (32-bit, shared with HPS) + 64 MB SDRAM.",
            "128 Mbit QSPI Flash for AS-mode configuration.",

            # I/O and peripherals
            "FPGA I/O: 10 LEDs, 4 buttons, 10 switches, 6 seven-segment displays.",
            "Multimedia: HDMI 1080p out, MIPI CSI/DSI (2-lane), composite video in.",
            "Audio: 24-bit CODEC (SSM2603), MIC/Line-In/Line-Out, 8–96 kHz sample rate.",
            "Expansion: 2×20 DE-GPIO header, 8-ch ADC header, HSMC (4 transceivers).",
            "IR TX/RX, I2C bus (audio codec, ADC, accelerometer), USB-Blaster III (USB-C).",

            # HSMC note — important design constraint
            "HSMC IMPORTANT: FPGA I/O on HSMC must be single-ended on Agilex 5 "
            "(no differential pairs via HSMC connector).",

            # HPS-connected peripherals (out of scope for FPGA fabric validation)
            "HPS-connected (not FPGA fabric): GbE, 2× USB-A host, microSD, "
            "128×64 LCD, G-sensor accelerometer.",
        ]

    # -------------------------------------------------------------------------
    # Peripheral summary (not used in checks — metadata for --board-info)
    # -------------------------------------------------------------------------

    def peripheral_summary(self) -> dict:
        """
        Full peripheral inventory for documentation and --board-info display.
        Not used in validation checks — purely informational.
        """
        return {
            "fpga_side": {
                "user_leds":          10,
                "push_buttons":        4,
                "slide_switches":     10,
                "seven_seg_displays":  6,
                "hdmi_out":           "HDMI 1.4, 1080p",
                "mipi_connector":     "2-lane CSI/DSI (22-pin)",
                "composite_video_in": "ADV7180 TV decoder (NTSC/PAL/SECAM)",
                "audio_codec":        "SSM2603 24-bit, 8–96 kHz, MIC/Line-In/Line-Out",
                "adc":                "8-channel, 2×5 header",
                "ir":                 "TX/RX",
                "gpio_header":        "2×20 DE-GPIO (3.3V, 40 pins)",
                "hsmc":               "HSMC connector with 4 transceivers (single-ended only)",
                "i2c_bus":            "Audio codec, ADC sensor, accelerometer",
                "configuration":      "USB-Blaster III (USB-C), ASx4 QSPI Flash (128 Mbit)",
                "soft_processor":     "Nios V (RISC-V ISA)",
                "ai_tensor_block":    "Yes (Agilex 5 built-in)",
            },
            "hps_side": {
                "processor":          "Quad-core ARM (2× Cortex-A55 + 2× Cortex-A76)",
                "ethernet":           "Gigabit (KSZ9031RN PHY) + RJ45",
                "usb_host":           "2× USB Type-A",
                "uart":               "UART-to-USB (via USB-C)",
                "storage":            "MicroSD socket",
                "lcd":                "128×64 B&W LCD module",
                "color_lcd":          "Color mini LCD (optional)",
                "accelerometer":      "G-sensor, I2C (0xA6/0xA7)",
                "gpio":               "1×6 GPIO header (3.3V)",
                "hps_led":            "1 HPS LED",
                "hps_button":         "1 HPS button + 1 Cold Reset button",
            },
            "memory": {
                "ddr4_shared":        "1 GB DDR4, 32-bit bus (FPGA + HPS shared)",
                "sdram_fpga":         "64 MB SDRAM, 32-bit bus (FPGA side)",
                "qspi_flash":         "128 Mbit (configuration)",
                "embedded_ram":       "8,420 Kbits (FPGA fabric M20K blocks)",
            },
            "board_management": {
                "system_controller":  "MAX10 FPGA (board management, power/temp monitoring)",
                "power_monitor":      "Yes",
                "temp_monitor":       "Yes",
                "fan_control":        "Auto fan control",
                "active_heatsink":    "Optional",
                "dashboard":          "Windows dashboard tool via USB-C UART",
            },
        }

    # -------------------------------------------------------------------------
    # Target-aware checks
    # -------------------------------------------------------------------------

    def check_project(self, manifest) -> BoardReadinessReport:
        report = BoardReadinessReport(
            board_id     = self.board_id(),
            board_name   = self.board_name(),
            board_family = self.board_family(),
            fpga_device  = self.fpga_device(),
            project_name = manifest.name,
            board_notes  = self.board_notes(),
        )

        # 1. Target block present
        report.checks.append(check_target_block_present(manifest))

        # 2. RTL sources exist on disk
        report.checks.append(check_sources_exist(manifest))

        # 3. Top module declared
        report.checks.append(check_top_module_declared(manifest))

        # 4. Clock source compatibility
        #    Agilex 5 has 3× 50 MHz + 1× 150 MHz differential
        report.checks.append(check_clock_source(manifest, self.clock_sources()))

        # 5. Clock frequency sanity
        #    Agilex 5 E-series can achieve 400–500+ MHz on simple paths.
        #    Setting ceiling at 500 MHz — anything above that is almost certainly
        #    a mistake for an educational/pre-lab context.
        report.checks.append(check_clock_frequency(
            manifest, self.clock_sources(), max_reasonable_mhz=500.0,
        ))

        # 6. I/O standard compatibility
        report.checks.append(check_io_standard(manifest, self.io_standards()))

        # 7. Resource estimate check
        report.checks.append(check_resource_estimate(manifest, self.resource_budget()))

        # 8. Toolchain requirement — Agilex 5 needs Quartus Pro, not Lite.
        #    This is INFO-level (never blocks simulation), but surfaces early
        #    so the user knows before they get to synthesis.
        report.checks.append(check_toolchain_declared(
            manifest,
            required_toolchain="Quartus Prime Pro",
            required_edition="Pro Edition",
            free_license_available=True,
        ))

        # 9. Agilex 5-specific: HSMC single-ended constraint check
        report.checks.append(self._check_hsmc_differential(manifest))

        # 10. Agilex 5-specific: DDR4 vs SDRAM interface hint
        report.checks.append(self._check_memory_interface(manifest))

        return report

    # -------------------------------------------------------------------------
    # DE25-Standard-specific checks (not reusable across other boards yet)
    # These live here rather than in common_checks.py because they are specific
    # to Agilex 5 architecture.  If more Agilex boards are added, extract them.
    # -------------------------------------------------------------------------

    def _check_hsmc_differential(self, manifest) -> BoardCheckResult:
        """
        Warn if the project declares use of HSMC differential I/O.
        Agilex 5 SoC restricts HSMC I/O to single-ended signals.
        """
        tb = manifest.target or {}
        hsmc_diff = tb.get("hsmc_differential", None)

        if hsmc_diff is True:
            return BoardCheckResult(
                check_id="hsmc_differential",
                check_name="HSMC Differential I/O",
                passed=False,
                level="WARN",
                message=(
                    "Project declares 'hsmc_differential: true' but Agilex 5 "
                    "restricts HSMC I/O to single-ended signals."
                ),
                detail=(
                    "This is an Agilex 5 architecture constraint — the HSMC "
                    "interface pins on this device do not support differential "
                    "pairs through the connector."
                ),
                suggestion=(
                    "Route differential signals through the GPIO header or "
                    "use the on-board MIPI/LVDS interfaces for differential I/O."
                ),
            )

        return BoardCheckResult(
            check_id="hsmc_differential",
            check_name="HSMC Differential I/O",
            passed=True,
            level="INFO",
            message=(
                "HSMC I/O is single-ended only on Agilex 5. "
                "If your design uses HSMC, ensure all signals are single-ended."
            ),
            suggestion=(
                "Add 'hsmc_differential: true' to your target block if your "
                "design attempts differential I/O through HSMC, to trigger "
                "an explicit warning."
            ),
        )

    def _check_memory_interface(self, manifest) -> BoardCheckResult:
        """
        Informational check about memory interfaces available on the DE25-Standard.

        Projects that declare a memory_interface in their target block are
        informed about what is actually available and any caveats.
        """
        tb = manifest.target or {}
        mem_iface = tb.get("memory_interface", None)

        memory_options = {
            "ddr4":  "1 GB DDR4, 32-bit bus (shared between FPGA and HPS — "
                     "requires Avalon-MM or AXI bridge for direct FPGA access)",
            "sdram": "64 MB SDRAM, 32-bit bus (FPGA-side, directly accessible "
                     "from FPGA logic without HPS involvement)",
            "qspi":  "128 Mbit QSPI Flash (read-only from FPGA for configuration; "
                     "writable from HPS/MAX10 for firmware update)",
        }

        if mem_iface is None:
            return BoardCheckResult(
                check_id="memory_interface",
                check_name="Memory Interface",
                passed=True,
                level="INFO",
                message="No memory_interface declared — informational summary below.",
                detail="\n".join(
                    f"  {k.upper()}: {v}" for k, v in memory_options.items()
                ),
                suggestion=(
                    "Add 'memory_interface: sdram' (or ddr4/qspi) to your target "
                    "block to get interface-specific guidance."
                ),
            )

        mem_iface_lower = mem_iface.strip().lower()

        if mem_iface_lower not in memory_options:
            return BoardCheckResult(
                check_id="memory_interface",
                check_name="Memory Interface",
                passed=False,
                level="WARN",
                message=f"Declared memory_interface '{mem_iface}' is not a known interface on this board.",
                detail=f"Available: {', '.join(memory_options.keys())}",
                suggestion="Use one of: ddr4, sdram, qspi",
            )

        return BoardCheckResult(
            check_id="memory_interface",
            check_name="Memory Interface",
            passed=True,
            level="INFO",
            message=f"Memory interface '{mem_iface_lower}' is available on this board.",
            detail=memory_options[mem_iface_lower],
        )
