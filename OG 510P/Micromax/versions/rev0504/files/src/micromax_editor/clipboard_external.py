from __future__ import annotations

"""micromax_editor.clipboard_external

Best-effort integration with external/system clipboards.

This module is intentionally tiny and optional:

- When no suitable clipboard tool exists, we fall back to the editor's
  internal clipboard (and UI layers may show a one-time hint).
- When a tool exists, we can export text by piping it to the tool's stdin.
- When a tool exists, we can import text by reading the tool's stdout.

Supported (auto-detect):

Write (export):
- Wayland: wl-copy (wl-clipboard)
- X11: xclip or xsel
- macOS: pbcopy
- Windows: clip / clip.exe

Read (import):
- Wayland: wl-paste (wl-clipboard)
- X11: xclip or xsel
- macOS: pbpaste
- Windows: powershell Get-Clipboard

Notes:
- Clipboard tools are heterogeneous; this module only targets plain-text flows.
- Some tools append a trailing newline when printing clipboard contents.
  We prefer no-newline flags where available (wl-paste -n).
"""

import shlex
import shutil
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class ClipboardCmd:
    argv: list[str]


def detect_external_clipboard_cmd() -> ClipboardCmd | None:
    """Return a best-effort clipboard *write* command, or None."""

    # Windows.
    if sys.platform.startswith('win'):
        for name in ('clip', 'clip.exe'):
            if shutil.which(name):
                return ClipboardCmd([name])
        return None

    # Wayland.
    if shutil.which('wl-copy'):
        return ClipboardCmd(['wl-copy'])

    # X11.
    if shutil.which('xclip'):
        return ClipboardCmd(['xclip', '-selection', 'clipboard'])
    if shutil.which('xsel'):
        return ClipboardCmd(['xsel', '--clipboard', '--input'])

    # macOS.
    if shutil.which('pbcopy'):
        return ClipboardCmd(['pbcopy'])

    return None


def detect_external_clipboard_read_cmd() -> ClipboardCmd | None:
    """Return a best-effort clipboard *read* command, or None."""

    # Windows.
    if sys.platform.startswith('win'):
        # Prefer PowerShell if present.
        for name in ('powershell', 'powershell.exe', 'pwsh', 'pwsh.exe'):
            if shutil.which(name):
                # -Raw: return a single string rather than enumerating lines.
                return ClipboardCmd([name, '-NoProfile', '-Command', 'Get-Clipboard -Raw'])
        return None

    # Wayland.
    if shutil.which('wl-paste'):
        # -n/--no-newline: do not append a newline after the content.
        return ClipboardCmd(['wl-paste', '-n'])

    # X11.
    if shutil.which('xclip'):
        return ClipboardCmd(['xclip', '-selection', 'clipboard', '-o'])
    if shutil.which('xsel'):
        return ClipboardCmd(['xsel', '--clipboard', '--output'])

    # macOS.
    if shutil.which('pbpaste'):
        return ClipboardCmd(['pbpaste'])

    return None


def parse_override(cmd: str, args: str) -> ClipboardCmd | None:
    """Parse user overrides (best-effort)."""

    c = str(cmd or '').strip()
    if not c:
        return None
    a = str(args or '').strip()
    argv = [c]
    if a:
        try:
            argv.extend(shlex.split(a))
        except Exception:
            argv.extend(a.split())
    return ClipboardCmd(argv)
