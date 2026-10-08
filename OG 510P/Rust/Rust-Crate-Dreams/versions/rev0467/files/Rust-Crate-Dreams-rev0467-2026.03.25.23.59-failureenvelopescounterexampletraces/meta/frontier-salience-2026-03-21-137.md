# Frontier salience snapshot — 2026-03-21-137

This pass did **not** add another advisory client, RSS mirror, or crates.io policy proposal.
It sharpened **P-0017 Trust Lens** into a more watch-aware dependency-trust contract.

## Why this frontier moved up

The Rust trust surface is now precise enough that the sharper missing layer is increasingly obvious:

- the January 2026 crates.io update says crate pages now have a **Security** tab that shows RustSec advisories and affected version ranges;
- the same update says crate owners can now enable **Trusted Publishing Only Mode**, which changes publish-identity posture but not the whole trust story;
- the February 2026 malicious-crate policy update says the crates.io team will **no longer publish a blog post for each malicious crate**, will **always** publish a RustSec advisory when a crate is removed for containing malware, and explicitly points readers to the **RustSec advisory RSS feed**;
- high-signal malware cases may still get both a blog post and a RustSec advisory, meaning blog coverage and advisory coverage are no longer the same class of watch surface;
- and the 2025 State of Rust survey still shows ecosystem-support pressure, which increases the practical need for boring, reviewable trust-watch posture rather than “someone will probably notice.”

That combination means the missing crate is not another trust score.
The missing crate is now a **reviewable trust-watch layer** that can publish **notification-channel coverage**, **change-class coverage**, and **feed-gap honesty** above today’s registry, advisory, and audit substrate.

## Main conclusion

Promote **P-0017** upward again, but keep it narrow.
The next worthy move is not more scoring and not another incident feed reader.

It should stay focused on:

1. freezing which watch channels were actually consulted,
2. making **coverage by change class** explicit,
3. warning when routine malware removal, publish-identity drift, or known-vulnerability watch depends on an unconfigured or partial channel,
4. and downgrading trust posture when a team is relying on a channel that is explicitly not comprehensive for the claim being made.

## Ranked near-term frontier from this pass

1. **P-0017 Trust Lens** — strengthened because trust signals are more useful than before, but also more distributed, so another team now needs a boring watch-coverage contract rather than another badge or score.
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still unusually strong because crate-choice bundles should eventually import, not reinvent, trust-watch artifacts.
3. **P-0011 Crate Health Contract Kit** — still strong because stewardship signals remain adjacent but should not masquerade as trust watch.
4. **P-0515 Crate Off-Ramp Pack Kit** — still strong because trust failures often end in migration work, but off-ramp owns the leaving workflow, not the watch surface.
5. **P-0483 Public API Readiness Bundle Kit** — still strong because release-review evidence remains adjacent but should not absorb dependency-trust watch duties.

## Keep these boundaries sharp

- **P-0017** is the graph trust / notification coverage / review debt bundle.
- **P-0509** is choice and frozen-decision guidance.
- **P-0011** is stewardship and maintenance coverage.
- **P-0515** is successor and exit planning.
- **P-0483** is public-release readiness.

Do not let “dependency security monitoring” flatten those lanes into one fake crate.
