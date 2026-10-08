# Rev651: macro arity guards

Problem:
- several macro subcommands still ignored stray tail tokens after Enter
- that made typoed commands like `macro stop now` or `macro play demo 2 extra` feel safer than they were
- completion also went quiet once users typed past the supported macro arity

What changed:
- added `Editor._prompt_macro_arity_row(...)` for exact extra-arg witnesses
- command completion now falls back to that row for:
  - no-arg macro subcommands with an extra token (`stop`, `end`, `cancel`, `abort`, `list`, `ls`, `status`, `st`)
  - `record`-family commands with more than one explicit argument
  - `play`/`run` with more than two explicit arguments
- `c_macro(...)` now rejects those over-arity forms before mutation or playback and emits alias-specific usage lines

Why it matters:
- trust: typoed macro commands stop instead of silently doing something adjacent
- flow: exact command-bar rows now explain the mistake before Enter
- coherence: preview and runtime now agree that extra macro tail tokens are errors, not ignorable noise

Focused coverage:
- `tests/test_editor_macros_named.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
