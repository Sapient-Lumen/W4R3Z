# Design: Keystone Stewardship Stack (`cargo keystone`, `keystone-pack/v0`)

## Goal
Treat **Maintenance Reality Stack**, **Trust Decision Stack**, and selected **Library Productization / Release Truth / Support Envelope** imports as one explicit **Keystone Stewardship Stack** for projects that have become foundational Rust infrastructure.

The missing contribution is not another health dashboard, another crate score, or a private spreadsheet for funders.
It is a portable, reviewable boundary that keeps six distinct truths separate while letting them compose:
- **subject truth** — what project/crate/service/toolchain subject is being reviewed;
- **criticality truth** — why it is keystone infrastructure and what blast radius or ecosystem role matters;
- **stewardship truth** — who maintains it, under what governance and with what public-vs-restricted operating posture;
- **institutional-support truth** — what funding, fiscal sponsorship, employer time, foundation hosting, legal/admin support, or other backing exists;
- **continuity-and-obligation truth** — what succession, security-response, release, docs/support, or compatibility obligations are expected and which remain best-effort;
- **consumer-import truth** — what Atlas/adoption, policy/trust, release, and funding consumers may conclude without reinterpreting the raw facts.

That separation matters because Rust now has projects that are too important to govern by vibes, but not so uniform that one universal badge would be honest.

## Why this seam matters now
Current Rust signals line up unusually well around keystone stewardship:
- The Rust Foundation’s 2026–2028 strategy explicitly centers **Stable Infrastructure**, **Sustainable Maintenance**, and **Adoption & Innovation**. That is a strong policy signal that critical-project continuity is ecosystem infrastructure rather than incidental admin work.
  https://rustfoundation.org/strategic-plan/
- The Maintainers Fund is designed for **consistent, transparent, long-term support**, aligned with high-impact project priorities and long-term maintainer continuity. That means support-routing and continuity evidence now have real downstream programs that could consume them.
  https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- The Rust Innovation Lab exists because Rust projects have matured into **critical pieces of global software infrastructure** and increasingly need **neutral, community-led governance and reliable institutional backing**. That is practically a statement that some Rust projects need a new layer above ordinary crate metadata.
  https://rustfoundation.org/media/rust-foundation-launches-rust-innovation-lab-with-rustls-as-inaugural-project/
- The Rustls / Innovation Lab framing is especially useful because it gives explicit criteria for what a keystone project looks like: **foundational infrastructure**, **clear industry traction and operational need**, and **deeply committed maintainers who need space to build**.
  https://rustfoundation.org/media/rustls-shortlisted-for-two-2025-openuk-awards/
- Official Rust writing on maintenance says the work includes triage, CI failures, docs upkeep, security incidents, review, refactoring, and contributor unblocking — and that this labor is multiplicative rather than merely janitorial. Keystone projects need a way to represent that reality explicitly.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- crates.io’s 2026 update adds stronger trusted-publishing and release-surface signals, but those still do not answer which projects need institutional backing or continuity planning. That is evidence for a companion keystone layer, not against it.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The 2025 State of Rust survey says docs remain canonical and support concerns remain visible, while explicitly encouraging companies to support the Rust contributors and crate authors they rely on. That is exactly the audience that needs a better keystone-support description than “we all know this crate matters”.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## What each stack layer should own
### Keystone layer
This new layer owns:
- criticality classification;
- institutional-support posture;
- keystone-specific obligations;
- continuity and succession posture;
- transition reports when a project moves into stronger stewardship.

Its question is:
> why is this project keystone infrastructure, what support/continuity posture exists, and what obligations follow from that status?

