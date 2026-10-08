# Design: Package Admission pilot program

## Why this needs a pilot program
The archive now has strong package-side ingredients — publish-set truth, dependency control, public API evidence, SBOM evidence, trust signals, and explainable policy — but they still mostly read as adjacent kits.

Current Rust/Cargo/crates.io signals point to a staged package-admission rollout instead of a giant all-at-once platform:
- Rust’s 2026 flagships keep **public/private dependencies** and **SBOM support** active supply-chain milestones.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo 1.94 still treats public/private dependencies as unfinished, which means the ecosystem needs room for partial-but-honest rollout.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- `cargo package` and `cargo publish` now expose more explicit publication-path facts — workspace-aware selection, verification controls, index polling, and unstable machine-readable packaging lists — which makes a publish-review bundle more plausible than it used to be.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- crates.io now surfaces Security-tab data, Trusted Publishing controls, and `pubtime`, but those are still signals, not full decision packs.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo publishing remains a durable event, which means admission decisions need to be explainable enough to survive later downstream consumption.
  https://doc.rust-lang.org/cargo/reference/publishing.html

That combination argues for a **ranked pilot program**: prove a reviewable package-admission bundle in narrow, high-value lanes before widening to registry or downstream consumers.

## Failure modes this pilot must prevent
The pilot program should explicitly prevent five kinds of package-side theater:
1. **publish theater** — package-admission conclusions made without explicit selected-package, payload, check, and receipt truth.
2. **graph theater** — policy or trust conclusions made without portable chosen-graph and activation truth.
3. **API theater** — semver or public/private conclusions made without explicit exposure evidence.
4. **inventory theater** — one exported BOM file treated as complete package truth.
5. **trust theater** — name-risk, publisher, freshness, or audit cues flattened into one score.
6. **release theater** — package upload evidence silently sold as complete binary-release truth.

## Ranked pilots

### Pilot 1 — Single-crate publish gate
**Who this is for:** maintainers of ordinary published crates.

**Why first:**
- This is the smallest lane that still exercises the whole package-admission story.
- It aligns with Rust’s upstream supply-chain direction without requiring Cargo or crates.io to absorb an umbrella design immediately.

**Required evidence inputs**
- `publish-pack/v0` or equivalent publish-set reports for selected package/payload/check/receipt posture
- dependency-control reports for selected graph and feature posture
- `api-pack/v0`
- `inventory-pack/v0` or explicit inventory-lane markers
- `trust-pack/v0`
- `policy-pack/v0`

**Acceptance bar**
- A maintainer can answer “what package and payload were under review, what graph did we publish against, what public contract changed, what inventory/trust facts mattered, and what rule/waiver admitted this package?” from one linked review bundle.
- The pilot must preserve `INCONCLUSIVE` outcomes where evidence is partial.

### Pilot 2 — Workspace publish group
**Who this is for:** workspaces publishing multiple related crates, especially with reexports or split package roles.

**Why second:**
- Workspace publication is where package-side scope, aggregation, and public/private drift become materially harder.
- It also tests whether package admission can stay honest without flattening per-crate truth.

**Required additions**
- package-selection rules
- per-crate publish-set retention
- per-crate evidence retention
- publish-group summary that does not erase per-crate waivers or unsupported lanes
- explicit shared-version / staggered-version posture markers

**Acceptance bar**
- A workspace can publish several crates with one review bundle while retaining crate-local graph, exposure, inventory, trust, and policy truth.

### Pilot 3 — Proc-macro / build-lane admission
**Who this is for:** crates whose admission risk is disproportionately shaped by build scripts, proc macros, or unusual host-side posture.

**Why third:**
- This is where trust and policy are most often forced into vague hand-waving today.
- Cargo and crates.io now expose enough supply-chain-relevant signals that this lane should stop being implicit folklore.

**Required additions**
- explicit host/build/proc-macro split-scope inputs
- publish-set receipts and check/waiver posture for the admitted package(s)
- cooldown / freshness posture when relevant
- imported trust signals that distinguish package risk from package popularity
- visible waiver budgets for exceptional publication

**Acceptance bar**
- Reviewers can say why a proc-macro/build-heavy package was admitted, delayed, or flagged without inventing a new crate-risk score.

### Pilot 4 — Package-to-release handoff
**Who this is for:** projects where package publication is only one part of a larger released product.

**Why fourth:**
- The stack needs to prove it can compose with broader release truth without pretending to replace it.
- This is where API / inventory / policy / trust facts become attached inputs to release packs, not silent duplicates.

**Required additions**
- explicit package subject ↔ release subject linkage
- attachment conventions into `release-pack/v0`
- visible statement of what later consumers still need (signatures, rebuild evidence, support-envelope, etc.)

**Acceptance bar**
- A release pipeline can import package-admission truth without confusing it for signed-binary or rebuild truth.

### Pilot 5 — Thin registry / downstream consumers
**Who this is for:** crates.io-facing views, downstream packagers, internal mirrors, review UIs, and assistants.

**Why fifth:**
- Consumer views are valuable, but only after the package-admission bundle is stable enough not to hard-code today’s rough edges.
- This is where the archive proves it can power better consumers without creating a new monopoly surface.

**Required additions**
- thin rendered summaries over linked packs
- explain / diff views for package-admission bundles
- explicit lossiness markers when a consumer view hides detail
- import profiles for downstream policy or curation systems

**Acceptance bar**
- A downstream consumer can ingest package-admission evidence without rerunning the whole publisher pipeline or inventing new semantics.

## Pilot artifact family
The pilot program should converge on a small shared artifact family early:
- `package-subject/v0`
- `package-graph-report/v0`
- `package-exposure-report/v0`
- `package-admission-brief/v0`
- `package-release-handoff/v0`
- `package-admission-pack/v0`

The point of the pilot is not merely to prove that each imported tool can emit something.
It is to prove that the imported outputs can be assembled into one reviewable package-admission story without erasing waivers, lossy inputs, or package-vs-release boundaries.

## Shared design rules across pilots
- **Per-crate truth survives aggregation.** Workspace/package-group summaries must not erase local publish-set receipts, waivers, or unsupported lanes.
- **Decision posture stays explainable.** Pass / warn / fail / inconclusive semantics must stay visible and rule-linked.
- **Package truth is not binary truth.** The pilot must preserve the handoff into Release Truth Stack rather than swallowing it.
- **Trust signals remain imported facts.** Publisher, freshness, name-risk, audit, and advisory imports are inputs, not verdicts.
- **Inventory remains provenance-aware.** Observed, inferred, binary-recovered, and manual supplement lanes stay distinct.
- **API evidence stays selective and scoped.** Witness-heavy or cross-crate expensive lanes should be used where they pay for themselves, not as mandatory ceremony everywhere.

## Immediate archive decision
Treat [`design/package-admission-stack.md`](./package-admission-stack.md) as the synthesis layer, this file as the rollout order, and [`proposals/epic-package-admission-stack.md`](../proposals/epic-package-admission-stack.md) as the explicit product-direction candidate.

The next credible move is **not** another “secure publish” wrapper or one registry-facing dashboard. It is proving that ordinary Rust packages can carry enough linked graph/exposure/inventory/trust/policy evidence to make publication reviewable, diffable, and reusable.
