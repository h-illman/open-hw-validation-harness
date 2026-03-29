# framework/boards/de10_standard.py
#
# Board profile for the Terasic DE10-Standard.
#
# Device  : Intel/Altera Cyclone V SX SoC — 5CSXFC6D6F31C6
# Family  : Cyclone V SX SoC
# Vendor  : Terasic / Intel (Altera)
# Toolchain: Quartus Prime Lite or Standard
#
# A popular university FPGA board with an ARM Cortex-A9 HPS subsystem.
# This profile covers the FPGA fabric only.  HPS validation is out of scope.
#
# Reference:
#   https://www.terasic.com.tw/cgi-bin/page/archive.pl?Language=English&No=1021

from __future__ import annotations
from framework.boards.base_board   import BoardProfile, BoardReadinessReport
from framework.boards.common_checks import (
    check_target_block_present,
    check_sources_exist,
    check_top_module_declared,
    check_clock_source,
    check_clock_frequency,
    check_io_standard,
    check_resource_estimate,
)


class DE10Standard(BoardProfile):

    def board_id(self)     -> str: return "de10_standard"
    def board_name(self)   -> str: return "DE10-Standard (Terasic)"
    def board_family(self) -> str: return "Cyclone V SX SoC"
    def fpga_device(self)  -> str: return "5CSXFC6D6F31C6"
    def vendor(self)       -> str: return "Terasic / Intel"
    def toolchain_hint(self) -> str: return "Quartus Prime Lite or Standard"

    def clock_sources(self):
        return [
            {"name": "CLOCK_50",  "freq_mhz": 50.0, "pin": "AF14"},
            {"name": "CLOCK2_50", "freq_mhz": 50.0, "pin": "AA16"},
            {"name": "CLOCK3_50", "freq_mhz": 50.0, "pin": "Y26"},
            {"name": "CLOCK4_50", "freq_mhz": 50.0, "pin": "K14"},
        ]

    def io_standards(self):
        return [
            "3.3V LVTTL",
            "3.3V LVCMOS",
            "2.5V LVTTL",
            "2.5V LVCMOS",
            "1.8V LVTTL",
            "1.8V LVCMOS",
            "LVDS",
            "SSTL-15 Class I",
        ]

    def resource_budget(self):
        # Cyclone V 5CSXFC6D6F31C6 approximate resources
        return {
            "luts":    41910,
            "ffs":     83820,
            "bram_kb": 5570,
            "dsps":    112,
            "plls":    6,
        }

    def board_notes(self):
        return [
            "Includes ARM Cortex-A9 HPS — this profile covers FPGA fabric only.",
            "Use CLOCK_50 (pin AF14, 50 MHz) as your primary FPGA clock.",
            "Quartus Prime Lite supports this device for student/academic use.",
            "4 x 50 MHz oscillators available on the FPGA fabric.",
        ]

    def check_project(self, manifest) -> BoardReadinessReport:
        report = BoardReadinessReport(
            board_id     = self.board_id(),
            board_name   = self.board_name(),
            board_family = self.board_family(),
            fpga_device  = self.fpga_device(),
            project_name = manifest.name,
            board_notes  = self.board_notes(),
        )

        report.checks.append(check_target_block_present(manifest))
        report.checks.append(check_sources_exist(manifest))
        report.checks.append(check_top_module_declared(manifest))
        report.checks.append(check_clock_source(manifest, self.clock_sources()))
        # Cyclone V SX fabric: ~250-300 MHz typical Fmax
        report.checks.append(check_clock_frequency(
            manifest, self.clock_sources(), max_reasonable_mhz=300.0,
        ))
        report.checks.append(check_io_standard(manifest, self.io_standards()))
        report.checks.append(check_resource_estimate(manifest, self.resource_budget()))

        return report
