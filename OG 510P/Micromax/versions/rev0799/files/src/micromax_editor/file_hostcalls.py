from __future__ import annotations

"""Structured editor file/recovery hostcalls.

The command bar already exposes `save!`, `revert!`, and `diskdiff` for humans.
This module gives plugins and scripts the same recovery lane without parsing
human-facing message strings.
"""

from typing import TYPE_CHECKING

from micromax import VM
from micromax.vm import MicromaxError

from .hostcall_boundary import peek_int_arg, peek_str_arg, pop_int_arg
from .file_scriptops import (
    disk_diff_lines_under_caps,
    disk_state_rows_under_caps,
    disk_state_under_caps,
    revert_buffer_under_caps,
    save_current_buffer_under_caps,
)

if TYPE_CHECKING:  # pragma: no cover - imported only for type checkers
    from .editor import Editor


FILE_HOSTCALL_FEATURES = {
    "ed.disk-state",
    "ed.disk-states",
    "ed.disk-rows",
    "ed.diff",
    "ed.revert",
    "ed.save-info",
    "ed.save-as-info",
}


def _push_result(vm: VM, ok: bool, value: object, err: object = "") -> None:
    vm.stack.append(1 if ok else 0)
    vm.stack.append(value)
    vm.stack.append(str(err or ""))


def install_file_recovery_hostcalls(ed: "Editor") -> None:
    """Install structured, capability-gated file recovery hostcalls."""

    vm: VM = ed.vm
    vm.host_features.update(FILE_HOSTCALL_FEATURES)

    def hc_ed_disk_state(vm: VM) -> None:
        """( -- m ) Return the active buffer disk freshness model."""

        vm.stack.append(disk_state_under_caps(ed))

    def hc_ed_disk_rows(vm: VM) -> None:
        """( include-all -- rows ) Return per-buffer disk freshness rows."""

        include_all = bool(pop_int_arg(vm, "ed.disk-states"))
        vm.stack.append(disk_state_rows_under_caps(ed, include_fresh=include_all))

    def hc_ed_diff(vm: VM) -> None:
        """( max-lines -- ok lines err ) Return disk-vs-buffer unified diff lines."""

        max_lines = pop_int_arg(vm, "ed.diff")
        try:
            lines = disk_diff_lines_under_caps(ed, max_lines=int(max_lines))
            _push_result(vm, True, [str(x) for x in lines], "")
        except MicromaxError:
            raise
        except Exception as e:
            _push_result(vm, False, [], str(e))

    def hc_ed_revert(vm: VM) -> None:
        """( force -- ok info err ) Reload current buffer from disk."""

        force = bool(pop_int_arg(vm, "ed.revert"))
        try:
            info = revert_buffer_under_caps(ed, force=force)
            _push_result(vm, True, dict(info), "")
        except MicromaxError:
            raise
        except Exception as e:
            _push_result(vm, False, {}, str(e))

    def hc_ed_save_info(vm: VM) -> None:
        """( force -- ok info err ) Save current buffer and return structured info."""

        force = bool(pop_int_arg(vm, "ed.save-info"))
        try:
            info = save_current_buffer_under_caps(ed, force=force)
            _push_result(vm, True, dict(info), "")
        except MicromaxError:
            raise
        except Exception as e:
            _push_result(vm, False, {}, str(e))

    def hc_ed_save_as_info(vm: VM) -> None:
        """( path force -- ok info err ) Save current buffer to path with structured info."""

        force = bool(peek_int_arg(vm, "ed.save-as-info", depth=1))
        path = peek_str_arg(vm, "ed.save-as-info", depth=2)
        del vm.stack[-2:]
        try:
            info = save_current_buffer_under_caps(ed, force=force, target=str(path))
            _push_result(vm, True, dict(info), "")
        except MicromaxError:
            raise
        except Exception as e:
            _push_result(vm, False, {}, str(e))

    vm.register_host("ed.disk-state", hc_ed_disk_state)
    vm.register_host("ed.disk-states", hc_ed_disk_rows)
    vm.register_host("ed.disk-rows", hc_ed_disk_rows)
    vm.register_host("ed.diff", hc_ed_diff)
    vm.register_host("ed.revert", hc_ed_revert)
    vm.register_host("ed.save-info", hc_ed_save_info)
    vm.register_host("ed.save-as-info", hc_ed_save_as_info)
