# framework/boards/registry.py
#
# Central registry for all supported board profiles.
#
# To add a new board:
#   1. Create framework/boards/your_board.py implementing BoardProfile
#   2. Import and add an instance to _BOARDS below
#   3. The --target flag and --list-boards command pick it up automatically
#
# Registration is explicit (not auto-discovery) so the list of supported
# boards is always visible and auditable in one place.

from __future__ import annotations
from typing import Dict, List, Optional
from framework.boards.base_board import BoardProfile


def _build() -> Dict[str, BoardProfile]:
    from framework.boards.de10_standard import DE10Standard
    from framework.boards.de0_cv        import DE0CV
    from framework.boards.de25_standard import DE25Standard

    boards: List[BoardProfile] = [
        DE10Standard(),
        DE0CV(),
        DE25Standard(),
    ]

    reg: Dict[str, BoardProfile] = {}
    for b in boards:
        bid = b.board_id()
        if bid in reg:
            raise RuntimeError(
                f"Duplicate board_id '{bid}' registered by "
                f"{b.__class__.__name__} and {reg[bid].__class__.__name__}"
            )
        reg[bid] = b
    return reg


# Lazily initialized singleton
_REGISTRY: Optional[Dict[str, BoardProfile]] = None


def _get() -> Dict[str, BoardProfile]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build()
    return _REGISTRY


def get_board(board_id: str) -> BoardProfile:
    """
    Return the board profile for board_id.
    Raises KeyError with a helpful message if not found.
    """
    reg = _get()
    if board_id not in reg:
        valid = ", ".join(sorted(reg.keys()))
        raise KeyError(
            f"Unknown board ID: '{board_id}'.  "
            f"Supported boards: {valid}"
        )
    return reg[board_id]


def list_board_ids() -> List[str]:
    """Return sorted list of registered board IDs."""
    return sorted(_get().keys())


def list_boards() -> List[BoardProfile]:
    """Return all registered board instances, sorted by board_id."""
    reg = _get()
    return [reg[k] for k in sorted(reg.keys())]


def describe_all_boards() -> str:
    """Return a formatted multiline string listing all supported boards."""
    lines = ["Supported boards:", ""]
    for b in list_boards():
        lines.append(f"  {b.board_id():<20}  {b.board_name()}")
        lines.append(f"    Family   : {b.board_family()}")
        lines.append(f"    Device   : {b.fpga_device()}")
        lines.append(f"    Vendor   : {b.vendor()}")
        lines.append(f"    Toolchain: {b.toolchain_hint()}")
        clocks = b.clock_sources()
        if clocks:
            clk_str = ", ".join(
                f"{c['name']} @ {c['freq_mhz']} MHz" for c in clocks
            )
            lines.append(f"    Clocks   : {clk_str}")
        lines.append("")
    return "\n".join(lines)
