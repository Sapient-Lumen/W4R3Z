# Epic Proposal: Lifecycle Ledger Kit (`cargo lifecycle`, `lifecycle-pack/v0`)

## One-sentence pitch
Make Rust crate maintenance, support windows, deprecation, succession, and explicit handoff intent first-class artifacts so the ecosystem stops overloading RustSec, README prose, yanks, and repo-activity heuristics as its lifecycle channel.

## Deliverables
- `cargo lifecycle` reference tool
- Schemas:
  - `lifecycle-intent/v0`
  - `support-window-map/v0`
  - `successor-map/v0`
  - `handoff-consent/v0`
  - `maintenance-report/v0`
  - `lifecycle-report/v0`
  - `lifecycle-diff-report/v0`
  - `lifecycle-pack/v0`
- Adapters / integrations for:
  - Cargo manifest metadata and future registry metadata lanes
  - crates.io UI / API surfacing
  - RustSec lifecycle-relevant advisories
  - `cargo-unmaintained`-style heuristics
  - trust/policy consumers
- Docs:
  - support-window guidance
  - successor verification semantics
  - maintainer-help / handoff consent guidance
  - “declared vs inferred lifecycle” semantics

## Why now (signals)
- The Rust Foundation Maintainer Fund work says maintenance labor is real, critical, and often invisible; that is a direct signal that the ecosystem needs a better way to publish and recognize maintenance state and work.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- crates.io now surfaces security advisories directly in a Security tab, showing that registry UX is already evolving toward richer dependency-selection-time health information.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io’s malicious-crate notification policy now routes most malware announcements through RustSec advisories, reinforcing that security channels should stay security-focused rather than carrying ordinary lifecycle meaning too.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo still documents a maintenance-status vocabulary in `[badges]`, while also noting that crates.io no longer uses badges directly. That is clear evidence of an abandoned metadata seam waiting for a better successor.
  https://doc.rust-lang.org/cargo/reference/manifest.html
- RFC 3537 explicitly highlights version maintenance status on crates.io as missing context for supported older versions and MSRV-aware dependency choice.
  https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
- crates.io policy requires explicit owner approval for transfer, so maintainership and handoff intent need structured explicit metadata rather than “looks inactive” folklore.
  https://crates.io/policies
- `cargo-unmaintained` proves there is real demand for lifecycle signals, but also shows that heuristics only partially recover the needed truth.
  https://docs.rs/crate/cargo-unmaintained/1.9.0

## Non-goals
- Automatic ownership transfer based on inactivity
- Treating RustSec as the canonical lifecycle channel
- One global crate health score
- Mandatory heavyweight maintenance reporting for all crates
- Resolver-level automatic dependency replacement based on successor hints

## Strategic value
This is a worthy contribution because it upgrades a soft but crucial ecosystem seam from folklore into infrastructure.

It unlocks:
- clearer dependency choice between deprecated, unsupported, supported-old, and successor-available crates,
- better policy and trust decisions without README scraping,
- richer crates.io UX without inventing opaque rankings,
- visible maintenance evidence that can support stewarding and funding,
- better migration/release workflows when lifecycle facts change,
- and cleaner separation between security incidents and normal lifecycle communication.

The archive already has Trust Signals, Policy, Incident, Migration, and Org/Registry UX threads.
Lifecycle Ledger fills the missing substrate beneath them.

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for lifecycle intent, support windows, successors, handoff consent, maintenance reports, derived lifecycle reports, diffs, and packs;
2. `cargo lifecycle report` to combine declared metadata, registry inputs, RustSec, and heuristics while keeping them distinct;
3. `cargo lifecycle pack` so release and registry tooling can attach lifecycle facts durably;
4. crates.io-style surfacing experiments for support windows, deprecation, successor links, and maintainer-help banners;
5. policy/trust examples that consume lifecycle artifacts without redefining them.

The winning version is boring, explicit, and artifact-first.
It should make today’s scattered lifecycle clues legible together rather than replacing them with a score.

## Initial pilots
- one stable but slow-moving crate that wants to declare supported version lines explicitly
- one deprecated crate with a verified successor and a migration note
- one crate seeking co-maintainers or handoff with explicit consent metadata
- one workspace or org that wants a lockfile-level lifecycle report combining declared metadata, RustSec, and heuristics

## Milestones
1. **v0 schemas + examples**
   - publish `lifecycle-intent`, `support-window-map`, and `lifecycle-report`
   - make declared versus inferred truth explicit
2. **Derived reporting + doctoring**
   - ship `cargo lifecycle report` / `doctor`
   - support conflicts, unknowns, and reason codes
3. **Successor + handoff workflows**
   - add `successor-map` and `handoff-consent`
   - document verification levels and registry policy boundaries
4. **Maintenance visibility + diffs**
   - add `maintenance-report` and `lifecycle-diff-report`
   - pilot release and stewardship workflows
5. **Registry / policy pilots**
   - show how crates.io/Cargo/trust/policy consumers can surface lifecycle state without overreach

## Success criteria
- maintainers can express support windows, deprecation, and maintainer-help state without README-only conventions,
- users can distinguish unsupported from merely non-latest,
- successor pointers become more useful without becoming spoofable magic,
- lifecycle facts stop being forced through RustSec or activity heuristics alone,
- and trust/policy/release tools can consume lifecycle artifacts directly.
