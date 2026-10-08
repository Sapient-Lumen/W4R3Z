# Text input and turbo mode

VHK started with a single `TypeText` step that delegated to the active keyboard
backend. That works for many cases, but real desktop automation tools usually end
up needing more than one text-injection path.

This revision adds two practical ideas inspired by other tools:
- **multiple text backends** for one logical `TypeText` step
- a narrow **turbo playback profile** that reduces incidental delays without
  weakening waits/assertions

## `TypeText` backends

`TypeText` now supports these modes:

- `backend: auto`
  - uses the normal keyboard backend by default
  - when the project uses `runner_profile: turbo`, VHK may switch large printable
    text to clipboard-paste automatically
- `backend: native`
  - use the normal keyboard backend (`xdotool`, `wtype`, or `ydotool`)
- `backend: clipboard`
  - write text to the chosen clipboard selection and paste it using a shortcut
- `backend: xvkbd`
  - X11-only fallback using `xvkbd -file ... -utf16`

Example:

```yaml
- type: TypeText
  text: "${email_body}"
  backend: clipboard
  preserve_clipboard: true
  paste_shortcut: ctrl+shift+v
```

## Clipboard-paste typing

Clipboard mode is useful when:
- the text is large
- a widget accepts paste more reliably than per-character typing
- you want a terminal-friendly paste chord like `ctrl+shift+v`

Relevant step fields:
- `selection`: `clipboard` or `primary`
- `preserve_clipboard`: capture the previous text and restore it afterward
- `paste_shortcut`: `auto`, `ctrl+v`, `ctrl+shift+v`, or `shift+insert`

`auto` currently maps to:
- `clipboard` selection → `ctrl+v`
- `primary` selection → `shift+insert`

## Turbo profile

Project settings now support:

```yaml
settings:
  runner_profile: turbo
  turbo_delay_scale: 0.25
  turbo_type_clipboard_threshold: 80
```

Behavior today:
- per-step incidental `delay_ms` values are scaled by `turbo_delay_scale`
- `TypeText(delay_ms_per_char=...)` is scaled the same way
- `TypeText(backend=auto)` can switch to clipboard mode when the text is at
  least `turbo_type_clipboard_threshold` characters and looks like printable text

What turbo mode **does not** do:
- it does not shorten logical waits/timeouts
- it does not weaken assertions or retry logic
- it does not change explicit `Delay` / `RandomWait` steps that the macro author
  intentionally inserted as semantics rather than playback overhead

## Doctor support

`vhk doctor` now reports `xvkbd` alongside the other helper binaries so projects
can surface whether the alternate X11 text backend is installed.

## Recorder / optimizer bridge

VHK now has an explicit authoring-time bridge for this distinction too:

- recorder cleanup can reconstruct final intended text into `TypeText(...)`
- `vhk optimize --promote-paste-text` can then rewrite **long literal single-line**
  `TypeText` steps to `backend: clipboard` when you want throughput over strict
  typed-key semantics
- `vhk optimize --segment-paste-text` can split **structured literal form text**
  into a hybrid lane where large field chunks paste through the clipboard while
  `Tab` / `Enter` remain explicit key semantics

This bridge stays conservative on purpose:
- no `${...}` interpolation
- no `delay_ms_per_char`
- single-line bulk text promotion still skips embedded `Tab` / `Enter`
- hybrid segmentation only kicks in when large literal chunks exist on at least
  one side of a `Tab` / `Enter` boundary
