from __future__ import annotations

import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from vhk.core.clipboard_watchers import run_clipboard_watcher
from vhk.core.models import I3WindowSelector
from vhk.core.panic import PanicConfig, clear_panic, set_panic
from vhk.core.runner import Runner
from vhk.project.bundle import bundle_project
from vhk.project.loader import load_project
from vhk.system.clipboard import choose_backend as clipboard_backend
from vhk.system.dialogs import choose_dialog_backend
from vhk.system.input import choose_keyboard_backend, choose_pointer_backend
from vhk.system.cursor import choose_backend as cursor_backend
from vhk.system.notify import choose_backend as notify_backend
from vhk.system.region_select import select_region
from vhk.system.screenshot import choose_backend as screenshot_backend
from vhk.system.session import detect_backend
from vhk.vision.assets import load_needle
from vhk.vision.ocr import tesseract_available

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


def _escape_i3_str(s: str) -> str:
    # i3 criteria strings are quoted; escape backslash + double quotes.
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _selector_to_i3_criteria(sel: I3WindowSelector) -> str:
    """Convert a selector to i3's criteria syntax.

    Notes
    -----
    i3 criteria such as class/instance/title are regular expressions (PCRE).
    We keep this conservative: only fields that cleanly map to criteria are
    emitted.
    """

    parts: list[str] = []
    if sel.wm_class:
        parts.append(f'class="{_escape_i3_str(sel.wm_class)}"')
    if sel.instance:
        parts.append(f'instance="{_escape_i3_str(sel.instance)}"')
    if sel.title:
        parts.append(f'title="{_escape_i3_str(sel.title)}"')
    # sway native windows use app_id.
    if getattr(sel, "app_id", None):
        parts.append(f'app_id="{_escape_i3_str(getattr(sel, "app_id"))}"')
    if not parts:
        return ""
    return "[" + " ".join(parts) + "]"


def _selector_to_criteria(sel: I3WindowSelector, *, wm: str) -> str:
    # i3 doesn't understand app_id criteria; sway does.
    if wm == "i3":
        sel2 = sel.model_copy()
        sel2.app_id = None  # type: ignore[attr-defined]
        return _selector_to_i3_criteria(sel2)
    return _selector_to_i3_criteria(sel)


def _default_wm() -> str:
    # If we're on a Wayland session, users are probably on sway-like configs.
    return "sway" if detect_backend() == "wayland" else "i3"


@app.command()
def run(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    macro: str = typer.Argument(..., help="Macro name to run"),
    vars_json: str | None = typer.Option(None, "--vars", help="Initial vars as JSON"),
    step: bool = typer.Option(False, "--step", help="Interactive step-through (press Enter per step)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Override project settings: do not execute side effects"),
):
    """Run a macro from a project folder."""

    project = load_project(project_dir)
    if dry_run:
        project.settings.dry_run = True
    if macro not in project.macros:
        raise typer.BadParameter(f"Unknown macro '{macro}'. Available: {', '.join(project.macros.keys())}")

    initial_vars = {}
    if vars_json:
        initial_vars = json.loads(vars_json)

    runner = Runner(project=project, console=console, step_mode=step)
    result = runner.run(macro_name=macro, initial_vars=initial_vars)
    if result.event_log:
        console.print(f"[dim]Event log:[/dim] {result.event_log}")
    if not result.ok:
        console.print(f"[red]Macro failed:[/red] {result.error}")
        raise typer.Exit(code=1)


@app.command()
def list_macros(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
):
    """List macros in a project."""

    project = load_project(project_dir)
    for name in sorted(project.macros.keys()):
        console.print(name)


@app.command()
def list_watchers(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
):
    """List clipboard watchers defined in project.yaml."""

    project = load_project(project_dir)
    if not project.clipboard_watchers:
        console.print("(no clipboard watchers)")
        raise typer.Exit(code=0)

    table = Table(title="VHK clipboard watchers")
    table.add_column("Name")
    table.add_column("Selection")
    table.add_column("Pattern")
    table.add_column("Macro")
    table.add_column("Enabled")

    for watcher in project.clipboard_watchers:
        table.add_row(
            watcher.name,
            watcher.selection,
            watcher.pattern or "(any)",
            watcher.macro,
            "yes" if watcher.enabled else "no",
        )
    console.print(table)


