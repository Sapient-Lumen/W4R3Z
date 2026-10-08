# Epic Proposal: Policy Kit (`cargo policy`)

## One-sentence pitch
Create a first-class, explainable policy substrate for Rust dependency and release decisions: one artifact family that records **subject**, **imported evidence**, **declared rules**, **waivers**, **decision outcomes**, and **diffs** across existing tools instead of replacing them.

## Why this is worthy
This is one of the highest-leverage ecosystem contributions available because it turns many separate good tools into a coherent operational surface.

Rust now has:
- registry-side security and publication controls,
- advisory databases and scanners,
- trusted-publisher and imported-audit workflows,
- richer dependency inventory work,
- and an emerging family of evidence kits in this archive.

What it still lacks is the shared, machine-readable answer to:
**“Why is this dependency set acceptable, blocked, or conditionally allowed?”**

That answer is valuable to:
- CI,
- code review,
- release review,
- incident response,
- security exceptions,
- migration planning,
- and LLM/assistant workflows that need durable reasoning artifacts rather than scraped logs.

## Deliverables
### Schemas
- `policy-subject/v0`
- `policy-input-catalog/v0`
- `policy-rule-catalog/v0`
- `policy-waiver/v0`
- `policy-decision-report/v0`
- `policy-diff-report/v0`
- `policy-pack/v0`

### Reference CLI
- `cargo policy init`
- `cargo policy check`
- `cargo policy report`
- `cargo policy explain`
- `cargo policy diff`
- `cargo policy waive`
- `cargo policy verify`

### Adapters / import lanes
- `cargo-deny`
- `cargo-audit` / `rustsec`
- `cargo-vet`
- Trust Signals Kit
- Lifecycle Ledger Kit
- SBOM Evidence Kit
- Typosquat Guard Kit
- Signed Binaries / Repro Build / Support Envelope kits

### Integration targets
- GitHub/GitLab CI summaries
- PR diff views
- release-candidate attachments
- human-readable waiver review
- machine-readable explanation API for bots and assistants

## Why now
### 1) Rust itself is prioritizing supply-chain controls
The 2026 roadmap explicitly includes supply-chain work like public/private dependencies and SBOM support, which means policy plumbing is becoming central to the ecosystem rather than optional enterprise garnish.
https://rust-lang.github.io/rust-project-goals/2026/flagships.html

### 2) crates.io is emitting richer policy-relevant facts
The 2026 crates.io update added a Security tab, Trusted Publishing improvements, blocked risky triggers, and `pubtime`. Those are exactly the kinds of signals a shared policy layer should consume.
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

### 3) `cargo vet` already proves policy is multi-dimensional
`cargo vet` distinguishes criteria, lets projects adjust policy by dependency type, supports imported audit sets, and has date-bounded trusted-publisher entries. That is already policy logic, but not yet a general-purpose policy artifact family.
https://mozilla.github.io/cargo-vet/audit-criteria.html
https://mozilla.github.io/cargo-vet/specifying-policies.html
https://mozilla.github.io/cargo-vet/trusted-entries.html

### 4) `cargo-deny` already proves structured inputs exist
Target-aware filtering, advisory classes, duplicate-version handling, SPDX-oriented license configuration, and machine-readable exit classes mean the raw policy ingredients are already there.
https://embarkstudios.github.io/cargo-deny/checks/cfg.html
https://embarkstudios.github.io/cargo-deny/checks/advisories/index.html
https://embarkstudios.github.io/cargo-deny/checks/bans/index.html
https://embarkstudios.github.io/cargo-deny/checks/licenses/cfg.html
https://embarkstudios.github.io/cargo-deny/cli/check.html

### 5) artifact-linked auditing is becoming more realistic
`cargo-audit` plus `rustsec`, and especially `cargo audit bin` when paired with auditable binaries, means policy can increasingly reason about what was actually shipped, not just what the workspace happened to resolve today.
https://docs.rs/crate/cargo-audit/latest
https://docs.rs/rustsec/latest/rustsec/

