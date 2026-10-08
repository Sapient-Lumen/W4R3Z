from __future__ import annotations

import argparse

from .editor import Editor
from .micromax_bridge import install_editor_hostcalls
from .plugins import PluginManager


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="micromax-editor", description="micromax micro-esque editor prototype")
    ap.add_argument("path", nargs="?", help="file to open")
    ap.add_argument("--plugins", default="plugins", help="plugin root directory")
    ap.add_argument("--tui", action="store_true", help="run the minimal curses TUI")
    args = ap.parse_args(argv)

    ed = Editor()
    install_editor_hostcalls(ed)

    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.load_tree(args.plugins)

    # Non-fatal plugin load errors are recorded on the manager.
    for name, err in getattr(pm, "load_errors", []):
        ed.message(f"plugin load failed: {name}: {err}")

    # User rc/init (best-effort). Loaded after plugins so it can override.
    ed.load_user_init()
    # Refresh capability advertisement now that init may have changed options.
    try:
        ed.refresh_capabilities()
    except Exception:
        pass
    # Optional recent-file persistence (best-effort; gated by recent.persist + cap.persist options).
    try:
        ed.load_recent_files()
    except Exception:
        pass
    # Optional prompt-history persistence (best-effort; gated by history.persist + cap.persist).
    try:
        ed.load_prompt_history()
    except Exception:
        pass
    # Optional savecursor persistence (best-effort; gated by savecursor + cap.persist).
    try:
        ed.load_saved_cursors()
    except Exception:
        pass


    if args.path:
        ed.open_file(args.path)
    else:
        ed.new_buffer("*scratch*", "")

    if args.tui:
        from .tui import run_tui
        return int(run_tui(args.path, plugins_root=args.plugins))

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
                print(f"(unbound) {key}")
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

        # If a prompt is active, treat raw input as prompt text.
        if ed.prompt is not None:
            ed.set_prompt_text(line)
            continue

        print("unknown command")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
