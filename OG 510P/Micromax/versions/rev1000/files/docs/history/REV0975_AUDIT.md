# Revision 0975 audit

## Priority judgment

Rev0974 explicitly named unbounded regex-child memory as the next measured
frontier. The failure was reproducible and severe: `(a?){1000000}$` over one
million characters completed before the normal regex deadline while reaching
roughly 140 MiB RSS; a three-million case reached roughly 386 MiB. Wall-clock
killability therefore did not own peak native allocation.

## Correction

- Every shared regex-worker request now carries a finite 144 MiB post-request
  address-space headroom default.
- Linux children lower both `RLIMIT_AS` limits after request decode and before
  compilation/matching; lower inherited limits win.
- `MemoryError` is a stable `memory-limit` operation failure, and one failed child
  cannot poison the next operation.
- A prebuilt bounded failure envelope remains writable if ordinary response JSON
  materialization itself runs out of headroom.
- The resource hook lives inside the fresh child instead of unsafe threaded-parent
  `preexec_fn` code.
- The pure executor remains side-effect free; both actual worker adapters enter
  the limited wrapper.

## Audit/refactor finding

Regex substitution budgeting still allocated temporary UTF-8 byte copies and
source slices before deciding whether output fit. It now performs exact
allocation-free UTF-8 preflight with an ASCII fast path, stops at first overrun,
and constructs slices/output only after acceptance.

The generated effect contract also treated every regex-named hostcall as a
worker operation. `re.escape` is local, so its row now advertises only its real
input/result budgets rather than a timeout and address-space owner it never uses.

## Scope

This is Linux regex-child memory containment, not total heap control, RSS policy,
cgroups, syscall filtering, crash isolation, or hostile-plugin sandboxing.
Parent request serialization and child JSON decode precede the post-request
ceiling; other platforms retain the existing killable timeout/result boundary.

## Research

Reviewed Python `resource` and `subprocess` documentation, Linux `getrlimit(2)`,
CPython `_sre` allocation state and issue history, and the current `re` API.
Details and source links are in
`docs/932-regex-worker-address-space-headroom.md`.

## Recommended next correction

Measure a plugin-accessible blocking native call, crash, or syscall journey—or a
real pre-decode child-memory failure—before adding a broader process/Wasm host.
