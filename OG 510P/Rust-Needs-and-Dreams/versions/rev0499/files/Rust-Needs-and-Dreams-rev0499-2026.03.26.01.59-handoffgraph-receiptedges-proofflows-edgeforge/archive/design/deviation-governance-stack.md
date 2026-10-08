# Design: Deviation Governance Stack (waivers, overrides, preview pins, allow-fails, emergency carries)

## Goal
Treat **bounded deviation from normal Rust policy** as a first-class control-plane seam.

Rust now has many respectable ways to depart from the default or nominal path:
- `#[allow]` / `#[expect]` / CLI lint controls,
- partial edition migrations and `--broken-code` carries,
- nightly pins and unstable feature gates,
- `[patch]` overrides for unpublished or emergency fixes,
- config-local patches and profile overrides,
- allow-fail canary lanes,
- yanks that stop new resolution but not existing lockfiles,
- multi-policy workspaces and release branches,
- and local source replacement / vendoring / mirroring boundaries.

But the downstream review story is still often a blur of inline comments, CI `continue-on-error`, forgotten `.cargo/config.toml` fragments, stale nightly pins, temporary dependency forks that became permanent, and oral-history explanations like “we had to do this for a while.”
The missing contribution is therefore **not** another linter, another policy wiki, another giant compliance engine, or another generic “governance” essay.
It is a thin **reviewable deviation layer** that keeps these truths separate:
- **normative-basis truth** — what ordinary rule, default, baseline, lane default, or support promise would apply absent the deviation;
- **deviation-subject truth** — what is actually being bent: lint posture, dependency source, feature gate, toolchain pin, branch floor, config override, canary gate, or incident containment carry;
- **mechanism truth** — how the deviation is realized: attribute, CLI flag, config file, `Cargo.toml`, `rust-toolchain.toml`, `[patch]`, source replacement, CI rule, branch split, or local overlay;
- **scope truth** — which crate, target, feature set, workspace member, branch, release line, CI lane, developer environment, or artifact flow is affected;
- **justification-and-owner truth** — why the deviation exists, who owns it, and what evidence or risk posture justified allowing it;
- **expiry/watch truth** — when it should be reviewed again, what condition should clear it, and what canary or issue feed should be watched;
- **exit truth** — whether the intended outcome is removal, renewal, promotion into a durable overlay/default, or replacement by a stronger upstream fix.

The point is to stop treating “we made an exception” as one blob.

## Why this seam matters now
Official Rust/Cargo signals are unusually aligned here:
- The rustc lints docs say Rust has multiple lint levels (`allow`, `expect`, `warn`, `force-warn`, `deny`, `forbid`), and `expect` specifically exists so a suppression can fail loudly once it is no longer needed. That is direct evidence that some deviations are meant to be temporary and self-checking rather than permanent folklore.
  https://doc.rust-lang.org/rustc/lints/levels.html
- The Edition Guide’s advanced migrations docs say `cargo fix --edition` may need repeated runs, may require separate passes for different targets/features, and may intentionally carry `--broken-code` or individual compatibility lints while a project incrementally migrates. That means staged exception-carry is not accidental; it is part of real Rust upgrade practice.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo’s unstable-features docs and the Rust book’s nightly appendix say nightly-only capabilities require explicit activation and often a per-project override or pin. That makes preview usage an explicit deviation path with a real support boundary, not just a hidden implementation detail.
  https://doc.rust-lang.org/cargo/reference/unstable.html
  https://doc.rust-lang.org/book/appendix-07-nightly-rust.html
- Cargo’s overriding-dependencies docs say `[patch]` is for testing bug fixes, carrying unpublished upstream work, and unblocking on fixes before they merge. That is a first-class temporary deviation lane, not a hack.
  https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- Cargo’s config docs say config-local `[patch]` usually should not be preferred because those files are not usually checked into source control, and they explain that config is hierarchical through parent directories. That is strong evidence that invisible local deviations are a real failure mode.
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo’s source-replacement docs say replacement sources must be **exactly the same source code** as the original source and are not appropriate for patching. That means different deviation mechanisms carry different semantic promises and should not be flattened together.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo’s publishing docs say a yank does not delete code and does not break existing `Cargo.lock` files. So even after upstream action, a local graph can remain on an exceptional carried path until it is explicitly exited.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo’s CI guide says latest-deps jobs may be marked `continue-on-error`, scheduled jobs may fail to notify the right people, and higher-risk projects may need more combinations. That is direct evidence that even watch lanes can be explicitly downgraded or scoped as bounded deviations from the main gate.
  https://doc.rust-lang.org/cargo/guide/continuous-integration.html
