from __future__ import annotations

import json
import os
import math
import random
import re
import shutil
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from typing import Any, Optional

from rich.console import Console

from vhk.core.events import EventLogger, make_default_eventlog_path
from vhk.core.expr import eval_expr, interpolate
from vhk.project.macro_proof_contract import summarize_macro_proof_contract
from vhk.project.desktop_session_contract import summarize_desktop_session_contract

from vhk.core.models import (
    Project,
    Step,
    StepCallMacro,
    StepBreak,
    StepContinue,
    StepReturn,
    StepCaptureScreenshot,
    StepCoordMode,
    StepImageSearch,
    StepImageSearchAll,
    StepWaitForImage,
    StepWaitForImageAll,
    StepWaitForImageVanish,
    StepPixelSearch,
    StepPixelSearchAll,
    StepWaitForPixel,
    StepWaitForPixelAll,
    StepWaitForPixelVanish,
    StepVisualAssert,
    StepVisualVerify,
    StepWaitForRegionChange,
    StepWaitForRegionStable,
    StepOcrReadText,
    StepOcrNeedleText,
    StepWaitForNeedleText,
    StepWaitForText,
    StepWaitForTextVanish,
    StepAssertText,
    StepOcrFindTextFile,
    StepOcrFindTextAllFile,
    StepOcrFindText,
    StepOcrFindTextAll,
    StepWaitForTextBox,
    StepClickText,
    StepClickTextAll,
    StepClickPixelAll,
    StepClickImageAll,
    StepMouseClickAt,
    StepClickNeedle,
    StepClipboardRead,
    StepClipboardSet,
    StepWaitForClipboardChange,
    StepWaitForClipboardEvent,
    StepPasteClipboard,
    StepOpenUrl,
    StepComposeEmail,
    StepHttpRequest,
    StepWaitForHttp,
    StepDownloadFile,
    StepShowMessage,
    StepAskYesNo,
    StepInputBox,
    StepPromptForm,
    StepChooseFromList,
    StepStartProcess,
    StepWaitForProcessExit,
    StepKillProcess,
    StepRegexReplace,
    StepTrimText,
    StepSplitText,
    StepJoinText,
    StepForEach,
    StepReadCsv,
    StepWriteCsv,
    StepReadJson,
    StepWriteJson,
    StepReadFile,
    StepWriteFile,
    StepAppendFile,
    StepListDirectory,
    StepWaitForFile,
    StepWaitForNewFile,
    StepWaitForFileEvent,
    StepWaitForDownload,
    StepDelay,
    StepFocusWindow,
    StepIf,
    StepWhile,
    StepWaitUntil,
    StepWaitForBusEvent,
    StepWaitForDbusSignal,
    StepTry,
    StepI3Command,
    StepI3GetTree,
    StepI3GetWorkspaces,
    StepImageSearchFile,
    StepImageSearchAllFile,
    StepKey,
    StepKeyDown,
    StepKeyUp,
    StepResetModifiers,
    StepLog,
    StepMouseClick,
    StepMouseDrag,
    StepMouseWheel,
    StepCursorHide,
    StepCursorShow,
    StepGetCursorPos,
    StepGetActiveWindow,
    StepGetWindowAtCursor,
    StepGetWindowList,
    StepGetIdleMs,
    StepGetSystemdUnitState,
    StepWaitForSystemdUnitState,
    StepWaitForIdle,
    StepWaitForUserActivity,
    StepMouseMove,
    StepNotify,
    StepOcrReadTextFile,
    StepPixelSearchFile,
    StepPixelSearchAllFile,
    StepPixelGetColorFile,
    StepRandomWait,
    StepRunShell,
    StepSetVar,
    StepTypeText,
    StepWaitForImageFile,
    StepWaitForPixelFile,
    StepPixelGetColor,
    StepWaitForWindowEvent,
    StepWaitForWindow,
    StepWaitForWindowVanish,
)
from vhk.core.panic import PanicConfig, PanicStop, is_panicking
from vhk.i3.ipc import I3Connection
from vhk.i3.tree import find_first
from vhk.system import clipboard as clipboard_mod
from vhk.system.event_bus import event_text as bus_event_text, get_bus_socket_path, wait_for_bus_event
from vhk.system import files as files_mod
from vhk.system import input as input_mod
from vhk.system import cursor as cursor_mod
from vhk.system import display as display_mod
import vhk.system.cursor_pos as cursor_pos_mod
from vhk.system import idle as idle_mod
from vhk.system import notify as notify_mod
from vhk.system import openers as openers_mod
from vhk.system import network as network_mod
from vhk.system import dialogs as dialogs_mod
from vhk.system import processes as processes_mod
from vhk.system import screenshot as screenshot_mod
from vhk.system import watch as watch_mod
from vhk.system import textops as text_mod
from vhk.system.fuzzy import fuzzy_score, normalize_text
from vhk.project.prompt_profiles import apply_saved_answers, make_prompt_profile_store, sanitize_prompt_answers
from vhk.system.session import set_preferred_backend
from vhk.system import active_window as active_window_mod
from vhk.system import dbus_bridge as dbus_bridge_mod
from vhk.system import wm_events as wm_events_mod
import vhk.system.systemd_units as systemd_units_mod
from vhk.system.active_window import ActiveWindowProbeError, get_active_window_geometry
from vhk.vision.match import image_search_all_file, image_search_file
from vhk.vision.assets import compute_click_offset, scale_needle, try_load_needle
from vhk.vision.ocr import (
    ocr_find_text_file,
    ocr_find_text_in_spans,
    ocr_find_text_all_in_spans,
    ocr_read_spans_file,
    ocr_read_text_file,
    ocr_spans_to_text,
)
from vhk.vision.pixel import PixelSearchNoMatch, pixel_search_file, pixel_search_all_file, pixel_get_color_file
from vhk.vision.compare import visual_compare_file, write_visual_diff_image


@dataclass
class RunResult:
    ok: bool
    error: str | None = None
    vars: dict[str, Any] | None = None
    event_log: str | None = None


class _ControlFlowSignal(Exception):
    pass


class _BreakSignal(_ControlFlowSignal):
    pass


class _ContinueSignal(_ControlFlowSignal):
    pass


class _ReturnSignal(_ControlFlowSignal):
    def __init__(self, out_var: str, value: Any | None):
        super().__init__(out_var)
        self.out_var = out_var
        self.value = value


