"""micromax.repl

Simple REPL for the micromax VM.
"""

from __future__ import annotations

import sys

from .vm import VM, MicromaxError


PROMPT = "mx> "


def main() -> None:
    vm = VM()
    print("micromax (rev12) — type 'bye' to exit")

    # Demo hostcall hook (for VM sanity): "py.add1" adds 1 to top int.
    def add1(v: VM) -> None:
        n = v.pop_int()
        v.stack.append(n + 1)

    vm.register_host("py.add1", add1)

    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            print()
            break
        if not line.strip():
            continue
        try:
            vm.eval(line, filename="<repl>")
        except SystemExit:
            raise
        except MicromaxError as e:
            print("error:", vm.format_error(e), file=sys.stderr)
        except Exception as e:
            print(f"fatal: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