### Maintenance Reality Stack
[`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md) owns:
- declared lifecycle intent;
- observed queue pressure and stewardship operations;
- help routing and mentoring posture.

Its question is:
> what does day-to-day maintenance and continuity work actually look like here?

### Trust Decision Stack
[`design/trust-decision-stack.md`](./trust-decision-stack.md) owns:
- release-authority and provenance inputs;
- advisory/freshness/trust-policy facts;
- package/release trust decisions.

Its question is:
> what trust, provenance, and release-policy facts are true for this project or release?

### Library Productization / Release Truth / Support imports
These remain imports when relevant.
They answer:
> what public product boundary, release boundary, and support boundary is being consumed downstream?

That boundary matters. A project can be keystone infrastructure even when its product boundary is only one input to the larger stewardship story.

## Artifact family
### `keystone-subject/v0`
Identifies the reviewed subject:
- project / crate / workspace / service identity
- governing org or neutral host where relevant
- subject class (library, infra service, build tool, interop building block, security primitive, etc.)
- included and excluded scope

### `criticality-profile/v0`
Explains why keystone review is justified:
- keystone class (`security`, `shared-building-block`, `build-distribution-infra`, `foundational-runtime`, `ecosystem-service`, etc.)
- evidence for ecosystem role or blast radius
- operational-dependence notes
- non-claims and uncertainty notes

### `keystone-support-profile/v0`
Describes backing and operating support:
- maintainer roster and role posture
- volunteer / employer-backed / grant-backed / foundation-hosted / mixed support posture
- fiscal/admin/legal support status
- public-vs-restricted operational capacity notes
- contact/routing posture where publishable

### `keystone-obligation-profile/v0`
States what obligations are expected or claimed:
- security-response posture
- release/provenance expectations
- docs/support expectations
- compatibility or migration expectations where relevant
- explicit `best-effort`, `committed`, `partial`, and `not-declared` lanes

### `keystone-risk-register/v0`
Makes continuity and governance risks visible:
- single-maintainer or key-person risks
- funding/hosting uncertainty
- governance ambiguity
- release-authority concentration
- operational or infra concentration
- known mitigation plans or lack thereof

### `keystone-transition-report/v0`
Records movement into or between stewardship states:
- transition trigger
- before/after governance/support posture
- added or removed institutional support
- successor or succession notes
- unresolved migration or communication tasks

### `keystone-review-report/v0`
Periodic refresh report:
- what criticality/support/obligation/risk facts were rechecked
- what drifted
- what remained private, unavailable, or uncertain
- freshness / next-review state

### `keystone-pack/v0`
Thin bundle for consumers:
- subject + criticality + support + obligation + risk + review artifacts
- imported maintenance/trust/release/support attachments where used
- checksums, provenance, and generator identity
- optional Atlas/adoption/funding consumer summaries derived from canonical artifacts

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without reading issue threads, blog posts, org charts, and foundation announcements separately:
1. Why is this project being treated as keystone infrastructure at all?
2. What kind of keystone is it, and what blast radius matters?
3. What governance, staffing, and institutional support actually exist today?
4. What continuity or succession risks remain, and which mitigations are real versus aspirational?
5. What obligations are actually declared or expected?
6. What may Atlas/adoption, trust/policy, or support/funding programs safely import?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs a ranked execution layer, captured in:
- [`design/keystone-stewardship-pilot-program.md`](./keystone-stewardship-pilot-program.md)

That pilot program should prove the stack in this order:
1. **security keystone lane**
2. **shared-building-block lane**
3. **ecosystem service / infra lane**
4. **continuity-transition lane**
5. **consumer-import lane**

That ordering is intentional.
The archive should not start with a global “critical crates” list or a foundation-admission board disguised as a schema.
It should first prove that keystone status can be represented honestly on a few high-leverage subjects.

## Design principles
1. **Keystone is a status with obligations, not a compliment.**
2. **Criticality is not popularity.** Widespread use may matter, but ecosystem role and operational consequence matter more.
3. **Institutional support is not trust and not product quality.** Funding, hosting, and admin backing are distinct signals.
4. **Private operations can still yield public summaries.** The stack must tolerate restricted details without collapsing into silence or overclaiming.
5. **Continuity matters as much as present maintainership.** Succession and transition posture should be first-class.
6. **Consumers import; they do not redefine.** Adoption, policy, and funding tools should consume keystone facts rather than silently invent them.

## What an epic contribution would look like in practice
A serious contribution here would:
- make keystone-criticality reviews explicit instead of folklore-driven;
- connect maintainer reality and trust facts to institutional-support posture without flattening them;
- let a project publish an honest continuity and obligation profile even if some details remain restricted;
- support transition reports when a keystone project enters foundation hosting, receives structured maintainer funding, or adopts a new governance path;
- and give Atlas/adoption and support/funding programs one reusable keystone pack instead of bespoke spreadsheets and blog-post archaeology.

## Anti-goals
Do not turn this stack into:
- a universal ecosystem scoreboard;
- a forced blessed-crates program;
- a popularity chart with extra fields;
- or a private governance database masquerading as public infrastructure.

The stack is a **review boundary**, not a political replacement for the ecosystem.
