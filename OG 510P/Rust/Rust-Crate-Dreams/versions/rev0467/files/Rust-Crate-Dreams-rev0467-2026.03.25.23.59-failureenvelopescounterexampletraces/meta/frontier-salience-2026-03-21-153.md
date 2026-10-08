# Frontier salience snapshot — 2026-03-21-153

This pass did **not** add another actor framework, another retry helper, or another shutdown cookbook.
It deepened **P-0095 Task Supervision & Restart Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- the Rust project still calls out async complexity and runtime lock-in as live ecosystem pain;
- Tokio exposes task groups, cancellation, and graceful-shutdown substrate, but not one shared restart/topology contract;
- `task-supervisor` proves there is real demand for task restarts, dead-task detection, and runtime control;
- `spry` proves startup/readiness and orderly restart conventions matter;
- `ractor-supervisor` proves OTP-style strategies, meltdown windows, and subtree-local policy are useful in Rust today;
- but the ecosystem still lacks one reviewable contract for **restart blast radius**, **trigger class**, **state reset**, **shutdown aftermath**, and **failure bundles**.

That combination means “supports supervised background tasks” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **supervision topology** truth,
2. **restart policy** truth,
3. **health / readiness basis** truth,
4. **state reset basis** truth,
5. **shutdown escalation** truth,
6. **failure bundle** truth.

## Main conclusion

Promote **P-0095** again, but keep it narrow.
The sharper next move is not another runtime and not another framework.
It is a boring contract that keeps **topology**, **restart policy**, **health/readiness**, **state reset**, **shutdown escalation**, and **failure bundles** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0095 Task Supervision & Restart Kit** — strengthened because the substrate is real but the contract layer is still missing.
2. **P-0520 Crate Lifecycle Surface Pack Kit** — remains strong because timeout aftermath and drain truth still need honest receivers.
3. **P-0073 Async Replay Debugger Kit** — remains strong because supervision incidents want replay/evidence without over-claiming.
4. **P-0532 Async Runtime Assurance Profile Kit** — remains strong because runtime choice and supervision policy are adjacent but distinct.
5. **P-0256 Evidence Bundle Core Kit** — remains strong because supervision incidents want portable, share-safe bundles.

## Keep these boundaries sharp

- **P-0095** is topology + restart policy + health/readiness + state reset + shutdown escalation + failure bundles.
- lifecycle/shutdown packs are separate.
- replay/debugging packs are separate.
- actor frameworks and worker libraries are separate.
- runtime-assurance receipts are separate.

Do not let “task supervision” flatten those into one fake crate.
