from __future__ import annotations

import argparse
import json
import sys
from typing import Callable

from .editor import Editor
from .screen_budget import ScreenBudgetError, checked_screen_dimensions
from .startup import create_editor_runtime, open_initial_buffer
from .workspace_trust import TRUST_STATES


DEFAULT_SCREEN_LINES = 24
DEFAULT_SCREEN_COLS = 80
SCREEN_DUMP_DETAILS = ("compact", "diagnostic")


def _screen_dump_payload(
    ed: Editor,
    *,
    lines: int,
    cols: int,
    detail: str,
) -> dict[str, object]:
    h, w = checked_screen_dimensions(lines, cols, label="screen dump")
    if str(detail) == "diagnostic":
        return dict(ed.screen_model(lines=h, cols=w))
    return dict(ed.screen_contract(lines=h, cols=w))


def _remember_active_cursor(ed: Editor) -> None:
    try:
        ed._remember_cursor_for_buffer(ed.cur())
    except Exception:
        pass


def _print_new_failure_message(ed: Editor, before: int) -> None:
    messages = list(getattr(ed, "messages", []) or [])
    if len(messages) > int(before):
        print(messages[-1])


def _stdin_is_tty() -> bool:
    try:
        return bool(sys.stdin.isatty())
    except Exception:
        return False


