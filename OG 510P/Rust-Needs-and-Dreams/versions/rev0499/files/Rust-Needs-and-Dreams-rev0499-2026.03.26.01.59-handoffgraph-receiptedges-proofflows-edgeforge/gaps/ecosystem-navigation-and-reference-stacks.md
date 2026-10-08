## 2026Q1 sharpening note
This gap is now sharpened by `design/adoption-navigation-contract-2026Q1.md`.

New reading rule:
- the gap is no longer best described only as “reference stacks”;
- the missing seam is now a **portable recommendation contract** above Atlas, canonical references, trust/maintenance imports, and local-fit checks;
- the hard problem is keeping **question**, **candidate lanes**, **canonical references**, **imported evidence**, **local fit**, and **bounded brief** separate enough that the ecosystem can review them instead of inheriting prestige-driven lore.

# Gap: ecosystem navigation and reference stacks

## What is missing
Rust still lacks a **portable, reviewable contract for reference stacks**.

The problem is no longer just “crate search is imperfect.” The Rust project’s own 2025 vision work says users need help getting oriented in the crates.io ecosystem, notes that people do not have a good place to get advice on a starter set of crates, and argues that smoother interop and shared building blocks are part of the answer. At the same time, the 2025 State of Rust survey says online documentation remains the preferred canonical reference, maintainers support is an explicit concern, and people are increasingly learning with LLM tooling in the loop. That combination changes the problem: the ecosystem now needs **curated, evidence-backed, freshness-aware guidance artifacts** that can feed docs, onboarding, policy, and assistants without pretending there is one globally blessed answer.

What is missing today is a shared way to describe and review:
- which **domains** are being served (CLI, service, desktop app, embedded, safety-oriented internal tool, etc.),
- which **lanes** exist inside a domain (conservative, batteries-included, low-footprint, regulated, experimental),
- which **slots** matter in that lane (runtime, HTTP stack, error story, config layer, testing story, persistence layer, etc.),
- which crates or crate families fill those slots,
- which **interop seams** make the stack compose,
- which **evidence** supports those recommendations,
- who is making the recommendation,
- how long the recommendation may be trusted before re-checking,
- and which human-readable guides or AI-facing contexts were derived from the canonical artifacts.

The raw ingredients are much better than they used to be. crates.io now exposes a Security tab, SLOC, `pubtime`, and stronger trusted-publishing controls. The crates.io / rustdoc search-and-discoverability problem is important enough that the Rust Foundation funded work on rustdoc search discoverability and crates.io search experience. But those improvements are still mostly **inputs**. They are not yet a portable review layer above search results and lore.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rustfoundation.org/media/announcing-the-rust-foundations-2024-fellows/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

## The current seam is awkward
Today, “what should I use?” gets answered by a messy mixture of:
- crates.io search and category pages,
- docs.rs,
- README prose,
- unofficial curated sites,
- conference talks and migration blog posts,
- GitHub stars / download counts / issue activity,
- and tacit local memory carried by the person on the team who “knows Rust.”

This is better than nothing, but it fails in predictable ways:
- recommendation logic is not portable,
- defaults and alternatives are rarely separated cleanly,
- interop burden is usually implicit,
- freshness is poorly expressed,
- maintenance and succession posture are easy to ignore,
- and generated guidance from humans, internal docs, and LLMs drifts because there is no common canonical substrate.

The result is not just beginner confusion. Experts repeatedly recreate private “approved stack” spreadsheets, half-curated starter templates, or internal platform docs that silently age out. Meanwhile, assistants and code generators learn from stale examples and prestige signals because the ecosystem does not publish enough first-class “this is a good lane for this problem, as of this date, for these reasons” artifacts.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blessed.rs/crates
- https://www.arewewebyet.org/topics/
- https://lib.rs/

## Why this matters
A reference-stack substrate would improve several things at once:
1. **time-to-first-productive-project** — users need lane-shaped starter guidance, not only package search;
2. **interop quality** — stacks compose around shared seams (`serde`, `http`, `tower`, `bytes`, tracing, async runtime assumptions, etc.);
3. **maintenance honesty** — recommendations should incorporate maintenance and succession reality instead of only popularity;
4. **policy and trust** — lifecycle, advisories, trusted publishing, and support-envelope signals should inform stack guidance without collapsing into one fake score;
5. **documentation quality** — canonical artifacts can derive human guides instead of letting prose drift away from the underlying recommendation state;
6. **assistant quality** — LLMs need canonical starter-stack truth more than they need another pile of blog posts;
7. **institutional memory** — teams need explicit stack decisions that survive turnover.

There is also a political reason to do this explicitly. Curation is already happening. The real choice is between **opaque prestige-driven curation** and **lane-based, evidence-backed, reviewable curation**.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## What “good” looks like
A worthy contribution here is **not** another search engine, another crate-score leaderboard, or one official blessed-crates page.

It is a **curator-aware, lane-based atlas boundary** with canonical artifacts such as:
- `atlas-domain/v0` — the problem domain and its major constraints;
- `stack-lane/v0` — the lane philosophy and success criteria;
- `stack-slot-map/v0` — the slots that matter in this lane and the selected crate families;
- `interop-seam-map/v0` — shared types, runtimes, middleware seams, wire contracts, or adapter burdens;
- `selection-evidence/v0` — why the chosen crates are in the lane;
- `alternative-set/v0` — respectable alternatives and why they are not default here;
- `curator-record/v0` — who is making the recommendation and under what stewardship posture;
- `freshness-budget/v0` — how long the lane can be trusted before re-checking and what invalidates it early;
- `atlas-check-report/v0` — what was re-checked and what drifted;
- `atlas-pack/v0` — the bundle consumed by docs, policy, onboarding, and long-term archaeology.

From those artifacts, tools can derive:
- human-readable domain guides,
- starter templates or manifests,
- org-specific “approved stack” overlays,
- and bounded `assistant-context/v0` outputs for LLM use.

The canonical truth should remain the structured atlas artifacts; generated prose and AI contexts are **derived outputs**, not the source of truth.

## Why this could be epic
This is the kind of contribution that does not look flashy at first, but it can have a multiplicative effect on the ecosystem:
- better onboarding without central lock-in,
- better interop visibility,
- more honest recommendation freshness,
- better use of the registry’s growing evidence surface,
- less duplicated local curation labor,
- and more reliable human + machine guidance.

If Rust wants to remain a language where the ecosystem is a strength rather than a gauntlet, it needs better **reference-stack infrastructure**, not just better arguments about crate popularity.
