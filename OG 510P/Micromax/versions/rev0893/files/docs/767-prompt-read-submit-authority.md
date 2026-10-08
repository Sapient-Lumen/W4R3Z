# Rev809 — prompt read and submit authority

Rev809 continues the protected-register audit on a deceptively small delayed-interaction surface: the active prompt. Prompts are not just transient UI text. They can hold a user command, a search query, a filesystem/path fragment, a picker selection, or completion rows containing previews and metadata. A lower-authority script should not be able to inspect or answer a trusted/user prompt merely because the prompt happens to be active.

## What was wrong

The previous prompt-origin work made delayed prompt submission run under the authority captured when a script/plugin prepared the prompt. That closed the major capability-escalation shape where a later Enter key could turn a script-authored command into trusted user execution.

The read side was still too open. Script-origin code could ask for `ed.prompt-text`, `ed.prompt-kind`, `ed.prompt-suggestions`, `ed.prompt-current-row`, picker window/display models, status prompt fields, or the shared interaction row and learn trusted/user prompt state. Direct script-origin `ed.prompt-submit` could also answer a prompt that was never created by the script.

## What changed

New policy seam:

`src/micromax_editor/prompt_policy.py`

It mirrors the other protected-register policies: trusted interactive callers keep normal visibility; scripts can read and answer their own prompts; trusted/user prompts and other-origin prompts require an explicit capability.

New capabilities:

- `cap.prompt-read` / `ed.prompt-read`
- `cap.prompt-write` / `ed.prompt-write`

Protected read surfaces now redact from lower-authority script context unless the active prompt is same-origin or `cap.prompt-read` is enabled:

- `ed.prompt-text`
- `ed.prompt-kind`
- `ed.prompt-suggestions`
- `ed.prompt-suggestion-rows`
- current-row/current-section/current-preview/current-position helpers
- prompt window/display/panel models
- status prompt fields
- the shared interaction prompt row

Direct script-origin `ed.prompt-submit` now refuses protected prompts unless `cap.prompt-write` is enabled. Same-origin script-created prompts still submit normally, including through the hostcall path, because the prompt’s captured origin is reused for the delayed submit.

One compatibility decision is intentional: script-origin `ed.prompt-set` can still replace a trusted prompt, but doing so stamps the prompt as script-originated. The script does not learn the previous prompt text, and the eventual submit runs under script authority rather than trusted user authority. That preserves the older prompt-control workflow while keeping the read/submit boundary closed.

## Why this matters

Prompt state often contains exactly the short-lived secret or intent that a user has not submitted yet: a file path, a destructive command, a URL, a search term, or a selected picker row. Treating it like a normal protected register keeps it aligned with marks, macros, undo/redo, recent rows, active search, and message history.

## Validation evidence

Focused validation in this cloudtainer included:

- `tests/test_editor_prompt_authority.py`
- the script prompt taint regression in `tests/test_editor_script_context_fs_caps.py`
- existing prompt completion, command-palette, prompt-history, screen-layout, statusline, search, interaction, and message-log authority tests

The broader prompt/command/status set passed after the hostcall-origin path was adjusted so script-owned prompt flows continue to work while protected prompt reads/submits fail closed.

## Remaining risk

The prompt mutation compatibility rule should stay under observation. It prevents old prompt-control workflows from breaking, but it still lets a script replace visible prompt text. The important safety property is that replacement does not disclose the previous text and does not regain trusted submit authority. If future policy wants stricter UI integrity, `cap.prompt-write` can be expanded from protected-submit authority to protected-mutation authority too.
