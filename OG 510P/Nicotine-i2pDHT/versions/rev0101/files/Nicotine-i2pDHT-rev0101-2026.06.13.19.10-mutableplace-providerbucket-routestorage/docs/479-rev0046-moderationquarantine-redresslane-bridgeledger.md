# rev0046 — moderationquarantine-redresslane-bridgeledger

This revision puts the subjective-maintainer/policy problem into executable cube surfaces instead of handwaving it away.

The design stance is deliberately narrow:

> A key can be refused by a local bridge, garden, official build, or policy capsule without being erased from the DHT's cryptographic reality.

The new lane is not global reputation. It is not DHT truth. It is local side-effect gating for high-risk public bridge behavior.

## New code surfaces

- `moderationquarantine` — signed scoped moderation capsules: warn, watch, deny, freeze.
- `redresslane` — signed appeal/counter-evidence receipts that can lift, narrow, or watch a local block.
- `bridgeledger` — local signed ledger entries joining shadow-fire, egress, moderation, and redress before future public bridge side effects.
- `moderationfold` — current-revision audit preserving rev0045 bridgeepoch/keyreceiptlane/shadowfire predecessor history.

## Strongest sentence

A subjective ban is not DHT truth, and a redress lift is not magic; both are scoped local evidence that must bind to the exact side-effect boundary.

## Risk-first tests

The tests cover replay, rollback, same-sequence fork, previous-link mismatch, profile/service/scope/request drift, bad signatures, active moderation blocks, redress hard-negative pressure, egress rejection, and component-digest drift.
