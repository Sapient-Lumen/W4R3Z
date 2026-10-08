from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path
from textwrap import dedent

from vhk.core.models import Project
from vhk.project.support_posture import (
    render_support_about_text,
    summarize_support_posture,
)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


def default_launcher_script_name(project: Project, *, launcher_id: str | None = None) -> str:
    if launcher_id:
        return re.sub(r"[^A-Za-z0-9._-]+", "-", str(launcher_id).strip()) or f"vhk-{_slugify(project.name)}-palette"
    return f"vhk-{_slugify(project.name)}-palette"


def default_launcher_install_path(
    project: Project,
    *,
    env: dict[str, str] | None = None,
    launcher_id: str | None = None,
) -> Path:
    env_map = dict(os.environ if env is None else env)
    xdg_bin_home = env_map.get("XDG_BIN_HOME")
    if xdg_bin_home:
        base = Path(xdg_bin_home)
    else:
        base = Path.home() / ".local" / "bin"
    return base / default_launcher_script_name(project, launcher_id=launcher_id)


_TEMPLATE = dedent(
    '''\
    #!/usr/bin/env python3
    from __future__ import annotations

    import json
    import os
    import shlex
    import shutil
    import subprocess
    import sys

    PROJECT_DIR = {project_dir!r}
    VHK_COMMAND = {command_argv}
    TITLE = {title!r}
    DEFAULT_BACKEND = {backend!r}
    PALETTE_ARGS = {palette_args}
    SUPPORT_POSTURE = {support_posture}
    SUPPORT_ABOUT_TEXT = {support_about_text!r}

    BACKEND_COMMANDS = {{
        "rofi": lambda title: ["rofi", "-dmenu", "-i", "-p", title],
        "dmenu": lambda title: ["dmenu", "-i", "-p", title],
        "wofi": lambda title: ["wofi", "--dmenu", "--prompt", title],
        "fuzzel": lambda title: ["fuzzel", "--dmenu", "--prompt", title],
        "tofi": lambda title: ["tofi", "--prompt-text", f"{{title}}: "],
    }}


    def session_type() -> str:
        hint = str(os.environ.get("XDG_SESSION_TYPE") or "").strip().lower()
        if hint in {{"wayland", "x11"}}:
            return hint
        if os.environ.get("WAYLAND_DISPLAY"):
            return "wayland"
        if os.environ.get("DISPLAY"):
            return "x11"
        return "tty"


    def detect_backend() -> str:
        override = str(os.environ.get("VHK_LAUNCHER_BACKEND") or os.environ.get("VHK_CHOOSER_BACKEND") or "").strip().lower()
        if override:
            if override in {{"console", "tty"}}:
                return "console"
            if override in BACKEND_COMMANDS and shutil.which(override):
                return override
        if DEFAULT_BACKEND != "auto":
            if DEFAULT_BACKEND in BACKEND_COMMANDS and shutil.which(DEFAULT_BACKEND):
                return DEFAULT_BACKEND
            if DEFAULT_BACKEND in {{"console", "tty"}}:
                return "console"
        order = {{
            "wayland": ("fuzzel", "tofi", "wofi", "rofi", "dmenu"),
            "x11": ("rofi", "dmenu", "wofi", "fuzzel", "tofi"),
            "tty": tuple(),
        }}.get(session_type(), ("rofi", "dmenu", "fuzzel", "tofi", "wofi"))
        for name in order:
            if shutil.which(name):
                return name
        return "console"


    def palette_payload() -> dict:
        cmd = [*VHK_COMMAND, "palette", PROJECT_DIR, "--json", *PALETTE_ARGS]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr or proc.stdout or f"Command failed: {{' '.join(cmd)}}\\n")
            raise SystemExit(proc.returncode or 1)
        return json.loads(proc.stdout)


    def render_rows(entries: list[dict]) -> tuple[list[str], dict[str, str]]:
        labels = [str(e.get("label") or e.get("entry_id") or "") for e in entries]
        counts = {{}}
        for label in labels:
            counts[label] = counts.get(label, 0) + 1
        rows = []
        mapping = {{}}
        for entry, label in zip(entries, labels):
            entry_id = str(entry.get("entry_id") or "")
            row = label
            if counts.get(label, 0) > 1:
                row = f"{{label}}  [{{entry_id}}]"
            rows.append(row)
            mapping[row] = entry_id
        return rows, mapping


    def _rofi_escape(value: str) -> str:
        return str(value).replace(chr(92), chr(92) * 2).replace(chr(10), " ")


    def emit_rofi_rows(entries: list[dict]) -> int:
        print("\\0prompt\\x1f" + _rofi_escape(TITLE))
        print("\\0no-custom\\x1ftrue")
        print("\\0markup-rows\\x1ffalse")
        for entry in entries:
            entry_id = str(entry.get("entry_id") or "")
            label = str(entry.get("label") or entry_id)
            meta = " ".join(str(x).strip() for x in (entry.get("search_terms") or []) if str(x).strip())
            icon = str(entry.get("icon") or "").strip()
            action = str(entry.get("action") or "run").strip() or "run"
            parts = ["display", _rofi_escape(label), "info", _rofi_escape(entry_id)]
            if meta:
                parts.extend(["meta", _rofi_escape(meta)])
            if icon:
                parts.extend(["icon", _rofi_escape(icon)])
            if action != "run":
                parts.extend(["active", "true"])
            if action == "delete_profile":
                parts.extend(["urgent", "true"])
            print(_rofi_escape(entry_id) + "\\0" + "\\x1f".join(parts))
        return 0


    def rofi_script_main(argv: list[str]) -> int:
        payload = palette_payload()
        entries = list(payload.get("entries") or [])
        retv = str(os.environ.get("ROFI_RETV") or "0").strip()
        if retv in {{"0", ""}}:
            return emit_rofi_rows(entries)
        entry_id = str(os.environ.get("ROFI_INFO") or (argv[0] if argv else "")).strip()
        if not entry_id:
            return 1
        return run_entry(entry_id)


    def choose_console(rows: list[str]) -> str | None:
        if not rows:
            return None
        for idx, row in enumerate(rows, start=1):
            print(f"{{idx:2d}}. {{row}}")
        try:
            raw = input(f"{{TITLE}}> ").strip()
        except EOFError:
            return None
        if not raw:
            return None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(rows):
                return rows[idx - 1]
        return raw if raw in rows else None


    def choose_row(rows: list[str]) -> str | None:
        backend_cmd = str(os.environ.get("VHK_LAUNCHER_CMD") or "").strip()
        if backend_cmd:
            cmd = shlex.split(backend_cmd)
            proc = subprocess.run(cmd, input="\\n".join(rows) + ("\\n" if rows else ""), capture_output=True, text=True)
            if proc.returncode != 0:
                return None
            return proc.stdout.rstrip("\\n") or None

        backend = detect_backend()
        if backend == "console":
            return choose_console(rows)

        cmd = BACKEND_COMMANDS[backend](TITLE)
        proc = subprocess.run(cmd, input="\\n".join(rows) + ("\\n" if rows else ""), capture_output=True, text=True)
        if proc.returncode != 0:
            return None
        return proc.stdout.rstrip("\\n") or None


    def run_entry(entry_id: str, *, no_run: bool = False) -> int:
        cmd = [*VHK_COMMAND, "palette", PROJECT_DIR, "--entry-id", entry_id, *PALETTE_ARGS]
        if no_run:
            cmd.append("--no-run")
        proc = subprocess.run(cmd)
        return int(proc.returncode)


    def main(argv: list[str]) -> int:
        if os.environ.get("ROFI_RETV") is not None:
            return rofi_script_main(argv)
        if argv and argv[0] in {{"--help", "-h"}}:
            print("Usage: launcher [--list] [--json] [--support-json] [--about] [--print-entry-id] [entry_id]")
            print("When invoked by rofi script mode, the same script also emits rows and executes ROFI_INFO entry ids.")
            return 0
        if argv and argv[0] == "--support-json":
            print(json.dumps(SUPPORT_POSTURE, indent=2))
            return 0
        if argv and argv[0] in {{"--about", "--support"}}:
            sys.stdout.write(SUPPORT_ABOUT_TEXT)
            return 0
        payload = palette_payload()
        entries = list(payload.get("entries") or [])
        if argv and argv[0] == "--json":
            print(json.dumps(payload, indent=2))
            return 0
        if argv and argv[0] == "--list":
            for entry in entries:
                print(f"{{entry.get('entry_id','')}}\t{{entry.get('label','')}}")
            return 0
        if argv and argv[0] == "--print-entry-id":
            rows, mapping = render_rows(entries)
            chosen = choose_row(rows)
            if not chosen:
                return 1
            print(mapping.get(chosen, chosen))
            return 0
        if argv:
            return run_entry(argv[0])
        rows, mapping = render_rows(entries)
        chosen = choose_row(rows)
        if not chosen:
            return 1
        entry_id = mapping.get(chosen)
        if not entry_id:
            sys.stderr.write(f"Unknown selection: {{chosen}}\\n")
            return 2
        return run_entry(entry_id)


    if __name__ == "__main__":
        raise SystemExit(main(sys.argv[1:]))
    '''
)