- Cargo’s `rust-version` docs say projects should choose and document a policy, warn that drift from policy leads users to infer support you did not intend, and allow multiple policies in one workspace. That means support-floor drift and branch/member variance are already recognized as governance surfaces rather than mere accidents.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- The March 2026 Rust challenges writeup says ecosystem navigation still depends too much on tacit knowledge, and the 2025 State of Rust survey says canonical docs still matter while editor/LLM-mediated workflows are rising. That makes durable, machine-usable deviation artifacts more valuable because invisible local carries are exactly the kind of tacit knowledge that derived tools tend to miss.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, ideal Rust needs a reviewable layer for **bounded deviation** above mechanism-specific waivers and below downstream support/release/trust claims.

## What belongs in deviation-subject truth
Not every case needs every field, but the stack should be able to name subjects like:
- lint suppression or temporary downgrade;
- partial edition or baseline migration carry;
- nightly pin / unstable feature / beta-only validation lane;
- dependency fork, local bugfix carry, or emergency `[patch]` override;
- config-local or parent-directory override that changes build behavior;
- source replacement / vendoring / mirror redirection with exactness claims;
- allow-fail canary job or downgraded verification lane;
- temporarily tolerated vulnerable or yanked dependency that still survives in a lockfile or release line;
- institutional or project-local exception to a public default;
- emergency incident-response containment that should later be retired or promoted into a durable rule.

A project does not become more honest by flattening all of these into “temporary workaround”.

## What each neighboring stack owns
### Institutional Overlay Stack
[`design/institutional-overlay-stack.md`](./institutional-overlay-stack.md) owns:
- durable local defaults,
- team/org/product-line deltas over public defaults,
- governance and freshness for those overlays.

Its question is:
> what local rule do we intend to be normal here?

Deviation Governance begins when a project is **not** just applying a durable local rule, but carrying a **bounded exception** to one.

### Preview Adoption Stack
[`design/preview-adoption-stack.md`](./preview-adoption-stack.md) owns:
- what preview subject is in use,
- how it is activated,
- what support boundary it imposes,
- and what stable landing is being watched.

Its question is:
> what unstable/preview capability are we using?

Deviation Governance owns the more general cross-stack question:
> how do we carry, renew, watch, and retire an exception at all?

### Baseline Ratchet Stack
[`design/baseline-ratchet-stack.md`](./baseline-ratchet-stack.md) owns:
- support-floor changes,
- release-line variance,
- and verification of those floor changes.

Its question is:
> what baseline policy are we changing?

Deviation Governance owns:
> what temporary drift, grandfathering, or branch/member carry remains outside the intended new normal?

### Canary Validation Stack
[`design/canary-validation-stack.md`](./canary-validation-stack.md) owns:
- watch lanes,
- cadence,
- gating rules,
- and escalation destinations.

Its question is:
> how do we watch for incoming breakage before users do?

Deviation Governance owns the case where one lane is intentionally downgraded, scoped, or temporarily non-blocking.

### Ecosystem Incident Response Stack
[`design/ecosystem-incident-response-stack.md`](./ecosystem-incident-response-stack.md) owns:
- incident subject,
- exposure,
- containment,
- rebuild/reissue truth,
- and communication.

Its question is:
> how did we respond to the incident?

Deviation Governance owns the smaller but persistent truth that often remains afterward:
> which emergency carries, temporary forks, or downgraded gates are still alive, who owns them, and when do they end?

