# Epic Proposal: Keystone Stewardship Stack (`cargo keystone` + `keystone-pack/v0`)

## Why this is worthy
Rust now has projects that have clearly crossed a threshold from “useful crate” to **keystone infrastructure**.
The Rust Foundation’s current strategy, Maintainers Fund, and Innovation Lab all point in the same direction: some Rust projects need reviewable continuity, governance, funding, and obligation boundaries above ordinary crate metadata and release pages.

But the ecosystem still has no single honest handoff for **keystone-project stewardship truth**.

That means adopters, funders, maintainers, and ecosystem curators still have to reconstruct the answer from:
- issue threads and maintainer comments;
- foundation announcements;
- release provenance and trusted-publishing settings;
- support docs and READMEs;
- social knowledge about “what everyone depends on”; and
- ad hoc private spreadsheets.

The missing contribution is a thin portable layer above those pieces, not another ranking site or political blessing mechanism.

## Proposal
Define a **Keystone Stewardship Stack** with:
- a reference review CLI, `cargo keystone`;
- a thin linked bundle, `keystone-pack/v0`;
- imported evidence from:
  - Maintenance Reality artifacts
  - Trust / release / support attachments where relevant
  - library or service productization artifacts where relevant
- stable keystone-facing artifacts:
  - `keystone-subject/v0`
  - `criticality-profile/v0`
  - `keystone-support-profile/v0`
  - `keystone-obligation-profile/v0`
  - `keystone-risk-register/v0`
  - `keystone-transition-report/v0`
  - `keystone-review-report/v0`

## Reference CLI shape
- `cargo keystone export`
  - emit `keystone-subject/v0` and `criticality-profile/v0` for one subject
- `cargo keystone review`
  - emit `keystone-review-report/v0` from imported maintenance / trust / release / support inputs
- `cargo keystone transition --against <prior-pack|ref>`
  - emit `keystone-transition-report/v0`
- `cargo keystone pack`
  - produce `keystone-pack/v0`
- `cargo keystone verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace the lower-layer kits.

## What `keystone-pack/v0` should contain
- `manifest.json`
- `keystone-subject.json`
- `criticality-profile.json`
- `keystone-support-profile.json`
- `keystone-obligation-profile.json`
- optional `keystone-risk-register.json`
- optional `keystone-transition-report.json`
- `keystone-review-report.json`
- imported maintenance / trust / release / support attachments or pointers
- checksums, provenance, and generator identity
- optional Atlas/adoption/funding consumer pointers

## Design principles
- **Keystone status is explicit, reasoned, and reviewable.**
- **Criticality stays separate from trust, quality, and popularity.**
- **Institutional support stays separate from product surface.**
- **Restricted detail is allowed, but non-claims must be visible.**
- **Transitions and continuity are first-class.**
- **Consumer imports come after canonical evidence.**

## Early implementation order
1. security keystone subject
2. shared-building-block subject
3. ecosystem-service / infra subject
4. continuity-transition reports
5. Atlas/adoption/funding consumer imports

## Non-goals
- a global critical-crates ranking;
- forced crate blessing;
- replacing trust policy or package admission;
- replacing Maintainers Fund or Innovation Lab processes;
- making funding or governance decisions inside the pack itself.

## Success bar
This becomes worthy when a maintainer, adopter, curator, or funder can answer:
- why this project is keystone infrastructure;
- what stewardship and institutional support actually exist;
- what continuity or governance risks remain;
- what obligations are declared or expected;
- and what changed when stewardship posture shifted,

without scraping blog posts, registry pages, issue trackers, and foundation updates separately.

## Read this with
- `gaps/keystone-projects-critical-infrastructure-and-institutional-stewardship-contracts.md`
- `design/keystone-stewardship-stack.md`
- `design/keystone-stewardship-pilot-program.md`
- `design/maintenance-reality-stack.md`
- `design/trust-decision-stack.md`
- `design/library-productization-stack.md`
