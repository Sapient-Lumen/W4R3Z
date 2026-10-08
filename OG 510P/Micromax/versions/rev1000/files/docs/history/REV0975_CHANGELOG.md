# Revision 0975 changelog

## Regex child memory containment

- Reproduced fast regex-native memory growth that completed before the existing
  foreground deadline.
- Added a central 144 MiB post-request memory-headroom default to every shared
  regex worker request.
- Added Linux child-owned `RLIMIT_AS` enforcement before regex compilation and
  matching, with lower inherited limits preserved.
- Classified allocation failure as the stable `memory-limit` operation kind and
  verified immediate fresh-worker recovery.
- Added a prebuilt failure envelope for the final response-serialization edge at
  address-space exhaustion.
- Kept resource mutation out of the pure executor and avoided threaded-parent
  `preexec_fn` hooks.

## Audit and refactor

- Removed substitution-budget UTF-8 byte copies and pre-acceptance source slices.
- Added exact allocation-free UTF-8 range counting with early stop and an ASCII
  fast path.
- Corrected the generated effect contract so `re.escape` no longer falsely
  advertises worker timeout or memory ownership.
- Added regressions for default and tuned memory ceilings, stable failure,
  recovery, pure-executor process-limit isolation, surrogate accounting, and
  allocation-before-denial removal.

## Handoff

- Added `docs/932-regex-worker-address-space-headroom.md` and decision D29.
- Updated the mission, risk boundary, roadmap, worklist, research notes, revision
  index, current handoff, and archive evidence.
