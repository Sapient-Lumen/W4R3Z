from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from .errors import LacunaError
from .sidecars import canonical_json_digest, make_private_directory
from .store import CUBE_CONFIG, DATABASE_NAME, Cube
from .util import atomic_write_json


def clone_cube_exact(
    source: Cube,
    destination: Path,
    *,
    expected_snapshot_sha256: str,
    error_prefix: str,
    kind_label: str,
) -> dict[str, Any]:
    """Create and verify one exact SQLite-backed Cube copy.

    The copy intentionally retains the source cube identity and ledger head.  Callers
    provide a snapshot digest captured before publication, so a copy cannot silently
    bind to a later semantic boundary.  The returned receipt is suitable for a higher
    level sidecar to retain under its own schema.
    """
    make_private_directory(destination)
    atomic_write_json(destination / CUBE_CONFIG, source.config)
    database_path = destination / DATABASE_NAME
    connection = sqlite3.connect(database_path, isolation_level=None)
    try:
        source.conn.backup(connection)
    finally:
        connection.close()
    try:
        os.chmod(database_path, 0o600)
    except OSError:
        pass

    with Cube.open(destination) as clone:
        verification = clone.verify()
        if verification["overall_status"] != "pass":
            raise LacunaError(
                f"{error_prefix}-clone-verification-failed",
                f"{kind_label} failed deterministic verification",
                verification,
            )
        source_cube_id = source.meta("cube_id")
        source_head = source.head()
        if clone.meta("cube_id") != source_cube_id or clone.head() != source_head:
            raise LacunaError(
                f"{error_prefix}-clone-identity-mismatch",
                f"{kind_label} does not match the source cube identity and head",
            )
        snapshot_sha256 = canonical_json_digest(
            clone.snapshot(),
            error_code=f"{error_prefix}-clone-snapshot-invalid",
            label=f"{kind_label} snapshot",
        )
        if snapshot_sha256 != expected_snapshot_sha256:
            raise LacunaError(
                f"{error_prefix}-clone-snapshot-mismatch",
                f"{kind_label} does not match the exact source semantic snapshot",
            )
        return {
            "cube_id": source_cube_id,
            "head": source_head,
            "event_count": clone.event_count(),
            "snapshot_sha256": snapshot_sha256,
            "verification_sha256": canonical_json_digest(
                verification,
                error_code=f"{error_prefix}-clone-verification-invalid",
                label=f"{kind_label} verification",
            ),
            "overall_status": "pass",
        }
