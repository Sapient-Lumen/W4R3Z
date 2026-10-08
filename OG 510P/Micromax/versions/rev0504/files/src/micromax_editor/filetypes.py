"""micromax_editor.filetypes

Minimal filetype detection.

This is intentionally tiny and deterministic:
- primarily based on extension
- with a small shebang fallback

The result is a short lowercase string ("python", "markdown", "micromax", ...).
"""

from __future__ import annotations

from pathlib import Path


def detect_filetype(path: str, text: str) -> str:
    p = Path(str(path or ""))
    suffix = p.suffix.lower().lstrip(".")

    # Extension-based mapping (MVP)
    ext_map: dict[str, str] = {
        "mx": "micromax",
        "mmx": "micromax",
        "mf": "micromax",
        "md": "markdown",
        "markdown": "markdown",
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "toml": "toml",
        "sh": "sh",
        "bash": "sh",
        "zsh": "sh",
        "rb": "ruby",
        "pl": "perl",
        "rs": "rust",
        "c": "c",
        "h": "c",
        "cpp": "cpp",
        "hpp": "cpp",
    }
    if suffix in ext_map:
        return ext_map[suffix]

    # Shebang-based fallback
    first = ""
    try:
        first = text.splitlines()[0] if text else ""
    except Exception:
        first = ""
    if first.startswith("#!"):
        line = first[2:].strip()
        # common pattern: /usr/bin/env python
        if "env" in line:
            parts = line.split()
            try:
                i = parts.index("env")
                if i + 1 < len(parts):
                    line = parts[i + 1]
            except ValueError:
                pass
        low = line.lower()
        if "python" in low:
            return "python"
        if "bash" in low or low.endswith("/sh") or " sh" in f" {low} ":
            return "sh"
        if "node" in low or "nodejs" in low:
            return "javascript"
        if "ruby" in low:
            return "ruby"
        if "perl" in low:
            return "perl"

    return "text"
