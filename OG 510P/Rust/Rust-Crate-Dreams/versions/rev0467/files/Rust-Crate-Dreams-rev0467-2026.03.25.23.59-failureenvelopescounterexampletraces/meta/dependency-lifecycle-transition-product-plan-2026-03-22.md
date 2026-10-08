# Dependency lifecycle transition product plan — 2026-03-22

This note sharpens **P-0535 Dependency Lifecycle Transition Kit** into a more implementation-ready `0.1` shape.

## Product question

If somebody started building **P-0535** this week, what should version `0.1` look like, what should it provide other people, and what should it leave for later?

## Product stance

The crate should stay **read-first, review-first, and architecture-adjacent**.
It should not try to redesign a system automatically.
It should help teams publish a compact answer to:

- where third-party crates are allowed today,
- what seam makes them replaceable,
- what transition is planned next,
- and what changed across releases.

## `0.1` artifact set

### `dependency-lifecycle.toml`
Human-authored policy with:
- lifecycle lanes,
- restricted packages / binaries / services,
- seam expectations,
- permitted exception classes,
- transition goals,
- owner notes.

### `dependency-lane.snapshot.json`
Normalized imported graph plus lifecycle-lane assignments.

### `criticality-boundary.report.json`
Flags third-party crates that enter packages or binaries whose lane forbids direct external use.

### `abstraction-seam.receipt.json`
Records the named seam, its type, covered consumers, and confidence posture.

### `replacement-readiness.report.json`
Classifies each tracked dependency as direct-coupled, facade-backed, protocol-seamed, process-isolated, vendor/fork ready, or manual review.

### `lifecycle-drift.diff.json`
Shows whether a release widened or tightened dependency posture.

### `override-authority.receipt.json`
Captures whether the current route is declared in checked-in policy, generated/shared config, local config, CI-only config, or manual process.

### `dependency-exception.ledger.json`
Typed, reviewable waivers with expiration or reevaluation notes.

### `signal-freshness.report.json`
Shows whether imported trust/support context is still fresh enough to support the current transition story.

### `exception-reevaluation.report.json`
Classifies whether a typed waiver is still active, nearing review, expired, stale, or exit-ready.

## CLI / workflow sketch

- `cargo dep-lifecycle capture`
- `cargo dep-lifecycle doctor`
- `cargo dep-lifecycle diff`
- `cargo dep-lifecycle summary`

A standard CI path should be:
1. import policy,
2. capture graph snapshot,
3. check restricted lanes,
4. emit seam receipts,
5. fail if a new direct crossing or seam regression appears without waiver,
6. warn if the transition route is only local/config-generated,
7. warn if imported context or exception status is stale.

## Receiver-facing value

### For maintainers
Catch accidental architectural widening before it becomes normal.

### For reviewers
See whether “replace later” is supported by a real seam and transition plan.

### For regulated teams
Archive one portable dependency-lifecycle bundle instead of relying on wiki prose.

### For downstream adopters
Understand which dependency choices are provisional and which are intentionally frozen.

## `0.1` boundaries

### Include
- Cargo graph import.
- Lifecycle-lane assignment.
- Criticality crossing detection.
- Seam receipts.
- Override-authority receipts.
- Imported-signal freshness.
- Exception reevaluation status.
- Lifecycle drift diff.

### Exclude
- Auto-generated architecture diagrams.
- Automatic dependency replacement suggestions.
- Full vulnerability/audit analysis.
- Universal standards-specific safety-case export.

## Suggested module split

- `policy`
- `graph_import`
- `lane_model`
- `boundary_check`
- `seam_capture`
- `readiness`
- `diff`
- `bundle`
- `cli`

## First proving grounds

1. a mixed workspace with one high-criticality core package,
2. a crate that moved behind a trait/process/FFI seam,
3. a crate replaced by an owned fork or vendored source,
4. a release that accidentally widened dependency placement.

## Sources

- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- https://doc.rust-lang.org/cargo/reference/config.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
