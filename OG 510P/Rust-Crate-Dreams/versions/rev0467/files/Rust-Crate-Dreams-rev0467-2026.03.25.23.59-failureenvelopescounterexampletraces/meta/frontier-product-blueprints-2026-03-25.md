# Frontier product blueprints — 2026-03-25

This note exists to keep the frontier stable **while making it more buildable**.

The archive no longer needs more broad dream-lane inflation.
It needs sharper answers to:

- what should be built first,
- what should a first release provide,
- and what packet another team should receive.

## Main judgment

The strongest missing crates are still mostly **receiver-facing control-plane kits**.
But the archive should now treat them as **product blueprints** with explicit maturity ladders.

## Blueprint board

### 1. P-0509 + P-0536 + minimal P-0535
**Role:** selection / knowledge / continuity front door

Why first:
- answers the common crate-choice problem directly;
- imports evidence that already exists today;
- and can produce a compact acceptance packet without needing a giant new ecosystem substrate.

What another team should receive:
- `decision-pack.report.json`
- `review-packet.pack.json`
- `basis-lock.json`
- `offer.summary.md`
- `recheck-trigger.ticket.json`

### 2. P-0472 + P-0484
**Role:** docs/build/target/toolchain support-envelope import ring

Why second:
- it turns hosted-doc, build, target, and toolchain ambiguity into bounded support language;
- it is especially relevant to embedded, safety-critical, GUI, cross-platform, and hard-domain receivers;
- and current official surfaces already expose a lot of the needed raw material.

What another team should receive:
- `docs-build-parity.report.json`
- `target-support.report.json`
- `toolchain-component.report.json`
- `support-ceiling.note.md`

### 3. P-0486
**Role:** debugger support envelope and diagnosability truth

Why third:
- debugging pain remains prominent;
- the missing value is not “invent a debugger”, but export honest matrixed support packets;
- and this lane becomes much stronger once the front door and support-import ring already exist.

What another team should receive:
- `debug-matrix.report.json`
- `sidecar-availability.report.json`
- `async-debug.claim-ceiling.note.md`
- `debug-support.summary.md`

### 4. P-0431 + P-0496 + P-0125
**Role:** public-boundary / source-parity / supply-chain carry-forward ring

Why fourth:
- current Rust substrate and current registry/security realities make post-adoption maintenance more visible;
- this ring keeps prior acceptance packets alive when publication, mirroring, boundary, or inventory facts change;
- and it is cross-domain enough to matter well beyond security teams.

What another team should receive:
- `public-boundary.report.json`
- `source-parity.report.json`
- `sbom-precursor.delta.json`
- `carry-forward.summary.md`

### 5. P-0537
**Role:** compile-iteration truth and rebuild explanation

Why fifth:
- the problem is real and broad;
- current Cargo build-analysis work makes it more plausible;
- but the substrate is still less ready for stable productization than the front door and support ring.

What another team should receive:
- `rebuild-explanation.report.json`
- `hotspot.summary.md`
- `actionable-suggestions.note.md`

### 6. P-0538
**Role:** concurrency semantics comparison and boundary language

Why sixth:
- the need is severe;
- but portable concurrency semantics are harder to capture honestly than package/docs/build/target truth;
- and the lane is more likely to deserve a research-first `0.1` than a broad operational claim.

What another team should receive:
- `concurrency-contract.matrix.json`
- `cancellation-ordering-fairness.report.json`
- `semantic-ceiling.note.md`

## Practical queue after this pass

1. **Front door** — P-0509 + P-0536 + minimal P-0535
2. **Support import ring** — P-0472 + P-0484
3. **Debugger support envelope** — P-0486
4. **Continuity / supply-chain ring** — P-0431 + P-0496 + P-0125
5. **Iteration truth** — P-0537
6. **Concurrency semantics** — P-0538

## Promotion rule

Do not promote a lane because it sounds important.
Promote it when the archive can name:

1. a receiver,
2. an acceptance packet family,
3. a truthful `0.1`,
4. a refusal boundary,
5. and a credible path to handoff-grade `1.0`.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://rust-lang.github.io/rust-project-goals/2026/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
