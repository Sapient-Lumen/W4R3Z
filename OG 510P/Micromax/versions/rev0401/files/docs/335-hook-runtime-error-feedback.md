# Hook runtime error feedback (rev393)

Editor lifecycle hooks (`ed.pre-action`, `ed.on-action`, `ed.on-open`,
`ed.on-save`, `ed.on-change`) are intentionally best-effort notification
surfaces: handlers run in the embedded VM, stack effects are discarded, and the
editor keeps going even if a hook blows up.

That boundary was already correct, but the message dialect lagged behind the
rest of the trust-first cleanup. Hook faults still surfaced as:

- `hook NAME error: DETAILS`

Rev393 keeps the behavior small but makes the message more self-identifying:

- `hook NAME: error: DETAILS`

That keeps failing hooks searchable and attributable in exactly the same shape
as nearby scripted surfaces like:

- `command NAME: error: DETAILS`
- `only: error: DETAILS`
- `closeall: error: DETAILS`

The change is intentionally tiny: it does not alter control flow, recovery, or
hook semantics. It only makes the failure surface easier to scan in logs,
headless tests, and future LLM-driven debugging loops.
