# framework/result_parser.py
#
# Parses the JUnit XML results file that cocotb writes after each simulation.
# Extracted here so the runner and any other tooling can share it.

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET


@dataclass
class TestResult:
    name:    str
    passed:  bool
    message: str = ""


@dataclass
class SimResults:
    project_name: str
    passed:       int = 0
    failed:       int = 0
    failures:     List[TestResult] = field(default_factory=list)
    error:        str = ""          # set if the XML file was missing or unreadable

    @property
    def total(self) -> int:
        return self.passed + self.failed

    @property
    def all_passed(self) -> bool:
        return self.failed == 0 and not self.error


def parse_results(project_name: str, xml_path: Path) -> SimResults:
    """
    Parse a cocotb JUnit XML results file.
    Returns a SimResults object regardless of whether the file exists.
    """
    if not xml_path.exists():
        return SimResults(
            project_name=project_name,
            error=f"Results file not found: {xml_path}"
        )

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return SimResults(
            project_name=project_name,
            error=f"Could not parse XML: {e}"
        )

    results = SimResults(project_name=project_name)

    for testcase in root.iter("testcase"):
        name = testcase.get("name", "unknown")
        failure_elem = testcase.find("failure")
        if failure_elem is not None:
            results.failed += 1
            results.failures.append(TestResult(
                name=name,
                passed=False,
                message=failure_elem.get("message", ""),
            ))
        else:
            results.passed += 1

    return results
