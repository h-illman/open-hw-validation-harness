# framework/tool_check.py
#
# Checks that required external tools are available before attempting to run.
# Keeps tool validation logic in one place.

from __future__ import annotations
import importlib.util
import shutil
from dataclasses import dataclass
from typing import List


@dataclass
class ToolStatus:
    name:      str
    available: bool
    path:      str = ""
    note:      str = ""


REQUIRED_TOOLS = [
    ("verilator", "Verilog simulator — install from source, see docs/getting_started.md"),
    ("make",      "Build system — sudo apt install make"),
]

REQUIRED_PYTHON_PACKAGES = [
    ("cocotb", "pip install cocotb"),
    ("yaml",   "pip install pyyaml"),
]


def check_tools(verbose: bool = False) -> List[ToolStatus]:
    """
    Check that all required tools and Python packages are available.
    Returns a list of ToolStatus objects.
    """
    statuses = []

    for tool, note in REQUIRED_TOOLS:
        path = shutil.which(tool)
        statuses.append(ToolStatus(
            name=tool,
            available=bool(path),
            path=path or "",
            note=note,
        ))

    for package, note in REQUIRED_PYTHON_PACKAGES:
        spec = importlib.util.find_spec(package)
        statuses.append(ToolStatus(
            name=f"python:{package}",
            available=spec is not None,
            note=note,
        ))

    if verbose:
        for s in statuses:
            tag  = "[OK]     " if s.available else "[MISSING]"
            loc  = f" -> {s.path}" if s.path else ""
            print(f"  {tag} {s.name}{loc}")

    return statuses


def all_tools_available(verbose: bool = False) -> bool:
    """Return True only if every required tool and package is present."""
    statuses = check_tools(verbose)
    missing = [s for s in statuses if not s.available]
    if missing and not verbose:
        for s in missing:
            print(f"  [MISSING] {s.name}  ({s.note})")
    return len(missing) == 0
