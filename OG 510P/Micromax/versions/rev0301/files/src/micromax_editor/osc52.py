"""micromax_editor.osc52

Best-effort OSC 52 clipboard export.

OSC 52 is a terminal escape sequence that can set the *system* clipboard via
some terminal emulators.

We intentionally keep this as a tiny helper:
- UI layers decide when/if to emit the sequence
- the headless editor keeps an internal clipboard regardless

Reference / prior art:
- micro editor's help docs discuss OSC 52 clipboard support and caveats.
"""

from __future__ import annotations

import base64


def osc52_sequence(text: str, *, max_bytes: int = 100000) -> tuple[str | None, str]:
    """Return an OSC 52 sequence that sets the clipboard to `text`.

    Args:
        text: clipboard contents (unicode)
        max_bytes: max UTF-8 bytes allowed (0 = unlimited)

    Returns:
        (seq, err)
        - seq is the escape sequence to emit to the terminal, or None
        - err is a human-facing reason when seq is None

    Notes:
        We use the BEL terminator (\a) which is commonly supported.
    """

    s = "" if text is None else str(text)
    try:
        data = s.encode("utf-8")
    except Exception as e:
        return (None, f"osc52: utf-8 encode failed: {e}")

    n = len(data)
    if max_bytes and n > int(max_bytes):
        return (None, f"osc52: clipboard too large ({n} bytes > {int(max_bytes)})")

    try:
        b64 = base64.b64encode(data).decode("ascii")
    except Exception as e:
        return (None, f"osc52: base64 failed: {e}")

    # OSC 52: ESC ] 52 ; c ; <base64> BEL
    seq = "\x1b]52;c;" + b64 + "\x07"
    return (seq, "")