### Trust Decision / Package Admission / Lint Governance / Cargo Report
Those stacks own their mechanism-specific evidence.
Deviation Governance should import them rather than replacing them.
Its job is not to reinterpret every lint, patch, or trust review from scratch, but to keep the **cross-cutting exception boundary** reviewable.

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. What is the normal rule or default we are departing from?
2. What exactly is the deviation subject, and by what mechanism is it realized?
3. How far does the deviation reach — crate, target, workspace member, branch, CI lane, or release line?
4. Why was it allowed, and who owns renewing or retiring it?
5. What signal should tell us it is stale, unsafe, or no longer justified?
6. Is the intended end-state removal, renewal, durable promotion, or replacement by a stronger upstream/default path?

If the stack cannot answer those six questions, it is still just exception folklore.

## Recommended execution posture
The archive should prefer a ranked rollout like this:

### 1. Lint and migration carries
Prove the stack first on the smallest honest subjects:
- `#[expect]` / `#[allow]` suppressions,
- partial compatibility-lint carries,
- `cargo fix --edition` leftovers,
- explicit broken-code or manual follow-up windows.

### 2. Preview and toolchain deviations
Next prove:
- nightly pins,
- unstable feature gates,
- beta-only validation lanes,
- per-project toolchain overrides.

### 3. Dependency and graph deviations
Then prove:
- `[patch]` carries,
- temporary forks,
- yanked-version survivals in lockfiles,
- vendored/mirrored/source-replacement exactness claims.

### 4. Gate and watch deviations
Then prove:
- allow-fail canary jobs,
- downgraded scheduled verification,
- scoped CI exclusions,
- temporary release-branch or platform exceptions.

### 5. Cross-stack handoff
Only after the above are reviewable should the deviation become an input to:
- support claims,
- release notes,
- package admission,
- trust posture,
- local overlays,
- or incident postmortems.

That order matters.
The archive should not jump straight to one giant universal waiver registry with no subject model.

## Design principles
1. **Normative basis first.** Do not start with the workaround before naming the rule it bends.
2. **Mechanism is not semantics.** `#[allow]`, `[patch]`, `rustup override`, source replacement, and `continue-on-error` are different mechanisms with different promises.
3. **Temporary and durable must stay separate.** A mature overlay/default is not the same as an emergency or transitional deviation.
4. **Scope stays explicit.** One target, one member, or one branch deviating is not the same as the whole project.
5. **Self-clearing is better than silent carry.** Prefer `expect`-like or canary-backed semantics where possible.
6. **Exit posture is part of the record.** A deviation without renewal/removal criteria is just unowned drift.
7. **Downstream claims inherit bounded authority.** Release/support/trust/admission consumers should import a named deviation record rather than scraping comments or CI YAML.

## What an epic contribution would look like in practice
A serious contribution here would publish a compact artifact family such as:
- `deviation-basis/v0` — the ordinary rule/default/baseline/lane default being departed from
- `deviation-subject/v0` — the thing being bent and the mechanism realizing it
- `deviation-scope-map/v0` — members, targets, branches, CI lanes, environments, or artifacts affected
- `deviation-watch/v0` — review date, watched issue/feed/canary, stale criteria, owner, and renewal conditions
- `deviation-exit/v0` — removal / renewal / durable-promotion / upstream-replacement decision and receipts
- `deviation-pack/v0` — checksummed pointer set linking the above plus imported evidence from preview, baseline, trust, canary, lint, migration, or incident stacks

That contribution should:
- compose with Cargo, rustup, CI, and existing ecosystem tools instead of replacing them;
- make local exceptions visible without pretending every one deserves the same severity;
- help teams avoid carrying hidden `.cargo/config.toml` state or stale branch/nightly debt;
- and let LLM/editor/CI surfaces say “this is a bounded exception with owner and exit” instead of silently narrating it as permanent policy.

## Anti-goals
Do not turn this stack into:
- one universal policy engine,
- one giant waiver spreadsheet that becomes the new source of truth,
- one excuse to bless perpetual drift,
- one replacement for mechanism-specific review in preview/trust/incident/migration stacks,
- or one hidden assistant memory of “temporary” exceptions.

The stack is a **review boundary for bounded deviation**, not a license to normalize drift.
