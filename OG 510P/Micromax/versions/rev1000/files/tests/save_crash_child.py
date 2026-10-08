from __future__ import annotations

"""One-process save driver used by the subprocess crash matrix.

This is intentionally not a pytest module.  The parent test starts a fresh
interpreter, requests one exact transaction stage, and the fault callback exits
without unwinding so Python cleanup cannot make the simulated crash safer than a
real process death.
"""

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from micromax_editor.file_write import plan_atomic_write, write_file_bytes
from micromax_editor.recovery_journal import (
    MODE_REPAIR_CONTRACT_V1,
    PRIVATE_ATOMIC_COMMIT_MODE,
    RecoveryJournal,
)
from micromax_editor.save_residue import new_save_lease_id

CRASH_EXIT = 86
NEW_BYTES = b"new payload\n"


def _mark_and_exit(marker: Path, stage: str) -> None:
    fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, stage.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os._exit(CRASH_EXIT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    parser.add_argument("stage")
    parser.add_argument("mode", choices=("atomic", "direct"))
    args = parser.parse_args()

    workspace = Path(args.workspace)
    target = workspace / "document.txt"
    marker = workspace / "crash-stage.txt"

    def fault(stage: str) -> None:
        if stage == args.stage:
            _mark_and_exit(marker, stage)

    journal = RecoveryJournal(workspace / "recovery", fault=fault)
    save_lease_id = new_save_lease_id()
    write_plan = (
        plan_atomic_write(target, preserve_mode=True)
        if args.mode == "atomic"
        else None
    )
    metadata = {"save_lease_id": save_lease_id}
    checkpoint_target = target
    if write_plan is not None:
        checkpoint_target = Path(write_plan.write_path)
        metadata = {
            "save_lease_id": save_lease_id,
            "mode_repair_contract": MODE_REPAIR_CONTRACT_V1,
            "private_commit_mode": format(PRIVATE_ATOMIC_COMMIT_MODE, "04o"),
            "intended_mode": format(write_plan.final_mode, "04o"),
            "target_parent_dev": str(write_plan.parent_dev),
            "target_parent_ino": str(write_plan.parent_ino),
        }
    entry_id = journal.checkpoint(
        checkpoint_target,
        NEW_BYTES,
        buffer_id="crash-matrix",
        commit_content=NEW_BYTES,
        metadata=metadata,
    )

    def writer(authority: Path, payload: bytes) -> None:
        write_file_bytes(
            authority,
            payload,
            atomic=args.mode == "atomic",
            write_plan=write_plan,
            temp_lease_id=save_lease_id,
            fsync=True,
            timeout_seconds=0.0,
            _fault=fault,
        )

    journal.commit_checkpoint(entry_id, NEW_BYTES, writer)
    return 22


if __name__ == "__main__":
    raise SystemExit(main())