@app.command()
def watch_clipboard(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    watcher: str = typer.Argument(..., help="Clipboard watcher name from project.yaml"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after this many clipboard-change events (useful for testing)"),
):
    """Run a project-defined clipboard watcher loop."""

    project = load_project(project_dir)
    try:
        stats = run_clipboard_watcher(project, watcher, console=console, max_events=max_events)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped clipboard watcher.[/yellow]")
        raise typer.Exit(code=130)

    console.print(
        f"watcher={stats.watcher} events={stats.events_seen} runs={stats.macro_runs} "
        f"skipped_duplicates={stats.skipped_duplicates} skipped_nonmatching={stats.skipped_nonmatching} failures={stats.macro_failures}"
    )


@app.command()
def gen_i3_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
):
    """Generate i3 bindsym lines from project.yaml bindings."""

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    text = _generate_wm_bindings(project_dir, project.name, project.bindings, wm="i3")
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote i3 config snippet: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


def _generate_wm_bindings(project_dir: Path, project_name: str, bindings, *, wm: str) -> str:
    lines: list[str] = []
    lines.append(f"# VHK {wm} bindings for project: {project_name}")
    lines.append(f"# Add these lines to your {wm} config.")
    lines.append("# Uses `bindsym --release` to avoid running macros while the keyboard is grabbed.")

    if not bindings:
        lines.append("# (No bindings defined. Add a 'bindings:' list to project.yaml.)")

    for b in bindings:
        args = ["vhk", "run", str(project_dir), b.macro]
        if b.vars:
            args += ["--vars", json.dumps(b.vars)]
        cmd = " ".join(shlex.quote(a) for a in args)
        desc = f"  # {b.description}" if b.description else ""
        criteria = _selector_to_criteria(b.when, wm=wm) + " " if b.when else ""

        if wm == "i3":
            lines.append(f"bindsym --release {b.keys} {criteria}exec --no-startup-id {cmd}{desc}")
        else:
            # sway has no --no-startup-id.
            lines.append(f"bindsym --release {b.keys} {criteria}exec {cmd}{desc}")

    return "\n".join(lines) + "\n"


@app.command()
def gen_wm_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    wm: str = typer.Option("auto", "--wm", help="Target window manager: auto, i3, sway"),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
):
    """Generate bindsym lines for i3 or sway.

    - i3: uses `exec --no-startup-id`
    - sway: uses `exec` (no --no-startup-id)
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)
    wm2 = wm.strip().lower()
    if wm2 == "auto":
        wm2 = _default_wm()
    if wm2 not in {"i3", "sway"}:
        raise typer.BadParameter("wm must be one of: auto, i3, sway")

    text = _generate_wm_bindings(project_dir, project.name, project.bindings, wm=wm2)
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote {wm2} config snippet: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


@app.command()
def bundle(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path = typer.Argument(..., help="Output .zip path"),
):
    """Create a shareable bundle (zip) for the project folder."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_project(project_dir, out_path)
    console.print(f"Wrote bundle: [bold]{out_path}[/bold]")


