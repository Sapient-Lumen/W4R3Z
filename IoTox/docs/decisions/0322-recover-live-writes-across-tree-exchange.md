# ADR 0322: Recover live writes across a tree-v2 exchange

- Status: accepted and implemented
- Date: 2026-09-03

## Context

Tree-v2 signs a pending workspace state before atomically exchanging a complete derived directory,
then signs the new stable state. A process or power interruption can leave either exact side, and
existing recovery joined those layouts. The persistent three-writer campaign exposed an additional
ordinary-writer race: an application changed the newly visible directory after the exchange but
before the stable workspace record was committed.

The signed state named active cycle 1 and pending cycle 2. The reserved staging directory was an
exact active projection, the visible projection marker named pending cycle 2, and the visible file
contained the user's intact cycle-3 edit. Exact-side-only recovery correctly refused ambiguity, but
could not make progress without discarding data or manual surgery.

## Decision

Before constructing the sync worker or exposing network service, load every writable/bidirectional
tree-v2 automation record. If its signed workspace is pending, acquire the namespace transaction
and run the existing reconciliation path. Startup fails closed on any unresolved state.

Recovery now recognizes one additional layout: the visible tree has the exact pending projection
marker and passes a structurally valid scan relative to the pending manifest, but contains local
changes, while any retained staging directory is the exact expected pre-exchange worktree with the
active marker. This proves the exchange orientation. Remove only that exact old staging tree,
finish the signed pending transition, preserve the visible local bytes, and let the same
reconciliation publish them as a new higher writer generation. No state is rewound.

A locally changed active-marker tree before exchange remains ambiguous and fails closed. A changed
or unrecognized staging tree also remains untouched and fails closed.

## Consequences

The existing owned exchange-recovery check now also proves that a post-exchange local edit survives
recovery and that the pre-exchange ambiguous case still refuses; the direct registry remains 831.
The accepted
persistent-ext4 VM then crossed 24 alternating writers; cycle 24 hit the 30-second journal-pressure
watchdog, restarted the exact writer, preserved its edit, reconfirmed both sessions, and converged
before the maintenance lifecycle completed.

This closes the observed path-based local-write/restart case, not arbitrary application I/O across
a directory swap. A process retaining an open descriptor to the old tree can continue writing the
reserved staging inode after exchange; if that makes the old side non-exact, IoTox refuses rather
than deleting it. Native filesystem watching, an explicit quiescence/lease mechanism, or a future
projection architecture is still needed for a stronger continuously writable-tree contract.
