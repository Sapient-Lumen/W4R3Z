from __future__ import annotations

import argparse
import json
import sys

from .startup import create_editor_runtime
from .workspace_trust import TRUST_STATES


DEFAULT_SCREEN_LINES = 24
DEFAULT_SCREEN_COLS = 80


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="micromax-editor", description="micromax micro-esque editor prototype")
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
    ap.add_argument("--tui", action="store_true", help="run the minimal curses TUI")
    ap.add_argument(
        "--dump-screen",
        metavar=("LINES", "COLS"),
        nargs=2,
        type=int,
        help="print screen_model(lines, cols) as JSON and exit",
    )
    args = ap.parse_args(argv)

    if args.path and args.help_doc:
        ap.error("pass either a path or --help-doc, not both")

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

    if args.help_doc:
        if not ed.open_help_doc(args.help_doc, allow_outside_root=True):
            print(f"help: could not open {args.help_doc}", file=sys.stderr)
            return 1
    elif args.path:
        ed.open_file(args.path)
    else:
        ed.new_buffer("*scratch*", "")

    if args.dump_screen is not None:
        lines, cols = (int(args.dump_screen[0]), int(args.dump_screen[1]))
        print(json.dumps(ed.screen_model(lines=lines, cols=cols), indent=2, sort_keys=True))
        return 0

    print(
        "micromax-editor (prototype). Headless REPL UI.\n"
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
        f"  :screen [L C]      dump shared screen model JSON (default {DEFAULT_SCREEN_LINES}x{DEFAULT_SCREEN_COLS})\n"
        "  :q                 quit\n"
    )

    while True:
        if ed.prompt is None:
            prompt = "> "
        else:
            prompt = ">" if ed.prompt.kind == "command" else ("/" if ed.prompt.kind == "find" else "?")
            prompt += " "

        try:
            line = input(prompt)
        except EOFError:
            print()
            try:
                ed._remember_cursor_for_buffer(ed.cur())
            except Exception:
                pass
            break

        if not line:
            continue

        if line == ":q":
            try:
                ed._remember_cursor_for_buffer(ed.cur())
            except Exception:
                pass
            break

        if line == ":p":
            text = ed.cur().buf.get_text().splitlines()
            for i, ln in enumerate(text, start=1):
                print(f"{i:4d}  {ln}")
            continue

        if line.startswith(":key "):
            key = line[5:].strip()
            b = ed.resolve_key_binding(key)
            if b is None:
                print(f"showkey: no such binding: {key}")
            else:
                extra = ""
                desc = ed.binding_desc(b)
                if desc:
                    extra += f"  [desc {desc}]"
                if b.mode and b.mode != "global":
                    extra += f"  [mode {b.mode}]"
                if b.span is not None:
                    extra += f"  [{b.span.filename}:{b.span.line}:{b.span.col}]"
                ok = ed.dispatch_key(key)
                print(f"{key} -> {b.action_spec}  ({'ok' if ok else 'fail'}){extra}")
            continue

        if line.startswith(":cmd "):
            ok = ed.exec_command_line(line[5:])
            print("ok" if ok else "fail")
            continue

        if line.startswith(":mx "):
            try:
                ed.vm.eval(line[4:], filename="<repl>")
            except Exception as e:
                print(e)
            continue

        if line.startswith(":prompt "):
            if ed.prompt is None:
                print("(no prompt active)")
                continue
            text = line[8:]
            ed.set_prompt_text(text)
            continue

        if line == ":enter":
            ok = ed.submit_prompt()
            print("ok" if ok else "fail")
            continue

        if line == ":esc":
            ed.cancel_prompt()
            continue

        if line == ":msgs":
            for m in ed.messages[-10:]:
                print(m)
            continue

        if line == ":status":
            print(ed.status_summary())
            continue

        if line.startswith(":screen"):
            parts = line.split()
            try:
                if len(parts) == 1:
                    lines, cols = (DEFAULT_SCREEN_LINES, DEFAULT_SCREEN_COLS)
                elif len(parts) == 3:
                    lines, cols = (int(parts[1]), int(parts[2]))
                else:
                    raise ValueError
            except ValueError:
                print("usage: :screen [LINES COLS]")
                continue
            print(json.dumps(ed.screen_model(lines=lines, cols=cols), indent=2, sort_keys=True))
            continue

        # If a prompt is active, treat raw input as prompt text.
        if ed.prompt is not None:
            ed.set_prompt_text(line)
            continue

        print(f"repl: no such command: {line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