class Runner:
    def __init__(
        self,
        project: Project,
        console: Console | None = None,
        *,
        step_mode: bool = False,
        input_func=input,
        prompt_profile: str | None = None,
        save_prompt_profile: str | None = None,
    ):
        self.project = project
        self.console = console or Console()
        self._event_logger: Optional[EventLogger] = None
        self._panic_cfg = PanicConfig(panic_file=self.project.settings.panic_file)
        self.step_mode = bool(step_mode)
        self._input_func = input_func
        self._last_capture_path: str | None = None
        self._processes: dict[int, Any] = {}
        self._cursor_handle = None
        self._prompt_profile = prompt_profile
        self._save_prompt_profile = save_prompt_profile
        self._prompt_store = make_prompt_profile_store(self.project.root_dir, self.project.settings.prompt_profile_store)

        # AHK-style coordinate modes (CoordMode). These affect subsequent steps.
        # Defaults match common automation expectations: screen-absolute.
        self._coord_mode_pixel: str = "screen"
        self._coord_mode_mouse: str = "screen"

        # Make backend choice available to all system modules.
        set_preferred_backend(self.project.settings.desktop_backend)

    def run(self, macro_name: str, initial_vars: dict[str, Any] | None = None) -> RunResult:
        macro = self.project.macros[macro_name]
        ctx: dict[str, Any] = {"project": {"name": self.project.name}, "macro": {"name": macro.name}}
        if initial_vars:
            ctx.update(initial_vars)

        # Run timestamps: useful for wait steps that care about "new" artifacts.
        ctx["_run_started_ts"] = time.time()
        try:
            ctx["_run_started_ns"] = time.time_ns()
        except Exception:
            ctx["_run_started_ns"] = int(time.time() * 1e9)

        run_id = time.strftime("%Y%m%d_%H%M%S") + f"_{int(time.time()*1000)%1000:03d}"
        log_dir = Path(self.project.root_dir) / self.project.settings.log_dir
        if self.project.settings.event_log:
            self._event_logger = EventLogger(make_default_eventlog_path(log_dir, run_id))
            try:
                macro_proof_contract = summarize_macro_proof_contract(self.project.root_dir, macro_name)
            except Exception:
                macro_proof_contract = None
            try:
                desktop_session_contract = summarize_desktop_session_contract()
            except Exception:
                desktop_session_contract = None
            self._event_logger.emit(
                "run_start",
                run_id=run_id,
                project=self.project.name,
                macro=macro_name,
                initial_vars=list((initial_vars or {}).keys()),
                dry_run=bool(self.project.settings.dry_run),
                macro_proof_contract=macro_proof_contract,
                desktop_session_contract=desktop_session_contract,
            )

        try:
            if self.project.settings.hide_cursor_during_run and not self.project.settings.dry_run:
                self._cursor_handle = cursor_mod.hide_cursor()
                self._emit("cursor", action="hide", reason="run_setting", backend=self._cursor_handle.backend)
            self._run_steps(macro.steps, ctx, macro_name=macro_name, path_prefix=[])  # type: ignore[arg-type]
            if self._event_logger:
                self._event_logger.emit("run_end", run_id=run_id, ok=True)
            return RunResult(ok=True, vars=ctx, event_log=str(self._event_logger.path) if self._event_logger else None)
        except _ReturnSignal as r:
            ctx[r.out_var] = r.value
            if self._event_logger:
                self._event_logger.emit("run_end", run_id=run_id, ok=True, returned=True, out_var=r.out_var)
            return RunResult(ok=True, vars=ctx, event_log=str(self._event_logger.path) if self._event_logger else None)
        except Exception as e:
            if self._event_logger:
                self._event_logger.emit("run_end", run_id=run_id, ok=False, error=str(e))
            return RunResult(
                ok=False,
                error=str(e),
                vars=ctx,
                event_log=str(self._event_logger.path) if self._event_logger else None,
            )
        finally:
            if self._cursor_handle is not None:
                cursor_mod.show_cursor(self._cursor_handle)
                self._emit("cursor", action="show", reason="run_end", backend=getattr(self._cursor_handle, "backend", None))
                self._cursor_handle = None

    # ---------------------------------------------------------------------

    def _check_panic(self) -> None:
        if is_panicking(self._panic_cfg):
            raise PanicStop(f"Panic file present: {self._panic_cfg.panic_file}")

    def _emit(self, event_type: str, **fields: Any) -> None:
        if self._event_logger:
            self._event_logger.emit(event_type, **fields)

    def _emit_wait_attempt(self, kind: str, **fields: Any) -> None:
        if self.project.settings.trace_wait_attempts:
            self._emit("wait_attempt", kind=kind, **fields)

    def _compute_wait_poll(self, step: Any) -> tuple[int, int]:
        """Return (poll_ms, max_poll_ms) for a wait step.

        Many wait-style steps support an optional scan_rate_hz (SikuliX-style
        "scans per second") which takes precedence over poll_ms when set.
        """

        scan_rate = getattr(step, "scan_rate_hz", None)
        if scan_rate is not None:
            hz = float(scan_rate)
            if hz <= 0:
                raise ValueError("scan_rate_hz must be > 0")
            poll_ms = int(round(1000.0 / hz))
            poll_ms = max(0, poll_ms)
            return poll_ms, poll_ms

        poll = max(0, int(getattr(step, "poll_ms", 0) or 0))
        max_poll = max(0, int(getattr(step, "max_poll_ms", poll) or 0))
        return poll, max_poll

    def _write_error_context(self, *, macro_name: str, step_id: str, step_type: str, error: Exception) -> dict[str, Any]:
        diag: dict[str, Any] = {"error": str(error), "error_type": type(error).__name__}
        root = Path(self.project.root_dir)
        log_dir = root / self.project.settings.log_dir
        base = log_dir / f"error_{macro_name}_{step_id}"

        capture_src = Path(self._last_capture_path).expanduser() if self._last_capture_path else None
        if self.project.settings.screenshot_on_error:
            try:
                screenshot_path = base.with_suffix(".png")
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                if capture_src and capture_src.exists():
                    shutil.copy2(capture_src, screenshot_path)
                else:
                    screenshot_mod.capture(screenshot_path)
                diag["screenshot"] = str(screenshot_path)
            except Exception as se:
                diag["screenshot_error"] = str(se)

        try:
            context_path = base.with_suffix(".json")
            payload = {
                "macro": macro_name,
                "step_id": step_id,
                "step_type": step_type,
                "error": str(error),
                "error_type": type(error).__name__,
                "last_capture": str(capture_src) if capture_src else None,
            }
            context_path.parent.mkdir(parents=True, exist_ok=True)
            context_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            diag["error_context"] = str(context_path)
        except Exception as se:
            diag["error_context_error"] = str(se)

        return diag

    def _dispatch_step(self, step: Step, ctx: dict[str, Any], macro_name: str, step_path: list[int]) -> None:
        if isinstance(step, StepDelay):
            self._exec_delay(step, ctx)
        elif isinstance(step, StepRandomWait):
            self._exec_random_wait(step, ctx)
        elif isinstance(step, StepLog):
            self._exec_log(step, ctx)
        elif isinstance(step, StepSetVar):
            self._exec_setvar(step, ctx)
        elif isinstance(step, StepRunShell):
            self._exec_runshell(step, ctx)
        elif isinstance(step, StepIf):
            self._exec_if(step, ctx, macro_name, step_path)
        elif isinstance(step, StepWhile):
            self._exec_while(step, ctx, macro_name, step_path)
        elif isinstance(step, StepWaitUntil):
            self._exec_wait_until(step, ctx, macro_name, step_path)
        elif isinstance(step, StepWaitForBusEvent):
            self._exec_wait_for_bus_event(step, ctx, macro_name, step_path)
        elif isinstance(step, StepWaitForDbusSignal):
            self._exec_wait_for_dbus_signal(step, ctx)
        elif isinstance(step, StepTry):
            self._exec_try(step, ctx, macro_name, step_path)
        elif isinstance(step, StepBreak):
            self._exec_break(step, ctx)
        elif isinstance(step, StepContinue):
            self._exec_continue(step, ctx)
        elif isinstance(step, StepReturn):
            self._exec_return(step, ctx)
        elif isinstance(step, StepImageSearchFile):
            self._exec_image_search_file(step, ctx)
        elif isinstance(step, StepImageSearchAllFile):
            self._exec_image_search_all_file(step, ctx)
        elif isinstance(step, StepWaitForImageFile):
            self._exec_wait_for_image_file(step, ctx)
        elif isinstance(step, StepPixelSearchFile):
            self._exec_pixel_search_file(step, ctx)
        elif isinstance(step, StepPixelSearchAllFile):
            self._exec_pixel_search_all_file(step, ctx)
        elif isinstance(step, StepWaitForPixelFile):
            self._exec_wait_for_pixel_file(step, ctx)
        elif isinstance(step, StepPixelGetColorFile):
            self._exec_pixel_get_color_file(step, ctx)
        elif isinstance(step, StepOcrReadTextFile):
            self._exec_ocr_file(step, ctx)
        elif isinstance(step, StepOcrFindTextFile):
            self._exec_ocr_find_text_file(step, ctx)
        elif isinstance(step, StepOcrFindTextAllFile):
            self._exec_ocr_find_text_all_file(step, ctx)
        elif isinstance(step, StepCaptureScreenshot):
            self._exec_capture_screenshot(step, ctx)
        elif isinstance(step, StepCoordMode):
            self._exec_coord_mode(step, ctx)
        elif isinstance(step, StepImageSearch):
            self._exec_image_search(step, ctx)
        elif isinstance(step, StepImageSearchAll):
            self._exec_image_search_all(step, ctx)
        elif isinstance(step, StepWaitForImage):
            self._exec_wait_for_image(step, ctx)
        elif isinstance(step, StepWaitForImageAll):
            self._exec_wait_for_image_all(step, ctx)
        elif isinstance(step, StepWaitForImageVanish):
            self._exec_wait_for_image_vanish(step, ctx)
        elif isinstance(step, StepPixelSearch):
            self._exec_pixel_search(step, ctx)
        elif isinstance(step, StepPixelSearchAll):
            self._exec_pixel_search_all(step, ctx)
        elif isinstance(step, StepWaitForPixel):
            self._exec_wait_for_pixel(step, ctx)
        elif isinstance(step, StepWaitForPixelAll):
            self._exec_wait_for_pixel_all(step, ctx)
        elif isinstance(step, StepWaitForPixelVanish):
            self._exec_wait_for_pixel_vanish(step, ctx)
        elif isinstance(step, StepPixelGetColor):
            self._exec_pixel_get_color(step, ctx)
        elif isinstance(step, StepOcrReadText):
            self._exec_ocr(step, ctx)
        elif isinstance(step, StepOcrNeedleText):
            self._exec_ocr_needle_text(step, ctx)
        elif isinstance(step, StepWaitForNeedleText):
            self._exec_wait_for_needle_text(step, ctx)
        elif isinstance(step, StepOcrFindText):
            self._exec_ocr_find_text(step, ctx)
        elif isinstance(step, StepOcrFindTextAll):
            self._exec_ocr_find_text_all(step, ctx)
        elif isinstance(step, StepVisualAssert):
            self._exec_visual_assert(step, ctx)
        elif isinstance(step, StepVisualVerify):
            self._exec_visual_verify(step, ctx)
        elif isinstance(step, StepWaitForRegionChange):
            self._exec_wait_for_region_change(step, ctx)
        elif isinstance(step, StepWaitForRegionStable):
            self._exec_wait_for_region_stable(step, ctx)
        elif isinstance(step, StepWaitForText):
            self._exec_wait_for_text(step, ctx)
        elif isinstance(step, StepWaitForTextVanish):
            self._exec_wait_for_text_vanish(step, ctx)
        elif isinstance(step, StepWaitForTextBox):
            self._exec_wait_for_text_box(step, ctx)
        elif isinstance(step, StepAssertText):
            self._exec_assert_text(step, ctx)
        elif isinstance(step, StepClickText):
            self._exec_click_text(step, ctx)
        elif isinstance(step, StepClickTextAll):
            self._exec_click_text_all(step, ctx)
        elif isinstance(step, StepClickPixelAll):
            self._exec_click_pixel_all(step, ctx)
        elif isinstance(step, StepClickImageAll):
            self._exec_click_image_all(step, ctx)
        elif isinstance(step, StepClickNeedle):
            self._exec_click_needle(step, ctx)
        elif isinstance(step, StepKey):
            self._exec_key(step, ctx)
        elif isinstance(step, StepKeyDown):
            self._exec_keydown(step, ctx)
        elif isinstance(step, StepKeyUp):
            self._exec_keyup(step, ctx)
        elif isinstance(step, StepResetModifiers):
            self._exec_reset_modifiers(step, ctx)
        elif isinstance(step, StepTypeText):
            self._exec_type(step, ctx)
        elif isinstance(step, StepMouseMove):
            self._exec_mousemove(step, ctx)
        elif isinstance(step, StepMouseClick):
            self._exec_mouseclick(step, ctx)
        elif isinstance(step, StepMouseDrag):
            self._exec_mousedrag(step, ctx)
        elif isinstance(step, StepMouseWheel):
            self._exec_mousewheel(step, ctx)
        elif isinstance(step, StepCursorHide):
            self._exec_cursor_hide(step, ctx)
        elif isinstance(step, StepCursorShow):
            self._exec_cursor_show(step, ctx)
        elif isinstance(step, StepGetCursorPos):
            self._exec_get_cursor_pos(step, ctx)
        elif isinstance(step, StepGetActiveWindow):
            self._exec_get_active_window(step, ctx)
        elif isinstance(step, StepGetWindowAtCursor):
            self._exec_get_window_at_cursor(step, ctx)
        elif isinstance(step, StepGetWindowList):
            self._exec_get_window_list(step, ctx)
        elif isinstance(step, StepGetIdleMs):
            self._exec_get_idle_ms(step, ctx)
        elif isinstance(step, StepGetSystemdUnitState):
            self._exec_get_systemd_unit_state(step, ctx)
        elif isinstance(step, StepWaitForSystemdUnitState):
            self._exec_wait_for_systemd_unit_state(step, ctx)
        elif isinstance(step, StepWaitForIdle):
            self._exec_wait_for_idle(step, ctx)
        elif isinstance(step, StepWaitForUserActivity):
            self._exec_wait_for_user_activity(step, ctx)
        elif isinstance(step, StepMouseClickAt):
            self._exec_mouseclickat(step, ctx)
        elif isinstance(step, StepNotify):
            self._exec_notify(step, ctx)
        elif isinstance(step, StepClipboardRead):
            self._exec_clipboard_read(step, ctx)
        elif isinstance(step, StepClipboardSet):
            self._exec_clipboard_set(step, ctx)
        elif isinstance(step, StepWaitForClipboardChange):
            self._exec_wait_for_clipboard_change(step, ctx)
        elif isinstance(step, StepWaitForClipboardEvent):
            self._exec_wait_for_clipboard_event(step, ctx)
        elif isinstance(step, StepPasteClipboard):
            self._exec_paste_clipboard(step, ctx)
        elif isinstance(step, StepOpenUrl):
            self._exec_open_url(step, ctx)
        elif isinstance(step, StepComposeEmail):
            self._exec_compose_email(step, ctx)
        elif isinstance(step, StepHttpRequest):
            self._exec_http_request(step, ctx)
        elif isinstance(step, StepWaitForHttp):
            self._exec_wait_for_http(step, ctx)
        elif isinstance(step, StepDownloadFile):
            self._exec_download_file(step, ctx)
        elif isinstance(step, StepShowMessage):
            self._exec_show_message(step, ctx)
        elif isinstance(step, StepAskYesNo):
            self._exec_ask_yes_no(step, ctx)
        elif isinstance(step, StepInputBox):
            self._exec_input_box(step, ctx)
        elif isinstance(step, StepPromptForm):
            self._exec_prompt_form(step, ctx)
        elif isinstance(step, StepChooseFromList):
            self._exec_choose_from_list(step, ctx)
        elif isinstance(step, StepStartProcess):
            self._exec_start_process(step, ctx)
        elif isinstance(step, StepWaitForProcessExit):
            self._exec_wait_for_process_exit(step, ctx)
        elif isinstance(step, StepKillProcess):
            self._exec_kill_process(step, ctx)
        elif isinstance(step, StepRegexReplace):
            self._exec_regex_replace(step, ctx)
        elif isinstance(step, StepTrimText):
            self._exec_trim_text(step, ctx)
        elif isinstance(step, StepSplitText):
            self._exec_split_text(step, ctx)
        elif isinstance(step, StepJoinText):
            self._exec_join_text(step, ctx)
        elif isinstance(step, StepForEach):
            self._exec_foreach(step, ctx, macro_name, step_path)
        elif isinstance(step, StepReadCsv):
            self._exec_read_csv(step, ctx)
        elif isinstance(step, StepWriteCsv):
            self._exec_write_csv(step, ctx)
        elif isinstance(step, StepReadJson):
            self._exec_read_json(step, ctx)
        elif isinstance(step, StepWriteJson):
            self._exec_write_json(step, ctx)
        elif isinstance(step, StepReadFile):
            self._exec_read_file(step, ctx)
        elif isinstance(step, StepWriteFile):
            self._exec_write_file(step, ctx)
        elif isinstance(step, StepAppendFile):
            self._exec_append_file(step, ctx)
        elif isinstance(step, StepListDirectory):
            self._exec_list_directory(step, ctx)
        elif isinstance(step, StepWaitForFile):
            self._exec_wait_for_file(step, ctx)
        elif isinstance(step, StepWaitForNewFile):
            self._exec_wait_for_new_file(step, ctx)
        elif isinstance(step, StepWaitForFileEvent):
            self._exec_wait_for_file_event(step, ctx)
        elif isinstance(step, StepWaitForDownload):
            self._exec_wait_for_download(step, ctx)
        elif isinstance(step, StepI3Command):
            self._exec_i3_command(step, ctx)
        elif isinstance(step, StepI3GetTree):
            self._exec_i3_get_tree(step, ctx)
        elif isinstance(step, StepI3GetWorkspaces):
            self._exec_i3_get_workspaces(step, ctx)
        elif isinstance(step, StepWaitForWindowEvent):
            self._exec_wait_for_window_event(step, ctx)
        elif isinstance(step, StepWaitForWindow):
            self._exec_wait_for_window(step, ctx)
        elif isinstance(step, StepWaitForWindowVanish):
            self._exec_wait_for_window_vanish(step, ctx)
        elif isinstance(step, StepFocusWindow):
            self._exec_focus_window(step, ctx)
        elif isinstance(step, StepCallMacro):
            self._exec_call_macro(step, ctx, macro_name, step_path)
        else:
            raise NotImplementedError(f"Unknown step type: {step.type}")

    def _run_steps(self, steps: list[Step], ctx: dict[str, Any], macro_name: str, path_prefix: list[int]) -> None:
        for idx, step in enumerate(steps):
            if not step.enabled:
                continue

            for rep in range(max(1, step.repeat)):
                self._check_panic()

                effective_step_delay = self._profile_scale_delay_ms(step.delay_ms)
                if effective_step_delay:
                    time.sleep(effective_step_delay / 1000.0)

                step_path = path_prefix + [idx]
                step_id = ".".join(str(x) for x in step_path)

                if self.step_mode:
                    desc = f"{step.type}"
                    if step.comment:
                        desc += f"  # {step.comment}"
                    self.console.print(f"[cyan]STEP {step_id}[/cyan] {desc}")
                    ans = str(self._input_func("Press Enter to run, or q to quit: ")).strip().lower()
                    if ans in {"q", "quit", "exit"}:
                        raise RuntimeError("Stopped by user")

                retries_left = max(0, int(step.retry_count))
                retry_delay_ms = max(0, int(step.retry_delay_ms))
                attempt = 0

                while True:
                    attempt += 1
                    started = time.time()
                    self._emit(
                        "step_start",
                        macro=macro_name,
                        step_id=step_id,
                        step_type=step.type,
                        repeat=rep,
                        attempt=attempt,
                        comment=step.comment,
                    )

                    try:
                        self._dispatch_step(step, ctx, macro_name, step_path)
                        self._emit(
                            "step_end",
                            macro=macro_name,
                            step_id=step_id,
                            step_type=step.type,
                            ok=True,
                            attempt=attempt,
                            duration_ms=int((time.time() - started) * 1000),
                        )
                        break
                    except PanicStop:
                        raise
                    except _ControlFlowSignal as cf:
                        fields = {
                            "macro": macro_name,
                            "step_id": step_id,
                            "step_type": step.type,
                            "ok": True,
                            "attempt": attempt,
                            "duration_ms": int((time.time() - started) * 1000),
                        }
                        if isinstance(cf, _BreakSignal):
                            fields["control_flow"] = "break"
                        elif isinstance(cf, _ContinueSignal):
                            fields["control_flow"] = "continue"
                        elif isinstance(cf, _ReturnSignal):
                            fields["control_flow"] = "return"
                            fields["out_var"] = cf.out_var
                        self._emit("step_end", **fields)
                        raise
                    except Exception as e:
                        diag = self._write_error_context(
                            macro_name=macro_name,
                            step_id=step_id,
                            step_type=step.type,
                            error=e,
                        )
                        duration_ms = int((time.time() - started) * 1000)

                        if retries_left > 0:
                            self._emit(
                                "step_retry",
                                macro=macro_name,
                                step_id=step_id,
                                step_type=step.type,
                                attempt=attempt,
                                retries_left=retries_left - 1,
                                retry_delay_ms=retry_delay_ms,
                                **diag,
                            )
                            if retry_delay_ms > 0:
                                sleep_ms = int(retry_delay_ms)
                                if getattr(step, "retry_jitter", "none") == "full":
                                    sleep_ms = random.randint(0, max(0, sleep_ms))
                                jitter_ms = int(getattr(step, "retry_jitter_ms", 0) or 0)
                                if jitter_ms:
                                    sleep_ms = max(0, sleep_ms + random.randint(-jitter_ms, jitter_ms))
                                time.sleep(sleep_ms / 1000.0)
                            retries_left -= 1
                            if retry_delay_ms > 0 and float(step.retry_backoff) != 1.0:
                                retry_delay_ms = int(max(0, round(retry_delay_ms * float(step.retry_backoff))))
                            continue

                        if step.continue_on_error:
                            err = {
                                "macro": macro_name,
                                "step_id": step_id,
                                "step_type": step.type,
                                "error": str(e),
                                "error_type": type(e).__name__,
                                "attempt": attempt,
                            }
                            ctx["last_error"] = err
                            ctx.setdefault("errors", []).append(err)
                            self._emit(
                                "step_end",
                                macro=macro_name,
                                step_id=step_id,
                                step_type=step.type,
                                ok=False,
                                continued=True,
                                attempt=attempt,
                                duration_ms=duration_ms,
                                **diag,
                            )
                            break

                        self._emit(
                            "step_end",
                            macro=macro_name,
                            step_id=step_id,
                            step_type=step.type,
                            ok=False,
                            attempt=attempt,
                            duration_ms=duration_ms,
                            **diag,
                        )
                        raise

    # ---------------------------------------------------------------------

    def _exec_delay(self, step: StepDelay, ctx: dict[str, Any]) -> None:
        ms = self._as_int(step.ms, ctx, field='Delay.ms')
        time.sleep(ms / 1000.0)

    def _exec_random_wait(self, step: StepRandomWait, ctx: dict[str, Any]) -> None:
        min_ms = self._as_int(step.min_ms, ctx, field='RandomWait.min_ms')
        max_ms = self._as_int(step.max_ms, ctx, field='RandomWait.max_ms')
        if min_ms > max_ms:
            raise ValueError('RandomWait: min_ms must be <= max_ms')
        ms = random.randint(min_ms, max_ms)
        time.sleep(ms / 1000.0)

    def _exec_log(self, step: StepLog, ctx: dict[str, Any]) -> None:
        msg = interpolate(step.message, ctx)
        self.console.print(msg)

    def _exec_setvar(self, step: StepSetVar, ctx: dict[str, Any]) -> None:
        ctx[step.name] = self._eval_or_render(step.value, ctx)

    def _exec_runshell(self, step: StepRunShell, ctx: dict[str, Any]) -> None:
        cmd = interpolate(step.command, ctx)
        if self.project.settings.dry_run:
            ctx["last_cmd"] = {"command": cmd, "returncode": 0, "stdout": "", "stderr": "", "dry_run": True}
            self._emit("shell", command=cmd, dry_run=True)
            return

        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        ctx["last_cmd"] = {
            "command": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
        self._emit("shell", command=cmd, returncode=proc.returncode)
        if step.check and proc.returncode != 0:
            raise RuntimeError(f"Command failed ({proc.returncode}): {cmd}\n{proc.stderr}")

    def _exec_if(self, step: StepIf, ctx: dict[str, Any], macro_name: str, path_prefix: list[int]) -> None:
        cond = interpolate(step.condition, ctx)
        ok = bool(eval_expr(cond, ctx))
        self.console.print(f"[dim]IF {cond} -> {ok}[/dim]")
        self._emit("if_eval", macro=macro_name, step_id=".".join(map(str, path_prefix)), condition=cond, result=ok)
        self._run_steps(step.then_steps if ok else step.else_steps, ctx, macro_name=macro_name, path_prefix=path_prefix + [0 if ok else 1])

    def _exec_while(self, step: StepWhile, ctx: dict[str, Any], macro_name: str, path_prefix: list[int]) -> None:
        step_id = ".".join(map(str, path_prefix))
        iterations = 0
        self._emit("while_start", macro=macro_name, step_id=step_id, condition=step.condition, max_iterations=step.max_iterations)
        while True:
            cond = interpolate(step.condition, ctx)
            ok = bool(eval_expr(cond, ctx))
            self._emit("while_eval", macro=macro_name, step_id=step_id, iteration=iterations, condition=cond, result=ok)
            if not ok:
                break
            if iterations >= int(step.max_iterations):
                raise RuntimeError(f"While exceeded max_iterations={step.max_iterations}")
            try:
                self._run_steps(step.steps, ctx, macro_name=macro_name, path_prefix=path_prefix + [iterations])
            except _ContinueSignal:
                iterations += 1
                continue
            except _BreakSignal:
                iterations += 1
                break
            iterations += 1
        ctx[step.out_iterations] = iterations
        self._emit("while_end", macro=macro_name, step_id=step_id, iterations=iterations)

    def _exec_wait_until(self, step: StepWaitUntil, ctx: dict[str, Any], macro_name: str, path_prefix: list[int]) -> None:
        step_id = ".".join(map(str, path_prefix))
        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last_value: Any = None

        self._emit(
            "wait_until_start",
            macro=macro_name,
            step_id=step_id,
            condition=step.condition,
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
        )

        while True:
            attempt += 1
            rendered = interpolate(step.condition, ctx)
            last_value = eval_expr(rendered, ctx)
            ok = bool(last_value)
            self._emit_wait_attempt(
                "expr",
                macro=macro_name,
                step_id=step_id,
                attempt=attempt,
                condition=rendered,
                result=ok,
                value=last_value,
            )
            if ok:
                ctx[step.out_value] = last_value
                ctx[step.out_attempts] = attempt
                self._emit(
                    "wait_until_end",
                    macro=macro_name,
                    step_id=step_id,
                    ok=True,
                    attempts=attempt,
                    value=last_value,
                )
                return
            if step.max_attempts is not None and attempt >= int(step.max_attempts):
                break
            if time.time() > deadline:
                break
            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        raise TimeoutError(
            f"WaitUntil timed out after {step.timeout_ms}ms "
            f"(attempts={attempt}, last_value={last_value!r}, condition={step.condition!r})"
        )

    def _exec_wait_for_bus_event(self, step: StepWaitForBusEvent, ctx: dict[str, Any], macro_name: str, path_prefix: list[int]) -> None:
        step_id = ".".join(map(str, path_prefix))
        flag_map = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
        }
        re_flags = 0
        for name in step.flags:
            re_flags |= flag_map.get(str(name), 0)
        pat = re.compile(step.pattern, re_flags) if step.pattern else None

        sock_path = get_bus_socket_path(Path(self.project.root_dir), configured=step.socket_path or self.project.settings.bus_socket)

        self._emit(
            "wait_bus_start",
            macro=macro_name,
            step_id=step_id,
            event=step.event,
            pattern=step.pattern,
            condition=step.condition,
            socket=str(sock_path),
            timeout_ms=step.timeout_ms,
        )

        attempts = 0

        def _accept(ev) -> bool:
            attempts_local_condition: str | None = None
            nonlocal attempts
            attempts += 1
            txt = bus_event_text(ev)
            ok = step.event == "*" or ev.name == step.event
            reason = "event"
            if ok and pat is not None:
                ok = pat.search(txt) is not None
                reason = "pattern"
            if ok and step.condition:
                probe = dict(ctx)
                probe.update(
                    {
                        "bus_event": ev.name,
                        "bus_data": ev.data,
                        "bus_text": txt,
                        "bus_raw": ev.raw,
                        "bus_ts": ev.ts,
                    }
                )
                attempts_local_condition = interpolate(step.condition, probe)
                ok = bool(eval_expr(attempts_local_condition, probe))
                reason = "condition"
            self._emit_wait_attempt(
                "bus",
                macro=macro_name,
                step_id=step_id,
                attempt=attempts,
                event=ev.name,
                matched=ok,
                match_stage=reason,
                text=txt,
                condition=attempts_local_condition,
            )
            return ok

        try:
            ev = wait_for_bus_event(
                sock_path,
                timeout_s=step.timeout_ms / 1000.0,
                force_unlink=step.force_unlink,
                use_systemd=step.use_systemd,
                fdname=step.fdname,
                accept=_accept,
            )
        except TimeoutError as exc:
            raise TimeoutError(
                f"WaitForBusEvent timed out after {step.timeout_ms}ms "
                f"(event={step.event!r}, pattern={step.pattern!r}, condition={step.condition!r}, attempts={attempts})"
            ) from exc

        txt = bus_event_text(ev)
        ctx[step.out_event] = ev.name
        ctx[step.out_data] = ev.data
        ctx[step.out_text] = txt
        ctx[step.out_raw] = ev.raw
        ctx[step.out_ts] = ev.ts
        self._emit(
            "wait_bus_end",
            macro=macro_name,
            step_id=step_id,
            ok=True,
            event=ev.name,
            attempts=attempts,
            socket=str(sock_path),
        )

    def _exec_try(self, step: StepTry, ctx: dict[str, Any], macro_name: str, path_prefix: list[int]) -> None:
        step_id = ".".join(map(str, path_prefix))
        pending: Exception | None = None
        try:
            self._emit("try_start", macro=macro_name, step_id=step_id)
            self._run_steps(step.steps, ctx, macro_name=macro_name, path_prefix=path_prefix + [0])
            self._emit("try_end", macro=macro_name, step_id=step_id, ok=True)
            return
        except (_BreakSignal, _ContinueSignal, _ReturnSignal) as cf:
            pending = cf
            raise
        except Exception as e:
            err = {
                "macro": macro_name,
                "step_id": step_id,
                "step_type": "Try",
                "error": str(e),
                "error_type": type(e).__name__,
            }
            ctx[step.out_error] = err
            ctx["last_error"] = err
            ctx.setdefault("errors", []).append(err)
            matched = step.catch_pattern is None or re.search(step.catch_pattern, str(e)) is not None
            self._emit("try_error", macro=macro_name, step_id=step_id, error=str(e), error_type=type(e).__name__, matched=matched)
            if matched and step.catch_steps:
                self._run_steps(step.catch_steps, ctx, macro_name=macro_name, path_prefix=path_prefix + [1])
                self._emit("try_end", macro=macro_name, step_id=step_id, ok=True, caught=True)
                return
            pending = e
            self._emit("try_end", macro=macro_name, step_id=step_id, ok=False, caught=False)
        finally:
            if step.finally_steps:
                self._emit("try_finally_start", macro=macro_name, step_id=step_id)
                self._run_steps(step.finally_steps, ctx, macro_name=macro_name, path_prefix=path_prefix + [2])
                self._emit("try_finally_end", macro=macro_name, step_id=step_id)
        if pending is not None:
            raise pending

    def _exec_break(self, step: StepBreak, ctx: dict[str, Any]) -> None:
        self._emit("loop_control", action="break")
        raise _BreakSignal()

    def _exec_continue(self, step: StepContinue, ctx: dict[str, Any]) -> None:
        self._emit("loop_control", action="continue")
        raise _ContinueSignal()

    def _exec_return(self, step: StepReturn, ctx: dict[str, Any]) -> None:
        value = self._eval_value_expr(step.value_expr, ctx) if step.value_expr is not None else None
        if step.out_var:
            ctx[step.out_var] = value
        self._emit("loop_control", action="return", out_var=step.out_var)
        raise _ReturnSignal(step.out_var, value)

    # --- Vision -----------------------------------------------------------

    def _exec_image_search_file(self, step: StepImageSearchFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        hay = root / interpolate(step.haystack_path, ctx)
        needle = root / interpolate(step.needle_path, ctx)
        match = image_search_file(hay, needle, region=step.region, threshold=step.threshold, scales=step.scales)
        ctx[step.out_x] = match.x
        ctx[step.out_y] = match.y
        ctx[step.out_score] = match.score
        self._emit("image_search", hay=str(hay), needle=str(needle), score=match.score, x=match.x, y=match.y)

    def _exec_image_search_all_file(self, step: StepImageSearchAllFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        hay = root / interpolate(step.haystack_path, ctx)
        needle = root / interpolate(step.needle_path, ctx)
        matches = image_search_all_file(
            hay,
            needle,
            region=step.region,
            threshold=step.threshold,
            scales=step.scales,
            max_results=step.max_results,
            overlap_threshold=step.overlap_threshold,
            sort=step.sort,
            scan_order=step.scan_order,
        )
        payload = [
            {"x": m.x, "y": m.y, "w": m.w, "h": m.h, "score": m.score, "scale": m.scale}
            for m in matches
        ]
        ctx[step.out_matches] = payload
        top = payload[:3]
        self._emit(
            "image_search_all",
            hay=str(hay),
            needle=str(needle),
            threshold=step.threshold,
            count=len(payload),
            top=top,
            file=True,
        )

    def _exec_wait_for_image_file(self, step: StepWaitForImageFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        hay = root / interpolate(step.haystack_path, ctx)
        needle = root / interpolate(step.needle_path, ctx)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last = None

        self._emit(
            "wait_start",
            kind="image",
            needle=str(needle),
            threshold=step.threshold,
            timeout_ms=step.timeout_ms,
        )

        # Always perform at least one attempt. Some environments have enough
        # overhead (event log writes, filesystem latency) that a very small
        # timeout could otherwise expire before the first check.
        while True:
            now = time.time()
            if attempt > 0 and now > deadline:
                break

            self._check_panic()
            attempt += 1
            last = image_search_file(hay, needle, region=step.region, threshold=-1e9, scales=step.scales)  # don't threshold inside
            self._emit_wait_attempt(
                "image",
                needle=str(needle),
                attempt=attempt,
                score=last.score,
                threshold=step.threshold,
                x=last.x,
                y=last.y,
                file=True,
            )
            if last.score >= step.threshold:
                ctx[step.out_x] = last.x
                ctx[step.out_y] = last.y
                ctx[step.out_score] = last.score
                self._emit(
                    "wait_end",
                    kind="image",
                    ok=True,
                    attempts=attempt,
                    score=last.score,
                    x=last.x,
                    y=last.y,
                )
                return

            # Backoff with jitter
            if time.time() > deadline:
                break

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        score = last.score if last else None
        self._emit("wait_end", kind="image", ok=False, attempts=attempt, score=score)
        raise TimeoutError(f"WaitForImageFile timed out after {step.timeout_ms}ms (last score={score})")

    def _exec_pixel_search_file(self, step: StepPixelSearchFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)
        match = pixel_search_file(
            img,
            color=self._render_value(step.color, ctx),
            region=step.region,
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            step=getattr(step, "step", 1),
            match_strategy=getattr(step, "match_strategy", "best"),
            scan_order=getattr(step, "scan_order", "tlbr"),
        )
        ctx[step.out_x] = match.x
        ctx[step.out_y] = match.y
        ctx[step.out_dist] = match.dist
        self._emit(
            "pixel_search",
            image=str(img),
            x=match.x,
            y=match.y,
            dist=match.dist,
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            step=getattr(step, "step", 1),
            match_strategy=getattr(step, "match_strategy", "best"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )

    def _exec_pixel_search_all_file(self, step: StepPixelSearchAllFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)
        color = self._render_value(step.color, ctx)

        hits = pixel_search_all_file(
            img,
            color=color,
            region=step.region,
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            step=getattr(step, "step", 1),
            group=getattr(step, "group", "none"),
            pick=getattr(step, "pick", "center"),
            min_area=getattr(step, "min_area", 1),
            max_results=getattr(step, "max_results", 200),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
        )

        payload = [
            {
                "x": int(h.x),
                "y": int(h.y),
                "dist": float(h.dist),
                "w": int(getattr(h, "w", 1)),
                "h": int(getattr(h, "h", 1)),
                "area": int(getattr(h, "area", 1)),
                "bbox_x": int(h.bbox_x) if getattr(h, "bbox_x", None) is not None else int(h.x),
                "bbox_y": int(h.bbox_y) if getattr(h, "bbox_y", None) is not None else int(h.y),
            }
            for h in hits
        ]

        ctx[step.out_matches] = payload
        ctx[step.out_count] = len(payload)

        self._emit(
            "pixel_search_all",
            image=str(img),
            file=True,
            color=color,
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            step=getattr(step, "step", 1),
            group=getattr(step, "group", "none"),
            pick=getattr(step, "pick", "center"),
            min_area=getattr(step, "min_area", 1),
            max_results=getattr(step, "max_results", 200),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            count=len(payload),
            top=payload[:3],
            region=step.region.model_dump() if step.region else None,
        )

    def _exec_wait_for_pixel_file(self, step: StepWaitForPixelFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last_dist: float | None = None
        last_xy: tuple[int, int] | None = None

        step_val = int(getattr(step, "step", 1) or 1)
        if step_val < 1:
            step_val = 1

        self._emit(
            "wait_start",
            kind="pixel",
            image=str(img),
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            timeout_ms=step.timeout_ms,
            step=step_val,
        )

        color = self._render_value(step.color, ctx)
        tol_mode = getattr(step, "tolerance_mode", "euclidean")

        while time.time() <= deadline:
            self._check_panic()
            attempt += 1
            try:
                phase_index = (attempt - 1) % (step_val * step_val)
                phase_y = phase_index // step_val
                phase_x = phase_index % step_val
                m = pixel_search_file(
                    img,
                    color=color,
                    region=step.region,
                    tolerance=step.tolerance,
                    tolerance_mode=tol_mode,
                    step=step_val,
                    phase_x=phase_x,
                    phase_y=phase_y,
                    match_strategy=getattr(step, "match_strategy", "best"),
                    scan_order=getattr(step, "scan_order", "tlbr"),
                )
                self._emit_wait_attempt(
                    "pixel",
                    image=str(img),
                    attempt=attempt,
                    dist=m.dist,
                    tolerance=step.tolerance,
                    tolerance_mode=tol_mode,
                    x=m.x,
                    y=m.y,
                    file=True,
                    step=step_val,
                )
                ctx[step.out_x] = m.x
                ctx[step.out_y] = m.y
                ctx[step.out_dist] = m.dist
                self._emit("wait_end", kind="pixel", ok=True, attempts=attempt, dist=m.dist, x=m.x, y=m.y)
                return
            except PixelSearchNoMatch as e:
                last_dist = e.dist
                last_xy = (e.x, e.y)
                self._emit_wait_attempt(
                    "pixel",
                    image=str(img),
                    attempt=attempt,
                    dist=last_dist,
                    tolerance=step.tolerance,
                    tolerance_mode=tol_mode,
                    x=last_xy[0],
                    y=last_xy[1],
                    file=True,
                    matched=False,
                    step=step_val,
                )
            except Exception:
                self._emit_wait_attempt(
                    "pixel",
                    image=str(img),
                    attempt=attempt,
                    dist=last_dist,
                    tolerance=step.tolerance,
                    tolerance_mode=tol_mode,
                    file=True,
                    matched=False,
                    step=step_val,
                )

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit("wait_end", kind="pixel", ok=False, attempts=attempt, dist=last_dist)
        raise TimeoutError(f"WaitForPixelFile timed out after {step.timeout_ms}ms")



    def _exec_pixel_get_color_file(self, step: StepPixelGetColorFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)
        c = pixel_get_color_file(img, x=int(step.x), y=int(step.y), region=step.region)
        ctx[step.out_hex] = c.hex
        ctx[getattr(step, "out_ahk_hex", "px_color_ahk")] = c.ahk_hex
        ctx[step.out_r] = c.r
        ctx[step.out_g] = c.g
        ctx[step.out_b] = c.b
        self._emit(
            "pixel_get_color",
            image=str(img),
            x=int(step.x),
            y=int(step.y),
            hex=c.hex,
            ahk_hex=c.ahk_hex,
            r=c.r,
            g=c.g,
            b=c.b,
            region=step.region.model_dump() if step.region else None,
        )
    def _exec_ocr_file(self, step: StepOcrReadTextFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)
        text = ocr_read_text_file(
            img,
            lang=step.lang,
            region=getattr(step, "region", None),
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )
        ctx[step.out_var] = text
        self._emit("ocr", image=str(img), chars=len(text))

    def _exec_ocr_find_text_file(self, step: StepOcrFindTextFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)

        pattern = interpolate(step.pattern, ctx)
        span = ocr_find_text_file(
            img,
            pattern=pattern,
            match=step.match,
            case_sensitive=step.case_sensitive,
            lang=step.lang,
            region=step.region,
            level=getattr(step, "level", "word"),
            match_strategy=getattr(step, "match_strategy", "first"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )

        ctx[step.out_x] = int(span.x)
        ctx[step.out_y] = int(span.y)
        ctx[step.out_w] = int(span.w)
        ctx[step.out_h] = int(span.h)
        ctx[step.out_text] = span.text
        ctx[step.out_conf] = float(span.conf)

        self._emit(
            "ocr_find_text",
            image=str(img),
            file=True,
            pattern=pattern,
            match=step.match,
            level=getattr(step, "level", "word"),
            match_strategy=getattr(step, "match_strategy", "first"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            x=int(span.x),
            y=int(span.y),
            w=int(span.w),
            h=int(span.h),
            conf=float(span.conf),
            text=span.text,
            region=step.region.model_dump() if step.region else None,
        )

    

    def _exec_ocr_find_text_all_file(self, step: StepOcrFindTextAllFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)

        pattern = interpolate(step.pattern, ctx)
        spans = ocr_find_text_all_file(
            img,
            pattern=pattern,
            match=step.match,
            case_sensitive=step.case_sensitive,
            lang=step.lang,
            region=step.region,
            level=getattr(step, "level", "word"),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            max_results=getattr(step, "max_results", None),
            min_conf=getattr(step, "min_conf", None),
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )

        matches = [
            {
                "x": int(s.x),
                "y": int(s.y),
                "w": int(s.w),
                "h": int(s.h),
                "text": s.text,
                "conf": float(s.conf),
            }
            for s in spans
        ]

        ctx[step.out_matches] = matches
        ctx[step.out_count] = len(matches)

        self._emit(
            "ocr_find_text_all",
            image=str(img),
            file=True,
            pattern=pattern,
            match=step.match,
            level=getattr(step, "level", "word"),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            count=len(matches),
            region=step.region.model_dump() if step.region else None,
        )

    def _exec_capture_screenshot(self, step: StepCaptureScreenshot, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        if step.path:
            out = root / interpolate(step.path, ctx)
        else:
            out = root / self.project.settings.log_dir / f"capture_{int(time.time()*1000)}.png"
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        out = screenshot_mod.capture(out, region=cap_region)
        ctx[step.out_var] = str(out)
        self._emit(
            "screenshot",
            path=str(out),
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

    def _exec_coord_mode(self, step: StepCoordMode, ctx: dict[str, Any]) -> None:
        # Keep ctx arg for symmetry, though this is runner state.
        before = self._coord_mode_get(step.target)
        self._coord_mode_set(step.target, step.mode)
        self._emit("coord_mode", target=str(step.target), before=before, after=str(step.mode))


    # --- Vision (screen capture) -----------------------------------------

    def _resolve_capture_path(self, screenshot_path: str | None, ctx: dict[str, Any], prefix: str) -> Path:
        root = Path(self.project.root_dir)
        if screenshot_path:
            out = root / interpolate(screenshot_path, ctx)
        else:
            out = root / self.project.settings.log_dir / f"{prefix}_{int(time.time()*1000)}.png"
        out = out.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        return out

    def _capture(self, out: Path, *, region=None) -> Path:
        captured = screenshot_mod.capture(out, region=region)
        self._last_capture_path = str(captured)
        return captured

    def _vision_safe_corner(self, corner: str, margin: int) -> tuple[int, int]:
        m = max(0, int(margin))
        c = (corner or "tl").strip().lower()
        try:
            sz = display_mod.get_virtual_screen_size()
            w, h = int(sz.width), int(sz.height)
        except Exception:
            w, h = 0, 0
        if w <= 0 or h <= 0:
            # Conservative fallback.
            return (m, m)

        if c == "tr":
            return (max(m, w - 1 - m), m)
        if c == "bl":
            return (m, max(m, h - 1 - m))
        if c == "br":
            return (max(m, w - 1 - m), max(m, h - 1 - m))
        return (m, m)

    @contextmanager
    def _vision_cursor_guard(self, step: Any):
        """Best-effort cursor hygiene for vision capture steps.

        When enabled, move the cursor to a safe corner before capturing screenshots
        to avoid hover/tooltips and pointer-over effects from altering pixels.

        This is best-effort: failures (no backend / permissions) are ignored.
        """

        avoid = getattr(step, "cursor_avoid", None) or "none"
        avoid = str(avoid).strip().lower()
        if avoid == "auto":
            avoid = (os.environ.get("VHK_VISION_CURSOR_AVOID") or "none").strip().lower()
        if avoid not in {"none", "corner"}:
            avoid = "none"

        if avoid != "corner":
            yield
            return

        corner = getattr(step, "cursor_corner", None) or (os.environ.get("VHK_VISION_CURSOR_CORNER") or "tl")
        margin = getattr(step, "cursor_margin", None)
        if margin is None:
            margin = os.environ.get("VHK_VISION_CURSOR_MARGIN", "2")
        try:
            margin_i = int(margin)
        except Exception:
            margin_i = 2

        restore = bool(getattr(step, "cursor_restore", False))
        if not restore:
            env_restore = (os.environ.get("VHK_VISION_CURSOR_RESTORE") or "").strip().lower()
            restore = env_restore in {"1", "true", "yes", "on"}

        orig = None
        if restore:
            try:
                pos = cursor_pos_mod.get_cursor_pos()
                orig = (int(pos.x), int(pos.y))
            except Exception:
                orig = None

        try:
            x, y = self._vision_safe_corner(str(corner), int(margin_i))
            input_mod.mouse_move(x=int(x), y=int(y))
            self._emit("cursor", action="park", x=int(x), y=int(y), reason="vision_capture")
        except Exception:
            # Ignore failures; some desktops do not allow cursor warping.
            pass

        try:
            yield
        finally:
            if restore and orig is not None:
                try:
                    input_mod.mouse_move(x=int(orig[0]), y=int(orig[1]))
                    self._emit("cursor", action="restore", x=int(orig[0]), y=int(orig[1]), reason="vision_capture")
                except Exception:
                    pass


    # --- CoordMode helpers ------------------------------------------------

    def _coord_mode_get(self, target: str) -> str:
        t = (target or "").strip().lower()
        if t == "mouse":
            return self._coord_mode_mouse
        # Pixel is also used for ImageSearch/screenshot regions (AHK semantics).
        return self._coord_mode_pixel

    def _coord_mode_set(self, target: str, mode: str) -> None:
        t = (target or "").strip().lower()
        m = (mode or "").strip().lower()
        if m not in {"screen", "window", "client"}:
            raise ValueError(f"CoordMode: invalid mode {mode!r} (use screen|window|client)")
        if t == "mouse":
            self._coord_mode_mouse = m
            return
        if t == "pixel":
            self._coord_mode_pixel = m
            return
        raise ValueError(f"CoordMode: invalid target {target!r} (use pixel|mouse)")

    def _active_window_offset(self, mode: str) -> tuple[int, int]:
        """Return (ox,oy) for the chosen mode.

        For screen mode, offset is (0,0).
        For window/client, offset uses the active window geometry.
        """

        m = (mode or "screen").strip().lower()
        if m == "screen":
            return (0, 0)

        rect, client, wm = get_active_window_geometry()
        base = rect if m == "window" else (client or rect)
        try:
            return (int(base.get("x") or 0), int(base.get("y") or 0))
        except Exception as exc:
            raise ActiveWindowProbeError(f"invalid active window geometry for {wm}: {base!r}") from exc

    def _resolve_region_spec(self, region, ctx: dict[str, Any]) -> Any:
        """Resolve a region spec to a concrete Region model.

        Supports:
        - inline mapping (already parsed as Region)
        - "@name" or "name" (if defined in project.yaml regions)
        - "WxH+X+Y" (e.g. 640x480+10+20)
        """

        if region is None:
            return None

        from vhk.core.models import Region as RegionModel

        if isinstance(region, RegionModel):
            return region

        if isinstance(region, str):
            import re

            s = interpolate(region, ctx).strip()
            if not s:
                return None

            regions = getattr(self.project, "regions", {}) or {}
            name: str | None = None
            if s.startswith("@"):  # explicit region reference
                name = s[1:].strip()
            elif s.lower().startswith("region:"):
                name = s.split(":", 1)[1].strip()
            elif s in regions:
                name = s

            if name is not None:
                r = regions.get(name)
                if r is None:
                    raise ValueError(f"Unknown region {name!r}. Define it under project.yaml 'regions:'")
                return r

            # Copy/paste-friendly geometry forms.
            m = re.match(r"^(-?\d+)x(-?\d+)\+(-?\d+)\+(-?\d+)$", s)
            if m:
                w = int(m.group(1))
                h = int(m.group(2))
                x = int(m.group(3))
                y = int(m.group(4))
                return RegionModel(x=x, y=y, w=w, h=h)

            parts = [p.strip() for p in re.split(r"[ ,]+", s) if p.strip()]
            if len(parts) == 4 and all(re.match(r"^-?\d+$", p) for p in parts):
                x, y, w, h = (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
                return RegionModel(x=x, y=y, w=w, h=h)

            raise ValueError(
                "Invalid region spec. Use a mapping {x,y,w,h}, a named region '@name', "
                "or a geometry string like '640x480+10+20' or 'x,y,w,h'."
            )

        raise TypeError(f"Invalid region type: {type(region)}")

    def _translate_region(self, region, *, target: str, ctx: dict[str, Any] | None = None) -> Any:
        region = self._resolve_region_spec(region, ctx or {})
        if region is None:
            return None
        mode = self._coord_mode_get(target)
        if mode == "screen":
            return region
        ox, oy = self._active_window_offset(mode)
        from vhk.core.models import Region as RegionModel

        return RegionModel(x=int(region.x) + ox, y=int(region.y) + oy, w=int(region.w), h=int(region.h))

    def _translate_xy(self, x: int, y: int, *, target: str) -> tuple[int, int]:
        mode = self._coord_mode_get(target)
        if mode == "screen":
            return int(x), int(y)
        ox, oy = self._active_window_offset(mode)
        return int(x) + ox, int(y) + oy

    def _text_matches(
        self,
        text: str,
        pattern: str,
        mode: str,
        *,
        case_sensitive: bool,
        fuzzy_threshold: float | None = None,
        fuzzy_mode: str = "partial",
    ) -> bool:
        m = (mode or "contains").strip().lower()

        if m == "fuzzy":
            t = normalize_text(text)
            p = normalize_text(pattern)
            if not case_sensitive:
                t = t.lower()
                p = p.lower()
            thr = float(fuzzy_threshold) if fuzzy_threshold is not None else 0.8
            score = fuzzy_score(p, t, mode=fuzzy_mode)
            return score >= thr

        # Preserve historic behavior for contains/regex (don't normalize).
        if not case_sensitive:
            text = text.lower()
            pattern = pattern.lower()
        if m == "contains":
            return pattern in text
        if m == "regex":
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.search(pattern, text, flags=flags) is not None
        raise ValueError(f"Unknown match mode: {mode}")

    def _exec_image_search(self, step: StepImageSearch, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="image_search")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        # If we captured a region, matching coordinates are relative to that capture.
        match = image_search_file(out, needle, region=None, threshold=step.threshold, scales=step.scales)
        x, y = match.x, match.y
        if cap_region is not None:
            x += cap_region.x
            y += cap_region.y

        ctx[step.out_x] = x
        ctx[step.out_y] = y
        ctx[step.out_score] = match.score
        ctx[step.out_w] = match.w
        ctx[step.out_h] = match.h

        self._emit(
            "image_search",
            hay=str(out),
            needle=str(needle),
            score=match.score,
            x=x,
            y=y,
            w=match.w,
            h=match.h,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

    def _exec_image_search_all(self, step: StepImageSearchAll, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="image_search_all")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        matches = image_search_all_file(
            out,
            needle,
            region=None,
            threshold=step.threshold,
            scales=step.scales,
            max_results=step.max_results,
            overlap_threshold=step.overlap_threshold,
            sort=step.sort,
            scan_order=step.scan_order,
        )

        payload = []
        for m in matches:
            x, y = int(m.x), int(m.y)
            if cap_region is not None:
                x += cap_region.x
                y += cap_region.y
            payload.append({"x": x, "y": y, "w": m.w, "h": m.h, "score": m.score, "scale": m.scale})

        ctx[step.out_matches] = payload
        top = payload[:3]
        self._emit(
            "image_search_all",
            hay=str(out),
            needle=str(needle),
            threshold=step.threshold,
            count=len(payload),
            top=top,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

    def _exec_wait_for_image(self, step: StepWaitForImage, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_image")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last = None

        stable_since: float | None = None
        stable_hits: int = 0
        stable_best = None
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        self._emit(
            "wait_start",
            kind="image",
            needle=str(needle),
            threshold=step.threshold,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        with self._vision_cursor_guard(step):

            while time.time() <= deadline:
                self._check_panic()
                if step.max_attempts is not None and attempt >= step.max_attempts:
                    break
                attempt += 1

                self._capture(out, region=cap_region)
                last = image_search_file(out, needle, region=None, threshold=-1e9, scales=step.scales)

                if last.score >= step.threshold:
                    if stable_since is None:
                        stable_since = time.time()
                        stable_hits = 1
                        stable_best = last
                    else:
                        stable_hits += 1
                        if stable_best is None or last.score > stable_best.score:
                            stable_best = last
                else:
                    stable_since = None
                    stable_hits = 0
                    stable_best = None

                stable_elapsed_ms = 0
                if stable_since is not None:
                    stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

                self._emit_wait_attempt(
                    "image",
                    needle=str(needle),
                    attempt=attempt,
                    score=last.score,
                    threshold=step.threshold,
                    x=last.x,
                    y=last.y,
                    screen=True,
                    stable_hits=stable_hits,
                    stable_elapsed_ms=stable_elapsed_ms,
                    stable_needed_hits=need_hits,
                    stable_needed_ms=need_ms,
                )

                ok_now = last.score >= step.threshold
                stable_ok = ok_now and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
                if stable_ok:
                    best = stable_best or last
                    x, y = best.x, best.y
                    if cap_region is not None:
                        x += cap_region.x
                        y += cap_region.y
                    ctx[step.out_x] = x
                    ctx[step.out_y] = y
                    ctx[step.out_score] = best.score
                    ctx[step.out_w] = best.w
                    ctx[step.out_h] = best.h
                    self._emit(
                        "wait_end",
                        kind="image",
                        ok=True,
                        attempts=attempt,
                        score=best.score,
                        x=x,
                        y=y,
                        w=best.w,
                        h=best.h,
                        screen=True,
                        stable_hits=stable_hits,
                        stable_elapsed_ms=stable_elapsed_ms,
                    )
                    return

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(sleep_ms / 1000.0)
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        score = last.score if last else None
        self._emit("wait_end", kind="image", ok=False, attempts=attempt, score=score, screen=True)

        if getattr(step, "debug_on_timeout", False) and last is not None:
            try:
                from vhk.vision.annotate import annotate_match

                meta = try_load_needle(needle)
                dbg = out.with_name(out.stem + "_annotated.png")
                annotate_match(out, dbg, last, needle_meta=meta, threshold=step.threshold, ok=False)
                if getattr(step, "out_debug_screenshot", None):
                    ctx[step.out_debug_screenshot] = str(dbg)
                self._emit("vision_debug", kind="wait_image", path=str(dbg), needle=str(needle), score=float(last.score), threshold=float(step.threshold))
            except Exception as de:
                self._emit("vision_debug", kind="wait_image", ok=False, error=str(de))
        raise TimeoutError(f"WaitForImage timed out after {step.timeout_ms}ms (last score={score})")

    def _exec_wait_for_image_all(self, step: StepWaitForImageAll, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_image_all")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last_best: float | None = None
        last_count: int = 0

        stable_since: float | None = None
        stable_hits: int = 0
        stable_payload: list[dict[str, Any]] | None = None
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        min_count = int(getattr(step, "min_count", 1) or 1)
        if min_count < 1:
            min_count = 1

        self._emit(
            "wait_start",
            kind="image_all",
            needle=str(needle),
            threshold=step.threshold,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            min_count=min_count,
            max_results=getattr(step, "max_results", 50),
            overlap_threshold=getattr(step, "overlap_threshold", 0.3),
            sort=getattr(step, "sort", "score"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            coord_mode=self._coord_mode_pixel,
        )

        with self._vision_cursor_guard(step):

            while time.time() <= deadline:
                self._check_panic()
                if step.max_attempts is not None and attempt >= step.max_attempts:
                    break
                attempt += 1

                self._capture(out, region=cap_region)

                # Fast path: get best score first (AHK-style ImageSearch reports the
                # best candidate quickly); only compute full FindAll when the best
                # candidate meets the threshold.
                best = image_search_file(out, needle, region=None, threshold=-1e9, scales=step.scales)
                last_best = float(best.score)

                matches_payload: list[dict[str, Any]] = []
                if best.score >= step.threshold:
                    matches = image_search_all_file(
                        out,
                        needle,
                        region=None,
                        threshold=step.threshold,
                        scales=step.scales,
                        max_results=getattr(step, "max_results", 50),
                        overlap_threshold=getattr(step, "overlap_threshold", 0.3),
                        sort=getattr(step, "sort", "score"),
                        scan_order=getattr(step, "scan_order", "tlbr"),
                    )
                    for m in matches:
                        x, y = int(m.x), int(m.y)
                        if cap_region is not None:
                            x += int(cap_region.x)
                            y += int(cap_region.y)
                        matches_payload.append({"x": x, "y": y, "w": int(m.w), "h": int(m.h), "score": float(m.score), "scale": float(m.scale)})

                last_count = len(matches_payload)

                ok = last_count >= min_count

                if ok:
                    if stable_since is None:
                        stable_since = time.time()
                        stable_hits = 1
                        stable_payload = matches_payload
                    else:
                        stable_hits += 1
                        stable_payload = matches_payload
                else:
                    stable_since = None
                    stable_hits = 0
                    stable_payload = None

                stable_elapsed_ms = 0
                if stable_since is not None:
                    stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))
                self._emit_wait_attempt(
                    "image_all",
                    needle=str(needle),
                    attempt=attempt,
                    score=float(last_best) if last_best is not None else None,
                    threshold=step.threshold,
                    count=last_count,
                    min_count=min_count,
                    screen=True,
                    stable_hits=stable_hits,
                    stable_elapsed_ms=stable_elapsed_ms,
                    stable_needed_hits=need_hits,
                    stable_needed_ms=need_ms,
                )

                stable_ok = ok and stable_hits >= need_hits and stable_elapsed_ms >= need_ms

                if stable_ok:
                    ctx[step.out_matches] = stable_payload or matches_payload
                    ctx[step.out_count] = last_count
                    self._emit(
                        "wait_end",
                        kind="image_all",
                        ok=True,
                        attempts=attempt,
                        score=float(last_best) if last_best is not None else None,
                        count=last_count,
                        screen=True,
                        stable_hits=stable_hits,
                        stable_elapsed_ms=stable_elapsed_ms,
                    )
                    return

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(sleep_ms / 1000.0)
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

            self._emit(
                "wait_end",
                kind="image_all",
                ok=False,
                attempts=attempt,
                score=float(last_best) if last_best is not None else None,
                count=last_count,
                screen=True,
            )
            raise TimeoutError(
                f"WaitForImageAll timed out after {step.timeout_ms}ms (last best score={last_best}, last count={last_count})"
            )

    def _exec_wait_for_image_vanish(self, step: StepWaitForImageVanish, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_image_vanish")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last = None
        seen_present = False
        last_seen = None

        stable_since: float | None = None
        stable_hits: int = 0
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        self._emit(
            "wait_start",
            kind="image_vanish",
            needle=str(needle),
            threshold=step.threshold,
            timeout_ms=step.timeout_ms,
            require_seen=bool(getattr(step, "require_seen", False)),
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        with self._vision_cursor_guard(step):
            while time.time() <= deadline:
                self._check_panic()
                if step.max_attempts is not None and attempt >= step.max_attempts:
                    break
                attempt += 1

                self._capture(out, region=cap_region)
                last = image_search_file(out, needle, region=None, threshold=-1e9, scales=step.scales)

                present = bool(last.score >= step.threshold)
                if present:
                    seen_present = True
                    last_seen = last
                    stable_since = None
                    stable_hits = 0
                else:
                    if stable_since is None:
                        stable_since = time.time()
                        stable_hits = 1
                    else:
                        stable_hits += 1

                stable_elapsed_ms = 0
                if stable_since is not None:
                    stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

                self._emit_wait_attempt(
                    "image_vanish",
                    needle=str(needle),
                    attempt=attempt,
                    score=last.score,
                    threshold=step.threshold,
                    present=present,
                    screen=True,
                    stable_hits=stable_hits,
                    stable_elapsed_ms=stable_elapsed_ms,
                    stable_needed_hits=need_hits,
                    stable_needed_ms=need_ms,
                )

                ok_now = not present
                if getattr(step, "require_seen", False) and not seen_present:
                    ok_now = False
                stable_ok = ok_now and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
                if stable_ok:
                    ctx[step.out_seen] = bool(seen_present)
                    ctx[step.out_last_score] = float(last.score)
                    if last_seen is not None:
                        x, y = int(last_seen.x), int(last_seen.y)
                        if cap_region is not None:
                            x += int(cap_region.x)
                            y += int(cap_region.y)
                        ctx[step.out_last_seen_x] = x
                        ctx[step.out_last_seen_y] = y
                        ctx[step.out_last_seen_score] = float(last_seen.score)
                    else:
                        ctx[step.out_last_seen_x] = None
                        ctx[step.out_last_seen_y] = None
                        ctx[step.out_last_seen_score] = None
                    self._emit(
                        "wait_end",
                        kind="image_vanish",
                        ok=True,
                        attempts=attempt,
                        score=float(last.score),
                        seen=bool(seen_present),
                        screen=True,
                        stable_hits=stable_hits,
                        stable_elapsed_ms=stable_elapsed_ms,
                    )
                    return

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(sleep_ms / 1000.0)
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        score = last.score if last else None
        self._emit(
            "wait_end",
            kind="image_vanish",
            ok=False,
            attempts=attempt,
            score=score,
            seen=bool(seen_present),
            screen=True,
        )

        if getattr(step, "debug_on_timeout", False) and last is not None:
            try:
                from vhk.vision.annotate import annotate_match

                meta = try_load_needle(needle)
                dbg = out.with_name(out.stem + "_annotated.png")
                annotate_match(out, dbg, last, needle_meta=meta, threshold=step.threshold, ok=False)
                if getattr(step, "out_debug_screenshot", None):
                    ctx[step.out_debug_screenshot] = str(dbg)
                self._emit(
                    "vision_debug",
                    kind="wait_image_vanish",
                    path=str(dbg),
                    needle=str(needle),
                    score=float(last.score),
                    threshold=float(step.threshold),
                )
            except Exception as de:
                self._emit("vision_debug", kind="wait_image_vanish", ok=False, error=str(de))

        raise TimeoutError(
            f"WaitForImageVanish timed out after {step.timeout_ms}ms (seen={seen_present}, last score={score})"
        )

    def _exec_pixel_search(self, step: StepPixelSearch, ctx: dict[str, Any]) -> None:
        """Search for a pixel matching a target color."""
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="pixel_search")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        color = self._render_value(step.color, ctx)
        match = pixel_search_file(
            out,
            color=color,
            region=None,
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            step=getattr(step, "step", 1),
            match_strategy=getattr(step, "match_strategy", "best"),
            scan_order=getattr(step, "scan_order", "tlbr"),
        )
        x, y = match.x, match.y
        if cap_region is not None:
            x += cap_region.x
            y += cap_region.y

        ctx[step.out_x] = x
        ctx[step.out_y] = y
        ctx[step.out_dist] = match.dist
        self._emit(
            "pixel_search",
            screen=True,
            color=color,
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            step=getattr(step, "step", 1),
            dist=match.dist,
            x=x,
            y=y,
            screenshot=str(out),
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

    def _exec_pixel_search_all(self, step: StepPixelSearchAll, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="pixel_search_all")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        color = self._render_value(step.color, ctx)
        hits = pixel_search_all_file(
            out,
            color=color,
            region=None,
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            step=getattr(step, "step", 1),
            group=getattr(step, "group", "none"),
            pick=getattr(step, "pick", "center"),
            min_area=getattr(step, "min_area", 1),
            max_results=getattr(step, "max_results", 200),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
        )

        payload: list[dict[str, Any]] = []
        for h in hits:
            x, y = int(h.x), int(h.y)
            bx = int(h.bbox_x) if getattr(h, "bbox_x", None) is not None else x
            by = int(h.bbox_y) if getattr(h, "bbox_y", None) is not None else y
            if cap_region is not None:
                x += int(cap_region.x)
                y += int(cap_region.y)
                bx += int(cap_region.x)
                by += int(cap_region.y)
            payload.append(
                {
                    "x": x,
                    "y": y,
                    "dist": float(h.dist),
                    "w": int(getattr(h, "w", 1)),
                    "h": int(getattr(h, "h", 1)),
                    "area": int(getattr(h, "area", 1)),
                    "bbox_x": bx,
                    "bbox_y": by,
                }
            )

        ctx[step.out_matches] = payload
        ctx[step.out_count] = len(payload)

        self._emit(
            "pixel_search_all",
            screen=True,
            color=color,
            tolerance=step.tolerance,
            tolerance_mode=getattr(step, "tolerance_mode", "euclidean"),
            step=getattr(step, "step", 1),
            group=getattr(step, "group", "none"),
            pick=getattr(step, "pick", "center"),
            min_area=getattr(step, "min_area", 1),
            max_results=getattr(step, "max_results", 200),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            count=len(payload),
            top=payload[:3],
            screenshot=str(out),
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

    def _exec_wait_for_pixel(self, step: StepWaitForPixel, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_pixel")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0
        last_dist: float | None = None
        last_xy: tuple[int, int] | None = None

        color = self._render_value(step.color, ctx)
        tol_mode = getattr(step, "tolerance_mode", "euclidean")
        step_val = int(getattr(step, "step", 1) or 1)
        if step_val < 1:
            step_val = 1

        self._emit(
            "wait_start",
            kind="pixel",
            screen=True,
            color=color,
            tolerance=step.tolerance,
            tolerance_mode=tol_mode,
            timeout_ms=step.timeout_ms,
            region=cap_region.model_dump() if cap_region else None,
            step=step_val,
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)
            try:
                phase_index = (attempt - 1) % (step_val * step_val)
                phase_y = phase_index // step_val
                phase_x = phase_index % step_val
                m = pixel_search_file(
                    out,
                    color=color,
                    region=None,
                    tolerance=step.tolerance,
                    tolerance_mode=tol_mode,
                    step=step_val,
                    phase_x=phase_x,
                    phase_y=phase_y,
                    match_strategy=getattr(step, "match_strategy", "best"),
                    scan_order=getattr(step, "scan_order", "tlbr"),
                )
                x, y = m.x, m.y
                if cap_region is not None:
                    x += cap_region.x
                    y += cap_region.y

                self._emit_wait_attempt(
                    "pixel",
                    screen=True,
                    attempt=attempt,
                    dist=m.dist,
                    tolerance=step.tolerance,
                    tolerance_mode=tol_mode,
                    x=x,
                    y=y,
                    screenshot=str(out),
                    step=step_val,
                )
                ctx[step.out_x] = x
                ctx[step.out_y] = y
                ctx[step.out_dist] = m.dist
                self._emit("wait_end", kind="pixel", ok=True, attempts=attempt, dist=m.dist, x=x, y=y, screen=True)
                return
            except PixelSearchNoMatch as e:
                last_dist = e.dist
                x, y = e.x, e.y
                if cap_region is not None:
                    x += cap_region.x
                    y += cap_region.y
                last_xy = (x, y)
                self._emit_wait_attempt(
                    "pixel",
                    screen=True,
                    attempt=attempt,
                    dist=last_dist,
                    tolerance=step.tolerance,
                    tolerance_mode=tol_mode,
                    x=last_xy[0],
                    y=last_xy[1],
                    screenshot=str(out),
                    matched=False,
                    step=step_val,
                )

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit(
            "wait_end",
            kind="pixel",
            ok=False,
            attempts=attempt,
            dist=last_dist,
            x=last_xy[0] if last_xy else None,
            y=last_xy[1] if last_xy else None,
            screen=True,
        )
        raise TimeoutError(f"WaitForPixel timed out after {step.timeout_ms}ms")

    def _exec_wait_for_pixel_all(self, step: StepWaitForPixelAll, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_pixel_all")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0
        last_count: int = 0
        last_best: float | None = None

        color = self._render_value(step.color, ctx)
        tol_mode = getattr(step, "tolerance_mode", "euclidean")
        step_val = int(getattr(step, "step", 1) or 1)
        if step_val < 1:
            step_val = 1

        self._emit(
            "wait_start",
            kind="pixel_all",
            screen=True,
            color=color,
            tolerance=step.tolerance,
            tolerance_mode=tol_mode,
            timeout_ms=step.timeout_ms,
            region=cap_region.model_dump() if cap_region else None,
            step=step_val,
            group=getattr(step, "group", "none"),
            pick=getattr(step, "pick", "center"),
            min_area=getattr(step, "min_area", 1),
            min_count=getattr(step, "min_count", 1),
            max_results=getattr(step, "max_results", 200),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)
            phase_index = (attempt - 1) % (step_val * step_val)
            phase_y = phase_index // step_val
            phase_x = phase_index % step_val

            hits = pixel_search_all_file(
                out,
                color=color,
                region=None,
                tolerance=step.tolerance,
                tolerance_mode=tol_mode,
                step=step_val,
                phase_x=phase_x,
                phase_y=phase_y,
                group=getattr(step, "group", "none"),
                pick=getattr(step, "pick", "center"),
                min_area=getattr(step, "min_area", 1),
                max_results=getattr(step, "max_results", 200),
                sort=getattr(step, "sort", "scan"),
                scan_order=getattr(step, "scan_order", "tlbr"),
            )

            payload = []
            for h in hits:
                x, y = int(h.x), int(h.y)
                bx = int(h.bbox_x) if getattr(h, "bbox_x", None) is not None else x
                by = int(h.bbox_y) if getattr(h, "bbox_y", None) is not None else y
                if cap_region is not None:
                    x += int(cap_region.x)
                    y += int(cap_region.y)
                    bx += int(cap_region.x)
                    by += int(cap_region.y)
                payload.append(
                    {
                        "x": x,
                        "y": y,
                        "dist": float(h.dist),
                        "w": int(getattr(h, "w", 1)),
                        "h": int(getattr(h, "h", 1)),
                        "area": int(getattr(h, "area", 1)),
                        "bbox_x": bx,
                        "bbox_y": by,
                    }
                )

            last_count = len(payload)
            last_best = min((float(p["dist"]) for p in payload), default=None)

            ok = last_count >= int(getattr(step, "min_count", 1) or 1)
            self._emit_wait_attempt(
                "pixel_all",
                screen=True,
                attempt=attempt,
                matched=ok,
                count=last_count,
                best_dist=last_best,
                screenshot=str(out),
                step=step_val,
            )

            if ok:
                ctx[step.out_matches] = payload
                ctx[step.out_count] = last_count
                self._emit(
                    "wait_end",
                    kind="pixel_all",
                    ok=True,
                    attempts=attempt,
                    count=last_count,
                    best_dist=last_best,
                    screen=True,
                )
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit(
            "wait_end",
            kind="pixel_all",
            ok=False,
            attempts=attempt,
            count=last_count,
            best_dist=last_best,
            screen=True,
        )
        raise TimeoutError(f"WaitForPixelAll timed out after {step.timeout_ms}ms")

    def _exec_wait_for_pixel_vanish(self, step: StepWaitForPixelVanish, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_pixel_vanish")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0

        color = self._render_value(step.color, ctx)
        tol_mode = getattr(step, "tolerance_mode", "euclidean")
        step_val = int(getattr(step, "step", 1) or 1)
        if step_val < 1:
            step_val = 1

        seen_present = False
        last_dist: float | None = None
        last_seen: tuple[int, int, float] | None = None

        stable_since: float | None = None
        stable_hits: int = 0
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        self._emit(
            "wait_start",
            kind="pixel_vanish",
            screen=True,
            color=color,
            tolerance=step.tolerance,
            tolerance_mode=tol_mode,
            timeout_ms=step.timeout_ms,
            require_seen=bool(getattr(step, "require_seen", False)),
            region=cap_region.model_dump() if cap_region else None,
            step=step_val,
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)

            phase_index = (attempt - 1) % (step_val * step_val)
            phase_y = phase_index // step_val
            phase_x = phase_index % step_val

            present = False
            try:
                m = pixel_search_file(
                    out,
                    color=color,
                    region=None,
                    tolerance=step.tolerance,
                    tolerance_mode=tol_mode,
                    step=step_val,
                    phase_x=phase_x,
                    phase_y=phase_y,
                    match_strategy=getattr(step, "match_strategy", "best"),
                    scan_order=getattr(step, "scan_order", "tlbr"),
                )
                present = True
                last_dist = float(m.dist)
                x, y = int(m.x), int(m.y)
                if cap_region is not None:
                    x += int(cap_region.x)
                    y += int(cap_region.y)
                seen_present = True
                last_seen = (x, y, float(m.dist))
                stable_since = None
                stable_hits = 0
            except PixelSearchNoMatch as e:
                last_dist = float(e.dist)
                # No match => absent.
                if stable_since is None:
                    stable_since = time.time()
                    stable_hits = 1
                else:
                    stable_hits += 1

            stable_elapsed_ms = 0
            if stable_since is not None:
                stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

            self._emit_wait_attempt(
                "pixel_vanish",
                screen=True,
                attempt=attempt,
                present=present,
                dist=last_dist,
                tolerance=step.tolerance,
                tolerance_mode=tol_mode,
                screenshot=str(out),
                step=step_val,
                stable_hits=stable_hits,
                stable_elapsed_ms=stable_elapsed_ms,
                stable_needed_hits=need_hits,
                stable_needed_ms=need_ms,
            )

            ok_now = not present
            if getattr(step, "require_seen", False) and not seen_present:
                ok_now = False
            stable_ok = ok_now and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
            if stable_ok:
                ctx[step.out_seen] = bool(seen_present)
                ctx[step.out_last_dist] = last_dist
                if last_seen is not None:
                    ctx[step.out_last_seen_x] = last_seen[0]
                    ctx[step.out_last_seen_y] = last_seen[1]
                    ctx[step.out_last_seen_dist] = last_seen[2]
                else:
                    ctx[step.out_last_seen_x] = None
                    ctx[step.out_last_seen_y] = None
                    ctx[step.out_last_seen_dist] = None
                self._emit(
                    "wait_end",
                    kind="pixel_vanish",
                    ok=True,
                    attempts=attempt,
                    seen=bool(seen_present),
                    dist=last_dist,
                    screen=True,
                    stable_hits=stable_hits,
                    stable_elapsed_ms=stable_elapsed_ms,
                )
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit(
            "wait_end",
            kind="pixel_vanish",
            ok=False,
            attempts=attempt,
            seen=bool(seen_present),
            dist=last_dist,
            screen=True,
        )
        raise TimeoutError(f"WaitForPixelVanish timed out after {step.timeout_ms}ms (seen={seen_present})")

    def _exec_pixel_get_color(self, step: StepPixelGetColor, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="pixel_get_color")

        abs_x, abs_y = self._translate_xy(int(step.x), int(step.y), target="pixel")

        # If no region is provided, capture a minimal 1x1 rectangle at (x,y).
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        if cap_region is None:
            from vhk.core.models import Region as RegionModel

            cap_region = RegionModel(x=abs_x, y=abs_y, w=1, h=1)
            local_x, local_y = 0, 0
        else:
            local_x = abs_x - int(cap_region.x)
            local_y = abs_y - int(cap_region.y)
            if local_x < 0 or local_y < 0 or local_x >= cap_region.w or local_y >= cap_region.h:
                raise ValueError(f"(x,y)=({abs_x},{abs_y}) lies outside capture region {cap_region}")

        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        c = pixel_get_color_file(out, x=local_x, y=local_y, region=None)
        ctx[step.out_hex] = c.hex
        ctx[getattr(step, "out_ahk_hex", "px_color_ahk")] = c.ahk_hex
        ctx[step.out_r] = c.r
        ctx[step.out_g] = c.g
        ctx[step.out_b] = c.b

        self._emit(
            "pixel_get_color",
            screen=True,
            x=abs_x,
            y=abs_y,
            hex=c.hex,
            ahk_hex=c.ahk_hex,
            r=c.r,
            g=c.g,
            b=c.b,
            screenshot=str(out),
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )
    def _compare_visual(self, *, baseline: Path, current: Path, color_tolerance: int) -> Any:
        return visual_compare_file(current, baseline, color_tolerance=color_tolerance)

    def _store_visual_diff(self, step: Any, ctx: dict[str, Any], diff: Any, *, ok: bool) -> None:
        ctx[step.out_ok] = bool(ok)
        ctx[step.out_changed_pixels] = int(diff.changed_pixels)
        ctx[step.out_total_pixels] = int(diff.total_pixels)
        ctx[step.out_change_ratio] = float(diff.change_ratio)
        ctx[step.out_max_channel_delta] = int(diff.max_channel_delta)

    def _visual_limits_ok(self, diff: Any, *, max_changed_pixels: int | None, max_change_ratio: float) -> bool:
        if max_changed_pixels is not None and int(diff.changed_pixels) > int(max_changed_pixels):
            return False
        if float(diff.change_ratio) > float(max_change_ratio):
            return False
        return True

    def _exec_visual_assert(self, step: StepVisualAssert, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        baseline = root / interpolate(step.baseline_path, ctx)
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="visual_assert")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        diff = self._compare_visual(baseline=baseline, current=out, color_tolerance=int(step.color_tolerance))
        ok = self._visual_limits_ok(diff, max_changed_pixels=step.max_changed_pixels, max_change_ratio=step.max_change_ratio)
        self._store_visual_diff(step, ctx, diff, ok=ok)
        self._emit(
            "visual_compare",
            mode="assert",
            ok=ok,
            baseline=str(baseline),
            current=str(out),
            changed_pixels=diff.changed_pixels,
            total_pixels=diff.total_pixels,
            change_ratio=diff.change_ratio,
            max_channel_delta=diff.max_channel_delta,
        )
        if not ok:
            diff_path = out.with_name(out.stem + ".diff.png")
            try:
                write_visual_diff_image(out, baseline, diff_path, color_tolerance=int(step.color_tolerance))
                ctx["last_visual_diff"] = str(diff_path)
                self._emit("visual_diff_artifact", mode="assert", path=str(diff_path), baseline=str(baseline), current=str(out))
            except Exception as de:
                self._emit("visual_diff_artifact", mode="assert", error=str(de), baseline=str(baseline), current=str(out))
            raise AssertionError(
                f"VisualAssert failed: changed_pixels={diff.changed_pixels} ratio={diff.change_ratio:.4f} \
limits(pixels<={step.max_changed_pixels}, ratio<={step.max_change_ratio})"
            )

    def _exec_visual_verify(self, step: StepVisualVerify, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        baseline = root / interpolate(step.baseline_path, ctx)
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="visual_verify")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        diff = self._compare_visual(baseline=baseline, current=out, color_tolerance=int(step.color_tolerance))
        ok = self._visual_limits_ok(diff, max_changed_pixels=step.max_changed_pixels, max_change_ratio=step.max_change_ratio)
        self._store_visual_diff(step, ctx, diff, ok=ok)
        self._emit(
            "visual_compare",
            mode="verify",
            ok=ok,
            baseline=str(baseline),
            current=str(out),
            changed_pixels=diff.changed_pixels,
            total_pixels=diff.total_pixels,
            change_ratio=diff.change_ratio,
            max_channel_delta=diff.max_channel_delta,
        )
        if not ok:
            diff_path = out.with_name(out.stem + ".diff.png")
            try:
                write_visual_diff_image(out, baseline, diff_path, color_tolerance=int(step.color_tolerance))
                ctx["last_visual_diff"] = str(diff_path)
                self._emit("visual_diff_artifact", mode="verify", path=str(diff_path), baseline=str(baseline), current=str(out))
            except Exception as de:
                self._emit("visual_diff_artifact", mode="verify", error=str(de), baseline=str(baseline), current=str(out))

    def _exec_wait_for_region_change(self, step: StepWaitForRegionChange, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_change")
        ctx[step.out_screenshot] = str(out)

        if step.baseline_path:
            baseline = root / interpolate(step.baseline_path, ctx)
        else:
            baseline = self._resolve_capture_path(None, ctx, prefix="wait_change_baseline")
            self._capture(baseline, region=cap_region)
        ctx[step.out_baseline] = str(baseline)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0
        last = None

        self._emit(
            "wait_start",
            kind="region_change",
            baseline=str(baseline),
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)
            last = self._compare_visual(baseline=baseline, current=out, color_tolerance=int(step.color_tolerance))
            self._emit_wait_attempt(
                "region_change",
                baseline=str(baseline),
                current=str(out),
                attempt=attempt,
                changed_pixels=last.changed_pixels,
                change_ratio=last.change_ratio,
                max_channel_delta=last.max_channel_delta,
                screen=True,
            )
            ctx[step.out_changed_pixels] = int(last.changed_pixels)
            ctx[step.out_total_pixels] = int(last.total_pixels)
            ctx[step.out_change_ratio] = float(last.change_ratio)
            ctx[step.out_max_channel_delta] = int(last.max_channel_delta)

            enough_pixels = int(last.changed_pixels) >= int(step.min_changed_pixels)
            enough_ratio = float(last.change_ratio) >= float(step.min_change_ratio)
            if enough_pixels and enough_ratio:
                self._emit(
                    "wait_end",
                    kind="region_change",
                    ok=True,
                    attempts=attempt,
                    changed_pixels=last.changed_pixels,
                    total_pixels=last.total_pixels,
                    change_ratio=last.change_ratio,
                    max_channel_delta=last.max_channel_delta,
                    screen=True,
                )
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit(
            "wait_end",
            kind="region_change",
            ok=False,
            attempts=attempt,
            changed_pixels=(last.changed_pixels if last else None),
            total_pixels=(last.total_pixels if last else None),
            change_ratio=(last.change_ratio if last else None),
            max_channel_delta=(last.max_channel_delta if last else None),
            screen=True,
        )
        if last is not None:
            diff_path = out.with_name(out.stem + ".diff.png")
            try:
                write_visual_diff_image(out, baseline, diff_path, color_tolerance=int(step.color_tolerance))
                ctx["last_visual_diff"] = str(diff_path)
                self._emit("visual_diff_artifact", mode="wait_change", path=str(diff_path), baseline=str(baseline), current=str(out))
            except Exception as de:
                self._emit("visual_diff_artifact", mode="wait_change", error=str(de), baseline=str(baseline), current=str(out))
        if last is None:
            raise TimeoutError(f"WaitForRegionChange timed out after {step.timeout_ms}ms")
        raise TimeoutError(
            f"WaitForRegionChange timed out after {step.timeout_ms}ms \
(last changed_pixels={last.changed_pixels}, ratio={last.change_ratio:.4f})"
        )

    def _exec_wait_for_region_stable(self, step: StepWaitForRegionStable, ctx: dict[str, Any]) -> None:
        """Wait until a region becomes visually stable.

        The algorithm is intentionally simple and explainable:
        - capture an initial baseline (first frame, or a provided baseline_path)
        - capture a current frame
        - compare; if within limits, count toward stability; if not, optionally roll baseline forward
        - repeat until stable_{attempts,ms} are satisfied

        This matches the "stable screenshot detection" strategy described by Vitest
        (rolling baseline on mismatch until the UI settles).
        """

        root = Path(self.project.root_dir)
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_stable")
        ctx[step.out_screenshot] = str(out)

        baseline = self._resolve_capture_path(None, ctx, prefix="wait_stable_baseline")
        if step.baseline_path:
            src = root / interpolate(step.baseline_path, ctx)
            baseline.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, baseline)
        else:
            self._capture(baseline, region=cap_region)
        ctx[step.out_baseline] = str(baseline)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last = None

        stable_since: float | None = None
        stable_hits: int = 0
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        ctx[step.out_ok] = False

        self._emit(
            "wait_start",
            kind="region_stable",
            baseline=str(baseline),
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
            rolling_baseline=bool(getattr(step, "rolling_baseline", True)),
            max_changed_pixels=getattr(step, "max_changed_pixels", None),
            max_change_ratio=float(getattr(step, "max_change_ratio", 0.0)),
        )

        with self._vision_cursor_guard(step):
            while time.time() <= deadline:
                self._check_panic()
                if step.max_attempts is not None and attempt >= step.max_attempts:
                    break
                attempt += 1

                self._capture(out, region=cap_region)
                last = self._compare_visual(baseline=baseline, current=out, color_tolerance=int(step.color_tolerance))

                ctx[step.out_changed_pixels] = int(last.changed_pixels)
                ctx[step.out_total_pixels] = int(last.total_pixels)
                ctx[step.out_change_ratio] = float(last.change_ratio)
                ctx[step.out_max_channel_delta] = int(last.max_channel_delta)

                ok_now = self._visual_limits_ok(last, max_changed_pixels=step.max_changed_pixels, max_change_ratio=step.max_change_ratio)

                if ok_now:
                    if stable_since is None:
                        stable_since = time.time()
                        stable_hits = 1
                    else:
                        stable_hits += 1
                else:
                    stable_since = None
                    stable_hits = 0
                    if getattr(step, "rolling_baseline", True):
                        try:
                            shutil.copy2(out, baseline)
                        except Exception:
                            pass

                stable_elapsed_ms = 0
                if stable_since is not None:
                    stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

                self._emit_wait_attempt(
                    "region_stable",
                    baseline=str(baseline),
                    current=str(out),
                    attempt=attempt,
                    ok=bool(ok_now),
                    changed_pixels=last.changed_pixels,
                    change_ratio=last.change_ratio,
                    max_channel_delta=last.max_channel_delta,
                    stable_hits=stable_hits,
                    stable_elapsed_ms=stable_elapsed_ms,
                    stable_needed_hits=need_hits,
                    stable_needed_ms=need_ms,
                    screen=True,
                )

                stable_ok = bool(ok_now) and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
                if stable_ok:
                    ctx[step.out_ok] = True
                    self._emit(
                        "wait_end",
                        kind="region_stable",
                        ok=True,
                        attempts=attempt,
                        changed_pixels=last.changed_pixels,
                        total_pixels=last.total_pixels,
                        change_ratio=last.change_ratio,
                        max_channel_delta=last.max_channel_delta,
                        screen=True,
                    )
                    return

                remaining = deadline - time.time()
                if remaining <= 0:
                    break

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(min(remaining, sleep_ms / 1000.0))

                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit(
            "wait_end",
            kind="region_stable",
            ok=False,
            attempts=attempt,
            changed_pixels=(last.changed_pixels if last else None),
            total_pixels=(last.total_pixels if last else None),
            change_ratio=(last.change_ratio if last else None),
            max_channel_delta=(last.max_channel_delta if last else None),
            screen=True,
        )

        if getattr(step, "debug_on_timeout", False) and last is not None:
            diff_path = out.with_name(out.stem + ".diff.png")
            try:
                write_visual_diff_image(out, baseline, diff_path, color_tolerance=int(step.color_tolerance))
                ctx[step.out_visual_diff] = str(diff_path)
                self._emit(
                    "visual_diff_artifact",
                    mode="wait_stable",
                    path=str(diff_path),
                    baseline=str(baseline),
                    current=str(out),
                )
            except Exception as de:
                self._emit(
                    "visual_diff_artifact",
                    mode="wait_stable",
                    error=str(de),
                    baseline=str(baseline),
                    current=str(out),
                )

        raise TimeoutError(f"WaitForRegionStable timed out after {step.timeout_ms}ms")


    def _exec_ocr(self, step: StepOcrReadText, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="ocr")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        text = ocr_read_text_file(
            out,
            lang=step.lang,
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )
        ctx[step.out_var] = text
        self._emit(
            "ocr",
            image=str(out),
            chars=len(text),
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )


    def _select_needle_ocr_areas(self, meta, *, area_id: str | None, area_index: int | None, strategy: str) -> list[Any]:
        """Select OCR areas from needle metadata.

        openQA supports "ocr" areas in the needle JSON. In VHK we allow
        selecting a specific OCR area either by:
          - `ocr_area_id` (VHK extension; optional `id` field on the area), or
          - `ocr_area_index` (0-based index in the JSON), or
          - a strategy (first/concat).
        """

        if meta is None:
            return []
        areas = list(getattr(meta, "ocr_areas", []) or [])
        if not areas:
            return []
        if area_id is not None:
            chosen = [a for a in areas if getattr(a, "id", None) == area_id]
            if not chosen:
                raise ValueError(f"No OCR area with id={area_id!r} in needle {meta.name}")
            return chosen
        if area_index is not None:
            i = int(area_index)
            if i < 0 or i >= len(areas):
                raise ValueError(f"ocr_area_index out of range (got {i}, available={len(areas)})")
            return [areas[i]]
        strat = (strategy or "first").strip().lower()
        if strat == "first":
            return [areas[0]]
        if strat == "concat":
            return areas
        raise ValueError("ocr_strategy must be first|concat")

    def _needle_ocr_from_match(
        self,
        screenshot_path: Path,
        *,
        needle_path: Path,
        match,
        ocr_area_id: str | None,
        ocr_area_index: int | None,
        ocr_strategy: str,
        ocr_join: str,
        fallback_to_match_bbox: bool,
        lang: str,
        preprocess: str | None,
        scale: float | int | None,
        psm: int | None,
        oem: int | None,
        tess_config: str | None,
    ) -> tuple[str, Any | None, list[Any]]:
        """Return (text, union_region, regions_used) for OCR relative to a needle match."""

        from vhk.core.models import Region as RegionModel

        meta = try_load_needle(needle_path)
        if meta is not None and abs(float(getattr(match, "scale", 1.0)) - 1.0) > 1e-9:
            meta = scale_needle(meta, float(match.scale))

        chosen = self._select_needle_ocr_areas(meta, area_id=ocr_area_id, area_index=ocr_area_index, strategy=ocr_strategy)

        # Base offset: match coords correspond to the union bbox of match areas when present.
        min_x, min_y = 0, 0
        if meta is not None and getattr(meta, "match_areas", None):
            ma = meta.match_areas
            if ma:
                min_x = min(int(a.xpos) for a in ma)
                min_y = min(int(a.ypos) for a in ma)

        regions: list[RegionModel] = []
        if chosen:
            for a in chosen:
                rx = int(match.x) + int(getattr(a, "xpos", 0)) - int(min_x)
                ry = int(match.y) + int(getattr(a, "ypos", 0)) - int(min_y)
                rw = int(getattr(a, "width", 0))
                rh = int(getattr(a, "height", 0))
                if rw <= 0 or rh <= 0:
                    continue
                regions.append(RegionModel(x=rx, y=ry, w=rw, h=rh))

        if not regions and bool(fallback_to_match_bbox):
            regions = [RegionModel(x=int(match.x), y=int(match.y), w=int(match.w), h=int(match.h))]

        if not regions:
            return "", None, []

        texts: list[str] = []
        for r in regions:
            txt = ocr_read_text_file(
                screenshot_path,
                lang=lang,
                region=r,
                preprocess=preprocess,
                scale=scale,
                psm=psm,
                oem=oem,
                tess_config=tess_config,
            )
            if txt:
                texts.append(txt)

        joiner = str(ocr_join) if ocr_join is not None else "\n"
        merged = joiner.join(texts).strip()

        ux1 = min(int(r.x) for r in regions)
        uy1 = min(int(r.y) for r in regions)
        ux2 = max(int(r.x) + int(r.w) for r in regions)
        uy2 = max(int(r.y) + int(r.h) for r in regions)
        union = RegionModel(x=ux1, y=uy1, w=max(1, ux2 - ux1), h=max(1, uy2 - uy1))
        return merged, union, regions

    def _exec_ocr_needle_text(self, step: StepOcrNeedleText, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="ocr_needle")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        m = image_search_file(out, needle, region=None, threshold=-1e9, scales=step.scales)
        if float(m.score) < float(step.threshold):
            raise RuntimeError(
                f"OcrNeedleText: needle did not meet threshold. best={m.score:.3f} threshold={float(step.threshold):.3f}"
            )

        txt, ocr_union, _regions = self._needle_ocr_from_match(
            out,
            needle_path=needle,
            match=m,
            ocr_area_id=getattr(step, "ocr_area_id", None),
            ocr_area_index=getattr(step, "ocr_area_index", None),
            ocr_strategy=getattr(step, "ocr_strategy", "first"),
            ocr_join=getattr(step, "ocr_join", "\n"),
            fallback_to_match_bbox=bool(getattr(step, "fallback_to_match_bbox", True)),
            lang=step.lang,
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )

        # Match coords in screen space.
        mx, my = int(m.x), int(m.y)
        if cap_region is not None:
            mx += int(cap_region.x)
            my += int(cap_region.y)

        ctx[step.out_text] = txt
        ctx[step.out_match_x] = mx
        ctx[step.out_match_y] = my
        ctx[step.out_match_score] = float(m.score)
        ctx[step.out_match_w] = int(m.w)
        ctx[step.out_match_h] = int(m.h)

        if ocr_union is not None:
            ox, oy = int(ocr_union.x), int(ocr_union.y)
            if cap_region is not None:
                ox += int(cap_region.x)
                oy += int(cap_region.y)
            ctx[step.out_ocr_x] = ox
            ctx[step.out_ocr_y] = oy
            ctx[step.out_ocr_w] = int(ocr_union.w)
            ctx[step.out_ocr_h] = int(ocr_union.h)

        self._emit(
            "ocr_needle",
            needle=str(needle),
            threshold=float(step.threshold),
            match_score=float(m.score),
            match_x=mx,
            match_y=my,
            match_w=int(m.w),
            match_h=int(m.h),
            ocr_chars=len(txt),
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

    def _exec_wait_for_needle_text(self, step: StepWaitForNeedleText, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_needle_text")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0

        stable_since: float | None = None
        stable_hits: int = 0
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        # When using stability criteria, allow a small grace window beyond the
        # nominal timeout so tight timeouts do not become flaky due to I/O
        # overhead (e.g. writing screenshots to disk).
        grace_s = max(0.25, (need_ms / 1000.0) + 0.05) if (need_hits > 1 or need_ms > 0) else 0.0

        self._emit(
            "wait_start",
            kind="needle_text",
            needle=str(needle),
            threshold=float(step.threshold),
            pattern=pattern,
            match=step.match,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        last_score: float | None = None
        last_txt: str = ""
        last_m = None
        last_ocr_union = None

        while True:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            now = time.time()
            if step.max_attempts is None and now > deadline:
                # If we have not started accumulating stability hits, respect the timeout.
                if stable_hits <= 0 or stable_since is None:
                    break
                # Otherwise, allow a small grace period to confirm stability.
                if grace_s and now > (deadline + grace_s):
                    break
            attempt += 1

            self._capture(out, region=cap_region)
            m = image_search_file(out, needle, region=None, threshold=-1e9, scales=step.scales)
            last_m = m
            last_score = float(m.score)

            ok = False
            txt = ""
            ocr_union = None
            if float(m.score) >= float(step.threshold):
                txt, ocr_union, _regions = self._needle_ocr_from_match(
                    out,
                    needle_path=needle,
                    match=m,
                    ocr_area_id=getattr(step, "ocr_area_id", None),
                    ocr_area_index=getattr(step, "ocr_area_index", None),
                    ocr_strategy=getattr(step, "ocr_strategy", "first"),
                    ocr_join=getattr(step, "ocr_join", "\n"),
                    fallback_to_match_bbox=bool(getattr(step, "fallback_to_match_bbox", True)),
                    lang=step.lang,
                    preprocess=getattr(step, "preprocess", None),
                    scale=getattr(step, "scale", 1.0),
                    psm=getattr(step, "psm", None),
                    oem=getattr(step, "oem", None),
                    tess_config=getattr(step, "tess_config", None),
                )
                ok = self._text_matches(
                    txt,
                    pattern,
                    step.match,
                    case_sensitive=step.case_sensitive,
                    fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
                    fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
                )

            last_txt = txt
            last_ocr_union = ocr_union
            ctx[step.out_text] = txt

            if ok:
                if stable_since is None:
                    stable_since = time.time()
                    stable_hits = 1
                else:
                    stable_hits += 1
            else:
                stable_since = None
                stable_hits = 0

            stable_elapsed_ms = 0
            if stable_since is not None:
                stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

            self._emit_wait_attempt(
                "needle_text",
                needle=str(needle),
                attempt=attempt,
                score=float(m.score),
                threshold=float(step.threshold),
                matched=ok,
                chars=len(txt),
                preview=txt[:120],
                screen=True,
                stable_hits=stable_hits,
                stable_elapsed_ms=stable_elapsed_ms,
                stable_needed_hits=need_hits,
                stable_needed_ms=need_ms,
            )

            stable_ok = ok and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
            if stable_ok:
                # Match coords in screen space
                mx, my = int(m.x), int(m.y)
                if cap_region is not None:
                    mx += int(cap_region.x)
                    my += int(cap_region.y)

                ctx[step.out_found] = True
                ctx[step.out_match_x] = mx
                ctx[step.out_match_y] = my
                ctx[step.out_match_score] = float(m.score)
                ctx[step.out_match_w] = int(m.w)
                ctx[step.out_match_h] = int(m.h)

                if ocr_union is not None:
                    ox, oy = int(ocr_union.x), int(ocr_union.y)
                    if cap_region is not None:
                        ox += int(cap_region.x)
                        oy += int(cap_region.y)
                    ctx[step.out_ocr_x] = ox
                    ctx[step.out_ocr_y] = oy
                    ctx[step.out_ocr_w] = int(ocr_union.w)
                    ctx[step.out_ocr_h] = int(ocr_union.h)

                self._emit(
                    "wait_end",
                    kind="needle_text",
                    ok=True,
                    attempts=attempt,
                    score=float(m.score),
                    screen=True,
                    stable_hits=stable_hits,
                    stable_elapsed_ms=stable_elapsed_ms,
                )
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        ctx[step.out_found] = False
        self._emit("wait_end", kind="needle_text", ok=False, attempts=attempt, score=last_score, screen=True)
        raise TimeoutError(
            f"WaitForNeedleText timed out after {step.timeout_ms}ms (last score={last_score}, last text={last_txt[:80]!r})"
        )


    def _exec_ocr_find_text(self, step: StepOcrFindText, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="ocr_find")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)
        span = ocr_find_text_file(
            out,
            pattern=pattern,
            match=step.match,
            fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
            fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
            case_sensitive=step.case_sensitive,
            lang=step.lang,
            region=None,
            level=getattr(step, "level", "word"),
            match_strategy=getattr(step, "match_strategy", "first"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )

        x, y = int(span.x), int(span.y)
        if cap_region is not None:
            x += int(cap_region.x)
            y += int(cap_region.y)

        ctx[step.out_x] = x
        ctx[step.out_y] = y
        ctx[step.out_w] = int(span.w)
        ctx[step.out_h] = int(span.h)
        ctx[step.out_text] = span.text
        ctx[step.out_conf] = float(span.conf)

        self._emit(
            "ocr_find_text",
            screen=True,
            pattern=pattern,
            match=step.match,
            level=getattr(step, "level", "word"),
            match_strategy=getattr(step, "match_strategy", "first"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            x=x,
            y=y,
            w=int(span.w),
            h=int(span.h),
            conf=float(span.conf),
            text=span.text,
            screenshot=str(out),
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

    

    def _exec_ocr_find_text_all(self, step: StepOcrFindTextAll, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="ocr_find_all")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)
        spans = ocr_find_text_all_file(
            out,
            pattern=pattern,
            match=step.match,
            fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
            fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
            case_sensitive=step.case_sensitive,
            lang=step.lang,
            region=None,
            level=getattr(step, "level", "word"),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            max_results=getattr(step, "max_results", None),
            min_conf=getattr(step, "min_conf", None),
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )

        matches = []
        for s in spans:
            x, y = int(s.x), int(s.y)
            if cap_region is not None:
                x += int(cap_region.x)
                y += int(cap_region.y)
            matches.append({"x": x, "y": y, "w": int(s.w), "h": int(s.h), "text": s.text, "conf": float(s.conf)})

        ctx[step.out_matches] = matches
        ctx[step.out_count] = len(matches)

        self._emit(
            "ocr_find_text_all",
            screen=True,
            pattern=pattern,
            match=step.match,
            level=getattr(step, "level", "word"),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            count=len(matches),
            screenshot=str(out),
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

    def _exec_wait_for_text(self, step: StepWaitForText, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_text")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0

        self._emit(
            "wait_start",
            kind="text",
            pattern=pattern,
            match=step.match,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)
            txt = ocr_read_text_file(
                out,
                lang=step.lang,
                preprocess=getattr(step, "preprocess", None),
                scale=getattr(step, "scale", 1.0),
                psm=getattr(step, "psm", None),
                oem=getattr(step, "oem", None),
                tess_config=getattr(step, "tess_config", None),
            )
            ctx[step.out_text] = txt
            ok = self._text_matches(
                txt,
                pattern,
                step.match,
                case_sensitive=step.case_sensitive,
                fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
                fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
            )
            self._emit_wait_attempt(
                "text",
                attempt=attempt,
                pattern=pattern,
                matched=ok,
                chars=len(txt),
                preview=txt[:120],
                screen=True,
            )
            if ok:
                ctx[step.out_found] = True
                self._emit("wait_end", kind="text", ok=True, attempts=attempt, screen=True)
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        ctx[step.out_found] = False
        self._emit("wait_end", kind="text", ok=False, attempts=attempt, screen=True)
        raise TimeoutError(f"WaitForText timed out after {step.timeout_ms}ms")



    def _exec_wait_for_text_vanish(self, step: StepWaitForTextVanish, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_text_vanish")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0

        seen_present = False
        last_text = ""
        last_present = False

        stable_since: float | None = None
        stable_hits: int = 0
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        self._emit(
            "wait_start",
            kind="text_vanish",
            pattern=pattern,
            match=step.match,
            timeout_ms=step.timeout_ms,
            require_seen=bool(getattr(step, "require_seen", False)),
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)
            txt = ocr_read_text_file(
                out,
                lang=step.lang,
                preprocess=getattr(step, "preprocess", None),
                scale=getattr(step, "scale", 1.0),
                psm=getattr(step, "psm", None),
                oem=getattr(step, "oem", None),
                tess_config=getattr(step, "tess_config", None),
            )
            ctx[step.out_text] = txt

            present = self._text_matches(
                txt,
                pattern,
                step.match,
                case_sensitive=step.case_sensitive,
                fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
                fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
            )

            last_present = bool(present)
            if present:
                seen_present = True
                last_text = txt
                stable_since = None
                stable_hits = 0
            else:
                if stable_since is None:
                    stable_since = time.time()
                    stable_hits = 1
                else:
                    stable_hits += 1

            stable_elapsed_ms = 0
            if stable_since is not None:
                stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

            self._emit_wait_attempt(
                "text_vanish",
                attempt=attempt,
                pattern=pattern,
                present=present,
                chars=len(txt),
                preview=txt[:120],
                screen=True,
                stable_hits=stable_hits,
                stable_elapsed_ms=stable_elapsed_ms,
                stable_needed_hits=need_hits,
                stable_needed_ms=need_ms,
            )

            ok_now = not present
            if getattr(step, "require_seen", False) and not seen_present:
                ok_now = False

            stable_ok = ok_now and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
            if stable_ok:
                ctx[step.out_seen] = bool(seen_present)
                ctx[step.out_last_text] = str(last_text)
                ctx[step.out_last_present] = bool(last_present)
                self._emit("wait_end", kind="text_vanish", ok=True, attempts=attempt, screen=True)
                return

            remaining = deadline - time.time()
            if remaining <= 0:
                break

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(min(remaining, sleep_ms / 1000.0))

            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        ctx[step.out_seen] = bool(seen_present)
        ctx[step.out_last_text] = str(last_text)
        ctx[step.out_last_present] = bool(last_present)
        self._emit("wait_end", kind="text_vanish", ok=False, attempts=attempt, screen=True)
        raise TimeoutError(f"WaitForTextVanish timed out after {step.timeout_ms}ms")
    def _exec_wait_for_text_box(self, step: StepWaitForTextBox, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_textbox")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)
        level = getattr(step, "level", "word")
        match_strategy = getattr(step, "match_strategy", "first")
        scan_order = getattr(step, "scan_order", "tlbr")

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0

        self._emit(
            "wait_start",
            kind="text_box",
            pattern=pattern,
            match=step.match,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        last_text = ""
        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)

            spans = ocr_read_spans_file(
                out,
                lang=step.lang,
                region=None,
                level=level,
                preprocess=getattr(step, "preprocess", None),
                scale=getattr(step, "scale", 1.0),
                psm=getattr(step, "psm", None),
                oem=getattr(step, "oem", None),
                tess_config=getattr(step, "tess_config", None),
            )
            last_text = ocr_spans_to_text(spans, level=level)
            ctx[step.out_ocr_text] = last_text

            ok = False
            try:
                span = ocr_find_text_in_spans(
                    spans,
                    pattern=pattern,
                    match=step.match,
                    fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
                    fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
                    case_sensitive=step.case_sensitive,
                    match_strategy=match_strategy,
                    scan_order=scan_order,
                )
                ok = True
            except Exception:
                span = None

            self._emit_wait_attempt(
                "text_box",
                attempt=attempt,
                pattern=pattern,
                matched=ok,
                chars=len(last_text),
                preview=last_text[:120],
                screen=True,
            )

            if ok and span is not None:
                x, y = int(span.x), int(span.y)
                if cap_region is not None:
                    x += int(cap_region.x)
                    y += int(cap_region.y)
                ctx[step.out_found] = True
                ctx[step.out_x] = x
                ctx[step.out_y] = y
                ctx[step.out_w] = int(span.w)
                ctx[step.out_h] = int(span.h)
                ctx[step.out_text] = span.text
                ctx[step.out_conf] = float(span.conf)

                self._emit(
                    "wait_end",
                    kind="text_box",
                    ok=True,
                    attempts=attempt,
                    x=x,
                    y=y,
                    w=int(span.w),
                    h=int(span.h),
                    conf=float(span.conf),
                    screen=True,
                )
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        ctx[step.out_found] = False
        self._emit("wait_end", kind="text_box", ok=False, attempts=attempt, screen=True)
        raise TimeoutError(f"WaitForTextBox timed out after {step.timeout_ms}ms")

    def _exec_assert_text(self, step: StepAssertText, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="assert_text")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)
        txt = ocr_read_text_file(
            out,
            lang=step.lang,
            preprocess=getattr(step, "preprocess", None),
            scale=getattr(step, "scale", 1.0),
            psm=getattr(step, "psm", None),
            oem=getattr(step, "oem", None),
            tess_config=getattr(step, "tess_config", None),
        )
        ctx[step.out_text] = txt

        ok = self._text_matches(
            txt,
            pattern,
            step.match,
            case_sensitive=step.case_sensitive,
            fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
            fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
        )
        self._emit("assert_text", ok=ok, match=step.match, screen=True, coord_mode=self._coord_mode_pixel)
        if not ok:
            raise AssertionError(f"AssertText failed ({step.match}): {pattern!r}")

    def _exec_click_text(self, step: StepClickText, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="click_text")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)
        level = getattr(step, "level", "word")
        match_strategy = getattr(step, "match_strategy", "first")
        scan_order = getattr(step, "scan_order", "tlbr")

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last_text = ""

        self._emit(
            "wait_start",
            kind="click_text",
            pattern=pattern,
            match=step.match,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)
            spans = ocr_read_spans_file(
                out,
                lang=step.lang,
                region=None,
                level=level,
                preprocess=getattr(step, "preprocess", None),
                scale=getattr(step, "scale", 1.0),
                psm=getattr(step, "psm", None),
                oem=getattr(step, "oem", None),
                tess_config=getattr(step, "tess_config", None),
            )
            last_text = ocr_spans_to_text(spans, level=level)

            try:
                span = ocr_find_text_in_spans(
                    spans,
                    pattern=pattern,
                    match=step.match,
                    fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
                    fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
                    case_sensitive=step.case_sensitive,
                    match_strategy=match_strategy,
                    scan_order=scan_order,
                )
            except Exception:
                span = None

            ok = span is not None
            self._emit_wait_attempt(
                "click_text",
                attempt=attempt,
                pattern=pattern,
                matched=ok,
                chars=len(last_text),
                preview=last_text[:120],
                screen=True,
            )

            if ok and span is not None:
                mx, my = int(span.x), int(span.y)
                if cap_region is not None:
                    mx += int(cap_region.x)
                    my += int(cap_region.y)

                offx = self._as_int(step.offset_x, ctx, field="ClickText.offset_x")
                offy = self._as_int(step.offset_y, ctx, field="ClickText.offset_y")
                cx = int(mx + (int(span.w) // 2) + offx)
                cy = int(my + (int(span.h) // 2) + offy)

                ctx[step.out_match_x] = mx
                ctx[step.out_match_y] = my
                ctx[step.out_match_w] = int(span.w)
                ctx[step.out_match_h] = int(span.h)
                ctx[step.out_match_text] = span.text
                ctx[step.out_match_conf] = float(span.conf)
                ctx[step.out_click_x] = cx
                ctx[step.out_click_y] = cy

                self._emit(
                    "wait_end",
                    kind="click_text",
                    ok=True,
                    attempts=attempt,
                    match_x=mx,
                    match_y=my,
                    click_x=cx,
                    click_y=cy,
                    screen=True,
                    dry_run=bool(self.project.settings.dry_run),
                )

                button = self._as_int(step.button, ctx, field="ClickText.button")
                self._emit(
                    "input",
                    kind="click_text",
                    x=cx,
                    y=cy,
                    button=button,
                    dry_run=bool(self.project.settings.dry_run),
                )
                if not self.project.settings.dry_run:
                    input_mod.mouse_move(x=cx, y=cy)
                    input_mod.mouse_click(button, clearmodifiers=step.clearmodifiers)
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit("wait_end", kind="click_text", ok=False, attempts=attempt, screen=True)
        raise TimeoutError(f"ClickText timed out after {step.timeout_ms}ms")

    def _exec_click_text_all(self, step: StepClickTextAll, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="click_text_all")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)
        level = getattr(step, "level", "word")
        sort = getattr(step, "sort", "scan")
        scan_order = getattr(step, "scan_order", "tlbr")

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0
        last_text = ""

        self._emit(
            "wait_start",
            kind="click_text_all",
            pattern=pattern,
            match=step.match,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)
            spans = ocr_read_spans_file(
                out,
                lang=step.lang,
                region=None,
                level=level,
                preprocess=getattr(step, "preprocess", None),
                scale=getattr(step, "scale", 1.0),
                psm=getattr(step, "psm", None),
                oem=getattr(step, "oem", None),
                tess_config=getattr(step, "tess_config", None),
            )
            last_text = ocr_spans_to_text(spans, level=level)

            try:
                matches_spans = ocr_find_text_all_in_spans(
                    spans,
                    pattern=pattern,
                    match=step.match,
                    fuzzy_threshold=getattr(step, "fuzzy_threshold", None),
                    fuzzy_mode=getattr(step, "fuzzy_mode", "partial"),
                    case_sensitive=step.case_sensitive,
                    sort=sort,
                    scan_order=scan_order,
                    max_results=getattr(step, "max_results", None),
                    min_conf=getattr(step, "min_conf", None),
                )
            except Exception:
                matches_spans = []

            ok = len(matches_spans) > 0
            self._emit_wait_attempt(
                "click_text_all",
                attempt=attempt,
                pattern=pattern,
                matched=ok,
                chars=len(last_text),
                preview=last_text[:120],
                screen=True,
            )

            if ok:
                offx = self._as_int(step.offset_x, ctx, field="ClickTextAll.offset_x")
                offy = self._as_int(step.offset_y, ctx, field="ClickTextAll.offset_y")
                button = self._as_int(step.button, ctx, field="ClickTextAll.button")

                matches = []
                click_points = []
                for s in matches_spans:
                    mx, my = int(s.x), int(s.y)
                    if cap_region is not None:
                        mx += int(cap_region.x)
                        my += int(cap_region.y)
                    matches.append({"x": mx, "y": my, "w": int(s.w), "h": int(s.h), "text": s.text, "conf": float(s.conf)})
                    cx = int(mx + (int(s.w) // 2) + offx)
                    cy = int(my + (int(s.h) // 2) + offy)
                    click_points.append({"x": cx, "y": cy, "text": s.text, "conf": float(s.conf)})

                ctx[step.out_matches] = matches
                ctx[step.out_count] = len(matches)
                ctx[step.out_clicks] = click_points
                ctx[step.out_clicked_count] = len(click_points)
                if click_points:
                    ctx[step.out_last_click_x] = int(click_points[-1]["x"])
                    ctx[step.out_last_click_y] = int(click_points[-1]["y"])

                self._emit(
                    "wait_end",
                    kind="click_text_all",
                    ok=True,
                    attempts=attempt,
                    count=len(matches),
                    screen=True,
                    dry_run=bool(self.project.settings.dry_run),
                )

                self._emit(
                    "input",
                    kind="click_text_all",
                    button=button,
                    count=len(click_points),
                    dry_run=bool(self.project.settings.dry_run),
                )

                if not self.project.settings.dry_run:
                    for idx, pt in enumerate(click_points):
                        cx = int(pt["x"])
                        cy = int(pt["y"])
                        input_mod.mouse_move(x=cx, y=cy)
                        input_mod.mouse_click(button, clearmodifiers=step.clearmodifiers)
                        if idx < len(click_points) - 1 and step.delay_between_clicks_ms:
                            time.sleep(max(0, int(step.delay_between_clicks_ms)) / 1000.0)
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit("wait_end", kind="click_text_all", ok=False, attempts=attempt, screen=True)
        raise TimeoutError(f"ClickTextAll timed out after {step.timeout_ms}ms")

    def _exec_click_image_all(self, step: StepClickImageAll, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="click_image_all")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0
        last_best: float | None = None
        last_count: int = 0

        min_count = int(getattr(step, "min_count", 1) or 1)
        if min_count < 1:
            min_count = 1

        meta = try_load_needle(needle)

        self._emit(
            "wait_start",
            kind="click_image_all",
            needle=str(needle),
            threshold=step.threshold,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            min_count=min_count,
            max_results=getattr(step, "max_results", 50),
            overlap_threshold=getattr(step, "overlap_threshold", 0.3),
            sort=getattr(step, "sort", "score"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            coord_mode=self._coord_mode_pixel,
        )

        with self._vision_cursor_guard(step):

            while time.time() <= deadline:
                self._check_panic()
                if step.max_attempts is not None and attempt >= step.max_attempts:
                    break
                attempt += 1

                self._capture(out, region=cap_region)

                best = image_search_file(out, needle, region=None, threshold=-1e9, scales=step.scales)
                last_best = float(best.score)

                matches = []
                if best.score >= step.threshold:
                    matches = image_search_all_file(
                        out,
                        needle,
                        region=None,
                        threshold=step.threshold,
                        scales=step.scales,
                        max_results=getattr(step, "max_results", 50),
                        overlap_threshold=getattr(step, "overlap_threshold", 0.3),
                        sort=getattr(step, "sort", "score"),
                        scan_order=getattr(step, "scan_order", "tlbr"),
                    )

                last_count = len(matches)
                ok = last_count >= min_count
                self._emit_wait_attempt(
                    "click_image_all",
                    needle=str(needle),
                    attempt=attempt,
                    score=float(last_best) if last_best is not None else None,
                    threshold=step.threshold,
                    count=last_count,
                    min_count=min_count,
                    screen=True,
                )

                if ok:
                    offx = self._as_int(step.offset_x, ctx, field="ClickImageAll.offset_x")
                    offy = self._as_int(step.offset_y, ctx, field="ClickImageAll.offset_y")
                    button = self._as_int(step.button, ctx, field="ClickImageAll.button")

                    payload_matches = []
                    click_points = []
                    for m in matches:
                        mx, my = int(m.x), int(m.y)
                        if cap_region is not None:
                            mx += int(cap_region.x)
                            my += int(cap_region.y)

                        # Default click point: center of match.
                        dx = int(m.w // 2)
                        dy = int(m.h // 2)

                        # openQA-style click points when metadata match areas exist.
                        if meta and meta.match_areas:
                            meta_s = scale_needle(meta, float(getattr(m, "scale", 1.0)))
                            dx, dy = compute_click_offset(meta_s, click_point_id=getattr(step, "click_point_id", None))

                        cx = int(mx + dx + offx)
                        cy = int(my + dy + offy)

                        payload_matches.append(
                            {"x": mx, "y": my, "w": int(m.w), "h": int(m.h), "score": float(m.score), "scale": float(m.scale)}
                        )
                        click_points.append({"x": cx, "y": cy, "score": float(m.score), "scale": float(m.scale)})

                    ctx[step.out_matches] = payload_matches
                    ctx[step.out_count] = len(payload_matches)
                    ctx[step.out_clicks] = click_points
                    ctx[step.out_clicked_count] = len(click_points)
                    if click_points:
                        ctx[step.out_last_click_x] = int(click_points[-1]["x"])
                        ctx[step.out_last_click_y] = int(click_points[-1]["y"])

                    self._emit(
                        "wait_end",
                        kind="click_image_all",
                        ok=True,
                        attempts=attempt,
                        score=float(last_best) if last_best is not None else None,
                        count=len(payload_matches),
                        screen=True,
                        dry_run=bool(self.project.settings.dry_run),
                    )

                    self._emit(
                        "input",
                        kind="click_image_all",
                        button=button,
                        count=len(click_points),
                        dry_run=bool(self.project.settings.dry_run),
                    )

                    if not self.project.settings.dry_run:
                        for idx, pt in enumerate(click_points):
                            input_mod.mouse_move(x=int(pt["x"]), y=int(pt["y"]))
                            input_mod.mouse_click(button, clearmodifiers=step.clearmodifiers)
                            if idx < len(click_points) - 1 and step.delay_between_clicks_ms:
                                time.sleep(max(0, int(step.delay_between_clicks_ms)) / 1000.0)
                    return

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(sleep_ms / 1000.0)
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

            self._emit(
                "wait_end",
                kind="click_image_all",
                ok=False,
                attempts=attempt,
                score=float(last_best) if last_best is not None else None,
                count=last_count,
                screen=True,
            )
            raise TimeoutError(
                f"ClickImageAll timed out after {step.timeout_ms}ms (last best score={last_best}, last count={last_count})"
            )

    def _exec_click_pixel_all(self, step: StepClickPixelAll, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="click_pixel_all")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0

        color = self._render_value(step.color, ctx)
        tol_mode = getattr(step, "tolerance_mode", "euclidean")
        step_val = int(getattr(step, "step", 1) or 1)
        if step_val < 1:
            step_val = 1

        self._emit(
            "wait_start",
            kind="click_pixel_all",
            screen=True,
            color=color,
            tolerance=step.tolerance,
            tolerance_mode=tol_mode,
            timeout_ms=step.timeout_ms,
            region=cap_region.model_dump() if cap_region else None,
            step=step_val,
            group=getattr(step, "group", "none"),
            pick=getattr(step, "pick", "center"),
            min_area=getattr(step, "min_area", 1),
            min_count=getattr(step, "min_count", 1),
            max_results=getattr(step, "max_results", 200),
            sort=getattr(step, "sort", "scan"),
            scan_order=getattr(step, "scan_order", "tlbr"),
            coord_mode=self._coord_mode_pixel,
        )

        while time.time() <= deadline:
            self._check_panic()
            if step.max_attempts is not None and attempt >= step.max_attempts:
                break
            attempt += 1

            self._capture(out, region=cap_region)
            phase_index = (attempt - 1) % (step_val * step_val)
            phase_y = phase_index // step_val
            phase_x = phase_index % step_val

            hits = pixel_search_all_file(
                out,
                color=color,
                region=None,
                tolerance=step.tolerance,
                tolerance_mode=tol_mode,
                step=step_val,
                phase_x=phase_x,
                phase_y=phase_y,
                group=getattr(step, "group", "none"),
                pick=getattr(step, "pick", "center"),
                min_area=getattr(step, "min_area", 1),
                max_results=getattr(step, "max_results", 200),
                sort=getattr(step, "sort", "scan"),
                scan_order=getattr(step, "scan_order", "tlbr"),
            )

            matches = []
            for h in hits:
                x, y = int(h.x), int(h.y)
                bx = int(h.bbox_x) if getattr(h, "bbox_x", None) is not None else x
                by = int(h.bbox_y) if getattr(h, "bbox_y", None) is not None else y
                if cap_region is not None:
                    x += int(cap_region.x)
                    y += int(cap_region.y)
                    bx += int(cap_region.x)
                    by += int(cap_region.y)
                matches.append(
                    {
                        "x": x,
                        "y": y,
                        "dist": float(h.dist),
                        "w": int(getattr(h, "w", 1)),
                        "h": int(getattr(h, "h", 1)),
                        "area": int(getattr(h, "area", 1)),
                        "bbox_x": bx,
                        "bbox_y": by,
                    }
                )

            ok = len(matches) >= int(getattr(step, "min_count", 1) or 1)
            best_dist = min((float(m["dist"]) for m in matches), default=None)
            self._emit_wait_attempt(
                "click_pixel_all",
                attempt=attempt,
                matched=ok,
                count=len(matches),
                best_dist=best_dist,
                screen=True,
                screenshot=str(out),
                step=step_val,
            )

            if ok:
                offx = self._as_int(step.offset_x, ctx, field="ClickPixelAll.offset_x")
                offy = self._as_int(step.offset_y, ctx, field="ClickPixelAll.offset_y")
                button = self._as_int(step.button, ctx, field="ClickPixelAll.button")

                click_points = []
                for m in matches:
                    bx = int(m.get("bbox_x", m["x"]))
                    by = int(m.get("bbox_y", m["y"]))
                    w = int(m.get("w", 1))
                    h = int(m.get("h", 1))
                    cx = int(bx + (w // 2) + offx)
                    cy = int(by + (h // 2) + offy)
                    click_points.append({"x": cx, "y": cy, "dist": float(m["dist"]), "area": int(m.get("area", 1))})

                ctx[step.out_matches] = matches
                ctx[step.out_count] = len(matches)
                ctx[step.out_clicks] = click_points
                ctx[step.out_clicked_count] = len(click_points)
                if click_points:
                    ctx[step.out_last_click_x] = int(click_points[-1]["x"])
                    ctx[step.out_last_click_y] = int(click_points[-1]["y"])

                self._emit(
                    "wait_end",
                    kind="click_pixel_all",
                    ok=True,
                    attempts=attempt,
                    count=len(matches),
                    best_dist=best_dist,
                    screen=True,
                    dry_run=bool(self.project.settings.dry_run),
                )
                self._emit(
                    "input",
                    kind="click_pixel_all",
                    button=button,
                    count=len(click_points),
                    dry_run=bool(self.project.settings.dry_run),
                )

                if not self.project.settings.dry_run:
                    for idx, pt in enumerate(click_points):
                        input_mod.mouse_move(x=int(pt["x"]), y=int(pt["y"]))
                        input_mod.mouse_click(button, clearmodifiers=step.clearmodifiers)
                        if idx < len(click_points) - 1 and step.delay_between_clicks_ms:
                            time.sleep(max(0, int(step.delay_between_clicks_ms)) / 1000.0)
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

        self._emit("wait_end", kind="click_pixel_all", ok=False, attempts=attempt, screen=True)
        raise TimeoutError(f"ClickPixelAll timed out after {step.timeout_ms}ms")

    def _exec_click_needle(self, step: StepClickNeedle, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="click_needle")
        cap_region = self._translate_region(step.region, target="pixel", ctx=ctx)
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0
        last = None

        self._emit(
            "wait_start",
            kind="click_needle",
            needle=str(needle),
            threshold=step.threshold,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
            coord_mode=self._coord_mode_pixel,
        )

        with self._vision_cursor_guard(step):

            while time.time() <= deadline:
                self._check_panic()
                if step.max_attempts is not None and attempt >= step.max_attempts:
                    break
                attempt += 1

                self._capture(out, region=cap_region)
                last = image_search_file(out, needle, region=None, threshold=-1e9, scales=step.scales)
                self._emit_wait_attempt(
                    "click_needle",
                    needle=str(needle),
                    attempt=attempt,
                    score=last.score,
                    threshold=step.threshold,
                    x=last.x,
                    y=last.y,
                    screen=True,
                )
                if last.score >= step.threshold:
                    mx, my = last.x, last.y
                    if cap_region is not None:
                        mx += cap_region.x
                        my += cap_region.y

                    # Determine click offset.
                    dx = last.w // 2
                    dy = last.h // 2
                    meta = try_load_needle(needle)
                    if meta and meta.match_areas:
                        meta_s = scale_needle(meta, float(getattr(last, "scale", 1.0)))
                        dx, dy = compute_click_offset(meta_s, click_point_id=step.click_point_id)

                    offx = self._as_int(step.offset_x, ctx, field='ClickNeedle.offset_x')
                    offy = self._as_int(step.offset_y, ctx, field='ClickNeedle.offset_y')
                    cx = int(mx + dx + offx)
                    cy = int(my + dy + offy)

                    ctx[step.out_match_x] = mx
                    ctx[step.out_match_y] = my
                    ctx[step.out_match_score] = last.score
                    ctx[step.out_match_w] = last.w
                    ctx[step.out_match_h] = last.h
                    ctx[step.out_click_x] = cx
                    ctx[step.out_click_y] = cy

                    self._emit(
                        "wait_end",
                        kind="click_needle",
                        ok=True,
                        attempts=attempt,
                        score=last.score,
                        match_x=mx,
                        match_y=my,
                        click_x=cx,
                        click_y=cy,
                        screen=True,
                        dry_run=bool(self.project.settings.dry_run),
                    )

                    # Execute click.
                    button = self._as_int(step.button, ctx, field='ClickNeedle.button')
                    self._emit(
                        "input",
                        kind="click_needle",
                        x=cx,
                        y=cy,
                        button=button,
                        dry_run=bool(self.project.settings.dry_run),
                    )
                    if not self.project.settings.dry_run:
                        input_mod.mouse_move(x=cx, y=cy)
                        input_mod.mouse_click(button, clearmodifiers=step.clearmodifiers)
                    return

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(sleep_ms / 1000.0)
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

            score = last.score if last else None
        self._emit("wait_end", kind="click_needle", ok=False, attempts=attempt, score=score, screen=True)

        if getattr(step, "debug_on_timeout", False) and last is not None:
            try:
                from vhk.vision.annotate import annotate_match

                meta = try_load_needle(needle)
                dbg = out.with_name(out.stem + "_annotated.png")
                annotate_match(out, dbg, last, needle_meta=meta, threshold=step.threshold, ok=False)
                if getattr(step, "out_debug_screenshot", None):
                    ctx[step.out_debug_screenshot] = str(dbg)
                self._emit("vision_debug", kind="click_needle", path=str(dbg), needle=str(needle), score=float(last.score), threshold=float(step.threshold))
            except Exception as de:
                self._emit("vision_debug", kind="click_needle", ok=False, error=str(de))
        raise TimeoutError(f"ClickNeedle timed out after {step.timeout_ms}ms (last score={score})")


    # --- Input ------------------------------------------------------------

    def _exec_key(self, step: StepKey, ctx: dict[str, Any]) -> None:
        keys = interpolate(step.keys, ctx)
        self._emit("input", kind="key", keys=keys, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        input_mod.key(keys, clearmodifiers=step.clearmodifiers)

    def _exec_keydown(self, step: StepKeyDown, ctx: dict[str, Any]) -> None:
        key_name = interpolate(step.key, ctx)
        self._emit("input", kind="keydown", key=key_name, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        input_mod.key_down(key_name, clearmodifiers=step.clearmodifiers)

    def _exec_keyup(self, step: StepKeyUp, ctx: dict[str, Any]) -> None:
        key_name = interpolate(step.key, ctx)
        self._emit("input", kind="keyup", key=key_name, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        input_mod.key_up(key_name, clearmodifiers=step.clearmodifiers)

    def _exec_reset_modifiers(self, step: StepResetModifiers, ctx: dict[str, Any]) -> None:
        self._emit("input", kind="reset_modifiers", dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        input_mod.reset_modifiers()

    def _exec_type(self, step: StepTypeText, ctx: dict[str, Any]) -> None:
        text = interpolate(step.text, ctx)
        effective_backend = self._choose_text_backend(step, text)
        effective_delay = self._profile_scale_delay_ms(step.delay_ms_per_char)
        self._emit(
            "input",
            kind="type",
            chars=len(text),
            backend=effective_backend,
            delay_ms_per_char=effective_delay,
            dry_run=bool(self.project.settings.dry_run),
        )
        if self.project.settings.dry_run:
            return

        if effective_backend == "clipboard":
            original: str | None = None
            original_known = False
            if step.preserve_clipboard:
                try:
                    original = clipboard_mod.read(selection=step.selection)
                    original_known = True
                except Exception:
                    original = None
                    original_known = False

            clipboard_mod.write(text, selection=step.selection)
            try:
                input_mod.paste(
                    selection=step.selection,
                    shortcut=step.paste_shortcut,
                    clearmodifiers=step.clearmodifiers,
                )
            finally:
                if step.preserve_clipboard and original_known:
                    try:
                        clipboard_mod.write(original or "", selection=step.selection)
                    except Exception as e:
                        self._emit(
                            "clipboard_restore_failed",
                            selection=step.selection,
                            error=str(e),
                        )
            ctx["last_type_backend"] = "clipboard"
            return

        used = input_mod.type_text(
            text,
            delay_ms_per_char=effective_delay,
            clearmodifiers=step.clearmodifiers,
            backend=("auto" if effective_backend == "auto" else effective_backend),
        )
        ctx["last_type_backend"] = used

    def _exec_mousemove(self, step: StepMouseMove, ctx: dict[str, Any]) -> None:
        self._emit("input", kind="mousemove", dry_run=bool(self.project.settings.dry_run), relative=step.relative)
        if self.project.settings.dry_run:
            return

        x = self._as_int(step.x, ctx, field="MouseMove.x") if step.x is not None else None
        y = self._as_int(step.y, ctx, field="MouseMove.y") if step.y is not None else None
        dx = self._as_int(step.dx, ctx, field="MouseMove.dx") if step.dx is not None else None
        dy = self._as_int(step.dy, ctx, field="MouseMove.dy") if step.dy is not None else None

        duration_ms = int(getattr(step, "duration_ms", 0) or 0)
        smooth_steps = int(getattr(step, "smooth_steps", 0) or 0)
        easing = str(getattr(step, "easing", "linear") or "linear").strip().lower()

        def _ease(t: float) -> float:
            if easing == "ease_in_out":
                # Cosine ease-in-out.
                return 0.5 - 0.5 * math.cos(math.pi * t)
            return t

        # Default behavior: a single move.
        if duration_ms <= 0 and smooth_steps <= 1:
            if not step.relative and x is not None and y is not None:
                x, y = self._translate_xy(int(x), int(y), target="mouse")
            input_mod.mouse_move(x=x, y=y, dx=dx, dy=dy, relative=step.relative)
            return

        # Smooth relative movement: split dx/dy across steps.
        if step.relative:
            if dx is None or dy is None:
                # Preserve legacy validation behavior.
                input_mod.mouse_move(x=x, y=y, dx=dx, dy=dy, relative=True)
                return
            steps = smooth_steps if smooth_steps > 0 else max(1, int(round(duration_ms / 16.0)))
            steps = max(1, min(steps, 240))
            if steps <= 1:
                input_mod.mouse_move(dx=dx, dy=dy, relative=True)
                return
            sleep_s = (float(duration_ms) / float(steps) / 1000.0) if duration_ms > 0 else 0.0

            # Use cumulative rounding so the sum of increments matches exactly.
            for i in range(steps):
                a0 = _ease(i / steps)
                a1 = _ease((i + 1) / steps)
                ix0 = int(round(dx * a0))
                iy0 = int(round(dy * a0))
                ix1 = int(round(dx * a1))
                iy1 = int(round(dy * a1))
                input_mod.mouse_move(dx=ix1 - ix0, dy=iy1 - iy0, relative=True)
                if sleep_s > 0 and i != steps - 1:
                    time.sleep(sleep_s)
            return

        # Smooth absolute movement: interpolate from current cursor position.
        if x is None or y is None:
            # Preserve legacy validation behavior.
            input_mod.mouse_move(x=x, y=y, dx=dx, dy=dy, relative=False)
            return

        x, y = self._translate_xy(int(x), int(y), target="mouse")

        try:
            start = cursor_pos_mod.get_cursor_pos()
            sx, sy = int(start.x), int(start.y)
        except Exception:
            # If we can't read the cursor, fall back to a direct move instead of failing the macro.
            input_mod.mouse_move(x=x, y=y, relative=False)
            return

        steps = smooth_steps if smooth_steps > 0 else max(1, int(round(duration_ms / 16.0)))
        steps = max(1, min(steps, 240))
        if steps <= 1:
            input_mod.mouse_move(x=x, y=y, relative=False)
            return

        sleep_s = (float(duration_ms) / float(steps) / 1000.0) if duration_ms > 0 else 0.0
        for i in range(1, steps + 1):
            t = _ease(i / steps)
            xi = int(round(sx + (x - sx) * t))
            yi = int(round(sy + (y - sy) * t))
            input_mod.mouse_move(x=xi, y=yi, relative=False)
            if sleep_s > 0 and i != steps:
                time.sleep(sleep_s)


    def _exec_mouseclick(self, step: StepMouseClick, ctx: dict[str, Any]) -> None:
        button = self._as_int(step.button, ctx, field='MouseClick.button')
        self._emit(
            "input",
            kind="mouseclick",
            button=button,
            down=step.down,
            up=step.up,
            dry_run=bool(self.project.settings.dry_run),
        )
        if self.project.settings.dry_run:
            return
        input_mod.mouse_click(button, clearmodifiers=step.clearmodifiers)

    def _exec_mouseclickat(self, step: StepMouseClickAt, ctx: dict[str, Any]) -> None:
        x = self._as_int(step.x, ctx, field='MouseClickAt.x')
        y = self._as_int(step.y, ctx, field='MouseClickAt.y')
        button = self._as_int(step.button, ctx, field='MouseClickAt.button')
        clicks = self._as_int(step.clicks, ctx, field='MouseClickAt.clicks')

        x, y = self._translate_xy(int(x), int(y), target="mouse")
        clicks = max(1, int(clicks))
        delay_between_clicks_ms = max(0, int(getattr(step, "delay_between_clicks_ms", 0) or 0))

        self._emit(
            "input",
            kind="mouseclickat",
            x=x,
            y=y,
            button=button,
            clicks=clicks,
            delay_between_clicks_ms=delay_between_clicks_ms,
            dry_run=bool(self.project.settings.dry_run),
        )
        if self.project.settings.dry_run:
            return

        input_mod.mouse_move(x=x, y=y)
        for idx in range(clicks):
            input_mod.mouse_click(button, clearmodifiers=step.clearmodifiers)
            if idx < clicks - 1 and delay_between_clicks_ms:
                time.sleep(delay_between_clicks_ms / 1000.0)

    def _exec_mousedrag(self, step: StepMouseDrag, ctx: dict[str, Any]) -> None:
        x1 = self._as_int(step.x1, ctx, field="MouseDrag.x1")
        y1 = self._as_int(step.y1, ctx, field="MouseDrag.y1")
        x2 = self._as_int(step.x2, ctx, field="MouseDrag.x2")
        y2 = self._as_int(step.y2, ctx, field="MouseDrag.y2")
        button = self._as_int(step.button, ctx, field="MouseDrag.button")

        x1, y1 = self._translate_xy(int(x1), int(y1), target="mouse")
        x2, y2 = self._translate_xy(int(x2), int(y2), target="mouse")

        duration_ms = int(getattr(step, "duration_ms", 0) or 0)
        smooth_steps = int(getattr(step, "smooth_steps", 0) or 0)
        easing = str(getattr(step, "easing", "linear") or "linear").strip().lower()

        def _ease(t: float) -> float:
            if easing == "ease_in_out":
                return 0.5 - 0.5 * math.cos(math.pi * t)
            return t

        self._emit("input", kind="mousedrag", x1=x1, y1=y1, x2=x2, y2=y2, button=button, duration_ms=duration_ms, smooth_steps=smooth_steps, easing=easing, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return

        input_mod.mouse_move(x=x1, y=y1)
        input_mod.mouse_click(button, down=True, clearmodifiers=step.clearmodifiers)

        if duration_ms > 0 or smooth_steps > 1:
            steps = smooth_steps if smooth_steps > 0 else max(1, int(round(duration_ms / 16.0)))
            steps = max(1, min(steps, 240))
            sleep_s = (float(duration_ms) / float(steps) / 1000.0) if duration_ms > 0 and steps > 0 else 0.0
            if steps <= 1:
                input_mod.mouse_move(x=x2, y=y2)
            else:
                for i in range(1, steps + 1):
                    t = _ease(i / steps)
                    xi = int(round(x1 + (x2 - x1) * t))
                    yi = int(round(y1 + (y2 - y1) * t))
                    input_mod.mouse_move(x=xi, y=yi)
                    if sleep_s > 0 and i != steps:
                        time.sleep(sleep_s)
        else:
            input_mod.mouse_move(x=x2, y=y2)

        input_mod.mouse_click(button, up=True, clearmodifiers=step.clearmodifiers)


    def _exec_mousewheel(self, step: StepMouseWheel, ctx: dict[str, Any]) -> None:
        clicks = self._as_int(step.clicks, ctx, field='MouseWheel.clicks')
        self._emit("input", kind="mousewheel", clicks=clicks, axis=step.axis, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        input_mod.mouse_wheel(clicks, axis=step.axis)

    def _exec_cursor_hide(self, step: StepCursorHide, ctx: dict[str, Any]) -> None:
        self._emit("cursor", action="hide", dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        if self._cursor_handle is not None:
            cursor_mod.show_cursor(self._cursor_handle)
        self._cursor_handle = cursor_mod.hide_cursor()

    def _exec_cursor_show(self, step: StepCursorShow, ctx: dict[str, Any]) -> None:
        self._emit("cursor", action="show", dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        cursor_mod.show_cursor(self._cursor_handle)
        self._cursor_handle = None

    def _exec_get_cursor_pos(self, step: StepGetCursorPos, ctx: dict[str, Any]) -> None:
        self._emit("cursorpos", action="get", dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            # Preserve deterministic vars for later steps.
            ctx[step.out_x] = 0
            ctx[step.out_y] = 0
            ctx[step.out_backend] = "dry_run"
            return

        pos = cursor_pos_mod.get_cursor_pos()
        ctx[step.out_x] = int(pos.x)
        ctx[step.out_y] = int(pos.y)
        ctx[step.out_backend] = pos.backend

    def _exec_get_active_window(self, step: StepGetActiveWindow, ctx: dict[str, Any]) -> None:
        self._emit(
            "window",
            action="sample",
            include_geometry=bool(step.include_geometry),
            require_geometry=bool(step.require_geometry),
            dry_run=bool(self.project.settings.dry_run),
        )
        if self.project.settings.dry_run:
            snapshot = {"wm": "dry_run", "geometry": None if step.include_geometry else None}
            ctx[step.out_var] = snapshot
            ctx[step.out_wm] = "dry_run"
            if step.emit_convenience_vars:
                ctx[step.out_title] = None
                ctx[step.out_class] = None
                ctx[step.out_workspace] = None
                ctx[step.out_urgent] = None
                ctx[step.out_pid] = None
                ctx[step.out_process] = None
            return

        snapshot, wm = active_window_mod.get_active_window_snapshot(
            include_geometry=bool(step.include_geometry),
            require_geometry=bool(step.require_geometry),
        )
        ctx[step.out_var] = snapshot
        ctx[step.out_wm] = wm
        if step.emit_convenience_vars:
            ctx[step.out_title] = snapshot.get("title")
            ctx[step.out_class] = snapshot.get("class") or snapshot.get("app_id")
            ctx[step.out_workspace] = snapshot.get("workspace")
            ctx[step.out_urgent] = snapshot.get("urgent")
            ctx[step.out_pid] = snapshot.get("pid")
            ctx[step.out_process] = snapshot.get("process_name")
        self._emit(
            "window_sample",
            wm=wm,
            title=snapshot.get("title"),
            window_class=snapshot.get("class") or snapshot.get("app_id"),
            workspace=snapshot.get("workspace"),
            has_geometry=bool(snapshot.get("geometry")),
        )

    def _exec_get_window_at_cursor(self, step: StepGetWindowAtCursor, ctx: dict[str, Any]) -> None:
        self._emit(
            "window",
            action="pointer_sample",
            include_geometry=bool(step.include_geometry),
            require_geometry=bool(step.require_geometry),
            require_window=bool(step.require_window),
            dry_run=bool(self.project.settings.dry_run),
        )
        if self.project.settings.dry_run:
            ctx[step.out_var] = None
            ctx[step.out_found] = False
            ctx[step.out_wm] = "dry_run"
            ctx[step.out_cursor_x] = 0
            ctx[step.out_cursor_y] = 0
            ctx[step.out_cursor_backend] = "dry_run"
            if step.emit_convenience_vars:
                ctx[step.out_title] = None
                ctx[step.out_class] = None
                ctx[step.out_workspace] = None
                ctx[step.out_focused] = None
                ctx[step.out_pid] = None
                ctx[step.out_process] = None
            return

        snapshot, wm, cursor = active_window_mod.get_window_at_cursor_snapshot(
            include_geometry=bool(step.include_geometry),
            require_geometry=bool(step.require_geometry),
            require_window=bool(step.require_window),
        )
        ctx[step.out_var] = snapshot
        ctx[step.out_found] = snapshot is not None
        ctx[step.out_wm] = wm
        ctx[step.out_cursor_x] = int(cursor.x)
        ctx[step.out_cursor_y] = int(cursor.y)
        ctx[step.out_cursor_backend] = cursor.backend
        if step.emit_convenience_vars:
            ctx[step.out_title] = None if snapshot is None else snapshot.get("title")
            ctx[step.out_class] = None if snapshot is None else snapshot.get("class") or snapshot.get("app_id")
            ctx[step.out_workspace] = None if snapshot is None else snapshot.get("workspace")
            ctx[step.out_focused] = None if snapshot is None else snapshot.get("focused")
            ctx[step.out_pid] = None if snapshot is None else snapshot.get("pid")
            ctx[step.out_process] = None if snapshot is None else snapshot.get("process_name")
        self._emit(
            "window_pointer_sample",
            wm=wm,
            found=snapshot is not None,
            cursor_x=int(cursor.x),
            cursor_y=int(cursor.y),
            cursor_backend=cursor.backend,
            title=None if snapshot is None else snapshot.get("title"),
            window_class=None if snapshot is None else snapshot.get("class") or snapshot.get("app_id"),
            workspace=None if snapshot is None else snapshot.get("workspace"),
            has_geometry=bool(snapshot and snapshot.get("geometry")),
        )

    def _exec_get_window_list(self, step: StepGetWindowList, ctx: dict[str, Any]) -> None:
        self._emit(
            "window",
            action="list",
            include_geometry=bool(step.include_geometry),
            focused_first=bool(step.focused_first),
            dry_run=bool(self.project.settings.dry_run),
        )
        if self.project.settings.dry_run:
            ctx[step.out_var] = []
            ctx[step.out_count] = 0
            ctx[step.out_wm] = "dry_run"
            return

        windows, wm = active_window_mod.get_window_list_snapshot(
            include_geometry=bool(step.include_geometry),
            selector=step.selector,
            focused_first=bool(step.focused_first),
        )
        ctx[step.out_var] = windows
        ctx[step.out_count] = len(windows)
        ctx[step.out_wm] = wm
        self._emit(
            "window_list",
            wm=wm,
            count=len(windows),
            focused=sum(1 for row in windows if row.get("focused")),
            has_geometry=bool(step.include_geometry),
        )

    def _exec_get_idle_ms(self, step: StepGetIdleMs, ctx: dict[str, Any]) -> None:
        self._emit("idle", action="sample", dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            ctx[step.out_ms] = 0
            ctx[step.out_backend] = "dry_run"
            ctx[step.out_source] = "dry_run"
            return

        sample = idle_mod.get_idle_ms()
        ctx[step.out_ms] = int(sample.ms)
        ctx[step.out_backend] = sample.backend
        ctx[step.out_source] = sample.source
        self._emit("idle_sample", idle_ms=sample.ms, backend=sample.backend, source=sample.source)

    def _set_systemd_unit_outputs(self, ctx: dict[str, Any], step: Any, sample: Any) -> None:
        payload = {
            "unit": sample.unit,
            "scope": sample.scope,
            "status": sample.status,
            "load_state": sample.load_state,
            "active_state": sample.active_state,
            "sub_state": sample.sub_state,
            "unit_file_state": sample.unit_file_state,
            "fragment_path": sample.fragment_path,
            "description": sample.description,
            "tool": sample.tool,
            "error": sample.error,
        }
        ctx[step.out_var] = payload
        ctx[step.out_status] = sample.status
        ctx[step.out_scope] = sample.scope
        ctx[step.out_active_state] = sample.active_state
        ctx[step.out_sub_state] = sample.sub_state
        ctx[step.out_load_state] = sample.load_state
        ctx[step.out_unit_file_state] = sample.unit_file_state
        ctx[step.out_fragment_path] = sample.fragment_path
        ctx[step.out_description] = sample.description

    def _exec_get_systemd_unit_state(self, step: StepGetSystemdUnitState, ctx: dict[str, Any]) -> None:
        unit = interpolate(step.unit, ctx)
        sample = systemd_units_mod.get_systemd_unit_state(unit, scope=step.scope, env=os.environ)
        self._set_systemd_unit_outputs(ctx, step, sample)
        self._emit(
            "systemd_unit_state",
            unit=unit,
            scope=sample.scope,
            status=sample.status,
            active_state=sample.active_state,
            sub_state=sample.sub_state,
            load_state=sample.load_state,
        )

    def _exec_wait_for_systemd_unit_state(self, step: StepWaitForSystemdUnitState, ctx: dict[str, Any]) -> None:
        unit = interpolate(step.unit, ctx)
        self._emit(
            "wait_start",
            kind="systemd_unit_state",
            unit=unit,
            scope=step.scope,
            status=step.status,
            load_state=step.load_state,
            active_state=step.active_state,
            sub_state=step.sub_state,
            unit_file_state=step.unit_file_state,
            timeout_ms=step.timeout_ms,
        )

        def on_attempt(attempt: int, sample, ok: bool):
            self._emit_wait_attempt(
                "systemd_unit_state",
                attempt=attempt,
                matched=ok,
                unit=unit,
                scope=sample.scope,
                status=sample.status,
                active_state=sample.active_state,
                sub_state=sample.sub_state,
                load_state=sample.load_state,
                unit_file_state=sample.unit_file_state,
            )

        sample = systemd_units_mod.wait_for_systemd_unit_state(
            unit,
            scope=step.scope,
            status=step.status,
            load_state=step.load_state,
            active_state=step.active_state,
            sub_state=step.sub_state,
            unit_file_state=step.unit_file_state,
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            env=os.environ,
            on_attempt=on_attempt,
        )
        self._set_systemd_unit_outputs(ctx, step, sample)
        self._emit(
            "wait_end",
            kind="systemd_unit_state",
            ok=True,
            unit=unit,
            scope=sample.scope,
            status=sample.status,
            active_state=sample.active_state,
            sub_state=sample.sub_state,
            load_state=sample.load_state,
            unit_file_state=sample.unit_file_state,
        )

    def _exec_wait_for_idle(self, step: StepWaitForIdle, ctx: dict[str, Any]) -> None:
        minimum_ms = self._as_int(step.minimum_ms, ctx, field="WaitForIdle.minimum_ms")
        self._emit(
            "wait_start",
            kind="idle",
            minimum_ms=minimum_ms,
            timeout_ms=step.timeout_ms,
        )

        def on_attempt(attempt: int, sample, ok: bool):
            self._emit_wait_attempt(
                "idle",
                attempt=attempt,
                minimum_ms=minimum_ms,
                idle_ms=sample.ms,
                backend=sample.backend,
                source=sample.source,
                matched=ok,
            )

        sample = idle_mod.wait_for_idle(
            minimum_ms,
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            on_attempt=on_attempt,
        )
        ctx[step.out_ms] = int(sample.ms)
        ctx[step.out_backend] = sample.backend
        ctx[step.out_source] = sample.source
        self._emit(
            "wait_end",
            kind="idle",
            ok=True,
            minimum_ms=minimum_ms,
            idle_ms=sample.ms,
            backend=sample.backend,
            source=sample.source,
        )

    def _exec_wait_for_user_activity(self, step: StepWaitForUserActivity, ctx: dict[str, Any]) -> None:
        maximum_ms = self._as_int(step.maximum_ms, ctx, field="WaitForUserActivity.maximum_ms")
        armed_after_ms = (
            None
            if step.armed_after_ms is None
            else self._as_int(step.armed_after_ms, ctx, field="WaitForUserActivity.armed_after_ms")
        )
        self._emit(
            "wait_start",
            kind="user_activity",
            maximum_ms=maximum_ms,
            armed_after_ms=armed_after_ms,
            timeout_ms=step.timeout_ms,
        )

        def on_attempt(attempt: int, sample, armed: bool, ok: bool):
            self._emit_wait_attempt(
                "user_activity",
                attempt=attempt,
                maximum_ms=maximum_ms,
                armed_after_ms=armed_after_ms,
                armed=armed,
                idle_ms=sample.ms,
                backend=sample.backend,
                source=sample.source,
                matched=ok,
            )

        sample = idle_mod.wait_for_user_activity(
            maximum_ms,
            armed_after_ms=armed_after_ms,
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            on_attempt=on_attempt,
        )
        ctx[step.out_ms] = int(sample.ms)
        ctx[step.out_backend] = sample.backend
        ctx[step.out_source] = sample.source
        self._emit(
            "wait_end",
            kind="user_activity",
            ok=True,
            maximum_ms=maximum_ms,
            armed_after_ms=armed_after_ms,
            idle_ms=sample.ms,
            backend=sample.backend,
            source=sample.source,
        )


    # --- Desktop helpers --------------------------------------------------

    def _exec_notify(self, step: StepNotify, ctx: dict[str, Any]) -> None:
        summary = interpolate(step.summary, ctx)
        body = interpolate(step.body, ctx) if step.body is not None else None
        app_name = interpolate(step.app_name, ctx) if step.app_name is not None else None
        icon = interpolate(step.icon, ctx) if step.icon is not None else None
        category = interpolate(step.category, ctx) if step.category is not None else None
        timeout_ms = self._as_int(step.timeout_ms, ctx, field="Notify.timeout_ms") if step.timeout_ms is not None else None
        replace_id = self._as_int(step.replace_id, ctx, field="Notify.replace_id") if step.replace_id is not None else None
        progress = self._as_int(step.progress, ctx, field="Notify.progress") if step.progress is not None else None
        transient = bool(self._render_value(step.transient, ctx))
        actions = [(interpolate(action.id, ctx), interpolate(action.label, ctx)) for action in getattr(step, "actions", [])]
        waits_for_feedback = bool(step.wait or step.out_action or actions)
        wants_id = bool(step.out_id)
        self._emit(
            "notify",
            summary=summary,
            urgency=step.urgency,
            app_name=app_name,
            category=category,
            timeout_ms=timeout_ms,
            replace_id=replace_id,
            transient=transient,
            progress=progress,
            action_count=len(actions),
            waits_for_feedback=waits_for_feedback,
            dry_run=bool(self.project.settings.dry_run),
        )
        if self.project.settings.dry_run:
            if step.out_id:
                ctx[step.out_id] = replace_id if replace_id is not None else 0
                ctx["last_notification_id"] = ctx[step.out_id]
            if step.out_action:
                ctx[step.out_action] = None
                ctx["last_notification_action"] = None
            return
        result = notify_mod.send(
            summary,
            body=body,
            urgency=step.urgency,
            app_name=app_name,
            icon=icon,
            category=category,
            timeout_ms=timeout_ms,
            replace_id=replace_id,
            transient=transient,
            progress=progress,
            actions=actions,
            wait=waits_for_feedback,
            print_id=wants_id,
        )
        if step.out_id:
            ctx[step.out_id] = result.notification_id
            ctx["last_notification_id"] = result.notification_id
        if step.out_action:
            ctx[step.out_action] = result.action_id
            ctx["last_notification_action"] = result.action_id

    def _exec_clipboard_read(self, step: StepClipboardRead, ctx: dict[str, Any]) -> None:
        txt = clipboard_mod.read(selection=step.selection)
        ctx[step.out_var] = txt
        self._emit("clipboard_read", selection=step.selection, chars=len(txt))

    def _exec_clipboard_set(self, step: StepClipboardSet, ctx: dict[str, Any]) -> None:
        txt = interpolate(step.text, ctx)
        self._emit("clipboard_set", selection=step.selection, chars=len(txt), dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        clipboard_mod.write(txt, selection=step.selection)

    def _compile_clipboard_pattern(self, pattern: str | None, flags: list[str]) -> re.Pattern[str] | None:
        if not pattern:
            return None
        flag_map = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
        }
        re_flags = 0
        for name in flags:
            re_flags |= flag_map.get(str(name), 0)
        return re.compile(pattern, re_flags)

    def _clipboard_wait_probe(
        self,
        *,
        step: StepWaitForClipboardChange | StepWaitForClipboardEvent,
        ctx: dict[str, Any],
        text: str,
        changed: bool,
        event_seen: bool,
        match: re.Match[str] | None,
    ) -> dict[str, Any]:
        probe = dict(ctx)
        probe.update(
            {
                step.out_text: text,
                step.out_changed: bool(changed),
                "clipboard_text": text,
                "clipboard_changed": bool(changed),
                "clipboard_selection": step.selection,
            }
        )
        if isinstance(step, StepWaitForClipboardEvent):
            probe.update({step.out_event: bool(event_seen), "clipboard_event": bool(event_seen)})
        if match is not None:
            groups = list(match.groups())
            probe.update(
                {
                    step.out_match: match.group(0),
                    step.out_groups: groups,
                    step.out_match_groups: {str(i): g for i, g in enumerate(match.groups())},
                    step.out_groupdict: match.groupdict(),
                    "clipboard_match": match.group(0),
                    "clipboard_groups": groups,
                    "clipboard_match_groups": {str(i): g for i, g in enumerate(match.groups())},
                    "clipboard_groupdict": match.groupdict(),
                }
            )
        return probe

    def _wait_for_clipboard_filtered(
        self,
        *,
        step: StepWaitForClipboardChange | StepWaitForClipboardEvent,
        ctx: dict[str, Any],
        wait_kind: str,
        event_mode: bool,
    ) -> tuple[str, bool, re.Match[str] | None]:
        initial = interpolate(step.initial_text, ctx) if step.initial_text is not None else None
        pat = self._compile_clipboard_pattern(step.pattern, list(step.flags))
        attempt_counter = 0
        deadline = time.time() + (step.timeout_ms / 1000.0)
        baseline = initial

        self._emit(
            "wait_start",
            kind=wait_kind,
            selection=step.selection,
            timeout_ms=step.timeout_ms,
            pattern=step.pattern,
            condition=step.condition,
        )

        def on_attempt(_attempt: int, cur: str, changed: bool, helper: str | None = None):
            nonlocal attempt_counter
            attempt_counter += 1
            self._emit_wait_attempt(
                wait_kind,
                attempt=attempt_counter,
                selection=step.selection,
                changed=changed,
                chars=len(cur),
                preview=cur[:120],
                helper=helper,
            )

        while True:
            remaining_ms = max(1, int((deadline - time.time()) * 1000.0))
            if remaining_ms <= 0:
                break

            if event_mode:
                txt, changed = watch_mod.wait_for_clipboard_event(
                    clipboard_mod.read,
                    selection=step.selection,
                    initial_text=baseline,
                    timeout_ms=remaining_ms,
                    poll_ms=step.poll_ms,
                    max_poll_ms=step.max_poll_ms,
                    jitter_ms=step.jitter_ms,
                    max_attempts=step.max_attempts,
                    on_attempt=on_attempt,
                )
                event_seen = True
            else:
                txt = watch_mod.wait_for_clipboard_change(
                    clipboard_mod.read,
                    selection=step.selection,
                    initial_text=baseline,
                    timeout_ms=remaining_ms,
                    poll_ms=step.poll_ms,
                    max_poll_ms=step.max_poll_ms,
                    jitter_ms=step.jitter_ms,
                    max_attempts=step.max_attempts,
                    on_attempt=on_attempt,
                )
                changed = True
                event_seen = True

            baseline = txt
            match = pat.search(txt) if pat is not None else None
            if pat is not None and match is None:
                continue
            if step.condition:
                probe = self._clipboard_wait_probe(
                    step=step,
                    ctx=ctx,
                    text=txt,
                    changed=bool(changed),
                    event_seen=event_seen,
                    match=match,
                )
                rendered = interpolate(step.condition, probe)
                if not bool(eval_expr(rendered, probe)):
                    continue
            return txt, bool(changed), match

        raise TimeoutError(
            f"{type(step).__name__} timed out after {step.timeout_ms}ms "
            f"(pattern={step.pattern!r}, condition={step.condition!r})"
        )

    def _apply_clipboard_wait_outputs(
        self,
        *,
        step: StepWaitForClipboardChange | StepWaitForClipboardEvent,
        ctx: dict[str, Any],
        text: str,
        changed: bool,
        event_seen: bool,
        match: re.Match[str] | None,
    ) -> None:
        ctx[step.out_text] = text
        ctx[step.out_changed] = bool(changed)
        if isinstance(step, StepWaitForClipboardEvent):
            ctx[step.out_event] = bool(event_seen)
        if match is not None:
            groups = list(match.groups())
            ctx[step.out_match] = match.group(0)
            ctx[step.out_groups] = groups
            ctx[step.out_match_groups] = {str(i): g for i, g in enumerate(match.groups())}
            ctx[step.out_groupdict] = match.groupdict()
        elif step.pattern:
            ctx[step.out_match] = None
            ctx[step.out_groups] = []
            ctx[step.out_match_groups] = {}
            ctx[step.out_groupdict] = {}

    def _exec_wait_for_clipboard_change(self, step: StepWaitForClipboardChange, ctx: dict[str, Any]) -> None:
        txt, changed, match = self._wait_for_clipboard_filtered(
            step=step,
            ctx=ctx,
            wait_kind="clipboard",
            event_mode=False,
        )
        self._apply_clipboard_wait_outputs(
            step=step,
            ctx=ctx,
            text=txt,
            changed=changed,
            event_seen=True,
            match=match,
        )
        self._emit(
            "wait_end",
            kind="clipboard",
            ok=True,
            selection=step.selection,
            chars=len(txt),
            changed=bool(changed),
            matched=bool(match) if step.pattern else None,
        )

    def _exec_wait_for_clipboard_event(self, step: StepWaitForClipboardEvent, ctx: dict[str, Any]) -> None:
        txt, changed, match = self._wait_for_clipboard_filtered(
            step=step,
            ctx=ctx,
            wait_kind="clipboard_event",
            event_mode=True,
        )
        self._apply_clipboard_wait_outputs(
            step=step,
            ctx=ctx,
            text=txt,
            changed=changed,
            event_seen=True,
            match=match,
        )
        self._emit(
            "wait_end",
            kind="clipboard_event",
            ok=True,
            selection=step.selection,
            chars=len(txt),
            changed=bool(changed),
            matched=bool(match) if step.pattern else None,
        )

    def _exec_paste_clipboard(self, step: StepPasteClipboard, ctx: dict[str, Any]) -> None:
        self._emit("clipboard_paste", selection=step.selection, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        input_mod.paste(selection=step.selection, clearmodifiers=step.clearmodifiers)

    def _exec_open_url(self, step: StepOpenUrl, ctx: dict[str, Any]) -> None:
        url = interpolate(step.url, ctx)
        ctx["last_open_url"] = url
        self._emit("open_url", url=url, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        openers_mod.open_target(url)

    def _exec_compose_email(self, step: StepComposeEmail, ctx: dict[str, Any]) -> None:
        def _render_listish(v: Any):
            if v is None:
                return None
            if isinstance(v, list):
                return [interpolate(str(x), ctx) for x in v]
            return interpolate(str(v), ctx)

        to = _render_listish(step.to)
        cc = _render_listish(step.cc)
        bcc = _render_listish(step.bcc)
        subject = interpolate(step.subject, ctx) if step.subject is not None else None
        body = interpolate(step.body, ctx) if step.body is not None else None
        attachments = _render_listish(step.attachments)
        ctx["last_email"] = {"to": to, "cc": cc, "bcc": bcc, "subject": subject, "body": body, "attachments": attachments}
        self._emit("compose_email", to=to, cc=cc, bcc=bcc, subject=subject, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        openers_mod.compose_email(to, cc=cc, bcc=bcc, subject=subject, body=body, attachments=attachments, utf8=step.utf8)

    def _exec_http_request(self, step: StepHttpRequest, ctx: dict[str, Any]) -> None:
        url = interpolate(step.url, ctx)
        headers = {str(k): interpolate(str(v), ctx) for k, v in step.headers.items()}
        params = {str(k): self._render_value(v, ctx) for k, v in step.params.items()}
        body = interpolate(step.body, ctx) if step.body is not None else None
        json_body = eval_expr(interpolate(step.json_expr, ctx), ctx) if step.json_expr else None
        if self.project.settings.dry_run:
            ctx[step.out_status] = 0
            ctx[step.out_reason] = "DRY_RUN"
            ctx[step.out_headers] = {}
            ctx[step.out_text] = ""
            ctx[step.out_url] = url
            if step.out_json:
                ctx[step.out_json] = None
            self._emit("http_request", method=step.method.upper(), url=url, dry_run=True)
            return
        resp = network_mod.http_request(
            step.method,
            url,
            headers=headers,
            params=params,
            body=body,
            json_body=json_body,
            timeout_ms=step.timeout_ms,
            allow_error_status=step.allow_error_status,
        )
        ctx[step.out_status] = int(resp.status)
        ctx[step.out_reason] = str(resp.reason)
        ctx[step.out_headers] = dict(resp.headers)
        ctx[step.out_text] = resp.text
        ctx[step.out_url] = resp.url
        if step.out_json:
            try:
                ctx[step.out_json] = resp.json()
            except Exception as e:
                raise RuntimeError(f"HttpRequest response was not valid JSON: {e}")
        ctx["last_http"] = {"status": resp.status, "reason": resp.reason, "url": resp.url, "headers": dict(resp.headers)}
        self._emit("http_request", method=step.method.upper(), url=resp.url, status=resp.status, reason=resp.reason, bytes=len(resp.body))


    def _exec_wait_for_http(self, step: StepWaitForHttp, ctx: dict[str, Any]) -> None:
        url = interpolate(step.url, ctx)
        headers = {str(k): interpolate(str(v), ctx) for k, v in step.headers.items()}
        params = {str(k): self._render_value(v, ctx) for k, v in step.params.items()}
        body = interpolate(step.body, ctx) if step.body is not None else None
        json_body = eval_expr(interpolate(step.json_expr, ctx), ctx) if step.json_expr else None
        cond_expr = interpolate(step.condition, ctx) if step.condition else None
        need_json = bool(step.out_json) or (cond_expr is not None and "http_json" in cond_expr)

        self._emit(
            "wait_start",
            kind="http",
            method=step.method.upper(),
            url=url,
            timeout_ms=step.timeout_ms,
        )

        if self.project.settings.dry_run:
            ctx[step.out_status] = 0
            ctx[step.out_reason] = "DRY_RUN"
            ctx[step.out_headers] = {}
            ctx[step.out_text] = ""
            ctx[step.out_url] = url
            if step.out_json:
                ctx[step.out_json] = None
            ctx[step.out_attempts] = 0
            ctx[step.out_elapsed_ms] = 0
            self._emit("wait_end", kind="http", ok=True, method=step.method.upper(), url=url, status=0, attempts=0, elapsed_ms=0, dry_run=True)
            return

        started = time.time()

        def check(resp) -> bool:
            if cond_expr is None:
                return True
            tmp = dict(ctx)
            tmp["http_status"] = int(resp.status)
            tmp["http_reason"] = str(resp.reason)
            tmp["http_headers"] = dict(resp.headers)
            tmp["http_text"] = resp.text
            tmp["http_url"] = resp.url
            if need_json:
                try:
                    tmp["http_json"] = resp.json()
                except Exception:
                    tmp["http_json"] = None
            return bool(eval_expr(cond_expr, tmp))

        def on_attempt(attempt: int, resp, ok: bool, err: str | None):
            status = int(resp.status) if resp is not None else None
            preview = resp.text[:160] if resp is not None else ""
            self._emit_wait_attempt(
                "http",
                attempt=attempt,
                url=url,
                status=status,
                ok=bool(ok),
                error=err,
                preview=preview,
            )

        resp, attempts = watch_mod.wait_for_http(
            network_mod.http_request,
            method=step.method,
            url=url,
            headers=headers,
            params=params,
            body=body,
            json_body=json_body,
            timeout_ms=step.timeout_ms,
            allow_error_status=step.allow_error_status,
            ok_statuses=step.ok_statuses,
            status_min=step.status_min,
            status_max=step.status_max,
            text_contains=interpolate(step.text_contains, ctx) if step.text_contains is not None else None,
            text_regex=interpolate(step.text_regex, ctx) if step.text_regex is not None else None,
            check_func=check if cond_expr else None,
            respect_retry_after=bool(step.respect_retry_after),
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            on_attempt=on_attempt,
        )

        elapsed_ms = int((time.time() - started) * 1000)
        ctx[step.out_status] = int(resp.status)
        ctx[step.out_reason] = str(resp.reason)
        ctx[step.out_headers] = dict(resp.headers)
        ctx[step.out_text] = resp.text
        ctx[step.out_url] = resp.url
        if step.out_json:
            try:
                ctx[step.out_json] = resp.json()
            except Exception as e:
                raise RuntimeError(f"WaitForHttp response was not valid JSON: {e}")
        ctx[step.out_attempts] = int(attempts)
        ctx[step.out_elapsed_ms] = elapsed_ms
        ctx["last_http"] = {"status": resp.status, "reason": resp.reason, "url": resp.url, "headers": dict(resp.headers)}
        self._emit("wait_end", kind="http", ok=True, method=step.method.upper(), url=resp.url, status=resp.status, attempts=attempts, elapsed_ms=elapsed_ms)

    def _exec_download_file(self, step: StepDownloadFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        url = interpolate(step.url, ctx)
        path = (root / interpolate(step.path, ctx)).resolve()
        headers = {str(k): interpolate(str(v), ctx) for k, v in step.headers.items()}
        ctx[step.out_path] = str(path)
        if self.project.settings.dry_run:
            ctx[step.out_bytes] = 0
            self._emit("download_file", url=url, path=str(path), dry_run=True)
            return
        sha256 = interpolate(step.sha256, ctx) if getattr(step, 'sha256', None) else None
        saved = network_mod.download_file(
            url,
            path,
            headers=headers,
            timeout_ms=step.timeout_ms,
            create_parents=step.create_parents,
            overwrite=step.overwrite,
            atomic=getattr(step, 'atomic', True),
            tmp_suffix=getattr(step, 'tmp_suffix', '.part'),
            sha256=sha256,
        )
        ctx[step.out_path] = str(saved)
        ctx[step.out_bytes] = saved.stat().st_size
        self._emit("download_file", url=url, path=str(saved), bytes=saved.stat().st_size)

    def _eval_value_expr(self, expr: str, ctx: dict[str, Any]) -> Any:
        rendered = interpolate(expr, ctx)
        return eval_expr(rendered, ctx)

    def _exec_show_message(self, step: StepShowMessage, ctx: dict[str, Any]) -> None:
        text = interpolate(step.text, ctx)
        title = interpolate(step.title, ctx) if step.title is not None else None
        if self.project.settings.dry_run:
            self._emit("show_message", level=step.level, title=title, text=text, dry_run=True)
            return
        dialogs_mod.show_message(text, title=title, level=step.level)
        self._emit("show_message", level=step.level, title=title, text=text)

    def _exec_ask_yes_no(self, step: StepAskYesNo, ctx: dict[str, Any]) -> None:
        text = interpolate(step.text, ctx)
        title = interpolate(step.title, ctx) if step.title is not None else None
        if self.project.settings.dry_run:
            answer = bool(step.default_yes)
            ctx[step.out_var] = answer
            self._emit("ask_yes_no", title=title, text=text, answer=answer, dry_run=True)
            return
        answer = dialogs_mod.ask_yes_no(text, title=title, default_yes=step.default_yes)
        ctx[step.out_var] = answer
        self._emit("ask_yes_no", title=title, text=text, answer=answer)

    def _exec_input_box(self, step: StepInputBox, ctx: dict[str, Any]) -> None:
        prompt = interpolate(step.prompt, ctx)
        title = interpolate(step.title, ctx) if step.title is not None else None
        default = interpolate(step.default, ctx) if step.default is not None else None
        if self.project.settings.dry_run:
            value = default
            ctx[step.out_var] = value
            self._emit("input_box", title=title, prompt=prompt, value=value, password=step.password, dry_run=True)
            return
        value = dialogs_mod.input_text(prompt, title=title, default=default, password=step.password)
        ctx[step.out_var] = value
        self._emit("input_box", title=title, prompt=prompt, value=value, password=step.password)

    def _exec_prompt_form(self, step: StepPromptForm, ctx: dict[str, Any]) -> None:
        title = interpolate(step.title, ctx) if step.title is not None else None
        text = interpolate(step.text, ctx) if step.text is not None else None
        profile_key = interpolate(step.profile_key, ctx) if step.profile_key is not None else None
        if not profile_key:
            macro_name = str(ctx.get("macro", {}).get("name", "macro"))
            profile_key = f"macro:{macro_name}:prompt:{step.out_var}"
        saved_values: dict[str, Any] = {}
        if self._prompt_profile:
            saved_values = self._prompt_store.load_profile(profile_key, self._prompt_profile)
        else:
            saved_values = self._prompt_store.load_last(profile_key)
        fields: list[dialogs_mod.FormField] = []
        for field in step.fields:
            default = self._render_value(field.default, ctx)
            choices: list[str] = [str(x) for x in self._render_value(field.choices, ctx)]
            if field.choices_expr is not None:
                resolved = self._eval_or_render(field.choices_expr, ctx)
                if not isinstance(resolved, (list, tuple)):
                    raise ValueError(
                        f"PromptForm field '{field.name}' choices_expr must resolve to a list/tuple, got {type(resolved).__name__}"
                    )
                choices = [str(x) for x in resolved]
            fields.append(
                dialogs_mod.FormField(
                    name=field.name,
                    label=interpolate(field.label, ctx) if field.label is not None else field.name,
                    kind=field.kind,
                    default=default,
                    choices=choices,
                    remember=bool(getattr(field, "remember", True)),
                )
            )
        fields = apply_saved_answers(fields, saved_values)
        if self.project.settings.dry_run:
            values: dict[str, Any] = {}
            for f in fields:
                value = f.default
                if value is None and f.kind == "choice" and f.choices:
                    value = f.choices[0]
                values[f.name] = value
            ctx[step.out_var] = values
            self._emit("prompt_form", title=title, text=text, values=values, count=len(fields), dry_run=True, profile_key=profile_key)
            return
        values = dialogs_mod.prompt_form(fields, title=title, text=text)
        ctx[step.out_var] = values
        if values is not None:
            saved = sanitize_prompt_answers(fields, values)
            if saved:
                self._prompt_store.save_last(profile_key, saved)
                if self._save_prompt_profile:
                    self._prompt_store.save_profile(profile_key, self._save_prompt_profile, saved)
        self._emit("prompt_form", title=title, text=text, values=values, count=len(fields), profile_key=profile_key)

    def _exec_choose_from_list(self, step: StepChooseFromList, ctx: dict[str, Any]) -> None:
        items = self._eval_or_render(step.items_expr, ctx)
        if not isinstance(items, (list, tuple)):
            raise ValueError(f"ChooseFromList.items_expr must resolve to a list/tuple, got {type(items).__name__}")
        values = [str(x) for x in items]
        title = interpolate(step.title, ctx) if step.title is not None else None
        text = interpolate(step.text, ctx) if step.text is not None else None
        if self.project.settings.dry_run:
            selection = values[:1] if step.multiple else (values[0] if values else None)
            ctx[step.out_var] = selection
            self._emit("choose_from_list", title=title, text=text, selection=selection, count=len(values), dry_run=True)
            return
        selection = dialogs_mod.choose_from_list(values, title=title, text=text, multiple=step.multiple)
        ctx[step.out_var] = selection
        self._emit("choose_from_list", title=title, text=text, selection=selection, count=len(values))

    def _exec_start_process(self, step: StepStartProcess, ctx: dict[str, Any]) -> None:
        cmd_value = self._render_value(step.command, ctx)
        cwd = interpolate(step.cwd, ctx) if step.cwd is not None else None
        env = self._render_value(step.env, ctx)
        if self.project.settings.dry_run:
            ctx[step.out_pid] = 0
            self._emit("start_process", command=cmd_value, shell=step.shell, cwd=cwd, pid=0, dry_run=True)
            return
        started = processes_mod.start_process(cmd_value, shell=step.shell, cwd=(Path(self.project.root_dir) / cwd if cwd and not Path(cwd).is_absolute() else cwd), env=env)
        self._processes[int(started.pid)] = started.popen
        ctx[step.out_pid] = int(started.pid)
        self._emit("start_process", command=cmd_value, shell=step.shell, cwd=started.cwd, pid=int(started.pid))

    def _exec_wait_for_process_exit(self, step: StepWaitForProcessExit, ctx: dict[str, Any]) -> None:
        pid = self._as_int(step.pid, ctx, field='WaitForProcessExit.pid')
        if self.project.settings.dry_run:
            ctx[step.out_returncode] = 0
            ctx[step.out_exited] = True
            self._emit("wait_process_exit", pid=pid, returncode=0, dry_run=True)
            return
        popen = self._processes.get(pid)
        rc = processes_mod.wait_for_process_exit(
            pid,
            popen=popen,
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            on_attempt=lambda attempt, exited, rc: self._emit_wait_attempt("process_exit", pid=pid, attempt=attempt, exited=bool(exited), returncode=rc),
        )
        ctx[step.out_returncode] = rc
        ctx[step.out_exited] = True
        self._emit("wait_process_exit", pid=pid, returncode=rc)

    def _exec_kill_process(self, step: StepKillProcess, ctx: dict[str, Any]) -> None:
        pid = self._as_int(step.pid, ctx, field='KillProcess.pid')
        sig = self._render_value(step.signal, ctx)
        if self.project.settings.dry_run:
            ctx[step.out_killed] = True
            self._emit("kill_process", pid=pid, signal=sig, killed=True, dry_run=True)
            return
        popen = self._processes.get(pid)
        killed = processes_mod.kill_process(pid, sig=sig, popen=popen, missing_ok=step.missing_ok, wait_ms=step.wait_ms)
        ctx[step.out_killed] = bool(killed)
        self._emit("kill_process", pid=pid, signal=sig, killed=bool(killed))

    def _exec_regex_replace(self, step: StepRegexReplace, ctx: dict[str, Any]) -> None:
        text = interpolate(step.text, ctx)
        pattern = interpolate(step.pattern, ctx)
        replacement = interpolate(step.replacement, ctx)
        out = text_mod.regex_replace(text, pattern, replacement, flags=list(step.flags), count=step.count)
        ctx[step.out_var] = out
        self._emit("text_regex_replace", pattern=pattern, out_var=step.out_var, chars=len(out), count=step.count)

    def _exec_trim_text(self, step: StepTrimText, ctx: dict[str, Any]) -> None:
        text = interpolate(step.text, ctx)
        chars = interpolate(step.chars, ctx) if step.chars is not None else None
        out = text_mod.trim_text(text, chars=chars, mode=step.mode)
        ctx[step.out_var] = out
        self._emit("text_trim", mode=step.mode, out_var=step.out_var, chars=len(out))

    def _exec_split_text(self, step: StepSplitText, ctx: dict[str, Any]) -> None:
        text = interpolate(step.text, ctx)
        sep = interpolate(step.sep, ctx) if step.sep is not None else None
        out = text_mod.split_text(text, sep=sep, maxsplit=int(step.maxsplit))
        ctx[step.out_var] = out
        self._emit("text_split", out_var=step.out_var, count=len(out), sep=sep)

    def _exec_join_text(self, step: StepJoinText, ctx: dict[str, Any]) -> None:
        items = self._eval_value_expr(step.items_expr, ctx)
        if not isinstance(items, (list, tuple)):
            raise ValueError(f"JoinText expects a list/tuple expression, got {type(items).__name__}")
        sep = interpolate(step.sep, ctx)
        out = text_mod.join_text(items, sep=sep)
        ctx[step.out_var] = out
        self._emit("text_join", out_var=step.out_var, count=len(items), chars=len(out), sep=sep)

    def _exec_foreach(self, step: StepForEach, ctx: dict[str, Any], macro_name: str, path_prefix: list[int]) -> None:
        items = self._eval_value_expr(step.items_expr, ctx)
        if isinstance(items, dict):
            iterator = list(items.items())
        elif isinstance(items, (list, tuple)):
            iterator = list(enumerate(items))
        else:
            raise ValueError(f"ForEach expects a list/tuple/dict expression, got {type(items).__name__}")

        self._emit("foreach_start", macro=macro_name, step_id=".".join(map(str, path_prefix)), count=len(iterator), items_expr=step.items_expr)
        completed = 0
        for idx, payload in enumerate(iterator):
            if isinstance(items, dict):
                key, value = payload
            else:
                key, value = payload
            child_ctx = ctx
            child_ctx[step.item_var] = value
            if step.index_var:
                child_ctx[step.index_var] = idx
            if step.key_var:
                child_ctx[step.key_var] = key
            self._emit("foreach_iter", macro=macro_name, step_id=".".join(map(str, path_prefix)), iter_index=idx, key=key if isinstance(items, dict) else None)
            try:
                self._run_steps(step.steps, child_ctx, macro_name=macro_name, path_prefix=path_prefix + [idx])
            except _ContinueSignal:
                completed += 1
                continue
            except _BreakSignal:
                completed += 1
                break
            completed += 1

        self._emit("foreach_end", macro=macro_name, step_id=".".join(map(str, path_prefix)), count=completed, items_expr=step.items_expr)

    def _exec_read_csv(self, step: StepReadCsv, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        rows = files_mod.read_csv(path, encoding=step.encoding, delimiter=step.delimiter, has_header=step.has_header)
        ctx[step.out_var] = rows
        ctx[step.out_row_count] = len(rows)
        self._emit("csv_read", path=str(path), rows=len(rows), has_header=step.has_header, delimiter=step.delimiter)

    def _exec_write_csv(self, step: StepWriteCsv, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        rows = self._eval_value_expr(step.rows_expr, ctx)
        if not isinstance(rows, list):
            raise ValueError(f"WriteCsv expects rows_expr to evaluate to a list, got {type(rows).__name__}")
        self._emit("csv_write", path=str(path), rows=len(rows), append=step.append, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        files_mod.write_csv(path, rows, encoding=step.encoding, delimiter=step.delimiter, create_parents=step.create_parents, append=step.append, include_header=step.include_header, fieldnames=step.fieldnames)

    def _exec_read_json(self, step: StepReadJson, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        value = files_mod.read_json(path, encoding=step.encoding)
        ctx[step.out_var] = value
        self._emit("json_read", path=str(path), value_type=type(value).__name__)

    def _exec_write_json(self, step: StepWriteJson, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        value = self._eval_value_expr(step.value_expr, ctx)
        self._emit("json_write", path=str(path), value_type=type(value).__name__, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        files_mod.write_json(path, value, encoding=step.encoding, indent=int(step.indent), create_parents=step.create_parents)

    def _exec_read_file(self, step: StepReadFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        txt = files_mod.read_text(path, encoding=step.encoding)
        ctx[step.out_var] = txt
        self._emit("file_read", path=str(path), chars=len(txt), encoding=step.encoding)

    def _exec_write_file(self, step: StepWriteFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        txt = interpolate(step.text, ctx)
        self._emit("file_write", path=str(path), chars=len(txt), append=False, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        files_mod.write_text(path, txt, encoding=step.encoding, create_parents=step.create_parents, append=False)

    def _exec_append_file(self, step: StepAppendFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        txt = interpolate(step.text, ctx)
        self._emit("file_write", path=str(path), chars=len(txt), append=True, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        files_mod.write_text(path, txt, encoding=step.encoding, create_parents=step.create_parents, append=True)

    def _exec_list_directory(self, step: StepListDirectory, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        items = files_mod.list_directory(
            path,
            pattern=interpolate(step.pattern, ctx) if step.pattern is not None else None,
            recursive=step.recursive,
            files_only=step.files_only,
            dirs_only=step.dirs_only,
            sort=step.sort,
        )
        ctx[step.out_var] = items
        self._emit("file_list", path=str(path), count=len(items), recursive=step.recursive, pattern=step.pattern)

    def _exec_wait_for_file(self, step: StepWaitForFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        path = root / interpolate(step.path, ctx)
        self._emit(
            "wait_start",
            kind="file",
            path=str(path),
            condition=step.condition,
            timeout_ms=step.timeout_ms,
        )

        def on_attempt(attempt: int, st, ok: bool, helper: str | None = None):
            self._emit_wait_attempt(
                "file",
                attempt=attempt,
                path=str(path),
                condition=step.condition,
                exists=st.exists,
                mtime_ns=st.mtime_ns,
                size=st.size,
                matched=ok,
                helper=helper,
            )

        st = watch_mod.wait_for_file(
            path,
            condition=step.condition,
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            on_attempt=on_attempt,
        )
        ctx[step.out_path] = str(path)
        ctx[step.out_exists] = st.exists
        ctx[step.out_mtime_ns] = st.mtime_ns
        ctx[step.out_size] = st.size
        self._emit(
            "wait_end",
            kind="file",
            ok=True,
            path=str(path),
            condition=step.condition,
            exists=st.exists,
            mtime_ns=st.mtime_ns,
            size=st.size,
        )

    def _exec_wait_for_file_event(self, step: StepWaitForFileEvent, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        directory = root / interpolate(step.directory, ctx)
        pattern = interpolate(step.pattern, ctx)
        exclude = step.exclude
        if isinstance(exclude, str):
            exclude_list = [interpolate(exclude, ctx)]
        elif isinstance(exclude, list):
            exclude_list = [interpolate(str(x), ctx) for x in exclude]
        else:
            exclude_list = None

        self._emit(
            "wait_start",
            kind="file_event",
            directory=str(directory),
            event=step.event,
            pattern=pattern,
            recursive=bool(step.recursive),
            exclude=exclude_list,
            min_size=int(step.min_size),
            stable_ms=int(step.stable_ms),
            quiet_ms=int(getattr(step, "quiet_ms", 0) or 0),
            timeout_ms=step.timeout_ms,
        )

        def on_attempt(attempt: int, ev, ok: bool, helper: str | None = None):
            self._emit_wait_attempt(
                "file_event",
                attempt=attempt,
                matched=ok,
                directory=str(directory),
                event=step.event,
                pattern=pattern,
                recursive=bool(step.recursive),
                helper=helper,
                path=(str(ev.path) if ev is not None else None),
                file_event=(ev.kind if ev is not None else None),
                exists=(ev.exists if ev is not None else None),
                size=(ev.size if ev is not None else None),
                mtime_ns=(ev.mtime_ns if ev is not None else None),
            )

        ev, _snap = watch_mod.wait_for_file_event(
            directory,
            event=step.event,
            pattern=pattern,
            recursive=step.recursive,
            exclude=exclude_list,
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            min_size=int(step.min_size),
            stable_ms=int(step.stable_ms),
            quiet_ms=int(getattr(step, "quiet_ms", 0) or 0),
            on_attempt=on_attempt,
        )

        ctx[step.out_event] = ev.kind
        ctx[step.out_path] = str(ev.path)
        ctx[step.out_name] = ev.name
        ctx[step.out_dir] = ev.directory
        ctx[step.out_exists] = bool(ev.exists)
        ctx[step.out_mtime_ns] = ev.mtime_ns
        ctx[step.out_size] = ev.size
        ctx[step.out_helper] = ev.helper
        ctx[step.out_raw_event] = ev.raw_event
        ctx[step.out_batch_count] = int(getattr(ev, "batch_count", 1) or 1)
        ctx[step.out_batch_paths] = list(getattr(ev, "batch_paths", []) or [str(ev.path)])
        ctx[step.out_batch_names] = list(getattr(ev, "batch_names", []) or [ev.name])
        ctx[step.out_batch_kinds] = list(getattr(ev, "batch_kinds", []) or [ev.kind])

        self._emit(
            "wait_end",
            kind="file_event",
            ok=True,
            directory=str(directory),
            event=ev.kind,
            path=str(ev.path),
            name=ev.name,
            exists=bool(ev.exists),
            mtime_ns=ev.mtime_ns,
            size=ev.size,
            helper=ev.helper,
            raw_event=ev.raw_event,
            batch_count=int(getattr(ev, "batch_count", 1) or 1),
            batch_paths=list(getattr(ev, "batch_paths", []) or [str(ev.path)]),
            batch_names=list(getattr(ev, "batch_names", []) or [ev.name]),
            batch_kinds=list(getattr(ev, "batch_kinds", []) or [ev.kind]),
        )


    def _exec_wait_for_new_file(self, step: StepWaitForNewFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        directory = root / interpolate(step.directory, ctx)
        pattern = interpolate(step.pattern, ctx)
        exclude = step.exclude
        if isinstance(exclude, str):
            exclude_list = [interpolate(exclude, ctx)]
        elif isinstance(exclude, list):
            exclude_list = [interpolate(str(x), ctx) for x in exclude]
        else:
            exclude_list = None

        # By default we treat modified pre-existing paths as candidates (useful for
        # overwrite-style producers). Users can disable this or override the
        # timestamp to reduce false positives in noisy directories.
        since_ns: int | None
        if not bool(step.include_existing_changes):
            since_ns = None
        elif "since_ns" in getattr(step, "model_fields_set", set()):
            if step.since_ns is None:
                since_ns = None
            else:
                since_ns = self._as_int(step.since_ns, ctx, field="WaitForNewFile.since_ns")
        else:
            since_ns = int(ctx.get("_run_started_ns") or 0) or None

        self._emit(
            "wait_start",
            kind="new_file",
            directory=str(directory),
            pattern=pattern,
            recursive=bool(step.recursive),
            exclude=exclude_list,
            include_existing_changes=bool(step.include_existing_changes),
            since_ns=since_ns,
            min_size=int(step.min_size),
            stable_ms=int(step.stable_ms),
            timeout_ms=step.timeout_ms,
        )

        def on_attempt(attempt: int, found: Path | None, ok: bool, helper: str | None = None):
            self._emit_wait_attempt(
                "new_file",
                attempt=attempt,
                directory=str(directory),
                pattern=pattern,
                found=(str(found) if found else None),
                matched=ok,
                helper=helper,
            )

        found = watch_mod.wait_for_new_file(
            directory,
            pattern=pattern,
            recursive=bool(step.recursive),
            exclude=exclude_list,
            min_size=int(step.min_size),
            stable_ms=int(step.stable_ms),
            timeout_ms=step.timeout_ms,
            since_ns=since_ns,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            on_attempt=on_attempt,
        )
        st = found.stat()
        ctx[step.out_path] = str(found)
        ctx[step.out_name] = found.name
        ctx[step.out_size] = st.st_size
        ctx[step.out_mtime_ns] = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
        self._emit(
            "wait_end",
            kind="new_file",
            ok=True,
            directory=str(directory),
            pattern=pattern,
            path=str(found),
            size=st.st_size,
        )

    def _exec_wait_for_download(self, step: StepWaitForDownload, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        directory = root / interpolate(step.directory, ctx)
        pattern = interpolate(step.pattern, ctx)

        exclude = step.exclude
        if isinstance(exclude, str):
            exclude_list = [interpolate(exclude, ctx)]
        elif isinstance(exclude, list):
            exclude_list = [interpolate(str(x), ctx) for x in exclude]
        else:
            exclude_list = None

        # Downloads default to *new paths only*, but users can opt into
        # overwrite-style producers.
        since_ns: int | None
        if not bool(step.include_existing_changes):
            since_ns = None
        elif "since_ns" in getattr(step, "model_fields_set", set()):
            if step.since_ns is None:
                since_ns = None
            else:
                since_ns = self._as_int(step.since_ns, ctx, field="WaitForDownload.since_ns")
        else:
            since_ns = int(ctx.get("_run_started_ns") or 0) or None

        self._emit(
            "wait_start",
            kind="download",
            directory=str(directory),
            pattern=pattern,
            recursive=bool(step.recursive),
            exclude=exclude_list,
            include_existing_changes=bool(step.include_existing_changes),
            since_ns=since_ns,
            min_size=int(step.min_size),
            stable_ms=int(step.stable_ms),
            timeout_ms=step.timeout_ms,
        )

        def on_attempt(attempt: int, found: Path | None, ok: bool, helper: str | None = None):
            self._emit_wait_attempt(
                "download",
                attempt=attempt,
                directory=str(directory),
                pattern=pattern,
                found=(str(found) if found else None),
                matched=ok,
                helper=helper,
            )

        found = watch_mod.wait_for_download(
            directory,
            pattern=pattern,
            recursive=bool(step.recursive),
            exclude=exclude_list,
            include_existing_changes=bool(step.include_existing_changes),
            since_ns=since_ns,
            min_size=int(step.min_size),
            stable_ms=int(step.stable_ms),
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            on_attempt=on_attempt,
        )
        st = found.stat()
        ctx[step.out_path] = str(found)
        ctx[step.out_name] = found.name
        ctx[step.out_size] = st.st_size
        ctx[step.out_mtime_ns] = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
        self._emit(
            "wait_end",
            kind="download",
            ok=True,
            directory=str(directory),
            pattern=pattern,
            path=str(found),
            size=st.st_size,
        )


    # --- i3 ---------------------------------------------------------------

    def _exec_i3_command(self, step: StepI3Command, ctx: dict[str, Any]) -> None:
        cmd = interpolate(step.command, ctx)
        i3 = I3Connection()
        res = i3.command(cmd)
        if step.out_var:
            ctx[step.out_var] = res
        self._emit("i3_command", command=cmd)

    def _exec_i3_get_tree(self, step: StepI3GetTree, ctx: dict[str, Any]) -> None:
        i3 = I3Connection()
        ctx[step.out_var] = i3.get_tree()
        self._emit("i3_get_tree", out_var=step.out_var)

    def _exec_wait_for_dbus_signal(self, step: StepWaitForDbusSignal, ctx: dict[str, Any]) -> None:
        flag_map = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
        }
        re_flags = 0
        for name in step.flags:
            re_flags |= flag_map.get(str(name), 0)
        pat = re.compile(step.pattern, re_flags) if step.pattern else None

        match_rule = dbus_bridge_mod.build_match_rule(
            sender=step.sender,
            path=step.path,
            interface=step.interface,
            member=step.member,
            raw_rule=step.match,
        )

        self._emit(
            "wait_start",
            kind="dbus_signal",
            bus=step.bus,
            sender=step.sender,
            path=step.path,
            interface=step.interface,
            member=step.member,
            match=step.match,
            pattern=step.pattern,
            condition=step.condition,
            timeout_ms=step.timeout_ms,
        )

        q: Queue[Any] = Queue()
        stop = object()

        def producer() -> None:
            try:
                for sig in dbus_bridge_mod.iter_dbus_signals(match_rule=match_rule, bus=step.bus):
                    q.put(sig)
            except Exception as exc:  # pragma: no cover - queue surface tested instead
                q.put({"__error__": str(exc)})
            finally:
                q.put(stop)

        Thread(target=producer, daemon=True).start()

        deadline = time.time() + (step.timeout_ms / 1000.0)
        attempt = 0
        producer_done = False
        producer_error: str | None = None

        while time.time() <= deadline:
            self._check_panic()
            remaining = max(0.0, deadline - time.time())
            timeout_s = min(0.25, remaining)
            if timeout_s <= 0:
                break
            try:
                item = q.get(timeout=timeout_s)
            except Empty:
                continue

            if item is stop:
                producer_done = True
                break
            if isinstance(item, dict) and "__error__" in item:
                producer_error = str(item.get("__error__") or "unknown D-Bus monitor error")
                self._emit_wait_attempt("dbus_signal", attempt=attempt + 1, matched=False, error=producer_error, bus=step.bus)
                producer_done = True
                break

            sig = item
            attempt += 1
            if not isinstance(sig, dbus_bridge_mod.DBusSignal):
                self._emit_wait_attempt("dbus_signal", attempt=attempt, matched=False, error=f"unexpected D-Bus payload: {type(sig).__name__}", bus=step.bus)
                continue

            matched = True
            if matched and step.path is not None and sig.path != step.path:
                matched = False
            if matched and step.interface is not None and sig.interface != step.interface:
                matched = False
            if matched and step.member is not None and sig.member != step.member:
                matched = False

            text_value = dbus_bridge_mod.signal_text(sig)
            payload = {
                "bus": step.bus,
                "sender": sig.sender,
                "path": sig.path,
                "interface": sig.interface,
                "member": sig.member,
                "args": sig.args,
                "raw": sig.raw,
                "text": text_value,
            }

            if matched and pat is not None:
                matched = pat.search(text_value) is not None
            if matched and step.condition:
                probe_ctx = dict(ctx)
                probe_ctx.update({
                    step.out_var: payload,
                    step.out_bus: step.bus,
                    step.out_args: sig.args,
                    step.out_sender: sig.sender,
                    step.out_path: sig.path,
                    step.out_interface: sig.interface,
                    step.out_member: sig.member,
                    step.out_text: text_value,
                    step.out_raw: sig.raw,
                    "dbus_signal": payload,
                    "dbus_bus": step.bus,
                    "dbus_args": sig.args,
                    "dbus_sender": sig.sender,
                    "dbus_path": sig.path,
                    "dbus_interface": sig.interface,
                    "dbus_member": sig.member,
                    "dbus_text": text_value,
                    "dbus_raw": sig.raw,
                })
                rendered = interpolate(step.condition, probe_ctx)
                matched = bool(eval_expr(rendered, probe_ctx))

            self._emit_wait_attempt(
                "dbus_signal",
                attempt=attempt,
                matched=matched,
                bus=step.bus,
                sender=sig.sender,
                path=sig.path,
                interface=sig.interface,
                member=sig.member,
            )

            if not matched:
                continue

            ctx[step.out_var] = payload
            ctx[step.out_bus] = step.bus
            ctx[step.out_args] = sig.args
            ctx[step.out_sender] = sig.sender
            ctx[step.out_path] = sig.path
            ctx[step.out_interface] = sig.interface
            ctx[step.out_member] = sig.member
            ctx[step.out_text] = text_value
            ctx[step.out_raw] = sig.raw

            self._emit(
                "wait_done",
                kind="dbus_signal",
                matched=True,
                attempts=attempt,
                bus=step.bus,
                sender=sig.sender,
                path=sig.path,
                interface=sig.interface,
                member=sig.member,
            )
            return

        if producer_error:
            raise RuntimeError(f"WaitForDbusSignal failed: {producer_error}")

        detail = "producer ended before a match" if producer_done else f"timed out after {step.timeout_ms}ms"
        raise TimeoutError(f"WaitForDbusSignal {detail}")

    def _exec_i3_get_workspaces(self, step: StepI3GetWorkspaces, ctx: dict[str, Any]) -> None:
        i3 = I3Connection()
        ctx[step.out_var] = i3.get_workspaces()
        self._emit("i3_get_workspaces", out_var=step.out_var)

    def _exec_wait_for_window_event(self, step: StepWaitForWindowEvent, ctx: dict[str, Any]) -> None:
        deadline = time.time() + (step.timeout_ms / 1000.0)

        selector_dump = step.selector.model_dump(by_alias=True) if step.selector is not None else None
        self._emit(
            "wait_start",
            kind="window_event",
            event=step.event,
            raw_name=step.raw_name,
            selector=selector_dump,
            timeout_ms=step.timeout_ms,
        )

        q: Queue[Any] = Queue()
        stop = object()

        def producer() -> None:
            try:
                for ev in wm_events_mod.iter_wm_events(kinds={step.event}, poll_ms=max(50, int(step.poll_ms))):
                    q.put(ev)
            except Exception as exc:  # pragma: no cover - exercised through queue surface
                q.put({"__error__": str(exc)})
            finally:
                q.put(stop)

        Thread(target=producer, daemon=True).start()

        attempt = 0
        producer_done = False
        producer_error: str | None = None

        while time.time() <= deadline:
            self._check_panic()
            remaining = max(0.0, deadline - time.time())
            timeout_s = min(0.25, remaining)
            if timeout_s <= 0:
                break
            try:
                item = q.get(timeout=timeout_s)
            except Empty:
                continue

            if item is stop:
                producer_done = True
                break
            if isinstance(item, dict) and "__error__" in item:
                producer_error = str(item.get("__error__") or "unknown WM event error")
                self._emit_wait_attempt("window_event", attempt=attempt + 1, matched=False, error=producer_error, event=step.event)
                producer_done = True
                break

            ev = item
            attempt += 1
            if not isinstance(ev, wm_events_mod.WmEvent):
                self._emit_wait_attempt("window_event", attempt=attempt, matched=False, error=f"unexpected WM event payload: {type(ev).__name__}", event=step.event)
                continue

            info, wm = wm_events_mod.event_context_from_wm_event(ev)
            workspace = wm_events_mod.workspace_from_event(ev)
            if workspace is None and isinstance(info, dict):
                workspace = info.get("workspace")

            payload = {
                "wm": wm,
                "kind": ev.kind,
                "name": ev.name,
                "data": ev.data,
                "window": info if info else None,
                "workspace": workspace,
            }

            matched = True
            if step.raw_name is not None and ev.name != step.raw_name:
                matched = False
            if matched and step.selector is not None:
                matched = active_window_mod.selector_matches_info(step.selector, info or {}, wm)
            if matched and step.condition:
                probe_ctx = dict(ctx)
                probe_ctx.update({
                    step.out_event: payload,
                    step.out_window: info,
                    step.out_workspace: workspace,
                    step.out_wm: wm,
                    "wm_event": payload,
                    "window": info,
                    "workspace": workspace,
                    "wm": wm,
                })
                matched = bool(eval_expr(step.condition, probe_ctx))

            self._emit_wait_attempt(
                "window_event",
                attempt=attempt,
                matched=matched,
                event=step.event,
                name=ev.name,
                wm=wm,
                workspace=workspace,
                selector=selector_dump,
                raw_name=step.raw_name,
            )

            if not matched:
                continue

            ctx[step.out_event] = payload
            ctx[step.out_window] = info
            ctx[step.out_workspace] = workspace
            ctx[step.out_wm] = wm
            self._emit(
                "wait_end",
                kind="window_event",
                ok=True,
                event=step.event,
                name=ev.name,
                wm=wm,
                workspace=workspace,
                selector=selector_dump,
                raw_name=step.raw_name,
                attempts=attempt,
            )
            return

        self._emit(
            "wait_end",
            kind="window_event",
            ok=False,
            event=step.event,
            selector=selector_dump,
            raw_name=step.raw_name,
            attempts=attempt,
            producer_done=producer_done,
            producer_error=producer_error,
        )
        raise TimeoutError(f"WaitForWindowEvent timed out after {step.timeout_ms}ms")


    def _exec_wait_for_window(self, step: StepWaitForWindow, ctx: dict[str, Any]) -> None:
        from vhk.system.active_window import detect_compositor

        wm = detect_compositor() or "unknown"
        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll, max_poll = self._compute_wait_poll(step)
        attempt = 0


        stable_since: float | None = None
        stable_hits: int = 0
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        self._emit(
            "wait_start",
            kind="window",
            wm=wm,
            selector=step.selector.model_dump(by_alias=True),
            timeout_ms=step.timeout_ms,
        )

        # --- Hyprland: prefer socket2 events + occasional `hyprctl -j clients` scans --
        if wm == "hyprland":
            from vhk.system.hyprctl import HyprctlError, hyprctl_dispatch, hyprctl_json

            import os
            import socket
            import select

            def _regex_match(value: str, pattern: str, regex: bool) -> bool:
                if regex:
                    return re.search(pattern, value or "") is not None
                return value == pattern

            # Hyprland exposes a streaming event socket (socket2). If available, it
            # lets us avoid spamming hyprctl (which is synchronous in the compositor).
            sock2: socket.socket | None = None
            sock2_buf = b""
            last_active_addr: str | None = None
            last_active_ts: float = 0.0

            wanted_events: set[str] = {"activewindow", "activewindowv2"}
            if step.selector.title is not None:
                wanted_events |= {"windowtitle", "windowtitlev2", "windowTitle", "windowTitlev2"}
            if step.selector.workspace is not None:
                wanted_events |= {"workspace", "workspacev2", "focusedmon", "focusedmonv2"}
            if step.selector.urgent is not None:
                wanted_events |= {"urgent"}

            if step.use_events:
                try:
                    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
                    xdg = os.environ.get("XDG_RUNTIME_DIR")
                    if not sig or not xdg:
                        raise RuntimeError("HYPRLAND_INSTANCE_SIGNATURE/XDG_RUNTIME_DIR not set")
                    sock_path = os.path.join(xdg, "hypr", sig, ".socket2.sock")
                    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    s.connect(sock_path)
                    s.setblocking(False)
                    sock2 = s
                    self._emit("hypr_subscribe", ok=True, socket2=sock_path)
                except Exception as exc:
                    sock2 = None
                    self._emit("hypr_subscribe", ok=False, error=str(exc))

            clients_cache: dict[str, Any] = {"ts": 0.0, "val": None}

            def _clients(ttl_s: float = 0.05) -> list[dict[str, Any]]:
                now = time.time()
                if clients_cache["val"] is not None and (now - float(clients_cache["ts"])) <= ttl_s:
                    return clients_cache["val"]
                data = hyprctl_json("clients")
                if not isinstance(data, list):
                    raise HyprctlError("hyprctl clients did not return a list")
                clients_cache["ts"] = now
                clients_cache["val"] = data
                return data

            def _active_addr(ttl_s: float = 0.05) -> str | None:
                nonlocal last_active_addr, last_active_ts
                now = time.time()
                if last_active_addr is not None and (now - float(last_active_ts)) <= ttl_s:
                    return last_active_addr
                try:
                    aw = hyprctl_json("activewindow")
                    if isinstance(aw, dict):
                        addr = str(aw.get("address") or "").strip() or None
                        last_active_addr = addr
                        last_active_ts = now
                        return addr
                except Exception:
                    return last_active_addr
                return last_active_addr

            def _wait_socket2(timeout_s: float) -> bool:
                """Wait for a relevant Hyprland socket2 event (best-effort)."""

                nonlocal sock2_buf, last_active_addr, last_active_ts
                if sock2 is None:
                    return False
                timeout_s = max(0.0, float(timeout_s))
                try:
                    r, _, _ = select.select([sock2], [], [], timeout_s)
                except Exception:
                    return False
                if not r:
                    return False
                try:
                    chunk = sock2.recv(4096)
                except BlockingIOError:
                    return False
                if not chunk:
                    raise RuntimeError("Hyprland socket2 closed")

                sock2_buf += chunk
                wake = False
                while b"\n" in sock2_buf:
                    line, sock2_buf = sock2_buf.split(b"\n", 1)
                    sline = line.decode("utf-8", errors="replace").strip()
                    if not sline or ">>" not in sline:
                        continue
                    ev, data = sline.split(">>", 1)
                    ev = ev.strip()
                    data = data.strip()
                    if ev == "activewindowv2":
                        last_active_addr = data or None
                        last_active_ts = time.time()
                    if ev in wanted_events:
                        wake = True
                return wake

            try:
                while time.time() <= deadline:
                    self._check_panic()
                    attempt += 1

                    try:
                        clients = _clients()
                    except Exception as exc:
                        self._emit_wait_attempt("window", attempt=attempt, matched=False, error=str(exc), wm=wm)
                        # If socket2 is connected, prefer waiting on it instead of sleeping.
                        remaining = max(0.0, deadline - time.time())
                        if sock2 is not None and remaining > 0:
                            try:
                                _wait_socket2(min(0.25, remaining))
                            except Exception:
                                sock2 = None
                        else:
                            time.sleep(0.25)
                        continue

                    active_addr: str | None = None
                    if step.selector.focused is not None:
                        active_addr = _active_addr()

                    matched: dict[str, Any] | None = None
                    matched_ws: str | None = None

                    for c in clients:
                        if not isinstance(c, dict):
                            continue

                        addr = str(c.get("address") or "").strip()
                        cls = str(c.get("class") or "").strip()
                        initial_cls = str(c.get("initialClass") or "").strip()
                        title = str(c.get("title") or "").strip()
                        initial_title = str(c.get("initialTitle") or "").strip()

                        ws_val = c.get("workspace")
                        ws_name: str | None = None
                        if isinstance(ws_val, dict):
                            ws_name = (str(ws_val.get("name") or "").strip() or None)
                        elif isinstance(ws_val, str):
                            ws_name = ws_val.strip() or None

                        info = dict(c)
                        info["title"] = title or initial_title
                        info["class"] = cls
                        info["initialClass"] = initial_cls
                        info["workspace"] = ws_name
                        info["focused"] = bool(active_addr) and (addr or "").lower() == (active_addr or "").lower()

                        if not active_window_mod.selector_matches_info(step.selector, info, "hyprland"):
                            continue

                        matched = c
                        matched_ws = ws_name
                        break

                    self._emit_wait_attempt(
                        "window",
                        attempt=attempt,
                        matched=bool(matched),
                        wm=wm,
                        address=(matched.get("address") if matched else None),
                        workspace=matched_ws,
                        selector=step.selector.model_dump(by_alias=True),
                    )


                    if matched is not None:


                        if stable_since is None:


                            stable_since = time.time()


                            stable_hits = 1


                        else:


                            stable_hits += 1



                        stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))


                        stable_ok = stable_hits >= need_hits and stable_elapsed_ms >= need_ms



                        if stable_ok:


                            ctx[step.out_var] = matched


                            ctx[step.out_con_id] = matched.get("address")


                            ctx[step.out_workspace] = matched_ws


                            self._emit(


                                "wait_end",


                                kind="window",


                                wm=wm,


                                ok=True,


                                attempts=attempt,


                                address=matched.get("address"),


                                workspace=matched_ws,


                                stable_hits=stable_hits,


                                stable_elapsed_ms=stable_elapsed_ms,


                            )



                            if step.focus:


                                addr = str(matched.get("address") or "").strip()


                                if addr:


                                    try:


                                        hyprctl_dispatch("focuswindow", f"address:{addr}")


                                        self._emit("hypr_focus", address=addr)


                                    except Exception as exc:


                                        self._emit("hypr_focus", address=addr, ok=False, error=str(exc))


                            return


                    else:


                        stable_since = None


                        stable_hits = 0

                    remaining = max(0.0, deadline - time.time())
                    if remaining <= 0:
                        break

                    if sock2 is not None:
                        # Use socket2 as the primary sleep/wakeup mechanism.
                        ev_timeout = (poll / 1000.0) if poll > 0 else 0.2
                        ev_timeout = max(0.05, min(1.0, float(ev_timeout)))
                        try:
                            _wait_socket2(min(ev_timeout, remaining))
                        except Exception:
                            sock2 = None
                    else:
                        if poll > 0:
                            jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                            sleep_ms = max(0, poll + jitter)
                            time.sleep(sleep_ms / 1000.0)

                    poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

                self._emit("wait_end", kind="window", wm=wm, ok=False, attempts=attempt)
                raise TimeoutError(f"WaitForWindow timed out after {step.timeout_ms}ms")
            finally:
                if sock2 is not None:
                    try:
                        sock2.close()
                    except Exception:
                        pass

        # --- Generic polling fallback (X11 / KWin / unknown) ------------------
        if wm not in {"i3", "sway"}:
            events = None

            if step.use_events:
                try:
                    events = wm_events_mod.iter_wm_events(kinds={"focus", "title"}, poll_ms=max(50, int(poll or 0) or 50))
                except Exception:
                    events = None

            while time.time() <= deadline:
                self._check_panic()
                attempt += 1

                try:
                    rows, wm2 = active_window_mod.get_window_list_snapshot(
                        selector=step.selector,
                        include_geometry=False,
                        focused_first=True,
                    )
                    if wm2:
                        wm = wm2
                except Exception as exc:
                    self._emit_wait_attempt("window", attempt=attempt, matched=False, error=str(exc), wm=wm)
                    rows = []

                matched = dict(rows[0]) if rows else None
                matched_id = None
                matched_ws = None
                if matched is not None:
                    matched_id = matched.get("id") or matched.get("address")
                    matched_ws = matched.get("workspace")

                self._emit_wait_attempt(
                    "window",
                    attempt=attempt,
                    matched=bool(matched),
                    con_id=matched_id,
                    workspace=matched_ws,
                    wm=wm,
                    selector=step.selector.model_dump(by_alias=True),
                )

                if matched:
                    if stable_since is None:
                        stable_since = time.time()
                        stable_hits = 1
                    else:
                        stable_hits += 1

                    stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))
                    stable_ok = stable_hits >= need_hits and stable_elapsed_ms >= need_ms

                    if stable_ok:
                        ctx[step.out_var] = matched
                        ctx[step.out_con_id] = matched_id
                        ctx[step.out_workspace] = matched_ws
                        self._emit(
                            "wait_end",
                            kind="window",
                            wm=wm,
                            ok=True,
                            attempts=attempt,
                            con_id=matched_id,
                            workspace=matched_ws,
                            stable_hits=stable_hits,
                            stable_elapsed_ms=stable_elapsed_ms,
                        )

                        if step.focus:
                            try:
                                focused_row, focused_wm = active_window_mod.focus_window_matching(
                                    step.selector,
                                    timeout_ms=max(500, int(step.timeout_ms)),
                                    poll_ms=max(50, int(step.poll_ms or 0) or 50),
                                )
                                self._emit(
                                    "window_focus",
                                    wm=focused_wm,
                                    window_id=focused_row.get("id") or focused_row.get("address"),
                                    workspace=focused_row.get("workspace"),
                                )
                            except Exception as exc:
                                raise RuntimeError(f"WaitForWindow matched but could not focus selector {step.selector.model_dump(by_alias=True)}: {exc}") from exc
                        return
                else:
                    stable_since = None
                    stable_hits = 0

                remaining = deadline - time.time()
                if remaining <= 0:
                    break

                woke = False
                if events is not None:
                    try:
                        next(events)
                        woke = True
                    except StopIteration:
                        events = None
                    except Exception:
                        events = None
                if woke:
                    continue

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(sleep_ms / 1000.0)
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

            self._emit("wait_end", kind="window", wm=wm, ok=False, attempts=attempt)
            raise TimeoutError(f"WaitForWindow timed out after {step.timeout_ms}ms")

        # --- i3 / sway: poll + optional IPC event wakeups ---------------------
        i3 = I3Connection()
        events = None

        if step.use_events:
            try:
                # Use a separate connection so the subscription socket stays open.
                sub = I3Connection(timeout=2.0)
                ev_timeout = (poll / 1000.0) if poll > 0 else 0.2
                ev_timeout = max(0.05, min(1.0, float(ev_timeout)))
                events = sub.subscribe(["window"], timeout=ev_timeout, yield_timeouts=True)
                self._emit("i3_subscribe", events=["window"], timeout_ms=int(ev_timeout * 1000))
            except Exception as exc:
                events = None
                self._emit("i3_subscribe", events=["window"], ok=False, error=str(exc))

        try:
            while time.time() <= deadline:
                self._check_panic()
                attempt += 1
                tree = i3.get_tree()
                m = find_first(tree, step.selector)

                self._emit_wait_attempt(
                    "window",
                    attempt=attempt,
                    matched=bool(m),
                    con_id=(m.node.get("id") if m else None),
                    workspace=(m.workspace if m else None),
                    wm=wm,
                    selector=step.selector.model_dump(by_alias=True),
                )


                if m:


                    if stable_since is None:


                        stable_since = time.time()


                        stable_hits = 1


                    else:


                        stable_hits += 1



                    stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))


                    stable_ok = stable_hits >= need_hits and stable_elapsed_ms >= need_ms



                    if stable_ok:


                        ctx[step.out_var] = m.node


                        ctx[step.out_con_id] = m.node.get("id")


                        ctx[step.out_workspace] = m.workspace


                        self._emit(


                            "wait_end",


                            kind="window",


                            wm=wm,


                            ok=True,


                            attempts=attempt,


                            con_id=m.node.get("id"),


                            workspace=m.workspace,


                            stable_hits=stable_hits,


                            stable_elapsed_ms=stable_elapsed_ms,


                        )



                        if step.focus:


                            con_id = m.node.get("id")


                            if con_id is not None:


                                i3.command(f"[con_id={con_id}] focus")


                                self._emit("i3_focus", con_id=con_id)


                        return


                else:


                    stable_since = None


                    stable_hits = 0

                remaining = deadline - time.time()
                if remaining <= 0:
                    break

                if events is not None:
                    try:
                        # Wake up on any window event (or a periodic timeout yield).
                        next(events)
                        continue
                    except StopIteration:
                        events = None
                    except Exception:
                        events = None

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(sleep_ms / 1000.0)
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0
        finally:
            try:
                if events is not None:
                    events.close()
            except Exception:
                pass

        self._emit("wait_end", kind="window", wm=wm, ok=False, attempts=attempt)
        raise TimeoutError(f"WaitForWindow timed out after {step.timeout_ms}ms")



    def _exec_wait_for_window_vanish(self, step: StepWaitForWindowVanish, ctx: dict[str, Any]) -> None:
        from vhk.system.active_window import detect_compositor

        wm = detect_compositor() or "unknown"
        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        max_poll = max(0, step.max_poll_ms)
        attempt = 0

        seen_present = False
        last_seen_con_id = None
        last_seen_ws = None
        last_seen_node = None

        stable_since: float | None = None
        stable_hits: int = 0
        need_hits = max(1, int(getattr(step, "stable_attempts", 1) or 1))
        need_ms = max(0, int(getattr(step, "stable_ms", 0) or 0))

        self._emit(
            "wait_start",
            kind="window_vanish",
            wm=wm,
            selector=step.selector.model_dump(by_alias=True),
            timeout_ms=step.timeout_ms,
            require_seen=bool(getattr(step, "require_seen", False)),
        )

        # --- Hyprland: socket2 wakeups + client scans (best-effort) ---------
        if wm == "hyprland":
            from vhk.system.hyprctl import HyprctlError, hyprctl_json

            import os
            import socket
            import select

            def _regex_match(value: str, pattern: str, regex: bool) -> bool:
                if regex:
                    return re.search(pattern, value or "") is not None
                return value == pattern

            sock2: socket.socket | None = None
            sock2_buf = b""
            wanted_events: set[str] = {
                "openwindow",
                "closewindow",
                "movewindow",
                "movewindowv2",
                "workspace",
                "workspacev2",
                "activewindow",
                "activewindowv2",
                "windowtitle",
                "windowtitlev2",
                "urgent",
            }

            if step.use_events:
                try:
                    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
                    xdg = os.environ.get("XDG_RUNTIME_DIR")
                    if not sig or not xdg:
                        raise RuntimeError("HYPRLAND_INSTANCE_SIGNATURE/XDG_RUNTIME_DIR not set")
                    sock_path = os.path.join(xdg, "hypr", sig, ".socket2.sock")
                    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    s.connect(sock_path)
                    s.setblocking(False)
                    sock2 = s
                    self._emit("hypr_subscribe", ok=True, socket2=sock_path)
                except Exception as exc:
                    sock2 = None
                    self._emit("hypr_subscribe", ok=False, error=str(exc))

            clients_cache: dict[str, Any] = {"ts": 0.0, "val": None}

            def _clients(ttl_s: float = 0.05) -> list[dict[str, Any]]:
                now = time.time()
                if clients_cache["val"] is not None and (now - float(clients_cache["ts"])) <= ttl_s:
                    return clients_cache["val"]
                data = hyprctl_json("clients")
                if not isinstance(data, list):
                    raise HyprctlError("hyprctl clients did not return a list")
                clients_cache["ts"] = now
                clients_cache["val"] = data
                return data

            def _wait_socket2(timeout_s: float) -> bool:
                nonlocal sock2_buf
                if sock2 is None:
                    return False
                timeout_s = max(0.0, float(timeout_s))
                try:
                    r, _, _ = select.select([sock2], [], [], timeout_s)
                except Exception:
                    return False
                if not r:
                    return False
                try:
                    chunk = sock2.recv(4096)
                except BlockingIOError:
                    return False
                if not chunk:
                    raise RuntimeError("Hyprland socket2 closed")
                sock2_buf += chunk
                wake = False
                while b"\n" in sock2_buf:
                    line, sock2_buf = sock2_buf.split(b"\n", 1)
                    sline = line.decode("utf-8", errors="replace").strip()
                    if not sline or ">>" not in sline:
                        continue
                    ev, _data = sline.split(">>", 1)
                    ev = ev.strip()
                    if ev in wanted_events:
                        wake = True
                return wake

            try:
                while time.time() <= deadline:
                    self._check_panic()
                    attempt += 1

                    try:
                        clients = _clients()
                    except Exception as exc:
                        self._emit_wait_attempt("window_vanish", attempt=attempt, present=False, error=str(exc), wm=wm)
                        remaining = max(0.0, deadline - time.time())
                        if sock2 is not None and remaining > 0:
                            try:
                                _wait_socket2(min(0.25, remaining))
                            except Exception:
                                sock2 = None
                        else:
                            time.sleep(0.25)
                        continue

                    def _matches(c: dict[str, Any]) -> tuple[bool, str | None]:
                        addr = str(c.get("address") or "").strip()
                        cls = str(c.get("class") or "").strip()
                        initial_cls = str(c.get("initialClass") or "").strip()
                        title = str(c.get("title") or "").strip()
                        initial_title = str(c.get("initialTitle") or "").strip()

                        ws_val = c.get("workspace")
                        ws_name: str | None = None
                        if isinstance(ws_val, dict):
                            ws_name = (str(ws_val.get("name") or "").strip() or None)
                        elif isinstance(ws_val, str):
                            ws_name = ws_val.strip() or None

                        try:
                            aw = hyprctl_json("activewindow")
                            addr_active = str(aw.get("address") or "").strip() if isinstance(aw, dict) else ""
                        except Exception:
                            addr_active = ""

                        info = dict(c)
                        info["title"] = title or initial_title
                        info["class"] = cls
                        info["initialClass"] = initial_cls
                        info["workspace"] = ws_name
                        info["focused"] = bool(addr_active) and (addr or "").lower() == addr_active.lower()
                        return active_window_mod.selector_matches_info(step.selector, info, "hyprland"), ws_name

                    matched = None
                    matched_ws = None
                    for c in clients:
                        if not isinstance(c, dict):
                            continue
                        ok, ws_name = _matches(c)
                        if ok:
                            matched = c
                            matched_ws = ws_name
                            break

                    present = bool(matched)
                    if present:
                        seen_present = True
                        last_seen_node = matched
                        last_seen_con_id = (matched.get("address") if matched else None)
                        last_seen_ws = matched_ws
                        stable_since = None
                        stable_hits = 0
                    else:
                        if stable_since is None:
                            stable_since = time.time()
                            stable_hits = 1
                        else:
                            stable_hits += 1

                    stable_elapsed_ms = 0
                    if stable_since is not None:
                        stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

                    self._emit_wait_attempt(
                        "window_vanish",
                        attempt=attempt,
                        present=present,
                        wm=wm,
                        address=(matched.get("address") if matched else None),
                        workspace=matched_ws,
                        selector=step.selector.model_dump(by_alias=True),
                        stable_hits=stable_hits,
                        stable_elapsed_ms=stable_elapsed_ms,
                        stable_needed_hits=need_hits,
                        stable_needed_ms=need_ms,
                    )

                    ok_now = not present
                    if getattr(step, "require_seen", False) and not seen_present:
                        ok_now = False

                    stable_ok = ok_now and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
                    if stable_ok:
                        ctx[step.out_seen] = bool(seen_present)
                        ctx[step.out_last_con_id] = last_seen_con_id
                        ctx[step.out_last_workspace] = last_seen_ws
                        ctx[step.out_last_window] = last_seen_node
                        self._emit("wait_end", kind="window_vanish", wm=wm, ok=True, attempts=attempt)
                        return

                    remaining = max(0.0, deadline - time.time())
                    if remaining <= 0:
                        break

                    if sock2 is not None:
                        ev_timeout = (poll / 1000.0) if poll > 0 else 0.2
                        ev_timeout = max(0.05, min(1.0, float(ev_timeout)))
                        try:
                            _wait_socket2(min(ev_timeout, remaining))
                        except Exception:
                            sock2 = None
                    else:
                        if poll > 0:
                            jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                            sleep_ms = max(0, poll + jitter)
                            time.sleep(min(remaining, sleep_ms / 1000.0))

                    poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

                ctx[step.out_seen] = bool(seen_present)
                ctx[step.out_last_con_id] = last_seen_con_id
                ctx[step.out_last_workspace] = last_seen_ws
                ctx[step.out_last_window] = last_seen_node
                self._emit("wait_end", kind="window_vanish", wm=wm, ok=False, attempts=attempt)
                raise TimeoutError(f"WaitForWindowVanish timed out after {step.timeout_ms}ms")
            finally:
                if sock2 is not None:
                    try:
                        sock2.close()
                    except Exception:
                        pass

        # --- Generic snapshot fallback (X11 / KWin / unknown) -----------------
        if wm not in {"i3", "sway", "hyprland"}:
            events = None

            if step.use_events:
                try:
                    events = wm_events_mod.iter_wm_events(kinds={"focus", "title", "new", "close"}, poll_ms=max(50, int(poll or 0) or 50))
                except Exception:
                    events = None

            while time.time() <= deadline:
                self._check_panic()
                attempt += 1

                rows: list[dict[str, Any]] | None
                try:
                    rows, wm2 = active_window_mod.get_window_list_snapshot(
                        selector=step.selector,
                        include_geometry=False,
                        focused_first=True,
                    )
                    if wm2:
                        wm = wm2
                except Exception as exc:
                    rows = None
                    self._emit_wait_attempt("window_vanish", attempt=attempt, present=False, error=str(exc), wm=wm)

                matched = dict(rows[0]) if rows else None
                matched_id = matched.get("id") or matched.get("address") if matched else None
                matched_ws = matched.get("workspace") if matched else None

                if rows is not None:
                    present = bool(matched)
                    if present:
                        seen_present = True
                        last_seen_node = matched
                        last_seen_con_id = matched_id
                        last_seen_ws = matched_ws
                        stable_since = None
                        stable_hits = 0
                    else:
                        if stable_since is None:
                            stable_since = time.time()
                            stable_hits = 1
                        else:
                            stable_hits += 1
                else:
                    present = None

                stable_elapsed_ms = 0
                if stable_since is not None:
                    stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

                self._emit_wait_attempt(
                    "window_vanish",
                    attempt=attempt,
                    present=present,
                    con_id=matched_id,
                    workspace=matched_ws,
                    wm=wm,
                    selector=step.selector.model_dump(by_alias=True),
                    stable_hits=stable_hits,
                    stable_elapsed_ms=stable_elapsed_ms,
                    stable_needed_hits=need_hits,
                    stable_needed_ms=need_ms,
                )

                ok_now = rows is not None and not bool(matched)
                if getattr(step, "require_seen", False) and not seen_present:
                    ok_now = False

                stable_ok = ok_now and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
                if stable_ok:
                    ctx[step.out_seen] = bool(seen_present)
                    ctx[step.out_last_con_id] = last_seen_con_id
                    ctx[step.out_last_workspace] = last_seen_ws
                    ctx[step.out_last_window] = last_seen_node
                    self._emit("wait_end", kind="window_vanish", wm=wm, ok=True, attempts=attempt)
                    return

                remaining = deadline - time.time()
                if remaining <= 0:
                    break

                woke = False
                if events is not None:
                    try:
                        next(events)
                        woke = True
                    except StopIteration:
                        events = None
                    except Exception:
                        events = None
                if woke:
                    continue

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(min(remaining, sleep_ms / 1000.0))
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0

            ctx[step.out_seen] = bool(seen_present)
            ctx[step.out_last_con_id] = last_seen_con_id
            ctx[step.out_last_workspace] = last_seen_ws
            ctx[step.out_last_window] = last_seen_node
            self._emit("wait_end", kind="window_vanish", wm=wm, ok=False, attempts=attempt)
            raise TimeoutError(f"WaitForWindowVanish timed out after {step.timeout_ms}ms")

        # --- i3 / sway: poll + optional IPC event wakeups -----------------
        i3 = I3Connection()
        events = None
        if step.use_events:
            try:
                sub = I3Connection(timeout=2.0)
                ev_timeout = (poll / 1000.0) if poll > 0 else 0.2
                ev_timeout = max(0.05, min(1.0, float(ev_timeout)))
                events = sub.subscribe(["window"], timeout=ev_timeout, yield_timeouts=True)
                self._emit("i3_subscribe", events=["window"], timeout_ms=int(ev_timeout * 1000))
            except Exception as exc:
                events = None
                self._emit("i3_subscribe", events=["window"], ok=False, error=str(exc))

        try:
            while time.time() <= deadline:
                self._check_panic()
                attempt += 1
                tree = i3.get_tree()
                m = find_first(tree, step.selector)

                present = bool(m)
                if present and m is not None:
                    seen_present = True
                    last_seen_node = m.node
                    last_seen_con_id = m.node.get("id")
                    last_seen_ws = m.workspace
                    stable_since = None
                    stable_hits = 0
                else:
                    if stable_since is None:
                        stable_since = time.time()
                        stable_hits = 1
                    else:
                        stable_hits += 1

                stable_elapsed_ms = 0
                if stable_since is not None:
                    stable_elapsed_ms = int(max(0.0, (time.time() - stable_since) * 1000.0))

                self._emit_wait_attempt(
                    "window_vanish",
                    attempt=attempt,
                    present=present,
                    con_id=(m.node.get("id") if m else None),
                    workspace=(m.workspace if m else None),
                    wm=wm,
                    selector=step.selector.model_dump(by_alias=True),
                    stable_hits=stable_hits,
                    stable_elapsed_ms=stable_elapsed_ms,
                    stable_needed_hits=need_hits,
                    stable_needed_ms=need_ms,
                )

                ok_now = not present
                if getattr(step, "require_seen", False) and not seen_present:
                    ok_now = False

                stable_ok = ok_now and stable_hits >= need_hits and stable_elapsed_ms >= need_ms
                if stable_ok:
                    ctx[step.out_seen] = bool(seen_present)
                    ctx[step.out_last_con_id] = last_seen_con_id
                    ctx[step.out_last_workspace] = last_seen_ws
                    ctx[step.out_last_window] = last_seen_node
                    self._emit("wait_end", kind="window_vanish", wm=wm, ok=True, attempts=attempt)
                    return

                remaining = deadline - time.time()
                if remaining <= 0:
                    break

                if events is not None:
                    try:
                        next(events)
                        continue
                    except StopIteration:
                        events = None
                    except Exception:
                        events = None

                if poll > 0:
                    jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                    sleep_ms = max(0, poll + jitter)
                    time.sleep(min(remaining, sleep_ms / 1000.0))
                poll = min(max_poll, int(poll * 1.4) + 1) if poll else 0
        finally:
            try:
                if events is not None:
                    events.close()
            except Exception:
                pass

        ctx[step.out_seen] = bool(seen_present)
        ctx[step.out_last_con_id] = last_seen_con_id
        ctx[step.out_last_workspace] = last_seen_ws
        ctx[step.out_last_window] = last_seen_node
        self._emit("wait_end", kind="window_vanish", wm=wm, ok=False, attempts=attempt)
        raise TimeoutError(f"WaitForWindowVanish timed out after {step.timeout_ms}ms")
    def _exec_focus_window(self, step: StepFocusWindow, ctx: dict[str, Any]) -> None:
        try:
            row, wm = active_window_mod.focus_window_matching(step.selector)
        except Exception as exc:
            raise RuntimeError(f"FocusWindow: could not focus selector {step.selector.model_dump(by_alias=True)}: {exc}") from exc
        self._emit(
            "window_focus",
            wm=wm,
            window_id=row.get("id") or row.get("address"),
            workspace=row.get("workspace"),
        )
        if wm in {"i3", "sway"}:
            self._emit("i3_focus", con_id=row.get("id"))
        elif wm == "hyprland":
            self._emit("hypr_focus", address=row.get("address") or row.get("id"))

    # --- Macro composition ------------------------------------------------

    def _exec_call_macro(self, step: StepCallMacro, ctx: dict[str, Any], macro_name: str, path_prefix: list[int]) -> None:
        if step.macro not in self.project.macros:
            raise ValueError(f"CallMacro: unknown macro '{step.macro}'")

        args_rendered = self._render_value(step.args, ctx)
        child_macro = self.project.macros[step.macro]
        child_ctx: dict[str, Any] = {
            "project": {"name": self.project.name},
            "macro": {"name": child_macro.name},
            **args_rendered,
        }

        self._emit("call_macro_start", parent_macro=macro_name, child_macro=step.macro)
        try:
            self._run_steps(child_macro.steps, child_ctx, macro_name=step.macro, path_prefix=path_prefix + [999])
        except _ReturnSignal as r:
            child_ctx[r.out_var] = r.value
            self._emit("call_macro_return", parent_macro=macro_name, child_macro=step.macro, out_var=r.out_var)
        self._emit("call_macro_end", parent_macro=macro_name, child_macro=step.macro)

        # Return mapping
        for child_key, parent_key in step.returns.items():
            if child_key in child_ctx:
                ctx[parent_key] = child_ctx[child_key]

        # Also expose last_child_ctx for debugging.
        ctx["last_child_ctx"] = {k: v for k, v in child_ctx.items() if k not in {"project", "macro"}}

    # ---------------------------------------------------------------------

    def _profile_scale_delay_ms(self, ms: int) -> int:
        value = max(0, int(ms))
        if self.project.settings.runner_profile != "turbo":
            return value
        scale = float(self.project.settings.turbo_delay_scale)
        if scale < 0:
            scale = 0.0
        return int(round(value * scale))

    def _choose_text_backend(self, step: StepTypeText, text: str) -> str:
        backend = str(step.backend)
        if backend != "auto":
            return backend

        if self.project.settings.runner_profile == "turbo":
            threshold = int(self.project.settings.turbo_type_clipboard_threshold)
            if len(text) >= max(1, threshold) and input_mod.text_looks_paste_friendly(text):
                return "clipboard"

        return "auto"

    def _eval_or_render(self, expr_or_value: Any, ctx: dict[str, Any]) -> Any:
        if isinstance(expr_or_value, str):
            rendered = interpolate(expr_or_value, ctx)
            try:
                return eval_expr(rendered, ctx)
            except Exception:
                return rendered
        return self._render_value(expr_or_value, ctx)

    def _as_int(self, v: Any, ctx: dict[str, Any], *, field: str = "") -> int:
        """Render/interpolate a value and coerce to int."""

        rv = self._render_value(v, ctx)
        # Allow expression evaluation for string-ish numeric fields.
        # This is especially handy for data-driven macros (e.g. "100 + jitter").
        if isinstance(rv, str):
            try:
                rv2 = eval_expr(rv, ctx)
                rv = rv2
            except Exception:
                # Fall back to plain int conversion below.
                pass
        if isinstance(rv, bool):
            return int(rv)
        if isinstance(rv, int):
            return rv
        if isinstance(rv, float):
            return int(rv)
        s = str(rv)
        try:
            return int(s)
        except Exception as e:
            label = f" ({field})" if field else ""
            raise ValueError(f"Expected integer{label}, got {rv!r}") from e

    def _render_value(self, v: Any, ctx: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return interpolate(v, ctx)
        if isinstance(v, list):
            return [self._render_value(x, ctx) for x in v]
        if isinstance(v, dict):
            return {k: self._render_value(val, ctx) for k, val in v.items()}
        return v