## Non-goals
- Replacing cargo-deny, cargo-vet, rustsec, registries, or CI systems.
- Defining one global policy for all Rust projects.
- Forcing crates.io to become the sole policy authority.
- Compressing many different evidence types into one scalar “security score”.
- Hiding missing evidence behind optimistic defaults.

## Theoretical shape
A good policy substrate should model five layers explicitly:
1. **Subject** — what workspace / lockfile / artifact slice is under review?
2. **Inputs** — what evidence sources and freshness bounds were imported?
3. **Rules** — what requirements applied to this slice and why?
4. **Decisions** — what PASS/WARN/FAIL/INCONCLUSIVE/WAIVED outcomes followed?
5. **Diffs** — what changed relative to the previous accepted baseline?

This is the critical theoretical move because it prevents these common category errors:
- treating missing evidence as failure when it is really inconclusive,
- treating waivers as passes,
- treating rule changes as evidence changes,
- and treating point-in-time scans as stable review baselines.

## Practical shape
The reference implementation should begin as an **orchestrator and validator**.
It should:
- import structured outputs where possible,
- normalize them into `policy-input-catalog/v0`,
- evaluate explicit rules,
- emit one policy pack,
- and provide explanation / diff UX.

It should not initially attempt to own every scanning engine.

## High-value early adopters
1. **Security-sensitive backend teams**
   - want proc-macro- and runtime-specific rules,
   - want audit criteria requirements for critical crates.
2. **Large monorepos**
   - need different rules for products, internal tools, and build-only code.
3. **Release engineering teams**
   - want artifact-linked policy decisions rather than only workspace-time scans.
4. **Open source maintainers**
   - want reproducible CI policy checks and explainable exceptions without bespoke scripting.

## Milestones
### Milestone 1 — Core decision layer
- define `policy-subject`, `policy-rule-catalog`, `policy-decision-report`
- import `cargo-deny` and `cargo-audit` outputs
- ship `cargo policy check/report/explain`
- package this milestone as the **Package Release Gate** pilot from [`design/policy-pilot-program.md`](../design/policy-pilot-program.md)

### Milestone 2 — Waivers and diffs
- define `policy-waiver` and `policy-diff-report`
- add expiry, owner, and justification rules
- add PR-friendly diff summaries
- widen into the **Workspace Split-Scope** pilot without letting waivers leak across subject slices

### Milestone 3 — Trust-aware composition
- import cargo-vet policy/trust material and Trust Signals Kit artifacts
- support freshness windows, cooldown rules, and issuer-aware explanation chains
- make the **Proc-Macro / Build-Lane Cooldown** pilot viable for security-sensitive workspaces

### Milestone 4 — Release-grade policy packs
- compose with SBOM Evidence, Signed Binaries, Repro Build, and Support Envelope kits
- support artifact/release-subject evaluation instead of workspace-only evaluation
- make the **Artifact-Linked Release Candidate** pilot viable without collapsing neighboring kits into Policy

### Milestone 5 — Regression corpus and public examples
- use the **Migration Diff / Review** pilot as the first explicit long-lived explanation corpus
- curated corpus of real policy cases:
  - new advisory,
  - license change,
  - newly trusted publisher,
  - duplicate-version ban,
  - proc-macro cooldown failure,
  - waived release exception,
  - stale imported audit set,
  - artifact-linked vs workspace-linked discrepancy

## Success criteria
- A CI failure can be explained in a few hops with referenced evidence.
- A waiver is visible, reviewable, and expiring.
- A policy diff can distinguish evidence change from rule change.
- Runtime/build/proc-macro/release scopes remain cleanly separated.
- Existing tools get **more valuable** when plugged into Policy Kit, not replaced.

## Strategic payoff
If this works, Rust gets something rarer than another good scanner:
it gets a shared decision language for dependency and release governance.

That would make many other archive threads stronger at once, because Trust, Lifecycle, SBOM, Support, Signed Binaries, Incident response, Migration, and Atlas all become easier to consume once there is a common policy boundary over them.


## Execution order
Use [`design/policy-pilot-program.md`](../design/policy-pilot-program.md) as the ranked rollout plan. The archive should now judge Policy work less by how many scanners it can ingest and more by whether `policy-pack/v0` survives those five concrete decision points honestly.
