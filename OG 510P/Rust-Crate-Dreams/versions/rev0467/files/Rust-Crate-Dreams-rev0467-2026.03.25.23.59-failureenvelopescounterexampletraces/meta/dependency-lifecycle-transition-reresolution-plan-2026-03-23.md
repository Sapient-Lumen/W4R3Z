# Dependency lifecycle transition re-resolution plan — 2026-03-23

This note deepens **P-0535 Dependency Lifecycle Transition Kit** around one product question:

> When a team says a dependency is “contained for now” or “on the path out”, what actually keeps that story true after a clean resolve, a lock refresh, or a new checkout?

## Product stance

The crate should stay **review-first and transition-first**.
It should not become a general-purpose update policy engine.
It should help a maintainer, reviewer, or downstream adopter answer:

- what currently anchors the realized route,
- whether that anchor is shared or local-only,
- what would happen if Cargo had to select again,
- and which lifecycle claims survive that test.

## Two new first-class review objects to promote now

### 1. `selection-anchor.receipt.json`

This is the missing object between “the graph is green today” and “the transition posture is really stable.”

It should record:
- dependency or dependency group,
- anchor kind (`checked_in_lockfile`, `root_manifest_patch`, `checked_in_config_patch`, `local_config_patch`, `ci_only_patch`, `source_replacement`, `git_rev_pin`, `manual_operator_step`, ...),
- scope (`workspace`, `package`, `developer_machine`, `ci_pipeline`, `release_branch`),
- whether the anchor is shared,
- what part of the posture the anchor is holding in place,
- and what event would invalidate it (`lock_refresh`, `clean_checkout`, `patch_removal`, `rust_version_change`, `registry_state_change`, ...).

### 2. `reresolution-risk.report.json`

This is the missing object between “the current build works” and “the dependency lifecycle story survives a future select.”

It should classify risks such as:
- `current_lock_only`
- `local_patch_not_shared`
- `yanked_but_locked`
- `source_replacement_not_transition_progress`
- `git_default_branch_drift`
- `rust_version_sensitive_selection`
- `fresh_resolve_may_cross_criticality_boundary`
- `manual_review_required`

It should answer:
- what fresh resolve scenario was considered,
- what currently selected route would change,
- whether the change widens or tightens lifecycle posture,
- and what review or mitigation is expected.

## Why this layer belongs inside P-0535

This is not just Cargo mechanics.
It is the review layer for whether a transition claim is:
- architecture-backed,
- team-shared,
- and durable enough to survive ordinary maintenance events.

That makes it natural lifecycle territory.

### Working rule

Inside **P-0535**:
- lockfiles, patches, source replacement, and `rust-version` are treated as **transition anchors**,
- clean-resolve changes are treated as **lifecycle posture risk**.

Outside **P-0535**:
- generic update policy stays with update-policy lanes,
- mirror/source equivalence stays with source-parity lanes,
- successor recommendation stays with off-ramp lanes.

## Suggested workflow

### `cargo dep-lifecycle capture`
Emit:
- `selection-anchor.receipt.json`
- `override-authority.receipt.json`
- `dependency-lane.snapshot.json`
- `criticality-boundary.report.json`
- `transition-plan.manifest.json`

### `cargo dep-lifecycle doctor`
Flag:
- restricted-lane posture that only holds because of a local patch,
- transitions that are only true under the current lockfile,
- yanked-but-locked dependencies that keep today green but leave future selection exposed,
- `rust-version`-sensitive selections that should be part of the transition story,
- and source-replacement routes that are over-read as fork progress.

### `cargo dep-lifecycle diff`
Compare two bundles and classify:
- `selection_anchor_changed`
- `lock_only_route_became_shared`
- `shared_route_became_local_only`
- `reresolution_risk_increased`
- `reresolution_risk_decreased`
- `yank_exposure_added`
- `rust_version_selection_shift`
- `manual_review_required`

## Receiver-facing value

### For maintainers
Know whether the “safe for now” story depends on the exact current lockfile or on a real shared route.

### For reviewers
See the difference between:
- a durable contained dependency,
- a local emergency patch,
- and a route that stays green only because no one has re-resolved yet.

### For downstream adopters
Understand whether the published lifecycle posture will reproduce on a clean checkout.

## MVP boundaries

### Include
- selection anchors,
- clean-resolve risk classes,
- lock-only route honesty,
- yank exposure as lifecycle context,
- `rust-version`-sensitive selection notes.

### Exclude
- full dependency update planning,
- mirror/source equivalence proofs,
- automatic successor choice,
- generic vulnerability scanning.

## Good proving grounds

1. **Local patch plus checked-in lockfile**
   Current builds work, but a clean checkout without the local patch loses the transition route.

2. **Yanked but locked dependency**
   Existing builds still work, but future default selection no longer matches the current route.

3. **`rust-version`-sensitive family split**
   A clean resolve under a different supported toolchain floor selects a different dependency family and changes posture.

4. **Vendor mirror mistaken for transition progress**
   A source-replacement route is useful for containment but does not itself prove architectural off-ramp progress.

## Sources

- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
- https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://doc.rust-lang.org/cargo/commands/cargo-update.html
- https://doc.rust-lang.org/cargo/commands/cargo-yank.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
