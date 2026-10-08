# Sandworm (Python Rewrite Notes)

Goal: explore a Python-based implementation of sandworm that is easier to test, extend, and reason about than a single large bash script — without breaking existing workflows.

Non-goal: “fix” Codex’s tool sandbox restrictions. Sandworm can surface and explain them, but it can’t override them from inside the sandbox.

## Strategy

- Keep `Original-Starting-Place/sandworm` as the stable reference implementation.
- Add Python utilities first where they buy us leverage:
  - diagnostics that can be unit-tested,
  - structured (JSON) output for tooling,
  - safer parsing/validation of config/state.
- Only migrate “heavy” commands (refresh/build/shell/codex) once the Python version has parity tests and a clean fallback path.

## First brick (done)

- `tools/sandworm_py.py` implements a minimal `doctor`/`netcheck` shim that detects:
  - sandworm context env (`SANDWORM_*`),
  - seccomp/no-new-privs state,
  - AF_INET socket availability (useful for debugging “no network” symptoms).

