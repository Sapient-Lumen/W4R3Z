# Frontier salience snapshot — 2026-03-20 (110)

This pass did **not** add another advisory client, another score dashboard, or another crates.io policy wish list.
It deepened **P-0017 Trust Lens** by making one more ecosystem-wide truth explicit:

- **trust posture is only reviewable when identity risk, signal provenance, assumptions, and residual review debt stay distinct**.

## Main judgment

The sharper missing layer is no longer “a Rust trust score.”
The sharper missing layer is a **reviewable trust bundle** for dependency decisions.

The current Rust/security substrate has changed enough to make that specific:

1. crates.io now exposes a Security tab and stronger Trusted Publishing posture,
2. malicious-crate reporting now routes routine incidents through RustSec advisories and RSS,
3. recent 2026 advisories show active typosquat / impersonation campaigns,
4. Cargo Sherlock makes trust assumptions explicit and machine-checkable,
5. Cargo Scan shows that many crates can be classified automatically while the dangerous remainder still carries concentrated manual-review debt,
6. and cargo-vet keeps trusted audit sharing practical without pretending that audit import alone publishes whole-graph trust posture.

That means the next worthy move is not “more score sophistication.”
It is a joined, conservative trust contract above those surfaces.

## Why this beat nearby work

The archive already had adjacent lanes for:

- pathfinder choice,
- crate health / support posture,
- off-ramp planning,
- upgrade review,
- public API readiness,
- and general supply-chain / publish receipts.

What it still lacked was one compact way to say:

- “this graph contains a confusable identity risk even though the registry surface looks otherwise ordinary,”
- “these trust cues came from distinct sources and should not be flattened into one verdict,”
- “these assumptions are carrying the result,”
- and “manual review is still owed here, even after imported audit signals.”

That is a real product boundary, not just another security checklist.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because freezeable choice compounds first.
2. **P-0514 Crate Upgrade Pack Kit** — still strongest among release-support lanes because migration truth remains broadly under-specified.
3. **P-0017 Trust Lens** — newly stronger because 2026 registry/advisory/security substrate makes joined trust posture more buildable and more urgent.
4. **P-0011 Crate Health Contract Kit** — still very strong because support/succession posture remains distinct from trust/risk posture.
5. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown/drain truth remains under-served and broadly useful.
