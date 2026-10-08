# Frontier salience snapshot — 2026-03-21-135

This pass did **not** add another ranking dashboard, maintainer-funding program, or social governance crate.
It sharpened **P-0011 Crate Health Contract Kit** into a more maintenance-aware stewardship contract.

## Why this frontier moved up

The official Rust ecosystem story is now precise enough that the sharper missing layer is increasingly obvious:

- the 2026 Inside Rust post on maintenance says maintenance is not one blob, but a diverse mix of issue triage, bug fixing, CI breakage work, security response, performance-regression handling, dependency updates, docs upkeep, review, refactoring, and contributor enablement;
- the 2025 State of Rust survey says worries about developer and maintainer support ticked upward;
- Cargo’s manifest docs still expose maintenance status mainly as a badge-era declaration and explicitly note that crates.io does not currently use it;
- the long-running crates.io issue on moving maintenance status into the UI/API exists precisely because release-bound metadata goes stale;
- crates.io now has stronger imported signals such as the Security tab, Trusted Publishing improvements, SLOC, and `pubtime`, but those still do not answer who actually owns invisible maintenance work.

That combination means the missing crate is not merely “show more activity metrics.”
The missing crate is now a **maintenance-aware health contract** that can publish **maintenance coverage**, **duty-map gaps**, and **visible-versus-invisible stewardship balance** above today’s scattered signals.

## Main conclusion

Promote **P-0011** upward again, but keep it narrow.
The next worthy move is not more popularity heuristics and not another maintainer score.

It should stay focused on:

1. freezing support and stewardship claims into a conservative contract,
2. making **keep-the-lights-on** versus **enable-evolution** work explicit,
3. making duty ownership or coverage gaps visible,
4. and downgrading health claims when important maintenance classes are still unowned or only inferred from activity.

## Ranked near-term frontier from this pass

1. **P-0011 Crate Health Contract Kit** — strengthened because maintainer-support pressure is real while the sharper missing layer is now duty-map and maintenance-coverage truth above registry/repo signals.
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strong because downstream selection still wants a compact choice surface, but should import rather than replace health truth.
3. **P-0515 Crate Off-Ramp Pack Kit** — still strong because stewardship gaps are most painful exactly when users need successor and exit clarity.
4. **P-0017 Trust Lens** — still strong because trust/security signals remain adjacent but should not masquerade as support or coverage promises.
5. **P-0483 Public API Readiness Bundle Kit** — still strong because healthy stewardship and safe release posture remain adjacent but distinct truths.

## Keep these boundaries sharp

- **P-0011** is the broad receiver-facing stewardship and maintenance contract.
- **P-0509** is task-fit and decision-pack guidance.
- **P-0515** is leaving/migrating a dependency.
- **P-0017** is trust, provenance, and security-adjacent risk.
- **P-0483** is release readiness.

Do not let “crate health” flatten those lanes into one fake crate.
