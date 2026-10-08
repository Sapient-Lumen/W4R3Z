# Design: Trust Decision Stack pilot program (`trust-decision-pack/v0`)

## Why this needs a stack-level pilot program
The archive already has:
- an evidence-first rollout in [`design/trust-signals-pilot-program.md`](./trust-signals-pilot-program.md), and
- a decision-first rollout in [`design/policy-pilot-program.md`](./policy-pilot-program.md).

What it still lacked was the **stack-level coordination layer** that proves those two halves can meet cleanly without turning:
- `cargo trust` into a stealth policy engine,
- `cargo policy` into a second trust-schema owner,
- or registry/search/review/adoption consumers into overclaiming summary machines.

Current ecosystem signals make that coordination worthwhile:
- crates.io now exposes Security-tab advisory views, stronger Trusted Publishing controls, blocked risky triggers, and `pubtime` in the index;
- the crates.io malicious-crate policy now routes routine malware removals through RustSec advisories as the durable record;
- Cargo Vet already supports imported audits, trusted-publisher windows, subtree-sensitive policy, and multi-repository aggregation;
- Cargo publishing remains permanent;
- Rust’s 2026 flagships keep public/private dependencies and SBOM support on the active supply-chain path.

Sources:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://doc.rust-lang.org/cargo/reference/publishing.html
- https://mozilla.github.io/cargo-vet/how-it-works.html
- https://mozilla.github.io/cargo-vet/config.html
- https://mozilla.github.io/cargo-vet/trusted-entries.html
- https://mozilla.github.io/cargo-vet/multiple-repositories.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

That combination argues for a thin, ranked stack pilot rather than another score, dashboard, or one-tool replacement pitch.

## Lane rule
Execute this stack pilot with [`design/trust-decision-lane-map.md`](./trust-decision-lane-map.md) as the separation rule: registry discovery, advisory feeds, audit attestations, graph-policy lint, artifact recovery, local policy decisions, and thin consumer views must remain visibly layered even when the stack emits one pack.

## Stack boundary
This pilot treats the following archive pieces as one execution band:
- [`design/trust-decision-stack.md`](./trust-decision-stack.md)
- [`design/trust-signals-kit.md`](./trust-signals-kit.md)
- [`design/trust-signals-pilot-program.md`](./trust-signals-pilot-program.md)
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/policy-pilot-program.md`](./policy-pilot-program.md)
- [`design/typosquat-guard-kit.md`](./typosquat-guard-kit.md)
- [`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md)
- [`design/sbom-evidence-kit.md`](./sbom-evidence-kit.md)
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md)

Design rule: **the pilot is about evidence-to-decision continuity first**.
Registry/search/review/adoption views are important, but they should arrive late and stay explicitly downstream.

## Ranked pilots

### Pilot 1 — Lockfile evidence-to-policy lane
**Who this is for:** teams doing routine dependency review in CI or code review.

**Why first:**
- It proves the minimal stack promise: trust reports and policy decisions can travel together without collapsing into one artifact.
- It produces immediate value for publish/review workflows without requiring registry-side UX.

**Required artifacts**
- `trust-report/v0`
- optional imported graph-policy-lint summary
- `policy-decision-report/v0`
- `trust-decision-brief/v0`
- `trust-decision-pack/v0`

**Acceptance bar**
- A reviewer can answer “which signals were considered, which rules applied, and why this ended as pass/fail/inconclusive/waived?” without scraping CI logs.

### Pilot 2 — Build / proc-macro split-scope lane
**Who this is for:** workspaces that need stricter handling of compile-time dependencies.

**Why second:**
- Cargo Vet already proves scope-sensitive policy is real, not theoretical.
- This is the smallest lane that demonstrates trust-decision work is more than a flat runtime-dependency review.

**Required additions**
- scope-aware trust slices
- subtree or dependency-kind-sensitive policy rules
- diff output showing scope changes and their effect on decisions
- explicit notes about what the consumer may and may not conclude

**Acceptance bar**
- The stack can preserve different scrutiny levels for runtime, build, dev, and proc-macro lanes without pretending they were one undifferentiated package verdict.

### Pilot 3 — Publisher/freshness/cooldown plus graph-policy lane
**Who this is for:** orgs that want reviewable publish-authority and recency posture.

**Why third:**
- crates.io’s recent changes make publisher-control and freshness much more usable than before.
- This lane proves registry facts can feed decisions without becoming registry-owned verdicts.

**Required additions**
- Trusted Publishing posture import
- freshness and cooldown fields using `pubtime`
- trusted-publisher/date-window imports where present
- local `cargo-deny` policy-lint imports when used
- `trust-decision-diff/v0` showing freshness-driven or lint-driven changes

**Acceptance bar**
- A team can distinguish “recent publish”, “unknown publisher posture”, “stale evidence”, and “explicitly waived cooldown” without hand-written CI prose.

### Pilot 4 — Package/release plus artifact-recovery lane
**Who this is for:** package-admission and release-review workflows.

**Why fourth:**
- This is where the stack proves it can attach to real upstream decision points.
- It also forces clean boundaries with Package Admission, Release Truth, Inventory, and Signed Binaries.

**Required additions**
- `package-admission-brief` and/or release-truth attachment imports
- optional signed-binary / SBOM / lifecycle imports
- optional artifact-recovery imports (`cargo audit bin` / `cargo-auditable`) when the subject is a shipped binary
- explicit handoff notes saying where trust-decision authority stops

**Acceptance bar**
- A package or release review can attach a trust-decision bundle without silently claiming to settle installation, runtime, or support truth.

### Pilot 5 — Thin consumer-view lane
**Who this is for:** registry/search UX, PR bots, adoption briefs, and assistants.

**Why fifth:**
- This is the lane most likely to flatten nuance into theater.
- Delaying it ensures the evidence and decision artifacts exist first.

**Required additions**
- `trust-decision-view/v0`
- explicit compression/profile rules
- consumer-specific “must not claim” lists
- scorecard showing whether the rendering remained honest

**Acceptance bar**
- A thin consumer view can summarize trust posture while still linking back to evidence, rules, waivers, and scope boundaries.

## Shared pilot rules
- **Signal truth stays distinct from decision truth.** Do not replace one with the other.
- **Issuer and scope stay visible.** Advisory facts, imported audits, registry facts, and local annotations are not interchangeable.
- **Freshness is first-class.** Cooldown and time-window posture must be explicit.
- **Inconclusive stays real.** Missing evidence should not be silently turned into a verdict.
- **Views come last.** Registry/search/assistant summaries are consumers, not canonical truth.
- **Package/release attachment must stay bounded.** Trust decision is not the same thing as release truth or distribution truth.

## Immediate archive decision
Treat [`design/trust-decision-stack.md`](./trust-decision-stack.md), [`design/trust-decision-pilot-program.md`](./trust-decision-pilot-program.md), and [`proposals/epic-trust-decision-stack.md`](../proposals/epic-trust-decision-stack.md) as one execution band.
Use [`design/trust-signals-pilot-program.md`](./trust-signals-pilot-program.md) for the evidence-first rollout and [`design/policy-pilot-program.md`](./policy-pilot-program.md) for the rule/verdict rollout beneath it.
