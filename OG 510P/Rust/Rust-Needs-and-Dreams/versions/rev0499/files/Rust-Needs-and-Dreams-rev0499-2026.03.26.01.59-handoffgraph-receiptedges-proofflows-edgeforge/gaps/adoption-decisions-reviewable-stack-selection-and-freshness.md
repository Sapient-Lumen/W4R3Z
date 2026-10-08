# Gap: adoption decisions, reviewable stack selection, and freshness-aware recommendation briefs

## What is missing
Rust now has multiple ways to discover, evaluate, and discuss crates, but it still lacks a **boring, reviewable project-scoped adoption layer**.

Today teams can separately:
- search crates.io,
- consult unofficial or semi-curated directories like Blessed.rs and lib.rs,
- read official docs, examples, and migration notes,
- inspect trust and publishing posture,
- look at maintenance signals,
- and increasingly ask editors or assistants for recommendations.

What is still missing is the shared layer that answers:
- what exact project question is being asked,
- which candidate lanes and seams were actually considered,
- which trust, maintenance, docs, and local-fit signals materially shaped the answer,
- what serious alternatives remain viable,
- how fresh the recommendation is,
- and what portable pack a human reviewer, team lead, or bounded assistant should consume.

## Why it matters
This is not just about discovery.

Rust’s own recent vision work now says users need help getting oriented in the crates.io ecosystem, that there is no clear place to get advice on a good “starter set” of crates, and that smoother interop is part of the solution.
The 2025 State of Rust survey simultaneously says online docs remain canonical while LLM/editor tooling is rising.
That combination means recommendation quality is now both a **human navigation** problem and a **machine-consumption** problem.

Without a real adoption-decision substrate, teams keep rebuilding the same fragile process:
- ask around in chat,
- compare stale blog posts,
- infer maintenance from vibes,
- combine registry metadata with folk wisdom,
- produce an undocumented local choice,
- and forget why the choice was made.

A worthy contribution here would make Rust stack choice easier to **review, renew, diff, and explain** without blessing one global crate canon.

## Existing building blocks worth composing
- The Rust vision work explicitly recommends helping users navigate the crates.io ecosystem and says users lack a clear place to get advice on a good “starter set” of crates.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while LLM/editor tooling is increasingly part of learning and navigation.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io now exposes Security-tab data, Trusted Publishing-only mode, SLOC, and `pubtime`, which are stronger decision inputs than the ecosystem had before.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- docs.rs target-default changes are a reminder that support claims drift and need freshness-aware imports.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- Cargo continues to emphasize that plugins matter because Cargo cannot be everything to everyone.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The Rust Foundation strategy now pairs responsible adoption growth with sustainable maintainer support and stable secure infrastructure.
  https://rustfoundation.org/media/annual-report-strategy-2025/
- Blessed.rs already serves as an unofficial recommended crate directory, which is strong evidence that the discovery problem is real.
  https://blessed.rs/crates

## Why existing tools are not yet the whole answer
The ecosystem has **registries, curated directories, docs, trust signals, and assistants**, but not the **shared adoption brief layer**:
- crates.io helps you find packages;
- Blessed.rs and lib.rs help you orient;
- docs.rs and project docs help you learn;
- trust and maintenance signals help you judge risk;
- assistants help you summarize;
- Atlas and Commons can map lanes and seams.

But teams still have to invent their own answers for:
- normalized project question capture,
- visible alternative sets,
- freshness budgets and re-check rules,
- imported trust/maintenance/docs/local-fit boundaries,
- renewable recommendation diffs,
- and bounded machine-renderable adoption outputs.

That is the same pattern seen elsewhere in this archive: strong point tools, weak shared artifacts.

## Target outcome
A project should be able to say:
- “this is the adoption question we are answering,”
- “these are the serious Rust lanes and seams we considered,”
- “these trust, maintenance, docs, and local-fit inputs shaped the answer,”
- “this is the recommendation and these are the viable alternatives,”
- “this recommendation expires or must be re-checked under these conditions,”
- and “this is the portable pack humans and assistants may consume.”

That is bigger than a curated crate list and smaller than a universal recommendation engine.
