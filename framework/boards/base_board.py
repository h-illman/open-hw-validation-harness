# framework/boards/base_board.py
#
# Abstract base class for all board/target profiles.
#
# Every supported board is a subclass of BoardProfile.
# A profile describes the board's capabilities and runs
# target-aware checks against a ProjectManifest.
#
# Phase 6 extension note:
#   When real hardware execution is added, BoardProfile can gain methods
#   like program() and capture_output() without touching this layer.

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Check result data types
# ---------------------------------------------------------------------------

@dataclass
class BoardCheckResult:
    """
    Result of one target-aware check for a (project, board) pair.
    """
    check_id:   str          # stable snake_case ID, e.g. "clock_source"
    check_name: str          # human-readable label
    passed:     bool
    level:      str          # "INFO" | "WARN" | "ERROR"
    message:    str
    detail:     Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class BoardReadinessReport:
    """
    Aggregated result of all target checks for one (project, board) pair.
    Produced by BoardProfile.check_project().
    """
    board_id:     str
    board_name:   str
    board_family: str
    fpga_device:  str
    project_name: str
    checks:       List[BoardCheckResult] = field(default_factory=list)
    board_notes:  List[str]              = field(default_factory=list)

    # ---- convenience accessors ----------------------------------------

    def errors(self)        -> List[BoardCheckResult]:
        return [c for c in self.checks if c.level == "ERROR"]

    def warnings(self)      -> List[BoardCheckResult]:
        return [c for c in self.checks if c.level == "WARN"]

    def infos(self)         -> List[BoardCheckResult]:
        return [c for c in self.checks if c.level == "INFO"]

    def passed_checks(self) -> List[BoardCheckResult]:
        return [c for c in self.checks if c.passed]

    def failed_checks(self) -> List[BoardCheckResult]:
        return [c for c in self.checks if not c.passed]

    @property
    def ready(self) -> bool:
        """True when no ERROR-level check failed."""
        return not any(
            c.level == "ERROR" and not c.passed for c in self.checks
        )

    def summary_line(self) -> str:
        status = "READY" if self.ready else "NOT READY"
        return (
            f"[{status}] {self.project_name} -> {self.board_name}  "
            f"errors={len(self.errors())}  "
            f"warnings={len(self.warnings())}  "
            f"checks={len(self.checks)}"
        )


# ---------------------------------------------------------------------------
# Abstract board profile
# ---------------------------------------------------------------------------

class BoardProfile(ABC):
    """
    Abstract base for board/target profiles.

    Subclasses must implement:
        board_id()       – stable snake_case ID used by --target flag
        board_name()     – human label
        board_family()   – FPGA family string
        fpga_device()    – device/part string
        check_project()  – run checks, return BoardReadinessReport
    """

    # ---- identity — must override ---------------------------------------

    @abstractmethod
    def board_id(self) -> str:
        """Stable snake_case identifier. E.g. 'de10_standard'."""

    @abstractmethod
    def board_name(self) -> str:
        """Human-readable board label. E.g. 'DE10-Standard (Terasic)'."""

    @abstractmethod
    def board_family(self) -> str:
        """FPGA family. E.g. 'Cyclone V SX SoC'."""

    @abstractmethod
    def fpga_device(self) -> str:
        """Device part string. E.g. '5CSXFC6D6F31C6'."""

    # ---- metadata — optional, defaults provided -------------------------

    def vendor(self) -> str:
        return "Unknown"

    def toolchain_hint(self) -> str:
        """Recommended synthesis toolchain (informational)."""
        return "Unknown"

    def clock_sources(self) -> List[dict]:
        """
        On-board clock sources.
        Each entry: {"name": str, "freq_mhz": float, "pin": str (optional)}
        """
        return []

    def io_standards(self) -> List[str]:
        """Supported I/O voltage standards."""
        return []

    def resource_budget(self) -> dict:
        """
        Approximate resource budget for sanity checks.
        e.g. {"luts": 41910, "ffs": 83820, "bram_kb": 5570, "dsps": 112}
        Not a substitute for synthesis reports.
        """
        return {}

    def board_notes(self) -> List[str]:
        """Free-form notes shown in reports."""
        return []

    # ---- target-aware checks — must override ----------------------------

    @abstractmethod
    def check_project(self, manifest) -> BoardReadinessReport:
        """
        Run all target-aware checks for this board against a ProjectManifest.
        Returns a BoardReadinessReport.
        """

    # ---- convenience ----------------------------------------------------

    def metadata_summary(self) -> dict:
        return {
            "board_id":       self.board_id(),
            "board_name":     self.board_name(),
            "board_family":   self.board_family(),
            "fpga_device":    self.fpga_device(),
            "vendor":         self.vendor(),
            "toolchain_hint": self.toolchain_hint(),
            "clock_sources":  self.clock_sources(),
            "io_standards":   self.io_standards(),
            "resource_budget": self.resource_budget(),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.board_id()!r}>"
