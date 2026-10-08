from __future__ import annotations

"""One-shot child entrypoint for opening an external URL.

The parent editor launches this module in a separate process group.  Python's
``webbrowser`` controllers may synchronously wait for a text-mode browser or a
platform launcher, so the editor must not call them on its UI/plugin thread.
"""

from contextlib import contextmanager
import os
import sys
import webbrowser


@contextmanager
def _browser_stdio_detached():
    """Prevent a successful detached browser from retaining parent capture pipes."""

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.flush()
        except Exception:
            pass

    null_fd = os.open(os.devnull, os.O_RDWR)
    saved: dict[int, int] = {}
    try:
        for fd in (1, 2):
            saved[fd] = os.dup(fd)
            os.dup2(null_fd, fd)
        yield
    finally:
        restore_error: OSError | None = None
        for fd, original in saved.items():
            try:
                os.dup2(original, fd)
            except OSError as exc:
                if restore_error is None:
                    restore_error = exc
            finally:
                try:
                    os.close(original)
                except OSError:
                    pass
        try:
            os.close(null_fd)
        except OSError:
            pass
        if restore_error is not None:
            raise restore_error


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("open-url child: expected exactly one URL", file=sys.stderr)
        return 2

    url = str(args[0])
    try:
        with _browser_stdio_detached():
            opened = bool(webbrowser.open(url, new=2))
    except Exception as exc:
        print(f"open-url child: {exc}", file=sys.stderr)
        return 1
    return 0 if opened else 1


if __name__ == "__main__":  # pragma: no cover - exercised through the parent process
    raise SystemExit(main())
