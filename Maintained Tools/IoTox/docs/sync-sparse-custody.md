# Tree-v2 sparse and on-demand custody

Status: ADRs 0295--0297 implement sparse custody, on-demand widening, complementary primary-lane
sources, and durable health. Complete signed metadata and selected content transfer, policy-safe
widening, repair, GC, status, exact-probe availability, signed health, and local commands are live.

## Commands

Inspect one node's local interest:

```bash
iotox sync-interest field-notes
```

Replace the complete local rule set:

```bash
iotox sync-interest field-notes \
  include=documents include=scripts exclude=documents/cache
```

Restore complete projection and content-custody intent:

```bash
iotox sync-interest-clear field-notes
```

An interest mutation does not itself contact a peer. Fetch the selected closure now with:

```bash
iotox sync-pull PEER field-notes
iotox sync-pull-multi PRIMARY field-notes SECONDARY [SOURCE...]
iotox sync-status
iotox sync-repair field-notes
iotox sync-health field-notes
```

Writable or bidirectional automation will also use the new policy on its next cycle. The explicit
pull is preferable when the operator wants immediate, attributable backfill.

When one sparse source may not hold the complete selected closure, register every expected source
atomically:

```bash
iotox sync-pull-multi laptop field-notes desktop nas
```

The primary supplies the signed frontier. Each other source can satisfy exact immutable objects from
that frontier but cannot replace it. `sync-source-add JOB FRIEND` can extend an already active pull.
IoTox uses the existing authenticated exact-object result as its availability probe: absence at one
source advances that digest to the next, and exhaustion fails closed. Tree-v2 multi-source currently
uses ordinary primary Tox carriers; `sync-pull-multi-route` remains content-v2-only.

Rules are relative canonical component prefixes, never globs. Empty includes mean the complete tree;
exclude wins. Supplying rules replaces both old sets atomically—it does not append. Each node chooses
its own rules, and a peer has no command or wire field that can select another node's path or local
destination.

## What “partial” means

A sparse pull still holds and verifies the complete reachable branch/manifest history needed to
understand writers, causality, tombstones, and conflicts. It may omit immutable file bytes that no
selected path needs. Consequently:

- `state=complete custody=partial` means protocol work completed for this node's exact current
  interest, not complete-replica convergence;
- `sync-conflicts` can show path, writer, generation, kind, digest, size, and mode for an omitted
  candidate without possessing or exposing its bytes;
- `sync-repair` verifies selected unique objects and reports declared/selected/skipped coverage;
- `sync-gc` retains all signed metadata but roots only selected content. Skipped bytes already on disk
  may enter recoverable quarantine;
- a pin preserves the selected content closure under the policy used by maintenance. It does not
  promise that omitted bytes exist here;
- a sparse node is not a backup, and clearing interest is not proof that a peer can still supply
  everything.

`sync-status` emits one `tree-job=` record with custody and coverage counters for every retained
tree-v2 pull, including `reconcile-` prefixed local apply counters after completion. `sync-interest`
emits `projection-current=0` while the worktree marker still represents an older policy. A
successful pull/reconcile installs the newly selected projection atomically and makes the marker
current. Repeated no-op subscriber applies keep a volatile in-process source digest cache, so stable
selected files are still observed but do not need to be re-hashed on every unchanged pull cycle.

## Safe policy transition

The worktree marker commits the manifest plus metadata/include/exclude policy. On the first scan
after a rule change, an absent path that was present in the signed baseline is retained rather than
published as a deletion. Existing files newly brought into scope become normal local events. The
subscriber fetches selected remote bytes, then the ordinary signed-branch and directory-exchange
path establishes the new marker. Once current, later file removal creates the expected tombstone.

This transition rule intentionally prefers a delayed deletion over accidental data loss. If the
marker is absent, obsolete, or ambiguous, IoTox preserves baseline absence for one reconstruction
cycle and rebuilds the exact marker.

## Health and remaining performance work

ADR 0296 deliberately uses serial exact probes rather than a new availability bitmap: correctness is
bounded, but a source with many misses can add one request/response round trip per object. Tree-v2
range/auxiliary lanes and parallel source scheduling remain performance work. ADR 0297 closes the
correctness gate with `sync-health`: a content-free signed record covers desired and verified
selected custody, source absence/exhaustion, conflicts, active-store pressure, workspace convergence,
and automation stalls. ADR 0350 makes positive sparse source scans selection-targeted: existing
ancestor directories are observed, included roots/subtrees are scanned directly, and unrelated
sibling branches below selected ancestors are not descended during source publication. Complete
interest still performs the full source walk, projection exchange still preserves unselected local
files, and `sync-publish` reports source-walk, digest-reuse, CAS, selected-projection, conflict, and
preservation counters. IoTox preserves the distinction between metadata knowledge, selected custody,
complete custody, and versioned recovery custody. See `sync-health.md`.
