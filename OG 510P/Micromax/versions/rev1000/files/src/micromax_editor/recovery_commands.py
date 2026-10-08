from __future__ import annotations

"""Interactive command surface for interrupted-save recovery."""

from .recovery_journal import RecoveryResidueKind, RecoveryStatus


def _display_path(candidate: object) -> str:
    metadata = getattr(candidate, "metadata", {})
    if isinstance(metadata, dict):
        requested = str(metadata.get("requested_path") or "").strip()
        if requested:
            return requested
    return str(getattr(candidate, "target", "") or "")


def _status_label(candidate: object) -> str:
    status = getattr(candidate, "status", None)
    if bool(getattr(candidate, "mode_repair_available", False)):
        if bool(getattr(candidate, "mode_repair_required", False)):
            return "permission repair required"
        return "permission sync pending"
    if bool(getattr(candidate, "mode_repair_conflict", False)):
        return "permission conflict"
    if status is RecoveryStatus.TARGET_CHANGED:
        return "target changed"
    if status is RecoveryStatus.TARGET_UNREADABLE:
        return "target unreadable"
    if status is RecoveryStatus.ALREADY_PERSISTED:
        return "already persisted"
    return "recoverable"


def c_recoveries(ed: "Editor", args: list[str]) -> bool:
    if args:
        ed.message("usage: recoveries")
        return False
    try:
        scan = ed.interrupted_save_scan()
    except Exception as exc:
        ed.message(f"recoveries: {exc}")
        return False
    candidates = list(scan.candidates)
    count = len(candidates)
    noun = "save" if count == 1 else "saves"
    limits: list[str] = []
    if scan.omitted:
        limits.append(f"omitted={scan.omitted}")
    if scan.truncated:
        limits.append("directory-truncated")
    if scan.corrupt:
        limits.append(f"quarantined={scan.corrupt}")
    if scan.comparison_limited:
        limits.append(f"comparison-limited={scan.comparison_limited}")
    if scan.record_bytes_limited:
        limits.append("record-bytes-limited")
    suffix = " (" + ", ".join(limits) + ")" if limits else ""
    ed.message(f"recoveries: {count} interrupted {noun}{suffix}")
    for index, candidate in enumerate(candidates, 1):
        size = int(getattr(candidate, "payload_size", 0) or 0)
        entry_id = str(getattr(candidate, "entry_id", "") or "")
        mode_note = ""
        current_mode = getattr(candidate, "current_mode", None)
        intended_mode = getattr(candidate, "intended_mode", None)
        if isinstance(current_mode, int) and isinstance(intended_mode, int):
            mode_note = f", mode {current_mode:04o}->{intended_mode:04o}"
        ed.message(
            f"#{index} [{_status_label(candidate)}] "
            f"{_display_path(candidate)} "
            f"({size} bytes{mode_note}, id {entry_id[:12]})"
        )
    return True


def c_recover(ed: "Editor", args: list[str]) -> bool:
    if len(args) > 1:
        ed.message("usage: recover [#N|ID]")
        return False
    query = str(args[0]) if args else None
    try:
        info = ed.open_interrupted_save(query)
    except Exception as exc:
        ed.message(f"recover: {exc}")
        return False
    if bool(info.get("already_persisted", False)):
        entry_id = str(info.get("entry_id") or "")
        if bool(info.get("mode_repair_available", False)):
            current_mode = int(info.get("current_mode") or 0)
            intended_mode = int(info.get("intended_mode") or 0)
            action = "repair" if bool(info.get("mode_repair_required", False)) else "sync"
            ed.message(
                "recover: target contains the saved bytes; permission "
                f"{action} {current_mode:04o}->{intended_mode:04o} is pending; "
                f"journal retained—run `recovermode {entry_id[:12]}`"
            )
            return True
        if bool(info.get("mode_repair_conflict", False)):
            detail = str(info.get("error") or "permission state changed")
            ed.message(
                "recover: target contains the saved bytes, but permission repair "
                f"was refused ({detail}); journal retained"
            )
            return False
        ed.message(
            "recover: target already contains the saved bytes; retired "
            f"{entry_id[:12]}"
        )
        return True
    buffer_name = str(info.get("buffer") or "")
    path = str(info.get("path") or "")
    message = f"recover: opened {buffer_name} as a dirty buffer; disk unchanged"
    if bool(info.get("requires_force", False)):
        message += "; target changed—review diff, then use save! or saveas"
    elif bool(info.get("nominal_moved", False)):
        if path:
            message += f"; original path moved, bound to {path}"
        else:
            message += "; target authority moved, use saveas FILE"
    ed.message(message)
    return True


