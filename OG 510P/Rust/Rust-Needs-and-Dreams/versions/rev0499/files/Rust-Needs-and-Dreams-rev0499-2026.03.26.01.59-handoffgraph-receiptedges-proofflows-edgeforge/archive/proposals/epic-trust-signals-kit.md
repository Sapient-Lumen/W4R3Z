# Epic Proposal: Trust Signals Kit (`cargo trust`, `trust-pack/v0`)

## One-sentence pitch
Create a portable, issuer-aware, policy-driven trust-evidence layer for Rust dependencies so users and organizations can automate dependency decisions without relying on opaque crate scores.

## Deliverables
- `cargo trust` reference implementation
- Schemas:
  - `trust-signal/v0`
  - `trust-report/v0`
  - `trust-import-profile/v0`
  - `trust-diff-report/v0`
  - `trust-pack/v0`
- Adapters / integrations for:
  - crates.io trust-relevant facts (Trusted Publishing posture, `pubtime`, security-tab/advisory data)
  - RustSec advisories
  - cargo-vet audits and imported criteria
  - lifecycle inputs
  - provenance / signing / reproducibility evidence
  - typosquat- and impersonation-risk inputs
- Example policies:
  - “Strict proc-macro policy”
  - “Pragmatic runtime policy”
  - “Recent-publish cooldown policy”

## Why now
- crates.io now exposes more trust-relevant facts directly: a Security tab, GitLab Trusted Publishing support, Trusted Publishing only mode, blocked risky triggers, and publication timestamps in the index.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- cargo-vet already demonstrates a mature decentralized audit-sharing workflow with built-in criteria like `safe-to-run` and `safe-to-deploy`, plus custom criteria for specialized reviews.
  https://mozilla.github.io/cargo-vet/how-it-works.html
  https://mozilla.github.io/cargo-vet/audit-criteria.html
- crates.io’s malware-notification policy now routes most malicious-crate removals through RustSec advisories, reinforcing the importance of advisory ingestion while also showing that advisories alone are not the full trust story.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- community appetite for crate reliability/verification remains strong, but in the absence of a shared evidence substrate the conversation repeatedly risks collapsing into opaque ranking proposals.
  https://internals.rust-lang.org/t/adding-a-reliability-rating-system-to-crates-io/23567
  https://rust-lang.github.io/rfcs/1824-crates.io-default-ranking.html

## Lane rule
Execute this epic with [`design/trust-decision-lane-map.md`](../design/trust-decision-lane-map.md) as the separation rule so registry facts, RustSec advisories, cargo-vet attestations, cargo-deny policy lints, artifact recovery, local waivers, and thin consumer views do not collapse into one fake verdict.

## Strategic value
This is a worthy contribution because it turns trust from a vague social judgment into structured infrastructure.

It unlocks:
- explainable policy decisions over lockfiles,
- cleaner registry and search UX,
- attachable trust posture for releases and CI,
- explicit differentiation between build/proc-macro/runtime dependency risk,
- and better incident and migration workflows when trust posture changes.

The archive already has Policy, Lifecycle, Incident, Signed Binaries, Typosquat Guard, and Release Pipeline threads.
Trust Signals Kit is the missing substrate connecting them.

## Non-goals
- One mandatory crates.io score for all users
- Replacing RustSec, cargo-vet, or provenance/signing tools
- Publishing private trust evidence without consent
- Treating popularity or stars as canonical trust truth
- Enforcing registry policy globally from day one

## Milestones
1. **v0 signals + report**
   - define `trust-signal/v0` and `trust-report/v0`
   - ingest basic registry facts, advisories, and cargo-vet audits
2. **v0.2 import profile + explanation**
   - define `trust-import-profile/v0`
   - preserve issuer/scope/freshness semantics and explanation chains
3. **v0.3 diff + release attachment**
   - define `trust-diff-report/v0` and `trust-pack/v0`
   - attach trust posture to CI and release candidates
4. **v1 ecosystem pilots**
   - at least one build/proc-macro-sensitive trust workflow
   - at least one policy handoff workflow
   - at least one registry/search UI experiment

## Success criteria
- users can understand why a dependency passed or failed trust policy,
- build/proc-macro/runtime trust thresholds can differ cleanly,
- trust posture diffs are explicit and reviewable,
- rankings, if any, are explainable thin views over the underlying artifacts,
- and the ecosystem gains a neutral trust-evidence substrate instead of another opaque score debate.


## Execution posture
- Execute this as part of the ranked trust rollout in [`design/trust-signals-pilot-program.md`](../design/trust-signals-pilot-program.md).
- Treat this as the evidence half of the broader Trust Decision Stack in [`design/trust-decision-stack.md`](../design/trust-decision-stack.md), not as a bid to replace Policy Kit or cargo-vet.
