from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Sequence


@dataclass
class DialogBackend:
    name: str
    exe: str | None


def choose_dialog_backend() -> DialogBackend:
    for name in ("zenity", "yad", "kdialog", "dialog"):
        exe = shutil.which(name)
        if exe:
            return DialogBackend(name=name, exe=exe)
    return DialogBackend(name="console", exe=None)


def _run_capture(cmd: list[str], *, ok_codes: set[int] | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if ok_codes is not None and proc.returncode not in ok_codes:
        raise RuntimeError(proc.stderr.strip() or f"Command failed ({proc.returncode}): {' '.join(cmd)}")
    return proc.returncode, proc.stdout, proc.stderr


def _dialog_dims() -> tuple[str, str]:
    # Traditional dialog(1) wants height/width args. Keep them fixed/simple.
    return "10", "70"


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
    backend = choose_dialog_backend()

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
