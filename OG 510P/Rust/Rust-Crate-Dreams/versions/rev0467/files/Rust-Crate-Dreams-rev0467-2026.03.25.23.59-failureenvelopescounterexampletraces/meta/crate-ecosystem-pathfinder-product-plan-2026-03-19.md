
# Crate ecosystem pathfinder product plan — 2026-03-19

This note refreshes **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**.
The archive had already decided that the missing value is a **task-oriented crate-choice contract** rather than another registry or another blessing list.
This pass answers a narrower question:

> If somebody actually started building **P-0509** this week, what should the next sharper `0.1` look like, what should it provide other people, and what distinctions must not be flattened?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- which task lane is being solved,
- which roles and hard constraints actually matter,
- which candidates were imported and on what evidence,
- whether a starter set is really ready to freeze,
- where choosing this stack buys lock-in,
- whether teaching and production defaults intentionally split,
- and what changed when the team revisits the decision later.

It should **not** become another central ranking website, another universal trust score, another façade crate, or another attempt to officially bless one crate per category for the whole ecosystem.
Those are adjacent debates, not the product.

## What the crate should provide other people

For downstream teams, educators, platform leads, support engineers, and release reviewers, the crate should provide:

1. **One compact decision bundle** instead of scattered README lore, issue-thread folklore, and stale internal wiki pages.
2. **A starter-set readiness report** that can say `freeze_ready`, `companion_gap_blocks_freeze`, `freshness_cooldown`, `scope_split_required`, or `manual_review_required`.
3. **A lock-in cost report** that makes runtime coupling, proc-macro dependence, trait-surface gravity, ecosystem expectation, and migration hotspots explicit.
4. **A scope-split receipt** that says whether teaching and production defaults are the same, intentionally diverge, or must remain manual.
5. **An evidence-origin report** so people can see which claims came from crates.io metadata, Cargo/imported facts, docs.rs target posture, maintainer docs, or inference.
6. **A decision pack** that keeps task fit, interop fit, maintenance/trust imports, adoption signal, and uncertainty visibly separate.
7. **A frozen starter-set lock** so teams can commit the choice locally and revisit it later.
8. **A summary fit for ADRs, onboarding docs, or policy review**.
9. **A diffable decision surface** so releases and ecosystem changes can be reviewed rather than silently absorbed.

For maintainers and internal platform teams, the crate should provide:

1. a small pack that is cheap to review,
2. a visible `manual_review_required` escape hatch instead of fake certainty,
3. one place to keep task fit, evidence weighting, freeze windows, and migration notes aligned,
4. a way to keep “ranked highly” separate from “safe to freeze as our default”,
5. and a CI-visible warning when a starter set has drifted out of its declared scope.

## Recommended `0.1` command surface

### `cargo pathfinder init`
Create a starter `pathfinder.toml` or `task-profile.json` for a named lane such as:

- `cli_baseline`
- `async_http_service`
- `embedded_no_std_baseline`
- `wasm_browser_client`
- `desktop_gui_baseline`

The generated file should be incomplete on purpose.
Anything uncertain should become `manual_review_required` rather than guessed.

### `cargo pathfinder import`
Collect normalized candidate facts from:

- Cargo manifest metadata,
- Cargo command surfaces such as `search`, `info`, and metadata,
- docs.rs target/default-target visibility,
- imported P-0011 / P-0017 artifacts when available,
- maintainers’ declared companion-crate requirements,
- and a small amount of local policy.

`import` should prefer cached, reviewable evidence.
It should not try to be a crawler-first mirror of the internet.

### `cargo pathfinder explain`
Emit one normalized explanation bundle from declared task plus imported facts.
This should capture:

- candidate set,
- role coverage,
- interop/runtime/target posture,
- maintenance/trust imports,
- freeze readiness,
- lock-in cost,
- scope split,
- and uncertainty.

### `cargo pathfinder gate`
Run the local validation pass:

- do candidates actually cover the named roles,
- do hidden companion crates block freezing,
- do scope labels still match the evidence,
- did a docs.rs target/default-target change alter the visible support story,
- did a very fresh publish signal slip past the cooldown window,
- and which parts remain manual-review-only?

### `cargo pathfinder freeze`
Emit a `starter-set.lock.json` only when readiness policy allows it.
A good `freeze` step should fail conservatively when:

- hidden companion crates exist,
- teaching and production defaults are being silently conflated,
- the evidence window is too fresh,
- or imported support/trust signals are too incomplete.

### `cargo pathfinder doctor`
Render human-facing warnings for suspicious situations such as:

