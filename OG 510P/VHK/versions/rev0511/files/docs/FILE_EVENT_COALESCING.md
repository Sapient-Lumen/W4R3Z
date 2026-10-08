# File event coalescing

Linux file producers rarely emit one clean, final event. Editors, downloaders,
renderers, and export tools often create a temporary path, write in bursts,
rename into place, and then touch metadata again.

VHK already had `stable_ms` for **one path becoming ready**. This pass adds
`quiet_ms` for **the event stream going quiet**.

Use `stable_ms` when the workflow is about a single file finishing its write.
Use `quiet_ms` when the workflow is about a noisy burst settling down so the
macro should run once instead of reacting to every low-level edge.

## Surfaces

- `file_watchers:` supports `quiet_ms`
- `WaitForFileEvent` supports `quiet_ms`
- matched events now expose:
  - `file_batch_count`
  - `file_batch_paths`
  - `file_batch_names`
  - `file_batch_kinds`

## Example

```yaml
file_watchers:
  - name: render_done
    directory: renders
    pattern: "*.png"
    event: changed
    stable_ms: 200
    quiet_ms: 500
    macro: on_render_batch
```

With the example above, VHK waits for the first matching change, then keeps
resetting a 500 ms quiet window while more matching events arrive. When the
window finally elapses, it runs the macro once with the most recent event as
`file_event` / `file_path` and the ordered burst summary in `file_batch_*`.
