# Design: Recommendation Posture Ladder

## Goal
Define a small, explicit ladder for **what kind of recommendation claim** a Rust ecosystem artifact is making.

The archive already has strong pieces for **adoption decisions**, **ecosystem atlas curation**, **profile-aware onramps**, **project bootstrap**, and **interop commons**. What it still lacked was a clean answer to a politically and operationally important question:

> how can Rust say something more useful than “it depends” without accidentally turning every good recommendation into a permanent blessed answer?

This note exists to keep future work from collapsing very different postures into one blob called “crate guidance”.

## Why this matters now
Fresh official Rust signals now describe the same tension from multiple angles:
- the December 2025 vision post says Rust users need help navigating crates.io, says there is no clear place to get advice on a good “starter set” of crates, and says the neutral stance makes this difficult because blessing crates carries political risk;
- the March 20, 2026 challenges post says ecosystem navigation still relies too much on tacit knowledge, describes choice paralysis directly, and says the tradeoff around recommending crates may be worth reevaluating or solved more creatively;
- the 2025 State of Rust survey says online documentation remains the canonical reference while editor/LLM-mediated learning continues to rise, which raises the cost of fuzzy recommendation authority;
- crates.io now exposes materially better recommendation inputs such as Security-tab advisory surfacing, Trusted Publishing posture, SLOC, and `pubtime`; and
- Cargo’s own development updates keep stressing that Cargo cannot be everything to everyone, which argues for a companion layer rather than turning Cargo itself into the one official curation engine.

References:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## The missing seam
Without an explicit posture ladder, ecosystem guidance keeps drifting between two bad extremes:
1. **non-answer neutrality** — there are many good crates, so the system refuses to say anything concrete;
2. **accidental blessing** — one pilot lane, starter repo, blog post, or assistant answer silently becomes the default answer for everyone.

The archive already has artifacts that *could* support a healthier middle path. But it still needed one compact rule saying that:
- not every recommendation is equally official,
- not every recommendation is equally durable,
- not every recommendation is allowed to become a default,
- and some recommendations should terminate at “good candidate”, while others may honestly rise to “shared common ground” or “local institutional default”.

## The ladder
Treat recommendation posture as a ladder with explicit promotion boundaries.
Not every domain needs every rung.
Not every crate or lane should climb.

### Level 0 — Raw evidence import
Purpose:
- collect inputs without making a recommendation yet.

Allowed claim:
- “these crates, signals, docs, advisories, and interop facts are relevant inputs.”

Typical inputs:
- crates.io Security-tab data, Trusted Publishing posture, SLOC, `pubtime`;
- docs.rs presence/targets;
- maintenance/support/trust evidence;
- interop/common-ground references;
- benchmark/build/debug/support evidence where relevant.

Not allowed:
- naming a default crate or lane.

Closest archive owners:
- Package Admission
- Maintenance Reality
- Trust Signals
- Build-State Evidence
- Compatibility Claims

### Level 1 — Curated candidate set
Purpose:
- reduce the search space honestly.

Allowed claim:
- “here are the serious candidates worth considering for this slot/domain/profile.”

Required traits:
- curator identity;
- scope and audience;
- reasons for inclusion;
- explicit freshness window;
- explicit non-claims.

Not allowed:
- pretending the shortlist is already the recommended default for every project.

Closest archive owners:
- Ecosystem Atlas
- Adoption Decision

### Level 2 — Reviewable lane recommendation
Purpose:
- recommend a concrete lane for a concrete project profile.

Allowed claim:
- “for this problem shape, constraints, and risk posture, start with this lane.”

Required traits:
- slot map and alternatives;
- interop notes;
- caveats and anti-goals;
- freshness budget;
- explanation of why this lane is default *here*.

Not allowed:
- implying that the lane is universally right outside the named profile.

Closest archive owners:
- Adoption Decision
- Ecosystem Atlas

### Level 3 — Profiled starter default
Purpose:
- give a newcomer or team one reviewable first route that actually gets them moving.

Allowed claim:
- “if you match this background/domain profile, this is the first lane and first starter path we recommend.”

Required traits:
- profile and background assumptions;
- canonical learning imports;
- bootstrap handoff;
- workspace/environment assumptions;
- strong freshness + expiration posture.

Not allowed:
- laundering one starter path into a domain-wide or ecosystem-wide permanent endorsement.

Closest archive owners:
- Profiled Onramp
- Project Bootstrap
- Starter Pack
- Workspace Environment

