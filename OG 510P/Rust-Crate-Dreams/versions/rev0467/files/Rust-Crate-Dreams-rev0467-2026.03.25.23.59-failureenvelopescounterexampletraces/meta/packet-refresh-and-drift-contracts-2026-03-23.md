# Packet refresh and drift contracts — 2026-03-23

## Why this note exists

The archive has become much stronger at describing first packets.
It still needed a cleaner shared model for **later packets**.

A good packet-producing crate should answer three different moments clearly:
- **compare** — choose among candidates,
- **freeze** — record the basis for that choice,
- **refresh** — describe what changed later and whether the old answer still stands.

Without that separation, future tools and future archive passes will keep overwriting frozen judgments by accident.

## The three moments

### 1. Comparator moment
Question:
- “Which option looks best for this task profile right now?”

Good artifacts:
- `task-profile.json`
- `decision-packet.manifest.json`
- `candidate-elimination.receipt.json`
- `starter-set.lock.json`

### 2. Freeze moment
Question:
- “What exact basis supported the decision we made?”

Good artifacts:
- `basis-lock.manifest.json`
- witness receipts and imports
- `answer-boundary.note.md`

### 3. Refresh / drift moment
Question:
- “What changed later, and does that reopen the old decision?”

Good artifacts:
- `decision-revalidation.report.json`
- `knowledge-diff.report.json`
- `signal-freshness.report.json`
- `lifecycle-drift.diff.json`
- `transition-review-packet.manifest.json`

## Shared rules for refresh packets

### Rule 1 — never overwrite a frozen basis
A refresh packet should point back to the old basis lock.
It should not silently replace it.

### Rule 2 — separate new facts from new decisions
A new release, advisory, target change, or docs.rs recipe change is a **new fact**.
Whether that fact changes the old answer is a **new decision**.
Keep them separate.

### Rule 3 — preserve task and policy identity
A revalidation packet should say whether it is:
- checking the same task and policy,
- or opening a genuinely new decision.

### Rule 4 — keep imports and architecture separate
An imported advisory, security tab, SLOC metric, or publishing posture can trigger review without becoming architecture truth.

### Rule 5 — make triggers explicit
A worthy refresh-capable crate should classify why review reopened.
Good trigger classes include:
- `new_release`
- `new_advisory`
- `docs_surface_changed`
- `target_filter_changed`
- `rust_floor_changed`
- `registry_or_source_route_changed`
- `manual_policy_change`

## What this should provide other people

For another team, refresh-capable crates should provide:
- a compact answer to **what changed**,
- a compact answer to **whether the old choice still stands**,
- a compact answer to **what next posture applies if it does not**,
- and a durable link back to the old basis.

That is much more useful than re-running an entire selection flow every time public facts move.

## Ranking implication

A crate that only produces first-day packets is less ecosystem-worthy than one that also produces **later-day refresh packets**, if both are otherwise plausible.

That does **not** mean every proposal needs a giant lifecycle platform.
It does mean the leading packet-producing lanes should be judged by whether they can survive drift honestly.

## Where this matters most right now

1. **P-0509 Pathfinder** — must say whether an old starter set still stands.
2. **P-0536 Knowledge Pack** — must say which knowledge surfaces changed.
3. **P-0535 Dependency Lifecycle Transition** — must say what posture follows from those changes.
4. **P-0472 Docs.rs Parity** — must connect hosted/local drift to concrete issue bundles.
5. **P-0496 Source Parity** — must say when source-route or mirror posture changed without pretending that content diverged the same way.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://docs.rs/about/rustdoc-json
