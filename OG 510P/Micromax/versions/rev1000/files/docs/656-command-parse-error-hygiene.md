# Rev715 - command parse error hygiene

## What changed

Micromax now treats malformed command-bar text as an editor-level failure instead of letting Python parser exceptions escape.

- `src/micromax_editor/cmdline.py` now exposes `CommandLineParseError`, a tiny wrapper around command-line parser failures.
- `parse_cmdline()` still uses `shlex.split(...)` for shell-like quoting, but unmatched quotes now become `CommandLineParseError` instead of raw `ValueError`.
- `Editor.exec_command_line()` catches that parse error, reports `command: parse error: ...`, and returns `False`.
- Prompt submission inherits the same behavior: the prompt closes, the parse error is visible in the normal message/status lane, and execution does not raise.
- Macro recording treats malformed command lines like any other failed command, so a typo such as an unmatched quote does not become a recorded macro step.

## Why it matters

This is a trust-first failure-mode fix.

The command bar is one of the editor's main control surfaces. Users will mistype quotes while opening paths, replacing text, or trying quick commands. A serious editor should make that mistake boring: show an error, preserve normal state, and let the user correct the command. It should not leak a host-language exception out of a headless execution path.

Rev715 keeps the boundary small and inspectable. Command dispatch/runtime errors still use the existing `command NAME: error: ...` lane after parsing succeeds; malformed command syntax now has its own earlier `command: parse error: ...` lane. That makes tests, future plugins, and future LLM-driven maintenance easier to reason about: parse failure, dispatch failure, and command runtime failure are no longer collapsed together.

## Follow-up ideas

- Consider surfacing the parse-error row in command-prompt completion/status while the quote is still unmatched.
- Add a tiny command history affordance that makes it obvious a failed malformed command can be edited from history.
- Audit other shell-ish parsing boundaries, such as action-chain `command:` payloads and external-tool helpers, for the same fail-closed behavior.
