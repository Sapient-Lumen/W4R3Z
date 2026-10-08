from __future__ import annotations

import json
import random
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from vhk.core.events import EventLogger, make_default_eventlog_path
from vhk.core.expr import eval_expr, interpolate
from vhk.core.models import (
    Project,
    Step,
    StepCallMacro,
    StepBreak,
    StepContinue,
    StepReturn,
    StepCaptureScreenshot,
    StepImageSearch,
    StepWaitForImage,
    StepVisualAssert,
    StepVisualVerify,
    StepWaitForRegionChange,
    StepOcrReadText,
    StepWaitForText,
    StepAssertText,
    StepMouseClickAt,
    StepClickNeedle,
    StepClipboardRead,
    StepClipboardSet,
    StepWaitForClipboardChange,
    StepPasteClipboard,
    StepOpenUrl,
    StepComposeEmail,
    StepHttpRequest,
    StepDownloadFile,
    StepShowMessage,
    StepAskYesNo,
    StepInputBox,
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
    StepDelay,
    StepFocusWindow,
    StepIf,
    StepWhile,
    StepTry,
    StepI3Command,
    StepI3GetTree,
    StepI3GetWorkspaces,
    StepImageSearchFile,
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
    StepMouseMove,
    StepNotify,
    StepOcrReadTextFile,
    StepPixelSearchFile,
    StepRandomWait,
    StepRunShell,
    StepSetVar,
    StepTypeText,
    StepWaitForImageFile,
    StepWaitForPixelFile,
    StepWaitForWindow,
)
from vhk.core.panic import PanicConfig, PanicStop, is_panicking
from vhk.i3.ipc import I3Connection
from vhk.i3.tree import find_first
from vhk.system import clipboard as clipboard_mod
from vhk.system import files as files_mod
from vhk.system import input as input_mod
from vhk.system import cursor as cursor_mod
from vhk.system import notify as notify_mod
from vhk.system import openers as openers_mod
from vhk.system import network as network_mod
from vhk.system import dialogs as dialogs_mod
from vhk.system import processes as processes_mod
from vhk.system import screenshot as screenshot_mod
from vhk.system import watch as watch_mod
from vhk.system import textops as text_mod
from vhk.system.session import set_preferred_backend
from vhk.vision.match import image_search_file
from vhk.vision.assets import compute_click_offset, try_load_needle
from vhk.vision.ocr import ocr_read_text_file
from vhk.vision.pixel import pixel_search_file
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
    def __init__(self, project: Project, console: Console | None = None, *, step_mode: bool = False, input_func=input):
        self.project = project
        self.console = console or Console()
        self._event_logger: Optional[EventLogger] = None
        self._panic_cfg = PanicConfig(panic_file=self.project.settings.panic_file)
        self.step_mode = bool(step_mode)
        self._input_func = input_func
        self._last_capture_path: str | None = None
        self._processes: dict[int, Any] = {}
        self._cursor_handle = None

        # Make backend choice available to all system modules.
        set_preferred_backend(self.project.settings.desktop_backend)

    def run(self, macro_name: str, initial_vars: dict[str, Any] | None = None) -> RunResult:
        macro = self.project.macros[macro_name]
        ctx: dict[str, Any] = {"project": {"name": self.project.name}, "macro": {"name": macro.name}}
        if initial_vars:
            ctx.update(initial_vars)

        run_id = time.strftime("%Y%m%d_%H%M%S") + f"_{int(time.time()*1000)%1000:03d}"
        log_dir = Path(self.project.root_dir) / self.project.settings.log_dir
        if self.project.settings.event_log:
            self._event_logger = EventLogger(make_default_eventlog_path(log_dir, run_id))
            self._event_logger.emit(
                "run_start",
                run_id=run_id,
                project=self.project.name,
                macro=macro_name,
                initial_vars=list((initial_vars or {}).keys()),
                dry_run=bool(self.project.settings.dry_run),
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
        elif isinstance(step, StepWaitForImageFile):
            self._exec_wait_for_image_file(step, ctx)
        elif isinstance(step, StepPixelSearchFile):
            self._exec_pixel_search_file(step, ctx)
        elif isinstance(step, StepWaitForPixelFile):
            self._exec_wait_for_pixel_file(step, ctx)
        elif isinstance(step, StepOcrReadTextFile):
            self._exec_ocr_file(step, ctx)
        elif isinstance(step, StepCaptureScreenshot):
            self._exec_capture_screenshot(step, ctx)
        elif isinstance(step, StepImageSearch):
            self._exec_image_search(step, ctx)
        elif isinstance(step, StepWaitForImage):
            self._exec_wait_for_image(step, ctx)
        elif isinstance(step, StepOcrReadText):
            self._exec_ocr(step, ctx)
        elif isinstance(step, StepVisualAssert):
            self._exec_visual_assert(step, ctx)
        elif isinstance(step, StepVisualVerify):
            self._exec_visual_verify(step, ctx)
        elif isinstance(step, StepWaitForRegionChange):
            self._exec_wait_for_region_change(step, ctx)
        elif isinstance(step, StepWaitForText):
            self._exec_wait_for_text(step, ctx)
        elif isinstance(step, StepAssertText):
            self._exec_assert_text(step, ctx)
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
        elif isinstance(step, StepPasteClipboard):
            self._exec_paste_clipboard(step, ctx)
        elif isinstance(step, StepOpenUrl):
            self._exec_open_url(step, ctx)
        elif isinstance(step, StepComposeEmail):
            self._exec_compose_email(step, ctx)
        elif isinstance(step, StepHttpRequest):
            self._exec_http_request(step, ctx)
        elif isinstance(step, StepDownloadFile):
            self._exec_download_file(step, ctx)
        elif isinstance(step, StepShowMessage):
            self._exec_show_message(step, ctx)
        elif isinstance(step, StepAskYesNo):
            self._exec_ask_yes_no(step, ctx)
        elif isinstance(step, StepInputBox):
            self._exec_input_box(step, ctx)
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
        elif isinstance(step, StepI3Command):
            self._exec_i3_command(step, ctx)
        elif isinstance(step, StepI3GetTree):
            self._exec_i3_get_tree(step, ctx)
        elif isinstance(step, StepI3GetWorkspaces):
            self._exec_i3_get_workspaces(step, ctx)
        elif isinstance(step, StepWaitForWindow):
            self._exec_wait_for_window(step, ctx)
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
                                time.sleep(retry_delay_ms / 1000.0)
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
        match = image_search_file(hay, needle, region=step.region, threshold=step.threshold)
        ctx[step.out_x] = match.x
        ctx[step.out_y] = match.y
        ctx[step.out_score] = match.score
        self._emit("image_search", hay=str(hay), needle=str(needle), score=match.score, x=match.x, y=match.y)

    def _exec_wait_for_image_file(self, step: StepWaitForImageFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        hay = root / interpolate(step.haystack_path, ctx)
        needle = root / interpolate(step.needle_path, ctx)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0
        last = None

        self._emit(
            "wait_start",
            kind="image",
            needle=str(needle),
            threshold=step.threshold,
            timeout_ms=step.timeout_ms,
        )

        while time.time() <= deadline:
            self._check_panic()
            attempt += 1
            last = image_search_file(hay, needle, region=step.region, threshold=-1e9)  # don't threshold inside
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
            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(step.max_poll_ms, int(poll * 1.4) + 1) if poll else 0

        score = last.score if last else None
        self._emit("wait_end", kind="image", ok=False, attempts=attempt, score=score)
        raise TimeoutError(f"WaitForImageFile timed out after {step.timeout_ms}ms (last score={score})")

    def _exec_pixel_search_file(self, step: StepPixelSearchFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)
        match = pixel_search_file(img, color=self._render_value(step.color, ctx), region=step.region, tolerance=step.tolerance)
        ctx[step.out_x] = match.x
        ctx[step.out_y] = match.y
        ctx[step.out_dist] = match.dist
        self._emit("pixel_search", image=str(img), x=match.x, y=match.y, dist=match.dist)

    def _exec_wait_for_pixel_file(self, step: StepWaitForPixelFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0
        last_dist: float | None = None

        self._emit(
            "wait_start",
            kind="pixel",
            image=str(img),
            tolerance=step.tolerance,
            timeout_ms=step.timeout_ms,
        )

        color = self._render_value(step.color, ctx)

        while time.time() <= deadline:
            self._check_panic()
            attempt += 1
            try:
                m = pixel_search_file(img, color=color, region=step.region, tolerance=step.tolerance)
                self._emit_wait_attempt(
                    "pixel",
                    image=str(img),
                    attempt=attempt,
                    dist=m.dist,
                    tolerance=step.tolerance,
                    x=m.x,
                    y=m.y,
                    file=True,
                )
                ctx[step.out_x] = m.x
                ctx[step.out_y] = m.y
                ctx[step.out_dist] = m.dist
                self._emit("wait_end", kind="pixel", ok=True, attempts=attempt, dist=m.dist, x=m.x, y=m.y)
                return
            except Exception as e:
                # Keep last distance if it's a tolerance miss.
                last_dist = getattr(e, "dist", None) if hasattr(e, "dist") else last_dist
                self._emit_wait_attempt(
                    "pixel",
                    image=str(img),
                    attempt=attempt,
                    dist=last_dist,
                    tolerance=step.tolerance,
                    file=True,
                    matched=False,
                )

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(step.max_poll_ms, int(poll * 1.4) + 1) if poll else 0

        self._emit("wait_end", kind="pixel", ok=False, attempts=attempt, dist=last_dist)
        raise TimeoutError(f"WaitForPixelFile timed out after {step.timeout_ms}ms")

    def _exec_ocr_file(self, step: StepOcrReadTextFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        img = root / interpolate(step.image_path, ctx)
        text = ocr_read_text_file(img, lang=step.lang)
        ctx[step.out_var] = text
        self._emit("ocr", image=str(img), chars=len(text))

    def _exec_capture_screenshot(self, step: StepCaptureScreenshot, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        if step.path:
            out = root / interpolate(step.path, ctx)
        else:
            out = root / self.project.settings.log_dir / f"capture_{int(time.time()*1000)}.png"
        out = screenshot_mod.capture(out, region=step.region)
        ctx[step.out_var] = str(out)
        self._emit("screenshot", path=str(out), region=step.region.model_dump() if step.region else None)


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

    def _text_matches(self, text: str, pattern: str, mode: str, *, case_sensitive: bool) -> bool:
        if not case_sensitive:
            text = text.lower()
            pattern = pattern.lower()
        if mode == "contains":
            return pattern in text
        if mode == "regex":
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.search(pattern, text, flags=flags) is not None
        raise ValueError(f"Unknown match mode: {mode}")

    def _exec_image_search(self, step: StepImageSearch, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="image_search")
        cap_region = step.region
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        # If we captured a region, matching coordinates are relative to that capture.
        match = image_search_file(out, needle, region=None, threshold=step.threshold)
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
        )

    def _exec_wait_for_image(self, step: StepWaitForImage, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_image")
        cap_region = step.region
        ctx[step.out_screenshot] = str(out)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0
        last = None

        self._emit(
            "wait_start",
            kind="image",
            needle=str(needle),
            threshold=step.threshold,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
        )

        while time.time() <= deadline:
            self._check_panic()
            attempt += 1
            if step.max_attempts is not None and attempt > step.max_attempts:
                break

            self._capture(out, region=cap_region)
            last = image_search_file(out, needle, region=None, threshold=-1e9)
            self._emit_wait_attempt(
                "image",
                needle=str(needle),
                attempt=attempt,
                score=last.score,
                threshold=step.threshold,
                x=last.x,
                y=last.y,
                screen=True,
            )
            if last.score >= step.threshold:
                x, y = last.x, last.y
                if cap_region is not None:
                    x += cap_region.x
                    y += cap_region.y
                ctx[step.out_x] = x
                ctx[step.out_y] = y
                ctx[step.out_score] = last.score
                ctx[step.out_w] = last.w
                ctx[step.out_h] = last.h
                self._emit(
                    "wait_end",
                    kind="image",
                    ok=True,
                    attempts=attempt,
                    score=last.score,
                    x=x,
                    y=y,
                    w=last.w,
                    h=last.h,
                    screen=True,
                )
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(step.max_poll_ms, int(poll * 1.4) + 1) if poll else 0

        score = last.score if last else None
        self._emit("wait_end", kind="image", ok=False, attempts=attempt, score=score, screen=True)
        raise TimeoutError(f"WaitForImage timed out after {step.timeout_ms}ms (last score={score})")

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
        cap_region = step.region
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
        cap_region = step.region
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
        cap_region = step.region
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
        )

        while time.time() <= deadline:
            self._check_panic()
            attempt += 1
            if step.max_attempts is not None and attempt > step.max_attempts:
                break

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
            poll = min(step.max_poll_ms, int(poll * 1.4) + 1) if poll else 0

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

    def _exec_ocr(self, step: StepOcrReadText, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="ocr")
        cap_region = step.region
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        text = ocr_read_text_file(out, lang=step.lang)
        ctx[step.out_var] = text
        self._emit("ocr", image=str(out), chars=len(text), screen=True, region=cap_region.model_dump() if cap_region else None)

    def _exec_wait_for_text(self, step: StepWaitForText, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="wait_text")
        cap_region = step.region
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)

        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0

        self._emit(
            "wait_start",
            kind="text",
            pattern=pattern,
            match=step.match,
            timeout_ms=step.timeout_ms,
            screen=True,
            region=cap_region.model_dump() if cap_region else None,
        )

        while time.time() <= deadline:
            self._check_panic()
            attempt += 1
            if step.max_attempts is not None and attempt > step.max_attempts:
                break

            self._capture(out, region=cap_region)
            txt = ocr_read_text_file(out, lang=step.lang)
            ctx[step.out_text] = txt
            ok = self._text_matches(txt, pattern, step.match, case_sensitive=step.case_sensitive)
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
            poll = min(step.max_poll_ms, int(poll * 1.4) + 1) if poll else 0

        ctx[step.out_found] = False
        self._emit("wait_end", kind="text", ok=False, attempts=attempt, screen=True)
        raise TimeoutError(f"WaitForText timed out after {step.timeout_ms}ms")

    def _exec_assert_text(self, step: StepAssertText, ctx: dict[str, Any]) -> None:
        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="assert_text")
        cap_region = step.region
        self._capture(out, region=cap_region)
        ctx[step.out_screenshot] = str(out)

        pattern = interpolate(step.pattern, ctx)
        txt = ocr_read_text_file(out, lang=step.lang)
        ctx[step.out_text] = txt

        ok = self._text_matches(txt, pattern, step.match, case_sensitive=step.case_sensitive)
        self._emit("assert_text", ok=ok, match=step.match, screen=True)
        if not ok:
            raise AssertionError(f"AssertText failed ({step.match}): {pattern!r}")

    def _exec_click_needle(self, step: StepClickNeedle, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        needle = root / interpolate(step.needle_path, ctx)

        out = self._resolve_capture_path(step.screenshot_path, ctx, prefix="click_needle")
        cap_region = step.region
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
        )

        while time.time() <= deadline:
            self._check_panic()
            attempt += 1
            if step.max_attempts is not None and attempt > step.max_attempts:
                break

            self._capture(out, region=cap_region)
            last = image_search_file(out, needle, region=None, threshold=-1e9)
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
                    dx, dy = compute_click_offset(meta, click_point_id=step.click_point_id)

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
            poll = min(step.max_poll_ms, int(poll * 1.4) + 1) if poll else 0

        score = last.score if last else None
        self._emit("wait_end", kind="click_needle", ok=False, attempts=attempt, score=score, screen=True)
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

        x = self._as_int(step.x, ctx, field='MouseMove.x') if step.x is not None else None
        y = self._as_int(step.y, ctx, field='MouseMove.y') if step.y is not None else None
        dx = self._as_int(step.dx, ctx, field='MouseMove.dx') if step.dx is not None else None
        dy = self._as_int(step.dy, ctx, field='MouseMove.dy') if step.dy is not None else None
        input_mod.mouse_move(x=x, y=y, dx=dx, dy=dy, relative=step.relative)

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

        self._emit(
            "input",
            kind="mouseclickat",
            x=x,
            y=y,
            button=button,
            dry_run=bool(self.project.settings.dry_run),
        )
        if self.project.settings.dry_run:
            return

        input_mod.mouse_move(x=x, y=y)
        input_mod.mouse_click(button, clearmodifiers=step.clearmodifiers)

    def _exec_mousedrag(self, step: StepMouseDrag, ctx: dict[str, Any]) -> None:
        x1 = self._as_int(step.x1, ctx, field='MouseDrag.x1')
        y1 = self._as_int(step.y1, ctx, field='MouseDrag.y1')
        x2 = self._as_int(step.x2, ctx, field='MouseDrag.x2')
        y2 = self._as_int(step.y2, ctx, field='MouseDrag.y2')
        button = self._as_int(step.button, ctx, field='MouseDrag.button')
        self._emit("input", kind="mousedrag", x1=x1, y1=y1, x2=x2, y2=y2, button=button, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        input_mod.mouse_move(x=x1, y=y1)
        input_mod.mouse_click(button, down=True, clearmodifiers=step.clearmodifiers)
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


    # --- Desktop helpers --------------------------------------------------

    def _exec_notify(self, step: StepNotify, ctx: dict[str, Any]) -> None:
        summary = interpolate(step.summary, ctx)
        body = interpolate(step.body, ctx) if step.body is not None else None
        self._emit("notify", summary=summary, urgency=step.urgency, dry_run=bool(self.project.settings.dry_run))
        if self.project.settings.dry_run:
            return
        notify_mod.send(summary, body=body, urgency=step.urgency)

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

    def _exec_wait_for_clipboard_change(self, step: StepWaitForClipboardChange, ctx: dict[str, Any]) -> None:
        initial = interpolate(step.initial_text, ctx) if step.initial_text is not None else None
        self._emit(
            "wait_start",
            kind="clipboard",
            selection=step.selection,
            timeout_ms=step.timeout_ms,
        )

        def on_attempt(attempt: int, cur: str, changed: bool, helper: str | None = None):
            self._emit_wait_attempt(
                "clipboard",
                attempt=attempt,
                selection=step.selection,
                changed=changed,
                chars=len(cur),
                preview=cur[:120],
                helper=helper,
            )

        txt = watch_mod.wait_for_clipboard_change(
            clipboard_mod.read,
            selection=step.selection,
            initial_text=initial,
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            on_attempt=on_attempt,
        )
        ctx[step.out_text] = txt
        ctx[step.out_changed] = True
        self._emit("wait_end", kind="clipboard", ok=True, selection=step.selection, chars=len(txt))

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
        saved = network_mod.download_file(url, path, headers=headers, timeout_ms=step.timeout_ms, create_parents=step.create_parents, overwrite=step.overwrite)
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

    def _exec_wait_for_new_file(self, step: StepWaitForNewFile, ctx: dict[str, Any]) -> None:
        root = Path(self.project.root_dir)
        directory = root / interpolate(step.directory, ctx)
        pattern = interpolate(step.pattern, ctx)
        self._emit(
            "wait_start",
            kind="new_file",
            directory=str(directory),
            pattern=pattern,
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
            timeout_ms=step.timeout_ms,
            poll_ms=step.poll_ms,
            max_poll_ms=step.max_poll_ms,
            jitter_ms=step.jitter_ms,
            max_attempts=step.max_attempts,
            on_attempt=on_attempt,
        )
        ctx[step.out_path] = str(found)
        ctx[step.out_name] = found.name
        ctx[step.out_size] = found.stat().st_size
        self._emit(
            "wait_end",
            kind="new_file",
            ok=True,
            directory=str(directory),
            pattern=pattern,
            path=str(found),
            size=found.stat().st_size,
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

    def _exec_i3_get_workspaces(self, step: StepI3GetWorkspaces, ctx: dict[str, Any]) -> None:
        i3 = I3Connection()
        ctx[step.out_var] = i3.get_workspaces()
        self._emit("i3_get_workspaces", out_var=step.out_var)

    def _exec_wait_for_window(self, step: StepWaitForWindow, ctx: dict[str, Any]) -> None:
        deadline = time.time() + (step.timeout_ms / 1000.0)
        poll = max(0, step.poll_ms)
        attempt = 0

        self._emit(
            "wait_start",
            kind="window",
            selector=step.selector.model_dump(by_alias=True),
            timeout_ms=step.timeout_ms,
        )

        i3 = I3Connection()

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
                selector=step.selector.model_dump(by_alias=True),
            )
            if m:
                ctx[step.out_var] = m.node
                ctx[step.out_con_id] = m.node.get("id")
                self._emit("wait_end", kind="window", ok=True, attempts=attempt, con_id=m.node.get("id"), workspace=m.workspace)

                if step.focus:
                    con_id = m.node.get("id")
                    if con_id is not None:
                        i3.command(f"[con_id={con_id}] focus")
                        self._emit("i3_focus", con_id=con_id)
                return

            if poll > 0:
                jitter = random.randint(-step.jitter_ms, step.jitter_ms) if step.jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(step.max_poll_ms, int(poll * 1.4) + 1) if poll else 0

        self._emit("wait_end", kind="window", ok=False, attempts=attempt)
        raise TimeoutError(f"WaitForWindow timed out after {step.timeout_ms}ms")

    def _exec_focus_window(self, step: StepFocusWindow, ctx: dict[str, Any]) -> None:
        i3 = I3Connection()
        tree = i3.get_tree()
        m = find_first(tree, step.selector)
        if not m:
            raise RuntimeError(f"FocusWindow: no window matched selector {step.selector.model_dump(by_alias=True)}")
        con_id = m.node.get("id")
        if con_id is None:
            raise RuntimeError("FocusWindow: matched node has no con id")
        i3.command(f"[con_id={con_id}] focus")
        self._emit("i3_focus", con_id=con_id)

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
