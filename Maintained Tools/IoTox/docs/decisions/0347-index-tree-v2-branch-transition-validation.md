# ADR 0347: Index tree-v2 branch transition validation by path

Status: accepted. Implemented 2026-09-09.

## Context

Tree-v2 branch acceptance must prove two separate safety properties before accepting a successor:

- carried historical entries must already be authenticated by the current frontier or by exact
  observed proof branches; and
- a branch must not drop an observed prior value for a path unless it introduces a new local event
  for that path.

The existing implementation enforced those rules correctly, but it repeatedly searched complete
baseline, successor, and proof manifests while checking each successor entry and each baseline path.
After ADRs 0345--0346, this was the remaining obvious local manifest-search hotspot in branch-store
transition validation.

## Decision

Build per-path indexes for the successor manifest, the optional merged baseline, and each exact
observed proof manifest inside `validate_successor_transition()`.

The transition rules are unchanged:

- new entries from the successor's writer/generation are allowed as the local event for that branch;
- non-local carried entries must appear in the indexed baseline or one indexed exact proof branch;
- baseline paths not mentioned by the successor remain available to the merge frontier and are not a
  silent drop; and
- when the successor does mention a baseline path, any observed omitted value is refused unless that
  path also has a new local replacement event.

No branch format, signature domain, merge semantics, storage layout, witness rule, or peer protocol
changes.

## Consequences

Branch acceptance does less repeated allocation and searching when large manifests carry many
historical values. This matters for read-write sync catch-up and checkpoint/recovery flows where
branches legitimately preserve substantial prior state.

This still does not implement path-level incremental source scanning, sparse branch records, or a
durable manifest index. The index is local to one validation call and is discarded before return.

## Evidence

The owned unit/integration registry now includes a store-level grouped-history regression: a remote
branch carries 128 historical paths from an exact observed branch and adds one new local value. The
branch-store accept path must authenticate every carried value through the indexed baseline/proof
logic.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
