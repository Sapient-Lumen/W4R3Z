# Dependency lifecycle transition lane boundaries — 2026-03-22

This note keeps **P-0535 Dependency Lifecycle Transition Kit** sharp and prevents it from collapsing into adjacent lanes.

## Main judgment

**P-0535** is about how dependency posture changes across system criticality, maturity, and release time.
Its distinctive truths are:

1. **criticality lane** — where a dependency is allowed to live,
2. **abstraction seam** — what boundary makes replacement plausible,
3. **transition posture** — retain, pin, freeze, fork, vendor, internalize, or replace,
4. **override authority** — where that posture is actually declared and who can review it,
5. **signal freshness / exception status** — whether imported context and waivers are still current enough to trust,
6. **lifecycle drift** — what changed between releases.

## What P-0535 must stay separate from

### Separate from trust scoring and malicious-crate triage
**P-0017 Trust Lens** asks whether a crate looks risky or needs more review.
**P-0535** asks where that crate is allowed to live in *your* architecture and what the exit plan is.

### Separate from MSRV and dependency-version floors
**P-0036 MSRV Workspace Lab** is about toolchain compatibility and command-family floors.
**P-0535** is about architectural placement and transition planning.

### Separate from crate off-ramp support
**P-0515 Crate Offramp Pack Kit** is about leaving one crate or moving to a successor.
**P-0535** is about a broader portfolio of dependency moves across system maturity and criticality.

### Separate from crate health / maintenance posture
**P-0011 Crate Health Contract Kit** is about support horizon and stewardship.
**P-0535** is about local architectural containment and replacement planning.

## Anti-flattening reminders

Do not say:

- “we can replace it later” without naming a seam,
- “the crate is trusted” as if trust solved placement,
- “we pinned the lockfile” as if pinning solved lifecycle planning,
- “there is a local `[patch]`” as if local override state were shared policy,
- “we vendored it” as if source-route choice proved fork progress,
- “the exception exists” as if reevaluation were still current,
- or “there are few dependencies” as if count alone captured exposure.

Those are exactly the flattenings **P-0535** should resist.

## Early `0.1` artifacts worth promoting

- `dependency-lane.snapshot.json`
- `criticality-boundary.report.json`
- `abstraction-seam.receipt.json`
- `replacement-readiness.report.json`
- `override-authority.receipt.json`
- `dependency-exception.ledger.json`
- `signal-freshness.report.json`
- `exception-reevaluation.report.json`
- `lifecycle-drift.diff.json`

## Sources

- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- https://doc.rust-lang.org/cargo/reference/config.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
