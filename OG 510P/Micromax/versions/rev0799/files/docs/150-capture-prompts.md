# Capture prompts + recovery contract (rev209)

Micromax already had real **capture keymodes** for confirm-each replacement (`qreplace`) and external-link confirmation (`openurl`).

Before rev209, those flows were semantically real but visually under-described: the active keymode intercepted keys, yet the bottom chrome could still look mostly idle unless an ordinary prompt object happened to exist.

Rev209 makes that surface more honest while keeping the implementation tiny.

## Editor/model side

The editor now exposes two tiny helpers:

- `current_capture_key_mode() -> str | None`
- `current_key_mode_capture() -> bool`

And `status_model()` now reports capture state a little more explicitly:

- `mode` prefers the active capture keymode when there is no ordinary prompt
- `keymode` continues to expose the top active keymode name
- `keymode_capture` is `1` when that top keymode is a capture/confirmation layer

This keeps the shared status snapshot truthful for scripts, tests, future UIs, and future LLMs without inventing a larger prompt subsystem.

## TUI side

The curses TUI now has one tiny helper:

- `capture_prompt_text(ed, width=...)`

When no ordinary prompt is active but a capture keymode is active, the bottom prompt row now renders a one-line summary for the current flow.

Current cases:

- `qreplace` → compact `?replace ... | search -> replacement` style summary
- `openurl` → compact `?open external link ... | URL` style summary

This row still appears even when `infobar=false`, because an active confirmation loop is not the same thing as idle chrome.

## Keymenu behavior

`keymenu_text()` now switches to capture-aware hints:

- `qreplace`: `Y/Enter Replace`, `N Skip`, `A All`, `L Last`, `Q/Esc Quit`
- `openurl`: `Y/Enter Open`, `N/Esc Cancel`, `C Copy`

That keeps the recent `keymenu` / `infobar` / `statusline=false` work coherent: the bottom rows now describe the active interaction rather than the idle editor.

## VM follow-up: `catch` must unwind return-stack depth too

While adding the portability follow-up for rev209, Micromax exposed a real VM bug: `catch` restored the data stack on `throw`, but it did **not** trim the return stack back to the entry depth.

That meant a protected quotation like:

```text
: boom 1 >r 99 throw ; [ boom ] catch rdepth
```

could incorrectly leave `rdepth = 1` after recovery.

Rev209 fixes that by saving the entry return-stack depth and truncating `vm.rstack` back to that depth when a `MicromaxError` escapes the protected quotation.

## Portability case

New JSON corpus case:

- `catch-throw-restores-return-stack-depth`

Source:

```text
: boom 1 >r 99 throw ; [ boom ] catch rdepth
```

Expected stack:

```text
[99, 0]
```

That keeps the recovery contract easy to replay in future Rust/WASM hosts without scraping Python tests.