@app.command()
def select_region_cmd(as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON")):
    """Interactively select a rectangle (requires slop)."""

    r = select_region()
    if as_json:
        sys.stdout.write(json.dumps(r.model_dump()) + "\n")
    else:
        sys.stdout.write(f"{r.w}x{r.h}+{r.x}+{r.y}\n")


@app.command()
def capture_needle(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    name: str = typer.Argument(..., help="Needle name (filename stem)"),
    out_dir: str = typer.Option("assets/needles", "--out-dir", help="Relative dir inside project"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags"),
    with_click_point: bool = typer.Option(True, "--click-point/--no-click-point"),
):
    """Capture a needle image + openQA-style JSON metadata.

    Uses slop for selection and maim/import for screenshot.
    """

    project_dir = project_dir.resolve()
    rel = Path(out_dir)
    out_path = (project_dir / rel / f"{name}.png").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    r = select_region()

    # Capture the region as the needle image.
    from vhk.system.screenshot import capture as capture_ss

    capture_ss(out_path, region=r)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    meta = {
        "tags": tag_list,
        "area": [
            {
                "type": "match",
                "xpos": 0,
                "ypos": 0,
                "width": r.w,
                "height": r.h,
            }
        ],
    }

    if with_click_point:
        meta["area"][0]["click_point"] = {"xpos": r.w // 2, "ypos": r.h // 2}

    out_json = out_path.with_suffix(".json")
    out_json.write_text(json.dumps(meta, indent=2) + "\n")

    console.print(f"Wrote needle: [bold]{out_path}[/bold]")
    console.print(f"Wrote metadata: [bold]{out_json}[/bold]")




@app.command()
def capture_baseline(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    name: str = typer.Argument(..., help="Baseline name (filename stem)"),
    out_dir: str = typer.Option("assets/baselines", "--out-dir", help="Relative dir inside project"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags"),
    with_stub_json: bool = typer.Option(True, "--json/--no-json", help="Write openQA-style sidecar JSON stub"),
):
    """Capture a visual baseline image for VisualAssert/Verify.

    The optional sidecar JSON uses the same openQA-style shape as needles, so you
    can add match/exclude areas later for more stable comparisons.
    """

    project_dir = project_dir.resolve()
    rel = Path(out_dir)
    out_path = (project_dir / rel / f"{name}.png").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    r = select_region()

    from vhk.system.screenshot import capture as capture_ss

    capture_ss(out_path, region=r)

    console.print(f"Wrote baseline: [bold]{out_path}[/bold]")

    if with_stub_json:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        meta = {
            "tags": tag_list,
            "area": [
                {
                    "type": "match",
                    "xpos": 0,
                    "ypos": 0,
                    "width": r.w,
                    "height": r.h,
                }
            ],
        }
        out_json = out_path.with_suffix(".json")
        out_json.write_text(json.dumps(meta, indent=2) + "\n")
        console.print(f"Wrote metadata stub: [bold]{out_json}[/bold]")

@app.command()
def needle_info(png_path: Path = typer.Argument(..., exists=True, dir_okay=False, help="Needle png path")):
    """Print needle metadata (openQA-style .json next to the .png)."""

    needle = load_needle(png_path)
    table = Table(title=f"Needle: {needle.name}")
    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Image", str(needle.image_path))
    table.add_row("Tags", ", ".join(needle.tags) if needle.tags else "(none)")
    table.add_row("Areas", str(len(needle.areas)))

    for i, a in enumerate(needle.areas):
        cp = ""
        if a.click_point:
            cid = f" id={a.click_point.id}" if a.click_point.id else ""
            cp = f" click=({a.click_point.xpos},{a.click_point.ypos}){cid}"
        mt = f" match={a.match}%" if a.match is not None else ""
        table.add_row(f"area[{i}]", f"{a.type}{mt} {a.width}x{a.height}+{a.xpos}+{a.ypos}{cp}")

    console.print(table)


@app.command()
def panic(project_dir: Path | None = typer.Option(None, "--project", help="Use project settings (panic_file)")):
    """Create the global panic file to stop long-running macros ASAP."""

    if project_dir:
        project = load_project(project_dir)
        cfg = PanicConfig(panic_file=project.settings.panic_file)
    else:
        cfg = PanicConfig()

    p = set_panic(cfg)
    console.print(f"[yellow]PANIC enabled[/yellow]: {p}")


@app.command()
def unpanic(project_dir: Path | None = typer.Option(None, "--project", help="Use project settings (panic_file)")):
    """Remove the global panic file."""

    if project_dir:
        project = load_project(project_dir)
        cfg = PanicConfig(panic_file=project.settings.panic_file)
    else:
        cfg = PanicConfig()

    clear_panic(cfg)
    console.print("[green]PANIC cleared[/green]")


@app.command()
def doctor(as_json: bool = typer.Option(False, "--json", help="Print machine-readable diagnostics")):
    """Print environment diagnostics (lightweight).

    This is our CLI placeholder for the eventual Studio "Modules" page: what
    helpers are installed, what capabilities they provide, and quick version info.
    """

    ss = screenshot_backend()
    cb = clipboard_backend()
    nb = notify_backend()
    kb = choose_keyboard_backend()
    pb = choose_pointer_backend()
    db = choose_dialog_backend()
    cur = cursor_backend()

    modules = {
        "screenshot": {
            "backend": ss.name if ss else None,
            "version": (
                _tool_version("grim", "--version") if (ss and ss.name == "grim")
                else (_tool_version("maim", "--version") if (ss and ss.name == "maim")
                else (_tool_version("scrot", "--version") if (ss and ss.name == "scrot")
                else (_tool_version("import", "-version") if (ss and ss.name == "import")
                else ((str(Path(ss.converter_exe).name) + " + " + _tool_version(Path(ss.converter_exe).name, "--version").splitlines()[0]) if (ss and ss.name == "xwd+convert" and ss.converter_exe) else "(not found)"))))),
            "available": bool(ss),
        },
        "cursor": {
            "backend": cur.name if cur else None,
            "version": _tool_version("unclutter", "--version") if (cur and cur.name == "unclutter" and shutil.which("unclutter")) else (_tool_version("unclutter-xfixes", "--version") if (cur and cur.name == "unclutter" and shutil.which("unclutter-xfixes")) else (_tool_version("xbanish", "-V") if (cur and cur.name == "xbanish") else "(not found)")),
            "available": bool(cur),
        },
        "clipboard": {
            "backend": cb.name if cb else None,
            "version": _tool_version("wl-paste", "--version") if (cb and cb.name == "wl-clipboard") else (_tool_version("xclip", "-version") if (cb and cb.name == "xclip") else _tool_version("xsel", "--version")),
            "available": bool(cb),
        },
        "notify": {
            "backend": nb.name if nb else None,
            "version": _tool_version("dunstify", "--version") if shutil.which("dunstify") else _tool_version("notify-send", "--version"),
            "available": bool(nb),
        },
        "keyboard": {
            "backend": kb.name if kb else None,
            "version": _tool_version("wtype", "--version") if (kb and kb.name == "wtype") else (_tool_version("xdotool", "-v") if (kb and kb.name == "xdotool") else _tool_version("ydotool", "--version")),
            "available": bool(kb),
        },
        "pointer": {
            "backend": pb.name if pb else None,
            "version": _tool_version("xdotool", "-v") if (pb and pb.name == "xdotool") else _tool_version("ydotool", "--version"),
            "available": bool(pb),
        },
        "dialogs": {
            "backend": db.name if db else None,
            "version": _tool_version("zenity", "--version") if (db and db.name == "zenity") else (_tool_version("yad", "--version") if (db and db.name == "yad") else (_tool_version("kdialog", "--version") if (db and db.name == "kdialog") else (_tool_version("dialog", "--version") if (db and db.name == "dialog") else "(console)"))),
            "available": bool(db),
        },
    }

    payload = {
        "python": sys.version.split()[0],
        "platform": f"{platform.system()} {platform.release()}",
        "display": os.environ.get("DISPLAY"),
        "xauthority": os.environ.get("XAUTHORITY"),
        "desktop_backend": detect_backend(),
        "tesseract": {"available": bool(tesseract_available()), "version": _tool_version("tesseract", "--version")},
        "modules": modules,
        "helpers": {
            "slop": shutil.which("slop"),
            "slurp": shutil.which("slurp"),
            "keyd": shutil.which("keyd"),
            "clipnotify": shutil.which("clipnotify"),
            "autocutsel": shutil.which("autocutsel"),
            "xbanish": shutil.which("xbanish"),
            "unclutter": shutil.which("unclutter") or shutil.which("unclutter-xfixes"),
            "scrot": shutil.which("scrot"),
            "xwd": shutil.which("xwd"),
            "magick": shutil.which("magick"),
            "convert": shutil.which("convert"),
            "copyq": shutil.which("copyq"),
            "clipmenud": shutil.which("clipmenud"),
            "cliphist": shutil.which("cliphist"),
            "inotifywait": shutil.which("inotifywait"),
            "xvkbd": shutil.which("xvkbd"),
            "xdg_open": shutil.which("xdg-open"),
            "xdg_email": shutil.which("xdg-email"),
            "zenity": shutil.which("zenity"),
            "yad": shutil.which("yad"),
            "kdialog": shutil.which("kdialog"),
            "dialog": shutil.which("dialog"),
            "i3": shutil.which("i3"),
            "sway": shutil.which("sway"),
        },
        "env": {
            "I3SOCK": os.environ.get("I3SOCK"),
            "SWAYSOCK": os.environ.get("SWAYSOCK"),
            "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR"),
        },
    }

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return

    table = Table(title="VHK doctor")
    table.add_column("Check")
    table.add_column("Result")

    table.add_row("Python", payload["python"])
    table.add_row("Platform", payload["platform"])
    table.add_row("DISPLAY", payload["display"] or "(not set)")
    table.add_row("XAUTHORITY", payload["xauthority"] or "(not set)")
    table.add_row("Desktop backend", payload["desktop_backend"])
    table.add_row("Tesseract", payload["tesseract"]["version"] if payload["tesseract"]["available"] else "MISSING")
    table.add_row("Screenshot module", f"{modules['screenshot']['backend'] or 'MISSING'} | {modules['screenshot']['version']}")
    table.add_row("Cursor module", f"{modules['cursor']['backend'] or 'MISSING'} | {modules['cursor']['version']}")
    table.add_row("Clipboard module", f"{modules['clipboard']['backend'] or 'MISSING'} | {modules['clipboard']['version']}")
    table.add_row("Notify module", f"{modules['notify']['backend'] or 'MISSING'} | {modules['notify']['version']}")
    table.add_row("Keyboard module", f"{modules['keyboard']['backend'] or 'MISSING'} | {modules['keyboard']['version']}")
    table.add_row("Pointer module", f"{modules['pointer']['backend'] or 'MISSING'} | {modules['pointer']['version']}")
    table.add_row("Dialog module", f"{modules['dialogs']['backend'] or 'MISSING'} | {modules['dialogs']['version']}")
    table.add_row("clipnotify", payload['helpers']['clipnotify'] or "(not found)")
    table.add_row("autocutsel", payload['helpers']['autocutsel'] or "(not found)")
    table.add_row("xbanish", payload['helpers']['xbanish'] or "(not found)")
    table.add_row("unclutter", payload['helpers']['unclutter'] or "(not found)")
    table.add_row("scrot", payload['helpers']['scrot'] or "(not found)")
    table.add_row("xwd", payload['helpers']['xwd'] or "(not found)")
    table.add_row("magick", payload['helpers']['magick'] or "(not found)")
    table.add_row("convert", payload['helpers']['convert'] or "(not found)")
    table.add_row("CopyQ", payload['helpers']['copyq'] or "(not found)")
    table.add_row("clipmenud", payload['helpers']['clipmenud'] or "(not found)")
    table.add_row("cliphist", payload['helpers']['cliphist'] or "(not found)")
    table.add_row("inotifywait", payload['helpers']['inotifywait'] or "(not found)")
    table.add_row("xvkbd", payload['helpers']['xvkbd'] or "(not found)")
    table.add_row("xdg-open", payload['helpers']['xdg_open'] or "(not found)")
    table.add_row("xdg-email", payload['helpers']['xdg_email'] or "(not found)")
    table.add_row("zenity", payload['helpers']['zenity'] or "(not found)")
    table.add_row("yad", payload['helpers']['yad'] or "(not found)")
    table.add_row("kdialog", payload['helpers']['kdialog'] or "(not found)")
    table.add_row("dialog", payload['helpers']['dialog'] or "(not found)")
    table.add_row("slop", payload['helpers']['slop'] or "(not found)")
    table.add_row("slurp", payload['helpers']['slurp'] or "(not found)")
    table.add_row("keyd", payload['helpers']['keyd'] or "(not found)")
    table.add_row("I3SOCK env", payload['env']['I3SOCK'] or "(not set)")
    table.add_row("SWAYSOCK env", payload['env']['SWAYSOCK'] or "(not set)")
    table.add_row("XDG_RUNTIME_DIR", payload['env']['XDG_RUNTIME_DIR'] or "(not set)")
    console.print(table)


@app.command()
def render(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    macro: str = typer.Argument(..., help="Macro name to render"),
):
    """Render a readable "script view" for a macro.

    This is intentionally *not* a full free-form editor; the goal is a stable,
    round-trippable view that matches the workflow graph.
    """

    project = load_project(project_dir)
    if macro not in project.macros:
        raise typer.BadParameter(f"Unknown macro '{macro}'. Available: {', '.join(project.macros.keys())}")

    m = project.macros[macro]

    def _render_steps(steps, indent: int = 0) -> list[str]:
        out: list[str] = []
        pad = "  " * indent
        for s in steps:
            if not s.enabled:
                out.append(pad + f"# (disabled) {s.type}")
                continue
            if s.comment:
                out.append(pad + f"# {s.comment}")
            if s.type == "If":
                cond = s.condition
                out.append(pad + f"if {cond}:")
                out.extend(_render_steps(s.then_steps, indent + 1))
                if s.else_steps:
                    out.append(pad + "else:")
                    out.extend(_render_steps(s.else_steps, indent + 1))
                continue
            if s.type == "While":
                out.append(pad + f"while {s.condition}:")
                out.extend(_render_steps(s.steps, indent + 1))
                continue
            if s.type == "Try":
                out.append(pad + "try:")
                out.extend(_render_steps(s.steps, indent + 1))
                if s.catch_steps:
                    extra = f" /{s.catch_pattern}/" if s.catch_pattern else ""
                    out.append(pad + f"catch{extra}:")
                    out.extend(_render_steps(s.catch_steps, indent + 1))
                if s.finally_steps:
                    out.append(pad + "finally:")
                    out.extend(_render_steps(s.finally_steps, indent + 1))
                continue

            # Compact one-liners for the common steps.
            d = s.model_dump(exclude={"enabled", "comment", "delay_ms", "repeat", "type", "retry_count", "retry_delay_ms", "retry_backoff", "continue_on_error"})
            # Make it pleasant to read.
            if s.type == "SetVar":
                out.append(pad + f"set {d['name']} = {d['value']!r}")
            elif s.type == "RunShell":
                out.append(pad + f"shell {d['command']!r}")
            elif s.type == "Key":
                out.append(pad + f"key {d['keys']!r}")
            elif s.type == "ResetModifiers":
                out.append(pad + "ResetModifiers")
            elif s.type == "TypeText":
                extra = []
                if d.get('backend') and d.get('backend') != 'auto':
                    extra.append(f"backend={d['backend']}")
                if d.get('paste_shortcut') and d.get('paste_shortcut') != 'auto':
                    extra.append(f"paste={d['paste_shortcut']}")
                suffix = (" " + " ".join(extra)) if extra else ""
                out.append(pad + f"type {d['text']!r}{suffix}")
            elif s.type in ("ImageSearchFile", "WaitForImageFile"):
                out.append(pad + f"{s.type} needle={d['needle_path']!r} hay={d.get('haystack_path')!r} thr={d.get('threshold')}")
            elif s.type in ("VisualAssert", "VisualVerify"):
                out.append(pad + f"{s.type} baseline={d['baseline_path']!r} max_pixels={d.get('max_changed_pixels')} max_ratio={d.get('max_change_ratio')}")
            elif s.type == "WaitForRegionChange":
                out.append(pad + f"WaitForRegionChange baseline={d.get('baseline_path')!r} min_pixels={d.get('min_changed_pixels')} min_ratio={d.get('min_change_ratio')}")
            elif s.type in ("WaitForWindow", "FocusWindow"):
                out.append(pad + f"{s.type} {d['selector']}")
            elif s.type == "WaitForFile":
                out.append(pad + f"WaitForFile path={d['path']!r} when={d['condition']!r}")
            elif s.type == "WaitForNewFile":
                out.append(pad + f"WaitForNewFile dir={d['directory']!r} pattern={d['pattern']!r}")
            elif s.type == "WaitForClipboardChange":
                out.append(pad + f"WaitForClipboardChange selection={d['selection']!r}")
            elif s.type == "PasteClipboard":
                out.append(pad + f"PasteClipboard selection={d['selection']!r}")
            elif s.type == "OpenUrl":
                out.append(pad + f"OpenUrl {d['url']!r}")
            elif s.type == "ComposeEmail":
                out.append(pad + f"ComposeEmail to={d['to']!r} subject={d.get('subject')!r}")
            elif s.type == "HttpRequest":
                out.append(pad + f"HttpRequest {d['method']} {d['url']!r}")
            elif s.type == "DownloadFile":
                out.append(pad + f"DownloadFile {d['url']!r} -> {d['path']!r}")
            elif s.type == "ShowMessage":
                out.append(pad + f"ShowMessage level={d['level']!r} text={d['text']!r}")
            elif s.type == "AskYesNo":
                out.append(pad + f"AskYesNo {d['text']!r} -> {d['out_var']}")
            elif s.type == "InputBox":
                out.append(pad + f"InputBox {d['prompt']!r} -> {d['out_var']}")
            elif s.type == "ChooseFromList":
                out.append(pad + f"ChooseFromList {d['items_expr']} -> {d['out_var']}")
            elif s.type == "StartProcess":
                out.append(pad + f"StartProcess {d['command']!r} -> {d['out_pid']}")
            elif s.type == "WaitForProcessExit":
                out.append(pad + f"WaitForProcessExit pid={d['pid']!r}")
            elif s.type == "KillProcess":
                out.append(pad + f"KillProcess pid={d['pid']!r} signal={d['signal']!r}")
            elif s.type == "ForEach":
                out.append(pad + f"for {d['item_var']} in {d['items_expr']}:")
                out.extend(_render_steps(s.steps, indent + 1))
                continue
            elif s.type == "Break":
                out.append(pad + "break")
            elif s.type == "Continue":
                out.append(pad + "continue")
            elif s.type == "Return":
                out.append(pad + (f"return {d['value_expr']}" if d.get('value_expr') is not None else "return"))
            elif s.type == "ReadCsv":
                out.append(pad + f"ReadCsv {d['path']!r} -> {d['out_var']}")
            elif s.type == "WriteCsv":
                out.append(pad + f"WriteCsv {d['path']!r} rows={d['rows_expr']}")
            elif s.type == "ReadJson":
                out.append(pad + f"ReadJson {d['path']!r} -> {d['out_var']}")
            elif s.type == "WriteJson":
                out.append(pad + f"WriteJson {d['path']!r} value={d['value_expr']}")
            elif s.type == "RegexReplace":
                out.append(pad + f"RegexReplace /{d['pattern']}/ -> {d['out_var']}")
            elif s.type == "TrimText":
                out.append(pad + f"TrimText mode={d['mode']!r} -> {d['out_var']}")
            elif s.type == "SplitText":
                out.append(pad + f"SplitText sep={d.get('sep')!r} -> {d['out_var']}")
            elif s.type == "JoinText":
                out.append(pad + f"JoinText {d['items_expr']} -> {d['out_var']}")
            elif s.type == "ReadFile":
                out.append(pad + f"ReadFile {d['path']!r} -> {d['out_var']}")
            elif s.type in ("WriteFile", "AppendFile"):
                out.append(pad + f"{s.type} {d['path']!r}")
            elif s.type == "ListDirectory":
                out.append(pad + f"ListDirectory {d['path']!r} pattern={d.get('pattern')!r}")
            elif s.type == "MouseDrag":
                out.append(pad + f"MouseDrag ({d['x1']},{d['y1']}) -> ({d['x2']},{d['y2']})")
            elif s.type == "MouseWheel":
                out.append(pad + f"MouseWheel clicks={d['clicks']} axis={d['axis']!r}")
            elif s.type == "CursorHide":
                out.append(pad + "CursorHide")
            elif s.type == "CursorShow":
                out.append(pad + "CursorShow")
            else:
                out.append(pad + f"{s.type} {json.dumps(d, ensure_ascii=False)}")

        return out

    sys.stdout.write(f"# Macro: {m.name}\n")
    sys.stdout.write("\n".join(_render_steps(m.steps)) + "\n")


_XWININFO_GEOM_RE = re.compile(r"^\s*(Absolute upper-left X|Absolute upper-left Y|Width|Height):\s*(\d+)")


def _run_capture(cmd: list[str]) -> str:
    proc = shutil.which(cmd[0])
    if not proc:
        raise RuntimeError(f"Missing dependency: {cmd[0]}")
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return out.stdout


def _tool_version(cmd: str, *args: str) -> str:
    exe = shutil.which(cmd)
    if not exe:
        return "(not found)"
    try:
        proc = subprocess.run([exe, *args], capture_output=True, text=True, timeout=2)
        lines = (proc.stdout or proc.stderr).strip().splitlines()
        return lines[0] if lines else exe
    except Exception:
        return exe


@app.command()
def pick_window(as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON")):
    """Pick an X11 window by clicking it and print i3-style criteria.

    Inspired by the i3 FAQ "i3-get-window-criteria" helper script.
    """

    if detect_backend() == "wayland":
        raise RuntimeError("pick-window is currently X11-only (uses xprop/xwininfo).")

    wid: str | None = None
    if shutil.which("xdotool"):
        wid = _run_capture(["xdotool", "selectwindow"]).strip()
    elif shutil.which("slop"):
        # slop can output the window id with %i
        wid = _run_capture(["slop", "-f", "%i"]).strip()
    else:
        raise RuntimeError("Need xdotool or slop to pick a window")

    if not wid:
        raise RuntimeError("No window selected")

    # Normalize id for xprop/xwininfo.
    if wid.startswith("0x"):
        wid_norm = wid
    else:
        # xdotool returns decimal.
        wid_norm = hex(int(wid))

    xprop_out = _run_capture([
        "xprop",
        "-id",
        wid_norm,
        "WM_CLASS",
        "_NET_WM_NAME",
        "WM_NAME",
        "_NET_WM_PID",
    ])

    wm_class = None
    instance = None
    title = None
    pid = None

    for line in xprop_out.splitlines():
        if line.startswith("WM_CLASS") and "=" in line:
            # WM_CLASS(STRING) = "instance", "class"
            parts = line.split("=", 1)[1].strip()
            vals = [v.strip().strip('"') for v in parts.split(",")]
            if len(vals) >= 2:
                instance, wm_class = vals[0], vals[1]
        if line.startswith("_NET_WM_NAME") and "=" in line:
            title = line.split("=", 1)[1].strip().strip('"')
        if line.startswith("WM_NAME") and "=" in line and not title:
            title = line.split("=", 1)[1].strip().strip('"')
        if line.startswith("_NET_WM_PID") and "=" in line:
            try:
                pid = int(line.split("=", 1)[1].strip())
            except Exception:
                pid = None

    # Geometry via xwininfo.
    geom_out = _run_capture(["xwininfo", "-id", wid_norm])
    gx = gy = gw = gh = None
    for line in geom_out.splitlines():
        m = _XWININFO_GEOM_RE.match(line)
        if not m:
            continue
        k, v = m.group(1), int(m.group(2))
        if k.endswith("X"):
            gx = v
        elif k.endswith("Y"):
            gy = v
        elif k == "Width":
            gw = v
        elif k == "Height":
            gh = v

    sel = I3WindowSelector(wm_class=wm_class, instance=instance, title=title)
    criteria = _selector_to_i3_criteria(sel)

    payload = {
        "window_id": wid_norm,
        "pid": pid,
        "class": wm_class,
        "instance": instance,
        "title": title,
        "geometry": {"x": gx, "y": gy, "w": gw, "h": gh},
        "i3_criteria": criteria,
    }

    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(criteria + "\n")


@app.command()
def gen_systemd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    macro: str = typer.Argument(..., help="Macro name to run"),
    unit_name: str | None = typer.Option(None, "--name", help="Unit basename (no .service/.timer)"),
    on_calendar: str | None = typer.Option(None, "--on-calendar", help="systemd OnCalendar= expression"),
    on_active_sec: str | None = typer.Option(None, "--on-active-sec", help="systemd OnUnitActiveSec= duration (e.g. 10m)"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write unit files"),
):
    """Generate a systemd .service + .timer that runs a macro.

    This doesn't install/enable units automatically; it just writes the files.
    """

    project = load_project(project_dir)
    if macro not in project.macros:
        raise typer.BadParameter(f"Unknown macro '{macro}'. Available: {', '.join(project.macros.keys())}")

    if not on_calendar and not on_active_sec:
        on_active_sec = "10m"

    unit = unit_name or f"vhk-{project.name}-{macro}".replace(" ", "-")
    target_dir = out_dir or (Path.home() / ".config" / "systemd" / "user")
    target_dir = target_dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    service_path = target_dir / f"{unit}.service"
    timer_path = target_dir / f"{unit}.timer"

    exec_cmd = " ".join(
        shlex.quote(x)
        for x in ["/usr/bin/env", "vhk", "run", str(Path(project.root_dir)), macro]
    )

    service = "\n".join(
        [
            "[Unit]",
            f"Description=VHK macro: {project.name}/{macro}",
            "",
            "[Service]",
            "Type=oneshot",
            f"ExecStart={exec_cmd}",
            "",
        ]
    )

    timer_lines = [
        "[Unit]",
        f"Description=Timer for VHK macro: {project.name}/{macro}",
        "",
        "[Timer]",
        "Persistent=true",
    ]
    if on_calendar:
        timer_lines.append(f"OnCalendar={on_calendar}")
    else:
        timer_lines.append(f"OnUnitActiveSec={on_active_sec}")

    timer_lines += [
        "",
        "[Install]",
        "WantedBy=timers.target",
        "",
    ]

    timer = "\n".join(timer_lines)

    service_path.write_text(service)
    timer_path.write_text(timer)

    console.print(f"Wrote: [bold]{service_path}[/bold]")
    console.print(f"Wrote: [bold]{timer_path}[/bold]")
    console.print("\nNext:\n  systemctl --user daemon-reload\n  systemctl --user enable --now " + f"{unit}.timer")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
