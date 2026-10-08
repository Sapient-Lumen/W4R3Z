# Retiming macros (speed up / slow down)

VHK recordings often contain explicit `Delay` steps and sometimes `RandomWait`.
Other macro ecosystems commonly provide a "play faster/slower" knob or speed
multiplier:

- Pulover's Macro Creator exposes **Speed Up / Slow Down** keys with a
  configurable multiplier (often used at 2x).  
  See PMC FAQ: "Can I make playback go faster/slower?".
- AutoHotkey provides global delay controls like `SetKeyDelay` and
  `SetMouseDelay`, which are a popular way to make macros less brittle or
  easier to debug.

VHK's runtime `runner_profile: turbo` scales some *incidental* per-step delays,
but it intentionally does **not** rewrite explicit `Delay` steps.

Use `vhk retime` to post-process a macro YAML and scale explicit delays.

## Examples

### Speed up a recording (2x)

```bash
vhk retime macros/login.yaml --speed 2.0 --out macros/login_fast.yaml
```

`--speed 2.0` means "twice as fast", so explicit delays are divided by 2.

### Slow down a recording (debugging)

```bash
vhk retime macros/login.yaml --factor 2.0 --min-ms 10 --out macros/login_slow.yaml
```

This doubles explicit delays, and also ensures no delay becomes smaller than
10ms.

### Bulk retime a project

```bash
vhk retime-project . --speed 1.5 --out-dir macros_retimed
```

## What gets scaled

By default, `vhk retime` scales:

- `Delay.ms`
- `RandomWait.min_ms` / `RandomWait.max_ms`
- per-step `delay_ms` (common base field)
- `retry_delay_ms`
- `TypeText.delay_ms_per_char`

These are the places users typically tweak when they say "make playback faster".

### Timeouts are *not* scaled by default

Wait steps (e.g. `WaitForImage`, `WaitForText`, etc.) include fields like
`timeout_ms`, `poll_ms`, and `jitter_ms`. Retiming those values can make macros
flaky if the UI is slower than expected.

If you want to scale those fields anyway, opt in:

- `--include-timeouts`
- `--include-polling`

## Non-numeric delay expressions

Delay values can be variables/expressions like `${delay_ms}`.
Retiming only scales delays that are numeric literals (including numeric
strings like `"250"`). Interpolated expressions are left untouched.
