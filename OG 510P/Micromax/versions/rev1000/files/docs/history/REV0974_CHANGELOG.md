# Revision 0974 changelog

## Native text allocation preflight

- Reproduced a plugin-visible single-dispatch allocation bypass: bounded inputs to
  `s-replace` could project hundreds of megabytes before the generic hostcall
  result postcheck ran.
- Added exact prospective byte/cell checks before `s+`, `s-split`, `s-join`, and
  `s-replace` enter CPython's allocating string operations.
- Preserved operands on budget denial and retained established type-error
  precedence.
- Made malformed, boolean, fractional, or absent host-result tuning fail to the
  finite defaults; a genuine integer `<= 0` remains an explicit embedding opt-out.

## Shared bounded value rendering

- Added `micromax.value_text`, a deterministic UTF-8-accounted builder used by
  `to-str`, `s-format`, `.`, and `.s`.
- Stopped repeated references from expanding one modest list/string graph into an
  unbounded Python result inside one VM dispatch.
- Kept top-level `.` string output unquoted and kept denied operands inspectable.
- Prevented the generic host-result guard from decimal-rendering giant integers
  merely to measure them.

## Audit and refactor

- Replaced temporary UTF-8 byte copies in core source counting, regex input
  preflight, and editor query preflight with one shared allocation-free counter.
- Removed the duplicated core value renderer and routed all matching text
  surfaces through one implementation.
- Made `s-format` validate specifiers and address its argument window without
  allocating a specifier list or copying the stack slice.
- Added a fixed-size identity cache to `s-join` preflight so repeated aliases are
  not rescanned byte-for-byte and the defensive cache cannot grow with input.
- Recorded remaining traversal and constant-factor allocation risks rather than
  disguising this as complete memory containment.

## Evidence and handoff

- Added focused exact-fit, Unicode/surrogate accounting, shared-reference,
  300 MB projection, Linux `RLIMIT_AS`, giant-integer, debug-output, and plugin
  recovery regressions.
- Added `docs/931-string-preallocation-bounded-value-rendering.md` and decision D28.
- Updated the compact mission, host API, security boundary, roadmap, worklist,
  research notes, revision index, and generated handoff.
- Moved rev0966 and rev0967 root evidence triplets into `docs/history/` to keep
  the current archive landing inside the 64-document handoff ceiling.