def render_launcher_script(
    project: Project,
    *,
    command: str = "vhk",
    title: str | None = None,
    launcher_backend: str = "auto",
    include_hidden: bool = False,
    include_presets: bool = True,
    include_profile_actions: bool = True,
    include_profile_management_actions: bool = False,
    alpha: bool = False,
    history_limit: int = 50,
) -> str:
    support_posture = summarize_support_posture(project.root_dir)
    palette_args: list[str] = []
    if include_hidden:
        palette_args.append("--include-hidden")
    if not include_presets:
        palette_args.append("--no-presets")
    if not include_profile_actions:
        palette_args.append("--no-profile-actions")
    if include_profile_management_actions:
        palette_args.append("--profile-management-actions")
    if alpha:
        palette_args.append("--alpha")
    if history_limit != 50:
        palette_args.extend(["--history-limit", str(int(history_limit))])

    return _TEMPLATE.format(
        project_dir=str(project.root_dir),
        command_argv=json.dumps(shlex.split(str(command)) or [str(command)]),
        title=str(title or project.name or "VHK"),
        backend=str(launcher_backend or "auto"),
        palette_args=json.dumps(palette_args),
        support_posture=json.dumps(support_posture, ensure_ascii=False, indent=2),
        support_about_text=render_support_about_text(support_posture),
    )
