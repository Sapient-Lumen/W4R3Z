"""rev0081 native hotpath reference functions.

The C side is optional.  These functions are the required Python reference and
portable fallback for any GCC-compiled leaf kernel.
"""
from __future__ import annotations

from pathlib import Path


def xor_compare_reference(pivot: bytes, left: bytes, right: bytes) -> int:
    """Compare XOR distance to pivot.

    Returns -1 if left is closer, 1 if right is closer, 0 if equal.
    """
    if not (len(pivot) == len(left) == len(right)):
        raise ValueError("pivot/left/right must have the same length")
    left_distance = bytes(a ^ b for a, b in zip(pivot, left))
    right_distance = bytes(a ^ b for a, b in zip(pivot, right))
    if left_distance < right_distance:
        return -1
    if left_distance > right_distance:
        return 1
    return 0


def sort_by_xor_reference(pivot: bytes, candidates: tuple[bytes, ...]) -> tuple[bytes, ...]:
    return tuple(sorted(candidates, key=lambda candidate: bytes(a ^ b for a, b in zip(pivot, candidate))))


def native_xor_source_path(root: str | Path) -> Path:
    return Path(root) / "native" / "gcc" / "xor_distance.c"


def expected_native_symbols() -> tuple[str, ...]:
    return ("i2pdht_abi_version", "i2pdht_xor_compare")
