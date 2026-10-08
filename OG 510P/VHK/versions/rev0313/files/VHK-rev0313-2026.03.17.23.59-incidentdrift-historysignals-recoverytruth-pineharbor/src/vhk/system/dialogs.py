from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class DialogBackend:
    name: str
    exe: str | None


@dataclass
class FormField:
    name: str
    label: str | None = None
    kind: str = "text"
    default: Any | None = None
    choices: list[str] = field(default_factory=list)
    remember: bool = True


@dataclass
class ChoiceBackend:
    name: str
    exe: str | None
    kind: str = "dialog"


def choose_dialog_backend() -> DialogBackend:
    for name in ("zenity", "yad", "kdialog", "dialog"):
        exe = shutil.which(name)
        if exe:
            return DialogBackend(name=name, exe=exe)
    return DialogBackend(name="console", exe=None)


def _session_type() -> str:
    hint = str(os.environ.get("XDG_SESSION_TYPE") or "").strip().lower()
    if hint in {"wayland", "x11"}:
        return hint
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("DISPLAY"):
        return "x11"
    return "tty"


def choose_choice_backend(*, multiple: bool = False) -> ChoiceBackend:
    override = str(os.environ.get("VHK_CHOOSER_BACKEND") or os.environ.get("VHK_CHOOSE_BACKEND") or "").strip().lower()
    if override:
        if override in {"console", "tty"}:
            return ChoiceBackend(name="console", exe=None, kind="console")
        exe = shutil.which(override)
        if exe:
            kind = "launcher" if override in {"rofi", "dmenu", "wofi", "fuzzel", "tofi"} else "dialog"
            return ChoiceBackend(name=override, exe=exe, kind=kind)

    session = _session_type()
    if multiple:
        candidates = {
            "wayland": ("zenity", "yad", "kdialog", "dialog"),
            "x11": ("zenity", "yad", "kdialog", "dialog"),
            "tty": ("dialog",),
        }.get(session, ("zenity", "yad", "kdialog", "dialog"))
    else:
        candidates = {
            "wayland": ("fuzzel", "tofi", "wofi", "zenity", "yad", "kdialog", "dialog"),
            "x11": ("rofi", "dmenu", "zenity", "yad", "kdialog", "dialog"),
            "tty": ("dialog",),
        }.get(session, ("rofi", "dmenu", "fuzzel", "tofi", "wofi", "zenity", "yad", "kdialog", "dialog"))

    for name in candidates:
        exe = shutil.which(name)
        if exe:
            kind = "launcher" if name in {"rofi", "dmenu", "wofi", "fuzzel", "tofi"} else "dialog"
            return ChoiceBackend(name=name, exe=exe, kind=kind)
    return ChoiceBackend(name="console", exe=None, kind="console")


