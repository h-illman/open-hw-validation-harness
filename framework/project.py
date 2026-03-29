# framework/project.py
#
# Project discovery and manifest loading.
#
# A "project" in this framework is any folder under projects/ that contains
# a project.yaml file.  This module finds those folders and parses the YAML
# so the runner knows what to do with each one.
#
# This is the core of the "bring your own DUT" workflow:
#   - users drop their files into projects/their_project/
#   - they write a project.yaml describing their DUT
#   - the runner calls discover_projects() and picks them up automatically
#   - no framework code needs to change when a project is added
#
# Phase 5 addition:
#   ProjectManifest gains an optional `target` dict populated from the
#   project.yaml `target:` block.  Existing projects without a target block
#   are unaffected — target defaults to None and everything still works.

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


@dataclass
class ProjectManifest:
    """
    Parsed contents of a project.yaml file.
    All paths are resolved to absolute paths at load time.
    """
    # From project.yaml
    name:        str
    description: str
    version:     str
    phase:       int
    top_module:  str
    sources:     List[str]
    sim_tool:    str
    test_module: str
    timeout_ns:  int
    results_xml: str
    waves_dir:   str

    # Phase 5: optional target/board block (None if not declared in project.yaml).
    #
    # Populated from:
    #   target:
    #     board: de10_standard            # required for target-aware validation
    #     clock_source: CLOCK_50          # optional
    #     target_clock_mhz: 50           # optional
    #     io_standard: "3.3V LVTTL"      # optional
    #     resource_estimate:             # optional
    #       luts: 500
    #       ffs:  200
    #
    # Absence of the target block is not an error — simulation validation
    # runs normally.  Target-aware checks simply will not run unless --target
    # is supplied on the CLI or this block is present.
    target: Optional[dict] = field(default=None)

    # Set by the loader, not from yaml
    project_dir: Path = field(default=None)  # absolute path to projects/<name>/
    sim_dir:     Path = field(default=None)  # absolute path to projects/<name>/sim/
    repo_root:   Path = field(default=None)


def load_manifest(yaml_path: Path, repo_root: Path) -> ProjectManifest:
    """
    Parse a project.yaml file and return a ProjectManifest.
    Falls back to a safe default if PyYAML is not installed.
    """
    if not _YAML_AVAILABLE:
        raise RuntimeError(
            "PyYAML is required for manifest-driven project discovery.\n"
            "Install it with: pip install pyyaml"
        )

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    project_dir = yaml_path.parent
    sim_dir     = project_dir / "sim"

    # Phase 5: read the optional target block as-is (dict or None).
    # Existing projects without a target: key are unaffected.
    target_block = data.get("target", None)

    return ProjectManifest(
        name        = data["name"],
        description = data.get("description", ""),
        version     = data.get("version", "0.0.1"),
        phase       = data.get("phase", 0),
        top_module  = data["dut"]["top_module"],
        sources     = data["dut"].get("sources", []),
        sim_tool    = data["sim"].get("tool", "verilator"),
        test_module = data["sim"]["test_module"],
        timeout_ns  = data["sim"].get("timeout_ns", 10000),
        results_xml = data["artifacts"]["results_xml"],
        waves_dir   = data["artifacts"]["waves_dir"],
        target      = target_block,
        project_dir = project_dir,
        sim_dir     = sim_dir,
        repo_root   = repo_root,
    )


def discover_projects(repo_root: Path, skip_template: bool = True) -> List[ProjectManifest]:
    """
    Scan projects/ for subdirectories containing a project.yaml.
    Returns a list of parsed ProjectManifest objects, sorted by name.

    The template project is skipped by default since it is not a runnable
    simulation target — it is documentation for users.
    """
    projects_dir = repo_root / "projects"
    if not projects_dir.exists():
        return []

    manifests = []
    for yaml_path in sorted(projects_dir.glob("*/project.yaml")):
        project_name = yaml_path.parent.name
        if skip_template and project_name == "template":
            continue
        try:
            m = load_manifest(yaml_path, repo_root)
            manifests.append(m)
        except Exception as e:
            print(f"  [WARN] Could not load manifest for '{project_name}': {e}")

    return manifests
