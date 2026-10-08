# Frontier salience snapshot — 2026-03-20 (104)

This pass did **not** add another warning family, another review queue, or another publication gate.
It deepened **P-0514 Crate Upgrade Pack Kit** by making one more receiver-facing truth explicit:

- **config-basis truth** — upgrade packs can now say which Cargo config layers or override surfaces materially shaped what the lane resolved or built, and whether that basis was checked into the repo, injected by CI, local to one user, or only present on an ephemeral command line.

## Main judgment

After lineage, capture context, lane selection, session honesty, replay bridges, export posture, public traceability, durable cues, freshness, and review provenance became explicit, one ordinary lie still remained:

1. a lane could still sound like ordinary reviewed Cargo behavior when hidden config hierarchy or override surfaces changed what it actually witnessed,
2. and an opaque `env` digest could still stand in for a real receiver-facing account of what hidden basis mattered.

Those are not small metadata details.
They are ordinary ways an upgrade-support artifact can overstate how portable or upstream-representative its witness family really is.

## Why this beat nearby work again

The archive already had enough to say:

- what was imported,
- which capture/session produced it,
- how it could be replayed,
- and how public readers could trace exported claims.

What it still lacked was one compact way to say:

- “this lane depended on checked-in `.cargo/config.toml`,“
- “this result was shaped by `[patch]` or source replacement,”
- “this baseline was CI-only rather than ordinary developer default,”
- or “do not summarize this as a default crates.io/toolchain witness.”

That is a real product refinement, not another naming flourish.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — stronger again because hidden Cargo config and override basis can no longer piggyback on ordinary-looking commands.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