def _run_capture(cmd: list[str], *, ok_codes: set[int] | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if ok_codes is not None and proc.returncode not in ok_codes:
        raise RuntimeError(proc.stderr.strip() or f"Command failed ({proc.returncode}): {' '.join(cmd)}")
    return proc.returncode, proc.stdout, proc.stderr


def _dialog_dims() -> tuple[str, str]:
    # Traditional dialog(1) wants height/width args. Keep them fixed/simple.
    return "10", "70"


def _run_capture_stdin(cmd: list[str], stdin_text: str) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, input=stdin_text, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def _bool_from_text(raw: str | None, *, default: bool = False) -> bool:
    value = str(raw or "").strip().lower()
    if value in {"1", "true", "yes", "y", "on", "checked"}:
        return True
    if value in {"0", "false", "no", "n", "off", "unchecked", ""}:
        return False
    return default


def _number_from_text(raw: str | None) -> int | float | None:
    value = str(raw or "").strip()
    if value == "":
        return None
    try:
        return int(value)
    except Exception:
        return float(value)


def _coerce_form_value(field: FormField, raw: str | None) -> Any:
    if field.kind == "bool":
        return _bool_from_text(raw, default=bool(field.default))
    if field.kind == "number":
        return _number_from_text(raw)
    if raw is None:
        return None
    return str(raw)


def _prompt_form_yad(fields: Sequence[FormField], *, title: str | None = None, text: str | None = None) -> dict[str, Any] | None:
    exe = shutil.which("yad")
    if not exe:
        return None
    sep = "\x1f"
    cmd = [exe, "--form", "--separator", sep]
    if title:
        cmd += ["--title", title]
    if text:
        cmd += ["--text", text]
    defaults: list[str] = []
    for field in fields:
        label = field.label or field.name
        kind = str(field.kind).lower()
        if kind == "password":
            cmd.append(f"--field={label}:H")
            defaults.append("" if field.default is None else str(field.default))
        elif kind == "multiline":
            cmd.append(f"--field={label}:TXT")
            defaults.append("" if field.default is None else str(field.default))
        elif kind == "number":
            cmd.append(f"--field={label}:NUM")
            defaults.append("" if field.default is None else str(field.default))
        elif kind == "bool":
            cmd.append(f"--field={label}:CHK")
            defaults.append("TRUE" if bool(field.default) else "FALSE")
        elif kind == "choice":
            cmd.append(f"--field={label}:CB")
            options = [str(x) for x in field.choices]
            default = None if field.default is None else str(field.default)
            if default and default in options:
                options = [default] + [x for x in options if x != default]
            elif default:
                options = [default] + options
            defaults.append("!".join(options))
        else:
            cmd.append(f"--field={label}")
            defaults.append("" if field.default is None else str(field.default))
    cmd += defaults
    code, out, _ = _run_capture(cmd)
    if code != 0:
        return None
    parts = out.rstrip("\n").split(sep) if fields else []
    if len(parts) < len(fields):
        parts.extend([""] * (len(fields) - len(parts)))
    result: dict[str, Any] = {}
    for field, raw in zip(fields, parts):
        result[field.name] = _coerce_form_value(field, raw)
    return result


def _prompt_form_sequential(fields: Sequence[FormField], *, title: str | None = None, text: str | None = None) -> dict[str, Any] | None:
    if text:
        show_message(text, title=title, level="info")
    result: dict[str, Any] = {}
    for field in fields:
        label = field.label or field.name
        if field.kind == "bool":
            result[field.name] = ask_yes_no(label, title=title, default_yes=bool(field.default))
            continue
        if field.kind == "choice":
            values = [str(x) for x in field.choices]
            chosen = choose_from_list(values, title=title, text=label, multiple=False)
            result[field.name] = chosen
            continue
        value = input_text(label, title=title, default=None if field.default is None else str(field.default), password=(field.kind == "password"))
        result[field.name] = _coerce_form_value(field, value)
    return result


def prompt_form(fields: Sequence[FormField], *, title: str | None = None, text: str | None = None) -> dict[str, Any] | None:
    """Prompt for multiple related values.

    We prefer YAD's native form support because it exposes a richer Linux-native
    multi-field dialog surface than the other helpers we currently probe.
    Other backends fall back to a sequential series of prompts so the macro
    semantics remain portable.
    """

    if not fields:
        return {}
    yad_res = _prompt_form_yad(fields, title=title, text=text)
    if yad_res is not None:
        return yad_res
    return _prompt_form_sequential(fields, title=title, text=text)


def show_message(text: str, *, title: str | None = None, level: str = "info") -> None:
    backend = choose_dialog_backend()
    level2 = str(level).lower()

    if backend.name == "zenity":
        flag = {"info": "--info", "warning": "--warning", "error": "--error"}.get(level2, "--info")
        cmd = [backend.exe, flag, "--text", text]
        if title:
            cmd += ["--title", title]
        _run_capture(cmd, ok_codes={0})
        return

    if backend.name == "yad":
        flag = {"info": "--info", "warning": "--warning", "error": "--error"}.get(level2, "--info")
        cmd = [backend.exe, flag, "--text", text]
        if title:
            cmd += ["--title", title]
        _run_capture(cmd, ok_codes={0})
        return

    if backend.name == "kdialog":
        flag = {"info": "--msgbox", "warning": "--sorry", "error": "--error"}.get(level2, "--msgbox")
        cmd = [backend.exe]
        if title:
            cmd += ["--title", title]
        cmd += [flag, text]
        _run_capture(cmd, ok_codes={0})
        return

    if backend.name == "dialog":
        h, w = _dialog_dims()
        # dialog writes to the terminal rather than stdout.
        cmd = [backend.exe, "--msgbox", text, h, w]
        if title:
            cmd = [backend.exe, "--title", title, "--msgbox", text, h, w]
        subprocess.run(cmd, check=False)
        return

    print(f"[{level2.upper()}] {title + ': ' if title else ''}{text}")


def ask_yes_no(text: str, *, title: str | None = None, default_yes: bool = True) -> bool:
    backend = choose_dialog_backend()

    if backend.name == "zenity":
        cmd = [backend.exe, "--question", "--text", text]
        if title:
            cmd += ["--title", title]
        code, _, _ = _run_capture(cmd)
        return code == 0

    if backend.name == "yad":
        cmd = [backend.exe, "--question", "--text", text]
        if title:
            cmd += ["--title", title]
        code, _, _ = _run_capture(cmd)
        return code == 0

    if backend.name == "kdialog":
        cmd = [backend.exe]
        if title:
            cmd += ["--title", title]
        cmd += ["--yesno", text]
        code, _, _ = _run_capture(cmd)
        return code == 0

    if backend.name == "dialog":
        h, w = _dialog_dims()
        cmd = [backend.exe]
        if title:
            cmd += ["--title", title]
        cmd += ["--yesno", text, h, w]
        proc = subprocess.run(cmd, check=False)
        return proc.returncode == 0

    prompt = f"{title + ': ' if title else ''}{text} [{'Y/n' if default_yes else 'y/N'}]: "
    raw = input(prompt).strip().lower()
    if not raw:
        return default_yes
    return raw in {"y", "yes", "1", "true"}


def input_text(prompt: str, *, title: str | None = None, default: str | None = None, password: bool = False) -> str | None:
    backend = choose_dialog_backend()

    if backend.name == "zenity":
        cmd = [backend.exe, "--entry", "--text", prompt]
        if title:
            cmd += ["--title", title]
        if default is not None:
            cmd += ["--entry-text", default]
        if password:
            cmd.append("--hide-text")
        code, out, _ = _run_capture(cmd)
        return out.rstrip("\n") if code == 0 else None

    if backend.name == "yad":
        cmd = [backend.exe, "--entry", "--text", prompt]
        if title:
            cmd += ["--title", title]
        if default is not None:
            cmd += ["--entry-text", default]
        if password:
            cmd.append("--hide-text")
        code, out, _ = _run_capture(cmd)
        return out.rstrip("\n") if code == 0 else None

    if backend.name == "kdialog":
        cmd = [backend.exe]
        if title:
            cmd += ["--title", title]
        if password:
            cmd += ["--password", prompt]
        else:
            cmd += ["--inputbox", prompt]
            if default is not None:
                cmd.append(default)
        code, out, _ = _run_capture(cmd)
        return out.rstrip("\n") if code == 0 else None

    if backend.name == "dialog":
        h, w = _dialog_dims()
        cmd = [backend.exe, "--stdout"]
        if title:
            cmd += ["--title", title]
        if password:
            cmd += ["--passwordbox", prompt, h, w, default or ""]
        else:
            cmd += ["--inputbox", prompt, h, w, default or ""]
        code, out, _ = _run_capture(cmd)
        return out.rstrip("\n") if code == 0 else None

    prompt2 = f"{title + ': ' if title else ''}{prompt}"
    if default:
        prompt2 += f" [{default}]"
    raw = input(prompt2 + ": ")
    if raw == "":
        return default
    return raw


def choose_from_list(
    items: Sequence[str],
    *,
    title: str | None = None,
    text: str | None = None,
    multiple: bool = False,
) -> str | list[str] | None:
    values = [str(x) for x in items]
    backend = choose_choice_backend(multiple=multiple)

    if backend.kind == "launcher":
        prompt = text or title or "Choose"
        stdin_text = ("\n".join(values) + "\n") if values else ""

        if backend.name == "rofi":
            cmd = [backend.exe, "-dmenu", "-p", prompt]
            code, out, _ = _run_capture_stdin(cmd, stdin_text)
            return out.rstrip("\n") if code == 0 else None

        if backend.name == "dmenu":
            cmd = [backend.exe, "-p", prompt]
            code, out, _ = _run_capture_stdin(cmd, stdin_text)
            return out.rstrip("\n") if code == 0 else None

        if backend.name == "wofi":
            cmd = [backend.exe, "--dmenu", "--prompt", prompt]
            code, out, _ = _run_capture_stdin(cmd, stdin_text)
            return out.rstrip("\n") if code == 0 else None

        if backend.name == "fuzzel":
            cmd = [backend.exe, "--dmenu", "--prompt", prompt]
            code, out, _ = _run_capture_stdin(cmd, stdin_text)
            return out.rstrip("\n") if code == 0 else None

        if backend.name == "tofi":
            cmd = [backend.exe]
            if prompt:
                cmd.append(f"--prompt-text={prompt}")
            code, out, _ = _run_capture_stdin(cmd, stdin_text)
            return out.rstrip("\n") if code == 0 else None

    if backend.name == "zenity":
        cmd = [backend.exe, "--list", "--column", "Value"]
        if title:
            cmd += ["--title", title]
        if text:
            cmd += ["--text", text]
        if multiple:
            cmd += ["--multiple", "--separator", "\n"]
        cmd += values
        code, out, _ = _run_capture(cmd)
        if code != 0:
            return None
        out2 = out.rstrip("\n")
        return out2.splitlines() if multiple else (out2 or None)

    if backend.name == "yad":
        cmd = [backend.exe, "--list", "--column=Value"]
        if title:
            cmd += ["--title", title]
        if text:
            cmd += ["--text", text]
        if multiple:
            cmd += ["--multiple", "--separator=\n"]
        cmd += values
        code, out, _ = _run_capture(cmd)
        if code != 0:
            return None
        out2 = out.rstrip("\n")
        return out2.splitlines() if multiple else (out2 or None)

    if backend.name == "kdialog" and not multiple:
        cmd = [backend.exe]
        if title:
            cmd += ["--title", title]
        cmd += ["--menu", text or "Choose an item"]
        for item in values:
            cmd += [item, item]
        code, out, _ = _run_capture(cmd)
        return out.rstrip("\n") if code == 0 else None

    # Console fallback also covers backends whose multi-select CLI shape is too
    # inconsistent to rely on without a real desktop session available here.
    if not values:
        return [] if multiple else None
    prompt = text or (title or "Choose an item")
    print(prompt)
    for idx, item in enumerate(values, start=1):
        print(f"  {idx}. {item}")
    if multiple:
        raw = input("Enter comma-separated numbers (blank to cancel): ").strip()
        if not raw:
            return None
        chosen: list[str] = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            i = int(part) - 1
            if 0 <= i < len(values):
                chosen.append(values[i])
        return chosen
    raw = input("Enter number (blank to cancel): ").strip()
    if not raw:
        return None
    i = int(raw) - 1
    if 0 <= i < len(values):
        return values[i]
    return None
