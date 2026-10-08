# Local-first Sync Kit — lane boundaries (2026-03-21)

This note keeps **P-0076 Local-first Sync Kit** from collapsing into generic “CRDT support”, “P2P support”, or “collaboration platform” language.

## What P-0076 owns

**P-0076** is the receiver-facing coordination contract above local-first substrate.
It owns the artifacts that tell another team:

- which durable repo/profile was in play,
- what durable sync state each replica had,
- what transport/bootstrap route was used,
- what membership/key epoch applied,
- what presence/awareness state can and cannot claim,
- what history/branch retention posture survived export or compaction,
- and why a session converged, stalled, or became only partially comparable.

## Distinct from CRDT engine crates

`automerge`, `loro`, and `yrs` are engine substrate.
They define document/update/history behavior.

**P-0076** sits above them and publishes the coordination artifact another team can review without assuming one engine forever.

## Distinct from repo/runtime plumbing

Automerge Repo / `samod` / Yjs/Yrs transport helpers are “live document” or wiring substrate.
They are important proving grounds.

**P-0076** is not another repo runtime.
It records which runtime posture was actually in play and how much of that posture is durable, ephemeral, or exportable.

## Distinct from transport substrate

`iroh`, websocket providers, relay services, and reliable ordered stream assumptions are transport substrate.

**P-0076** may import those facts, but it is about the **receipt** for direct/relay/bootstrap/session behavior, not about replacing transport stacks.

## Distinct from membership / encrypted-group substrate

MLS / OpenMLS or app-specific membership layers govern key epochs, removals, and forward-secrecy posture.

**P-0076** may import them, but it should not claim to solve authorization or private-group design by itself.
It reports which membership epoch and removal posture applied.

## Distinct from presence / awareness implementations

Awareness, cursors, typing indicators, and peer metadata are often session-level or best-effort surfaces.

**P-0076** should publish whether those surfaces are durable, persisted, identity-strong, or exportable.
It should not silently promote ephemeral presence into durable sync truth.

## Distinct from history/version-control engines

Some engines expose branches, checkout/time travel, and rich version control; some mostly expose update exchange and frontier/state-vector comparators; some export shallow snapshots that keep current state while narrowing history reach.

**P-0076** should record the resulting history-retention posture.
It should not silently flatten “supports sync” into “supports durable branching and historical comparison forever”.

## Distinct from bundle substrate

The archive’s bundle/evidence lanes can define reusable containers and signing/redaction substrate.

**P-0076** should reuse that substrate where possible.
Its missing value is the local-first contract inside the bundle, not a brand new forever-container.

## Working rule for future revisions

When touching local-first work, keep these truths separate:

1. durable document state,
2. ephemeral presence/awareness state,
3. history/branch retention posture,
4. transport/bootstrap/session posture,
5. membership/device epoch truth,
6. and support-bundle export policy.

Do not let them collapse into one fake “sync support” story.
