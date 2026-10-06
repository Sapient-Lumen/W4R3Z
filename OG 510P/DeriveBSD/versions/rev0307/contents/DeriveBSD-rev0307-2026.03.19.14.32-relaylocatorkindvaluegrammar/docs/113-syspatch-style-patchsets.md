# Signed, revertible patchsets (syspatch-style)

OpenBSD’s `syspatch` is a useful operational model:
- fetch
- verify
- install
- revert
…for **binary patches to the base system**, with rollback bundles created automatically.

References:
- `syspatch(8)` man page (fetch/verify/install/revert; rollback tarballs). https://man.openbsd.org/syspatch.8

## Why DeriveBSD should care

DeriveBSD’s ideal story is “rebuild everything”. Reality includes:
- urgent patches
- long rebuild times
- small targets (one library, one daemon)

A patchset lane provides speed without lying about provenance.

## DeriveBSD direction

A **patchset artifact** is:
- a signed bundle of file replacements (or binary deltas)
- scoped to a specific base set digest (or host generation digest)
- with an automatically-generated rollback payload
- time-bounded by policy (expiry)

Patchsets must be explainable:
- “which set/generation is being patched?”
- “which CVE/advisory is this for?” (metadata)
- “who approved this override?” (policy decision record)

## Relationship to emergency grafts

- Emergency grafts: a pipeline-level concept (new Plan + closure proof).
- Patchsets: a distribution/installation mechanism for small deltas.

See RFC-0081.
