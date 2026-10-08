# Dependency lifecycle transition seam-proof plan — 2026-03-22

This note deepens **P-0535 Dependency Lifecycle Transition Kit** around one product question:

> What does another person need to see before “replace later”, “forked for stability”, or “contained behind a seam” counts as an honest lifecycle claim?

## Product stance

The crate should stay **review-first and architecture-adjacent**.

It should not try to:
- redesign the system,
- infer full architecture from Cargo metadata alone,
- or promise that every vendored/forked dependency is now harmless.

It should instead emit a small set of artifacts that help a maintainer, reviewer, downstream integrator, or safety lead answer:

- where a dependency is allowed to live,
- what replacement boundary exists right now,
- which exceptions are still knowingly accepted,
- what imported trust/support facts were considered,
- and what next transition step is expected.

## Three first-class review objects to promote now

### 1. `transition-plan.manifest.json`

This is the missing object between a static lane assignment and a real lifecycle plan.

It should answer:
- current lane,
- intended next lane,
- seam reference,
- owner class,
- exit criteria,
- blockers,
- review deadline or reevaluation window,
- and what counts as completion.

Typical transitions worth expressing:

- `prototype -> contained`
- `contained -> vendor_frozen`
- `contained -> owned_fork`
- `replace_planned -> internal_only`
- `production_pinned -> replace_planned`
- `owned_fork -> internal_only`
- `vendor_frozen -> remove`

### 2. `dependency-exception.ledger.json`

This is the missing object between policy and reality.

It should record:
- which dependency or lane is violating the nominal rule,
- what type of exception it is,
- why it was accepted,
- who accepted it,
- how long it remains valid,
- what compensating controls or monitoring exist,
- and whether reevaluation is mandatory.

Useful early exception classes:
- `restricted_lane_direct_dep`
- `fork_without_exit_plan`
- `vendored_without_equivalence_review`
- `temporary_git_patch`
- `manual_review_required`

### 3. `imported-signal.receipt.json`

This keeps imported ecosystem facts useful without letting them impersonate local architecture judgment.

It should record:
- signal source (`crates_io`, `trust_lens`, `security_advisory_feed`, `manual_note`, ...),
- signal kind (`security_tab_visible`, `trusted_publishing_only`, `sloc_metric`, `pubtime`, ...),
- dependency it refers to,
- when it was imported,
- and what decision weight it was allowed to carry.

## The crucial source boundary

A lifecycle tool absolutely may say:
- “this crate moved from registry use to an owned fork,”
- “this lane moved from live registry dependency to vendored read-only source,”
- or “the current transition plan depends on a temporary `[patch]` overlay.”

But it must **not** absorb the whole job of proving:
- source identity equivalence,
- offline completeness,
- mirror correctness,
- or vendored parity.

Those remain owned by **P-0496 Cargo Vendor & Source Parity Kit**.

### Working rule

Inside **P-0535**:
- source posture is a **local transition fact**,
- source equivalence is **external imported evidence or adjacent-lane territory**.

That separation prevents a fake verdict where “we vendored it” gets mistaken for “we proved the source boundary is complete and honest.”

## Suggested workflow

### `cargo dep-lifecycle capture`
Emit:
- `dependency-lane.snapshot.json`
- `criticality-boundary.report.json`
- `abstraction-seam.receipt.json`
- `replacement-readiness.report.json`
- `transition-plan.manifest.json`
- `dependency-exception.ledger.json`
- `imported-signal.receipt.json`

### `cargo dep-lifecycle doctor`
Flag:
- restricted lanes with direct third-party edges,
- seam claims without named consumers,
- stale transition plans,
- exceptions without expiry or reevaluation windows,
- and imported trust signals that appear to be masquerading as local policy decisions.

### `cargo dep-lifecycle diff`
Compare two bundles and classify:
- `criticality_crossing_added`
- `seam_removed`
- `replacement_improved`
- `replacement_regressed`
- `source_posture_changed`
- `temporary_dependency_became_sticky`
- `exception_added`
- `exception_expired`
- `manual_review_required`

## Receiver-facing value

### For maintainers
A compact way to publish “use now, contain later, replace eventually” without folklore.

### For reviewers
A visible difference between:
- “we rely on this crate directly,”
- “we contain it behind a seam,”
- and “we imported some positive registry signals.”

### For downstream adopters
One answer to which third-party crates still reach the sensitive parts of the system.

### For regulated teams
A reviewable artifact family for exceptions, transition windows, and next-step ownership.

## MVP boundaries

### Include
- lane assignment
- seam receipts
- transition plans
- typed exceptions
- imported signal receipts
- release-to-release drift

### Exclude
- automated architecture diagrams
- automated replacement recommendations
- whole-workspace mirror/offline equivalence proofs
- vulnerability scanning replacement
- maintainer-quality scoring

## Good proving grounds

1. **Prototype tooling vs restricted control core**
   Many third-party crates are acceptable in tooling, but not in the control binary.

2. **Trait facade containment**
   A parsing or codec crate is allowed only behind one trait/module seam while an owned rewrite is planned.

3. **Owned-fork stabilization lane**
   A third-party dependency becomes an owned fork for stability, but the exception must still expire or be reevaluated.

4. **Accidental direct-leak regression**
   A release adds a new direct registry crate inside the restricted lane and the drift report must make that loud.

## Sources

- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- https://rustfoundation.org/strategic-plan/
