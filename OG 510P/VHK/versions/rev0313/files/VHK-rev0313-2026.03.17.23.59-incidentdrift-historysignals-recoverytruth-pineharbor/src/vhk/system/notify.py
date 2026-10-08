from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Optional

Urgency = Literal["low", "normal", "critical"]


@dataclass
class NotifyResult:
    backend: str
    notification_id: int | None = None
    action_id: str | None = None


@dataclass
class NotifyBackend:
    name: str
    exe: str


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None


def choose_backend() -> NotifyBackend | None:
    # Prefer dunstify when available (more features), otherwise notify-send.
    dunstify = _which("dunstify")
    if dunstify:
        return NotifyBackend(name="dunstify", exe=dunstify)
    ns = _which("notify-send")
    if ns:
        return NotifyBackend(name="notify-send", exe=ns)
    return None


def _parse_notification_id(stdout: str) -> int | None:
    text = str(stdout or "").strip()
    if not text:
        return None
    first_line = text.splitlines()[0].strip()
    try:
        return int(first_line)
    except Exception:
        return None


def _iter_stdout_lines(stdout: str) -> list[str]:
    return [line.strip() for line in str(stdout or "").splitlines() if line.strip()]


def _parse_notification_output(stdout: str) -> tuple[int | None, str | None]:
    lines = _iter_stdout_lines(stdout)
    notification_id: int | None = None
    action_id: str | None = None
    for line in lines:
        if notification_id is None:
            try:
                notification_id = int(line)
                continue
            except Exception:
                pass
        if action_id is None:
            action_id = line
    return notification_id, action_id


def _normalize_action_id(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError("Notification action ids must be non-empty strings")
    if any(ch in text for ch in "=,\n\r"):
        raise ValueError("Notification action ids may not contain '=', ',' or newlines")
    return text


def _normalize_action_label(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError("Notification action labels must be non-empty strings")
    if any(ch in text for ch in "\n\r"):
        raise ValueError("Notification action labels may not contain newlines")
    return text


def _normalize_actions(actions: Iterable[tuple[object, object]] | None) -> list[tuple[str, str]]:
    normalized: list[tuple[str, str]] = []
    seen: set[str] = set()
    for raw in actions or []:
        action_id, label = raw
        action_id_text = _normalize_action_id(action_id)
        if action_id_text in seen:
            raise ValueError(f"Duplicate notification action id: {action_id_text}")
        seen.add(action_id_text)
        normalized.append((action_id_text, _normalize_action_label(label)))
    return normalized


def send(
    summary: str,
    body: Optional[str] = None,
    urgency: Urgency = "normal",
    *,
    app_name: Optional[str] = None,
    icon: Optional[str] = None,
    category: Optional[str] = None,
    timeout_ms: Optional[int] = None,
    replace_id: Optional[int] = None,
    transient: bool = False,
    progress: Optional[int] = None,
    actions: Iterable[tuple[object, object]] | None = None,
    wait: bool = False,
    print_id: bool = False,
) -> NotifyResult:
    backend = choose_backend()
    if not backend:
        raise RuntimeError("No notification backend found. Install 'notify-send' (libnotify-bin) or 'dunstify'.")

    normalized_actions = _normalize_actions(actions)
    capture_action = wait or bool(normalized_actions)

    cmd = [backend.exe]
    if backend.name == "dunstify":
        if app_name:
            cmd += ["--appname", app_name]
        cmd += ["--urgency", urgency]
        if icon:
            cmd += ["--icon", icon]
        if category:
            cmd += ["--category", category]
        if timeout_ms is not None:
            cmd += ["--timeout", str(int(timeout_ms))]
        if replace_id is not None:
            cmd += ["--replace", str(int(replace_id))]
        if transient:
            cmd += ["--hints", "BOOLEAN:transient:true"]
        if progress is not None:
            cmd += ["--hints", f"INT:value:{int(progress)}"]
        for action_id, label in normalized_actions:
            cmd += ["--action", f"{action_id},{label}"]
        if print_id:
            cmd += ["--printid"]
        if capture_action:
            cmd += ["--block"]
    else:
        if app_name:
            cmd += ["--app-name", app_name]
        cmd += ["--urgency", urgency]
        if icon:
            cmd += ["--icon", icon]
        if category:
            cmd += ["--category", category]
        if timeout_ms is not None:
            cmd += ["--expire-time", str(int(timeout_ms))]
        if replace_id is not None:
            cmd += ["--replace-id", str(int(replace_id))]
        if transient:
            cmd += ["--transient"]
        if progress is not None:
            cmd += ["--hint", f"INT:value:{int(progress)}"]
        for action_id, label in normalized_actions:
            cmd += ["--action", f"{action_id}={label}"]
        if print_id:
            cmd += ["--print-id"]
        if wait:
            cmd += ["--wait"]

    cmd += [summary]
    if body is not None:
        cmd += [body]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Notification failed via {backend.name}: {proc.stderr.strip()}")
    notification_id, action_id = _parse_notification_output(proc.stdout)
    return NotifyResult(
        backend=backend.name,
        notification_id=notification_id if print_id else None,
        action_id=action_id if capture_action else None,
    )
