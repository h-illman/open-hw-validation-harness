# framework/boards/de0_cv.py
#
# Board profile for the Terasic DE0-CV.
#
# Device  : Intel/Altera Cyclone V — 5CEBA4F23C7
# Family  : Cyclone V E
# Vendor  : Terasic / Intel (Altera)
# Toolchain: Quartus Prime Lite
#
# A smaller, lower-cost Cyclone V board popular in entry-level courses.
# No HPS subsystem.  Fewer resources than the DE10-Standard.
#
# Reference:
#   https://www.terasic.com.tw/cgi-bin/page/archive.pl?Language=English&No=364

from __future__ import annotations
from framework.boards.base_board    import BoardProfile, BoardReadinessReport
from framework.boards.common_checks import (
    check_target_block_present,
    check_sources_exist,
    check_top_module_declared,
    check_clock_source,
    check_clock_frequency,
    check_io_standard,
    check_resource_estimate,
)


class DE0CV(BoardProfile):

    def board_id(self)     -> str: return "de0_cv"
    def board_name(self)   -> str: return "DE0-CV (Terasic)"
    def board_family(self) -> str: return "Cyclone V E"
    def fpga_device(self)  -> str: return "5CEBA4F23C7"
    def vendor(self)       -> str: return "Terasic / Intel"
    def toolchain_hint(self) -> str: return "Quartus Prime Lite"

    def clock_sources(self):
        return [
            {"name": "CLOCK_50",  "freq_mhz": 50.0, "pin": "M9"},
            {"name": "CLOCK2_50", "freq_mhz": 50.0, "pin": "H13"},
        ]

    def io_standards(self):
        return [
            "3.3V LVTTL",
            "3.3V LVCMOS",
            "2.5V LVTTL",
            "2.5V LVCMOS",
            "LVDS",
        ]

    def resource_budget(self):
        # Cyclone V 5CEBA4F23C7 approximate resources
        return {
            "luts":    18480,
            "ffs":     36960,
            "bram_kb": 3080,
            "dsps":    50,
            "plls":    4,
        }

    def board_notes(self):
        return [
            "No HPS — pure FPGA fabric board.",
            "Fewer resources than DE10-Standard: watch LUT and FF budgets.",
            "Use CLOCK_50 (pin M9, 50 MHz) as your primary clock.",
            "Quartus Prime Lite fully supports this device.",
            "5 pushbuttons and 10 slide switches for simple I/O designs.",
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
        # Cyclone V E (C7 speed grade): ~200-250 MHz typical Fmax
        report.checks.append(check_clock_frequency(
            manifest, self.clock_sources(), max_reasonable_mhz=250.0,
        ))
        report.checks.append(check_io_standard(manifest, self.io_standards()))
        report.checks.append(check_resource_estimate(manifest, self.resource_budget()))

        return report
