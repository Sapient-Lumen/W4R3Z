# Gap: keystone Rust projects still lack an honest institutional-stewardship boundary

Rust now has projects that are clearly more than “just another crate”. Some have become **foundational infrastructure** for the ecosystem or for critical downstream systems. But the ecosystem still lacks a portable way to say:
- why a project is keystone infrastructure,
- what continuity and security obligations follow from that status,
- what governance, funding, staffing, or administrative backing exists,
- what succession or transfer path is in place,
- and what downstream users, funders, or atlas/adoption tools may reasonably conclude.

Today those answers are scattered across:
- crate metadata and docs;
- issue trackers and release notes;
- maintainer blog posts and social channels;
- foundation announcements, grants, or sponsorship pages;
- trusted-publishing settings and release provenance;
- and org-specific memory about “which projects really matter”.

That fragmentation becomes dangerous precisely when a project becomes important enough that many others depend on it.

## Why this now matters more
Several current Rust signals make the missing seam unusually explicit:

- The Rust Foundation’s 2026–2028 strategy elevates **Stable Infrastructure** and **Sustainable Maintenance** to core pillars. That is strong evidence that critical-project continuity is no longer just community etiquette; it is strategic ecosystem infrastructure.
- The Rust Foundation Maintainers Fund is explicitly about providing **consistent, transparent, long-term support**, aligning support with high-impact priorities, giving visibility into how funding is used, and creating conditions for long-term maintainer roles and continuity.
- The Rust Innovation Lab was created because Rust adoption has accelerated, many Rust projects have matured into **critical pieces of global software infrastructure**, and those projects increasingly need **neutral, community-led governance and reliable institutional backing**.
- The Innovation Lab’s own Rustls framing is especially clarifying: the Foundation describes the kinds of projects it wants to support as ones that **provide foundational infrastructure**, have **clear industry traction and operational need**, and are driven by **deeply committed maintainers who need space to build**.
- The 2025 State of Rust survey says online docs remain canonical while concerns about developer and maintainer support remain visible and companies are explicitly encouraged to support Rust contributors and crate authors they rely on.
- crates.io now exposes richer trust-facing signals such as Trusted Publishing enforcement and SLOC, but those still do not answer the institutional question: **what should happen when a project becomes keystone infrastructure?**

Taken together, the missing problem is not merely “how do we rank crates?”
The missing problem is:

**how does Rust describe, support, and review projects that have become keystone infrastructure without turning the answer into popularity theater or a political blessing contest?**

## What is missing
The ecosystem needs a portable layer that keeps these truths distinct but composable:

1. **Criticality truth**
   - why the project matters to the ecosystem
   - what kind of keystone it is (security, interop/common building block, build/distribution infra, product substrate, etc.)
   - what dependency or operational blast radius is relevant

2. **Stewardship truth**
   - who maintains it
   - what governance model exists
   - what public-vs-restricted stewardship work is happening
   - whether the project is volunteer-bound, employer-backed, foundation-hosted, grant-backed, or otherwise institutionally supported

3. **Continuity truth**
   - what succession/handoff plans exist
   - whether long-term maintainer roles or explicit continuity funding exist
   - what single points of failure remain

4. **Obligation truth**
   - what security response, release, compatibility, support, or documentation obligations follow from keystone status
   - what is promised versus best effort versus aspirational

5. **Consumer truth**
   - what Atlas/adoption, policy/trust, funding, release, and downstream organizations may safely import
   - what remains partial, local, or non-public

## What this should not become
This should **not** become:
- a universal crate-quality score;
- a popularity leaderboard;
- a forced blessing system for crates.io;
- an ownership-transfer mechanism disguised as a dashboard;
- or a foundation-only gatekeeper for what “counts”.

The missing contribution is a **reviewable keystone-stewardship boundary** above existing trust, maintenance, release, and support surfaces.

## What a worthy contribution would look like
A real contribution here would define a thin artifact family and workflow that can:
- identify when a project is being reviewed as keystone infrastructure;
- attach explicit criticality reasons instead of prestige vibes;
- describe existing governance, funding, staffing, and continuity posture honestly;
- record keystone obligations and risk registers without pretending every project owes the same service level;
- support transition reports when a project moves toward foundation hosting, explicit support funding, or successor planning;
- and let Atlas/adoption, trust/policy, funding, and enterprise consumers import the same facts instead of reconstructing them from announcements and issue threads.

## Likely shape of the solution
The strongest path is an explicit **Keystone Stewardship Stack** that composes:
- **Maintenance Reality Stack** for declared lifecycle plus observed stewardship operations;
- **Trust Decision Stack** for release authority, advisory, and provenance-facing inputs;
- **Library Productization / Release Truth / Support Envelope** where the keystone subject is a user-consumed library or toolchain product;
- and a new keystone layer for **criticality, institutional support, continuity, obligations, and transition reports**.

This would finally let Rust describe a project not just as “popular” or “important”, but as **keystone infrastructure with reviewable stewardship posture**.

## Why this belongs in the archive now
The archive already has strong lower layers for maintenance, trust, release, and support.
What it still lacked was the explicit synthesis saying that a worthy contribution may need to be partly **institutional infrastructure**, not only more crate-local tooling.

That is especially important now that Rust has both:
- richer technical trust signals; and
- more explicit ecosystem programs for maintenance and foundation-hosted infrastructure.

## References (signals)
- Rust Foundation Strategic Plan 2026–2028:
  https://rustfoundation.org/strategic-plan/
- Announcing the Rust Foundation Maintainers Fund:
  https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- Rust Foundation Launches Rust Innovation Lab with Rustls as Inaugural Project:
  https://rustfoundation.org/media/rust-foundation-launches-rust-innovation-lab-with-rustls-as-inaugural-project/
- Rustls & the Rust Innovation Lab criteria:
  https://rustfoundation.org/media/rustls-shortlisted-for-two-2025-openuk-awards/
- What is maintenance, anyway?
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