def run_headless_repl(
    ed: Editor,
    *,
    input_fn: Callable[[str], str] | None = None,
    stdin_isatty: bool | None = None,
) -> int:
    """Run the inspectable line REPL without bypassing editor quit policy."""

    read_line = input_fn if input_fn is not None else input
    tty = _stdin_is_tty() if stdin_isatty is None else bool(stdin_isatty)

    print(
        "micromax-editor. Headless reference UI.\n"
        "Commands:\n"
        "  :p                 print buffer\n"
        "  :key KEY           simulate key (uses bindings)\n"
        "  :cmd LINE          execute command bar line\n"
        "  :mx CODE           eval micromax\n"
        "  :prompt TEXT       set current prompt text (command/find/topic)\n"
        "  :enter             submit current prompt\n"
        "  :esc               cancel prompt\n"
        "  :msgs              show recent messages\n"
        "  :status            show current status summary\n"
        f"  :screen [L C]      dump compact screen contract JSON (default {DEFAULT_SCREEN_LINES}x{DEFAULT_SCREEN_COLS})\n"
        "  :screen diagnostic [L C]  dump the full internal diagnostic graph\n"
        "  :q                 safe quit (repeat only if the warning is unchanged)\n"
        "  :q!                force quit and discard unsaved buffers\n"
    )

    try:
        while not ed.should_quit:
            if ed.prompt is None:
                prompt = "> "
            else:
                prompt = ">" if ed.prompt.kind == "command" else ("/" if ed.prompt.kind == "find" else "?")
                prompt += " "

            try:
                line = read_line(prompt)
            except EOFError:
                print()
                before = len(ed.messages)
                if ed.exec_command_line("quit"):
                    return 0
                _print_new_failure_message(ed, before)
                # EOF is not an explicit second confirmation. On a terminal,
                # return to the prompt; on exhausted non-interactive input,
                # fail loudly instead of silently claiming a clean exit.
                ed._clear_discard_confirmation()
                if tty:
                    print("EOF did not discard unsaved buffers; use :q or :q! explicitly")
                    continue
                print("EOF refused a clean shutdown because unsaved buffers remain; exiting with status 2")
                return 2

            if not line:
                continue

            if line in {":q", ":q!"}:
                before = len(ed.messages)
                command = "quit!" if line == ":q!" else "quit"
                if ed.exec_command_line(command):
                    return 0
                _print_new_failure_message(ed, before)
                continue

            if line == ":p":
                text = ed.cur().buf.get_text().splitlines()
                for i, ln in enumerate(text, start=1):
                    print(f"{i:4d}  {ln}")
                continue

            if line.startswith(":key "):
                key = line[5:].strip()
                binding = ed.resolve_key_binding(key)
                if binding is None:
                    print(f"showkey: no such binding: {key}")
                else:
                    extra = ""
                    desc = ed.binding_desc(binding)
                    if desc:
                        extra += f"  [desc {desc}]"
                    if binding.mode and binding.mode != "global":
                        extra += f"  [mode {binding.mode}]"
                    if binding.span is not None:
                        extra += f"  [{binding.span.filename}:{binding.span.line}:{binding.span.col}]"
                    ok = ed.dispatch_key(key)
                    print(f"{key} -> {binding.action_spec}  ({'ok' if ok else 'fail'}){extra}")
                continue

            if line.startswith(":cmd "):
                ok = ed.exec_command_line(line[5:])
                print("ok" if ok else "fail")
                continue

            if line.startswith(":mx "):
                try:
                    ed.vm.eval(line[4:], filename="<repl>")
                except Exception as exc:
                    print(exc)
                continue

            if line.startswith(":prompt "):
                if ed.prompt is None:
                    print("(no prompt active)")
                    continue
                ed.set_prompt_text(line[8:])
                continue

            if line == ":enter":
                ok = ed.submit_prompt()
                print("ok" if ok else "fail")
                continue

            if line == ":esc":
                ed.cancel_prompt()
                continue

            if line == ":msgs":
                for message in ed.messages[-10:]:
                    print(message)
                continue

            if line == ":status":
                print(ed.status_summary())
                continue

            if line.startswith(":screen"):
                parts = line.split()
                detail = "compact"
                rest = parts[1:]
                if rest and rest[0] in {"diagnostic", "full"}:
                    detail = "diagnostic"
                    rest = rest[1:]
                try:
                    if not rest:
                        lines, cols = (DEFAULT_SCREEN_LINES, DEFAULT_SCREEN_COLS)
                    elif len(rest) == 2:
                        lines, cols = (int(rest[0]), int(rest[1]))
                    else:
                        raise ValueError
                except ValueError:
                    print("usage: :screen [diagnostic] [LINES COLS]")
                    continue
                try:
                    payload = _screen_dump_payload(
                        ed,
                        lines=lines,
                        cols=cols,
                        detail=detail,
                    )
                except ScreenBudgetError as exc:
                    print(exc)
                    continue
                print(json.dumps(payload, indent=2, sort_keys=True))
                continue

            # If a prompt is active, treat raw input as prompt text.
            if ed.prompt is not None:
                ed.set_prompt_text(line)
                continue

            print(f"repl: no such command: {line}")
    finally:
        _remember_active_cursor(ed)

    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="micromax-editor",
        description="calm, scriptable editor with explicit effects and headless truth",
    )
    ap.add_argument("path", nargs="?", help="file to open")
    ap.add_argument("--help-doc", dest="help_doc", help="open a docs markdown file/topic in a protected help buffer")
    ap.add_argument(
        "--plugins",
        default=None,
        help="plugin root directory (default: ./plugins, then bundled installed plugins)",
    )
    ap.add_argument(
        "--trust",
        choices=TRUST_STATES,
        default=None,
        help="startup trust state: trusted loads plugins/user init; restricted scans plugins only",
    )
    ap.add_argument("--tui", action="store_true", help="run the reference curses TUI")
    ap.add_argument(
        "--dump-screen",
        metavar=("LINES", "COLS"),
        nargs=2,
        type=int,
        help="print the compact micromax.screen.v1 contract as JSON and exit",
    )
    ap.add_argument(
        "--dump-screen-detail",
        choices=SCREEN_DUMP_DETAILS,
        default=None,
        help="screen dump detail: compact (default) or full internal diagnostic graph",
    )
    args = ap.parse_args(argv)

    if args.path and args.help_doc:
        ap.error("pass either a path or --help-doc, not both")
    if args.dump_screen is None and args.dump_screen_detail is not None:
        ap.error("--dump-screen-detail requires --dump-screen")
    if args.dump_screen is not None:
        try:
            checked_screen_dimensions(
                args.dump_screen[0],
                args.dump_screen[1],
                label="screen dump",
            )
        except ScreenBudgetError as exc:
            ap.error(str(exc))

    if args.tui and args.dump_screen is None:
        from .tui import run_tui

        return int(
            run_tui(
                args.path,
                help_doc=args.help_doc,
                plugins_root=args.plugins,
                workspace_trust=args.trust,
            )
        )

    runtime = create_editor_runtime(plugins_root=args.plugins, workspace_trust=args.trust)
    ed = runtime.editor
    initial = open_initial_buffer(
        ed,
        path=args.path,
        help_doc=args.help_doc,
        allow_help_outside_root=True,
    )
    if initial.message:
        print(initial.message, file=sys.stderr)

    if args.dump_screen is not None:
        lines, cols = (int(args.dump_screen[0]), int(args.dump_screen[1]))
        detail = str(args.dump_screen_detail or "compact")
        print(
            json.dumps(
                _screen_dump_payload(
                    ed,
                    lines=lines,
                    cols=cols,
                    detail=detail,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0 if initial.ok else 1

    return run_headless_repl(ed)


if __name__ == "__main__":
    raise SystemExit(main())