def c_recovermode(ed: "Editor", args: list[str]) -> bool:
    if len(args) > 1:
        ed.message("usage: recovermode [#N|ID]")
        return False
    query = str(args[0]) if args else None
    try:
        info = ed.repair_interrupted_save_mode(query)
    except Exception as exc:
        ed.message(f"recovermode: {exc}")
        return False
    previous_mode = int(info.get("previous_mode") or 0)
    intended_mode = int(info.get("intended_mode") or 0)
    action = "restored" if bool(info.get("changed", False)) else "verified"
    message = (
        f"recovermode: {action} {previous_mode:04o}->{intended_mode:04o}; "
        "file and directory synchronization attempted"
    )
    if not bool(info.get("recovery_retired", False)):
        detail = str(info.get("cleanup_error") or "journal cleanup incomplete")
        message += f"; recovery record retained ({detail})"
    ed.message(message)
    return True


def c_recovertemps(ed: "Editor", args: list[str]) -> bool:
    """List bounded private save residue without opening document bytes."""

    if args:
        ed.message("usage: recovertemps")
        return False
    try:
        scan = ed.interrupted_save_residue_scan()
    except Exception as exc:
        ed.message(f"recovertemps: {exc}")
        return False

    residues = list(scan.residues)
    count = len(residues)
    noun = "temp" if count == 1 else "temps"
    limits: list[str] = []
    if scan.omitted:
        limits.append(f"omitted={scan.omitted}")
    if scan.truncated:
        limits.append("inventory-truncated")
    if scan.records_omitted:
        limits.append(f"records-omitted={scan.records_omitted}")
    if scan.record_bytes_limited:
        limits.append("record-bytes-limited")
    if scan.unreadable_directories:
        limits.append(f"directories-unreadable={scan.unreadable_directories}")
    suffix = " (" + ", ".join(limits) + ")" if limits else ""
    eligible = sum(1 for row in residues if row.cleanup_eligible)
    ed.message(
        f"recovertemps: {count} private save {noun}, "
        f"{eligible} cleanup eligible{suffix}"
    )
    for index, residue in enumerate(residues, 1):
        kind = (
            "checkpoint"
            if residue.kind is RecoveryResidueKind.CHECKPOINT_TEMP
            else "document"
        )
        state = residue.owner_state.value
        cleanup = "cleanup eligible" if residue.cleanup_eligible else residue.reason
        mode = f"{int(residue.mode):04o}"
        ed.message(
            f"#{index} [{state}; {cleanup}] {kind} {residue.path} "
            f"({residue.size} bytes, mode {mode}, id {residue.residue_id[:12]})"
        )
    return True


def c_recoverclean(ed: "Editor", args: list[str]) -> bool:
    """Explicitly remove one inventoried and revalidated stale private temp."""

    if len(args) > 1:
        ed.message("usage: recoverclean [#N|ID]")
        return False
    query = str(args[0]) if args else None
    try:
        info = ed.cleanup_interrupted_save_residue(query)
    except Exception as exc:
        ed.message(f"recoverclean: {exc}")
        return False
    sync = (
        "directory synced"
        if bool(info.get("directory_synced", False))
        else "directory sync unsupported"
    )
    ed.message(
        f"recoverclean: removed {str(info.get('residue_id') or '')[:12]} "
        f"({sync}) from {str(info.get('path') or '')}"
    )
    return True


def c_recoverdismiss(ed: "Editor", args: list[str]) -> bool:
    if len(args) > 1:
        ed.message("usage: recoverdismiss [#N|ID]")
        return False
    query = str(args[0]) if args else None
    try:
        info = ed.dismiss_interrupted_save(query)
    except Exception as exc:
        ed.message(f"recoverdismiss: {exc}")
        return False
    ed.message(
        f"recoverdismiss: discarded {str(info.get('entry_id') or '')[:12]} "
        f"for {str(info.get('path') or '')}"
    )
    return True
