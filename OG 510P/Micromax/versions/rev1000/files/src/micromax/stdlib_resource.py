"""Bounded loading and provenance for bundled Micromax stdlib resources.

The VM's boot stdlib is trusted package data, not workspace/plugin input.  It is
still bytes read through Python's import machinery, so keep its authority and
resource contract explicit instead of hiding it inside VM startup.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.resources as importlib_resources
from typing import Any

STDLIB_RESOURCE_SCHEMA = "micromax.stdlib-resource.v1"
STDLIB_RESOURCE_PACKAGE = "micromax"
STDLIB_RESOURCE_PATH = "stdlib/core.mx"
STDLIB_RESOURCE_NAME = f"{STDLIB_RESOURCE_PACKAGE}/{STDLIB_RESOURCE_PATH}"
STDLIB_SOURCE_NAME = "<stdlib/core.mx>"
# The shipped core.mx is intentionally tiny (about 4 KiB in rev0927).  A 64 KiB
# ceiling leaves real growth room while catching packaging mistakes and stopping
# startup from silently slurping an unbounded package resource.
STDLIB_RESOURCE_MAX_BYTES = 64 * 1024


class StdlibResourceError(RuntimeError):
    """Base class for bounded stdlib package-resource failures."""


class StdlibResourceLimitError(StdlibResourceError):
    """Raised when the bundled stdlib resource exceeds its startup byte budget."""


@dataclass(frozen=True)
class StdlibResourceLoad:
    """Decoded stdlib source plus machine-readable package-resource metadata."""

    text: str
    metadata: dict[str, Any]


def stdlib_resource_contract(*, max_bytes: int = STDLIB_RESOURCE_MAX_BYTES) -> dict[str, Any]:
    """Return the static trust/resource contract for the bundled stdlib."""

    return {
        "schema": STDLIB_RESOURCE_SCHEMA,
        "resource": STDLIB_RESOURCE_NAME,
        "package": STDLIB_RESOURCE_PACKAGE,
        "path": STDLIB_RESOURCE_PATH,
        "source": STDLIB_SOURCE_NAME,
        "trust": "bundled-package-resource",
        "authority": "package-local; not workspace/plugin filesystem authority",
        "max_bytes": int(max_bytes),
        "reader": "importlib.resources.files(...).joinpath(...).open('rb')",
    }


def read_stdlib_resource_bounded(*, max_bytes: int = STDLIB_RESOURCE_MAX_BYTES) -> StdlibResourceLoad:
    """Read the bundled stdlib through a package-resource byte budget.

    ``Traversable.read_text()`` is convenient, but it hides byte accounting inside
    startup.  Reading at most ``max_bytes + 1`` bytes gives the VM a precise
    provenance row and a fail-closed size check before UTF-8 decoding/eval.
    """

    if int(max_bytes) < 1:
        raise ValueError("stdlib resource max_bytes must be positive")
    contract = stdlib_resource_contract(max_bytes=int(max_bytes))
    traversable = importlib_resources.files(STDLIB_RESOURCE_PACKAGE).joinpath(STDLIB_RESOURCE_PATH)
    with traversable.open("rb") as handle:
        data = handle.read(int(max_bytes) + 1)
    if len(data) > int(max_bytes):
        raise StdlibResourceLimitError(
            f"{STDLIB_RESOURCE_NAME} exceeds stdlib resource budget "
            f"({len(data)} > {int(max_bytes)} bytes)"
        )
    text = data.decode("utf-8")
    metadata = dict(contract)
    metadata.update(
        {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    )
    return StdlibResourceLoad(text=text, metadata=metadata)