- `candidate_requires_hidden_companion_crate`
- `starter_set_freeze_before_cooldown_window`
- `teaching_default_and_production_default_conflated`
- `high_lockin_stack_presented_as_low_commitment`
- `docsrs_visibility_story_shifted`
- `manual_review_required`

### `cargo pathfinder diff <old> <new>`
Compare two receipts or bundles and classify:

- `candidate_added`
- `candidate_removed`
- `starter_set_changed`
- `freeze_readiness_changed`
- `lockin_cost_changed`
- `scope_split_changed`
- `evidence_origin_changed`
- `decision_axis_weight_changed`
- `manual_review_boundary_changed`

### `cargo pathfinder bundle`
Emit one compact `.pathfinder-pack.zip` bundle for ADRs, CI artifacts, education baselines, or org-policy review.

## Recommended crate/workspace split

A reasonable first implementation would be:

- `pathfinder_model`
  - shared Rust types for task profiles, candidate facts, reports, locks, summaries, and diffs
- `pathfinder_import`
  - Cargo/crates.io/docs.rs adapters and evidence-origin receipts
- `pathfinder_policy`
  - readiness rules, cooldown windows, lock-in scoring, and scope-split rules
- `pathfinder_render`
  - summaries, markdown output, diff rendering, and zip bundle emission
- `cargo-pathfinder`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `pathfinder_health_import`
- `pathfinder_trust_import`
- `pathfinder_docsrs_import`
- `pathfinder_migration_notes`

## `0.1` artifact set

The archive already had the right center of gravity around task profiles, candidate imports, interop surfaces, decision axes, starter-set locks, evidence origins, and freshness windows.
`0.1` should still revolve around:

- `task-profile.json`
- `candidate-import.report.json`
- `role-coverage.report.json`
- `interop-surface.report.json`
- `decision-axis.report.json`
- `decision-pack.report.json`
- `starter-set.lock.json`
- `evidence-weight.policy.json`
- `evidence-origin.report.json`
- `freshness-window.policy.json`
- `starter-set-scope.report.json`

This pass adds three more important artifacts:

- `starter-set-readiness.report.json` — whether the default is actually mature enough to freeze, and why not if not.
- `lockin-cost.report.json` — where exit friction really lives, even when the short-term onboarding story is excellent.
- `scope-split.receipt.json` — whether teaching and production defaults intentionally diverge, and what rationale supports the split.

Those files matter because decision bundles become vague again if the archive only records that “candidate A ranked above candidate B” but not:

- whether a starter set may be frozen,
- whether that stack is easy to teach but expensive to leave,
- and whether one default is being over-claimed for two different jobs.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared task lane and role expectations**
   - `task-profile.json`
   - maintainer/team lane vocabulary
2. **Candidate facts**
   - Cargo manifest metadata
   - Cargo search/info/metadata surfaces
   - docs.rs visible target posture
3. **Interop and role coverage**
   - runtime coupling
   - target posture
   - companion-crate requirements
   - trait ecosystem expectations
4. **Imported health and trust receipts**
   - P-0011 and P-0017 when available
5. **Freeze-boundary facts**
   - freshness windows
   - hidden companion crates
   - unstable support visibility
6. **Scope-split facts**
   - teaching baseline
   - production baseline
   - org policy
   - niche target/runtime lanes
7. **Manual review zones**
   - highly conflicting signals
   - very fresh releases
   - unclear migration posture
   - hidden transitive policy coupling

The importer should prefer visible uncertainty over synthesis.

## Starter-set readiness

The first implementation should treat **starter-set readiness** as a first-class review object and keep it separate from raw rank or adoption.

### What should count as starter-set-readiness classes in `0.1`

- `freeze_ready`
- `companion_gap_blocks_freeze`
- `freshness_cooldown`
- `scope_split_required`
- `manual_review_required`

## Lock-in cost

The first implementation should treat **lock-in cost** as a first-class review object and keep it separate from popularity, current convenience, or raw maintenance score.

A good first report should make visible:

- runtime lock-in,
- trait ecosystem lock-in,
- proc-macro / derive lock-in,
- configuration format lock-in,
- hidden companion-crate dependency,
- migration recipe presence or absence.

## Scope split

The first implementation should treat **scope split** as a positive, legitimate outcome when warranted.
Do not force one universal winner when the evidence really says:

- one stack is better for teaching,
- another is better for production,
- and both are honest within their own scopes.

## Recommended `0.1` success bar

`0.1` is good enough when a maintainer can:

1. declare one task lane,
2. import a small candidate set,
3. emit a reviewable bundle,
4. tell whether the starter answer may be frozen,
5. show where lock-in lives,
6. explain why teaching and production do or do not split,
7. and diff the result later without rebuilding the whole story from scratch.

That is already enough to be a real ecosystem multiplier.