### Level 4 — Neutral shared common ground
Purpose:
- identify the small shared building block that many lanes can rely on without forcing one whole framework.

Allowed claim:
- “this seam is common ground across multiple ecosystems.”

Typical examples:
- common HTTP types,
- common service/middleware seams,
- other interop traits/types that stay intentionally small.

Required traits:
- explicit adopter diversity;
- adapter/conformance evidence;
- semantic exclusions;
- stewardship posture.

Not allowed:
- using “common ground” as a disguised way to bless one entire higher-level stack.

Closest archive owner:
- Interop Commons

### Level 5 — Local institutional default
Purpose:
- let a company, project, product family, or regulated environment adopt a stronger default without pretending it is universal Rust truth.

Allowed claim:
- “for this org or product family, this is our approved lane/default/overlay.”

Required traits:
- owning institution or team;
- review owner;
- policy/support horizon;
- overlay diffs from public base guidance;
- explicit expiration / renewal posture.

Not allowed:
- presenting local policy as if the broader ecosystem endorsed it.

Closest archive owners:
- Atlas overlays
- Starter overlays
- Package Admission policy overlays
- Workspace / Support / Release overlays

## Promotion rules
A worthy recommendation system does not just define levels; it defines **what must be true to move upward**.

### 0 → 1
Promote only when the archive can explain:
- why these candidates were chosen,
- why others were excluded or deferred,
- and what freshness/recheck budget applies.

### 1 → 2
Promote only when the archive can explain:
- which project profile is being optimized for,
- which slots and interop seams matter,
- why one lane is default here,
- and what major alternatives remain first-class.

### 2 → 3
Promote only when the archive can actually hand the user off to:
- canonical learning,
- a first reviewable project skeleton,
- and a realizable local environment.

### 2/3 → 4
Promote only when the archive has real evidence that the common ground is:
- smaller than a framework,
- adopted across multiple serious ecosystems,
- and testable through adapters/conformance rather than only prose.

### any → 5
Promote only as a local overlay.
This is a scope increase in authority, not a proof that the public ecosystem should follow.

## Required metadata for every rung above Level 0
Every recommendation artifact or rendered recommendation should carry:
- **scope** — domain, profile, slot, project class, or institution;
- **curator** — who is making the claim;
- **posture level** — which rung this claim occupies;
- **freshness** — when it expires or must be rechecked;
- **alternatives** — what remains credible and why;
- **authority boundary** — what this claim does *not* settle;
- **promotion boundary** — what additional evidence would justify moving up a rung.

Without that metadata, a recommendation is too easy to over-read.

## What this changes elsewhere in the archive
### Adoption Decision
Should stop at **Level 2** unless it is explicitly emitting a profiled starter handoff.
Its job is to recommend a lane for a project, not to create an ecosystem-wide default.

### Ecosystem Atlas
Should explicitly support **Level 1** and **Level 2**.
It can host candidate sets and lane defaults, but should not silently imply Level 4 or Level 5 authority.

### Profiled Onramp
Should consume **Level 2** guidance and emit **Level 3** first-route defaults for named learner/team profiles.

### Project Bootstrap / Starter Pack
Should realize **Level 3** guidance without laundering the starter repo into the original authority source.

### Interop Commons
Should own **Level 4** when the answer is “shared building block”, not “best framework”.

### Local overlays / package policy / regulated environments
Should sit at **Level 5** and remain visibly local.

## Worthy contribution, sharpened
The worthy contribution here is **not** another blessed-crates page, popularity leaderboard, hidden recommender model, or assistant that speaks with one mysterious level of confidence.

It is a thin recommendation-control layer — whether or not it ever gets its own CLI — that lets Rust ecosystem guidance say:
- when it is only importing evidence,
- when it is narrowing to candidates,
- when it is recommending a project-scoped lane,
- when it is giving a profiled first default,
- when it has identified true neutral common ground,
- and when it has crossed into local institutional policy.

That is the missing political and practical seam between “say nothing” and “accidentally bless everything”.

## Failure modes to avoid
- one fake universal crate-quality score;
- one undifferentiated recommendation blob mixing public guidance and local overlays;
- one starter template being mistaken for the ecosystem verdict;
- one interop crate being mistaken for the whole domain answer;
- one assistant rendering being treated as the source of truth;
- or one pilot lane silently becoming a permanent blessing because it shipped first.
