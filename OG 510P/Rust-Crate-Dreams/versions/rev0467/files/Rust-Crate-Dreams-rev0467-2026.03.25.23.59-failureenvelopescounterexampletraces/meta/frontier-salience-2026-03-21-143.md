# Frontier salience snapshot — 2026-03-21-143

This pass did **not** add another CRDT engine, another transport stack, or another “local-first platform”.
It deepened **P-0076 Local-first Sync Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- Automerge explicitly supports old-version comparison, branches, and merging, while Automerge Repo also exposes **ephemeral** messages that have **no delivery guarantee** and are **not persisted**;
- Yrs’ sync protocol is explicitly modeled around an `Awareness` structure, which makes collaboration-state handling separate from raw document state;
- Loro now presents version control, checkout/time travel, and export modes including **shallow snapshots** that keep current state while narrowing history reach.

That combination means “supports local-first sync” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. durable sync-state truth,
2. presence/awareness truth,
3. history-retention / branch truth,
4. transport/bootstrap/session truth,
5. and membership/key-epoch truth.

## Main conclusion

Promote **P-0076** upward again, but keep it narrow.
The sharper next move is not a universal collaboration framework.
It is a boring contract that keeps **durable state**, **ephemeral presence**, and **history retention** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0076 Local-first Sync Kit** — strengthened because the ecosystem now clearly splits durable sync, ephemeral presence, and history-retention truth across real substrate.
2. **P-0532 Async Runtime Assurance Profile Kit** — still strong because runtime-family choice remains one of the biggest cross-cutting missing support contracts.
3. **P-0533 Error Surface Contract Kit** — still strong because error identity/audience/remediation/sensitivity remain broadly under-specified.
4. **P-0521 Crate Resource Surface Pack Kit** — still strong because retained-capacity truth continues to be a major support gap.
5. **P-0017 Trust Lens** — still strong because collaboration stacks still need honest watch/identity coverage, but that is a separate lane from local-first coordination artifacts.

## Keep these boundaries sharp

- **P-0076** is durable sync state + presence posture + history retention + transport/bootstrap + membership epochs.
- raw CRDT engines are separate substrate.
- transport stacks are separate substrate.
- presence frameworks are separate implementation layers.
- bundle substrate remains separate from the local-first contract itself.

Do not let “local-first” flatten those into one fake crate.
