# Runner logging & safety controls

## JSONL event logs

When `settings.event_log: true`, the runner writes a JSONL timeline to
`<project>/logs/run_<run_id>.jsonl`.

Events include:
- `run_start`, `run_end`
- `step_start`, `step_end`, `step_retry`
- `wait_start`, `wait_attempt`, `wait_end`
- `image_search`, `pixel_search`, `ocr`, `screenshot`
- `input` (key/mouse/type)
- `notify`, `clipboard_*`, `shell`
- `i3_*`

The intent is to eventually power a Studio "timeline" and support bundles.

## Dry run

If `settings.dry_run: true`, the runner will skip side-effecting actions like:
- `RunShell`
- `Key/TypeText/Mouse*`
- `Notify`
- `ClipboardSet`

The runner still records events so you can sanity-check the control flow.

## Panic file

To mitigate runaway macros, the runner checks for a panic file before each step.

- Configure the path in `settings.panic_file` (default `/tmp/vhk_panic`).
- Create/remove the file via:

```bash
vhk panic
vhk unpanic
```

If the file exists, the runner aborts as soon as it reaches a step boundary.

## Error artifacts

When `settings.screenshot_on_error: true`, VHK now prefers the *last capture that
actually caused the failure* instead of taking a fresh screenshot after the fact.
It also writes a small `error_<macro>_<step>.json` context file next to the saved
PNG so failures are easier to inspect offline.

For `VisualAssert`, `VisualVerify` mismatches, and `WaitForRegionChange` timeouts,
VHK also writes a `.diff.png` image that highlights changed pixels in red and dims
ignored areas.


## New control-flow events

Recent revisions add structured events for control-flow blocks:
- `while_start` / `while_eval` / `while_end`
- `try_start` / `try_error` / `try_end` / `try_finally_start` / `try_finally_end`
- `loop_control` for `break`, `continue`, and `return`

These make it easier to explain why a loop stopped or which error path a macro took.
