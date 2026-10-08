## Current note (rev0379)
This framework now has an explicit companion layer in `design/lane-default-evidence-bundle.md`.
Use that layer when applying this rubric.

Practical consequence:
- question 2 (“explainable from canonical references”) should import a `canon-import-set` rather than freehand link lists;
- question 4 (“maintenance and trust reality rather than vibes”) should import registry / API / maintenance / support-envelope evidence explicitly;
- question 8 (“renew cheaply”) should result in a visible renewal judgment and, ideally, a diffable evidence pack.

The framework remains the rubric.
The evidence bundle becomes the portable receipt.

# Design: Lane Default Evaluation Framework

## Goal
Turn **Reviewable Lane Defaults** from a good abstract layer into a repeatable evaluation practice.

The archive already has the right structural insight:
- Atlas should map candidate space.
- Reviewable Lane Defaults should publish scoped reusable defaults.
- Adoption Navigation should compose project-specific briefs.
- Onramp / Bootstrap / Overlay should consume the result without laundering it into universal truth.

What the archive still lacked was the review discipline for answering a harder question:
> when multiple respectable Rust lanes exist for one recurring project class, what makes one of them the default *right now*, and how do we keep that answer reviewable instead of folkloric?

This file defines that discipline.
It is **not** another recommendation engine and **not** another universal score.
It is the rubric future revisions should use when evaluating or renewing default cards in `defaults/`.

Read with:
- `design/reviewable-lane-defaults.md`
- `design/reviewable-lane-defaults-corpus.md`
- `design/adoption-navigation-bundle.md`
- `design/recommendation-posture-ladder.md`
- `design/ecosystem-atlas-kit.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

## Why this matters now
Fresh official Rust signals keep pointing to the same failure mode:
- ecosystem navigation still depends too much on **choice paralysis** and **tacit knowledge**;
- users still need help getting to a good “starter set” of crates, but broad blessing is politically risky;
- canonical docs still matter, while editor/LLM-mediated workflows are rising;
- crates.io and docs.rs now expose stronger machine-usable signals than they used to; and
- Cargo itself keeps emphasizing plugins and companion tools rather than swallowing every ecosystem workflow.

References:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- https://rustfoundation.org/strategic-plan/

The practical consequence is simple:
**the ecosystem now needs reviewable default cards more than it needs another ungrounded “best crates” page.**

## What this framework evaluates
This framework evaluates **scoped reusable defaults** for recurring Rust project classes such as:
- conservative internal CLI / automation tool;
- conservative HTTP/service baseline;
- Rust component inside an existing polyglot workspace;
- script / repro / tiny utility lane;
- safety-tilted or regulated conservative lane.

It does **not** evaluate:
- universal Rust rankings;
- popularity contests;
- org-local overlays masquerading as public guidance;
- one-off project-specific briefs;
- starter repos without imported lane/default truth.

## Core evaluation questions
Every proposed default should answer these questions explicitly.

### 1) Is the scope real and narrow enough?
A default must name its:
- project class,
- runtime family,
- team-maturity assumptions,
- risk/support posture,
- environment posture,
- and escalation threshold.

If the scope is vague, the default will be over-read.

### 2) Is the default explainable from canonical references?
A default should point to maintainer-authored or official sources for its core lane.
A lane with weak or scattered canon may still be respectable, but it should usually lose the default unless the other candidates are clearly worse.

### 3) Is the lane coherent across the main slots?
A default lane should minimize hidden glue across parser/runtime/router/middleware/config/diagnostics/testing/boundary slots.
A lane can still have alternatives, but the default should not require many caveats just to stand up a normal first implementation.

### 4) Does it import maintenance and trust reality rather than vibes?
A default should be renewed using visible inputs such as:
- maintainer-authored docs,
- crates.io Security tab,
- Trusted Publishing posture,
- source links,
- `pubtime`,
- maintenance notes,
- and compatibility/support facts.

### 5) Does it minimize accidental lock-in for the target class?
The default may knowingly accept lock-in where it buys coherence, but it should say so.
Where runtime or host-language choice is still open, the default should often stay closer to neutral substrate or boundary-separation patterns.

### 6) Is the first-route experience good?
The default should make the first successful project, first debugging session, and first package-admission review easier rather than harder.

### 7) Is it overlay-friendly?
A public reusable default should tolerate local overlays and project-specific overrides without needing a hard fork.

### 8) Can it be renewed cheaply?
A default that cannot be re-checked without major manual archaeology is not strong enough to publish as a maintained reusable default.

## The eight-axis rubric
Use this rubric when comparing candidate lanes for one project class.
The point is not to compute fake precision.
The point is to force the archive to compare like with like.

### A. Canon quality
Questions:
- Is there a strong maintainer-authored learning surface?
- Are getting-started docs, API docs, examples, and operational notes easy to find?
- Would an assistant or internal guide have credible canonical references to import?

Good signs:
- official guide or book;
- well-structured docs.rs / book / project site;
- explicit examples and support surfaces.

### B. Slot coherence
Questions:
- Does the lane fit together naturally across the common slots for this project class?
- Does it compose with expected middleware, diagnostics, testing, and config approaches?

Good signs:
- one obvious happy path;
- low adapter count for routine use;
- explicit extension points rather than hidden glue.

### C. Build / debug reality
Questions:
- Does the lane keep the local inner loop comprehensible?
- Does it make logging, tracing, testing, and failure reporting straightforward?

Good signs:
- simple startup path;
- ordinary Cargo workflow;
- common tooling works without special ceremony.

### D. Trust / maintenance visibility
Questions:
- Can a reviewer inspect freshness, source, advisories, and publishing posture?
- Are support expectations legible?

Good signs:
- docs/source are easy to reach;
- registry signals are reviewable;
- maintenance burden is not hidden.

### E. Bootstrap friendliness
Questions:
- Is there a clean path into starter repos, onramps, and project bootstrap?
- Can a new team get to “first real success” without a maze of preconditions?

### F. Escape-hatch quality
Questions:
- Can a team safely diverge later?
- Are serious alternatives still first-class?
- Does the default preserve a sane migration story?

### G. Overlay compatibility
Questions:
- Can an organization narrow, harden, or augment the lane without rewriting the world?
- Are policy and environment additions bounded?

### H. Renewal cost
Questions:
- Can this default be rechecked from current canon and current ecosystem signals in bounded time?
- Does drift show up as a visible diff instead of lore?

## Decision vocabulary
Use these decision labels on default cards:
- **default** — preferred reusable starting lane for this exact scope.
- **default-with-caveats** — still best reusable starting lane, but hidden costs must stay visible.
- **serious alternative** — respectable lane that should remain visible and may win under known conditions.
- **watch** — promising lane, but not default-worthy yet for this scope.
- **defer** — intentionally not recommended as a reusable default for now.
- **project-specific only** — too sensitive to local constraints to publish as a reusable public default.

## Default-card structure
Every card in `defaults/` should include at least:
1. scope
2. why this default now
3. default lane summary
4. serious alternatives
5. slot guidance
6. escalation triggers
7. canonical references
8. imported evidence and renewal inputs
9. explicit non-goals

## Ranking the first defaults to publish
The archive should publish defaults in this order:

### 1. Conservative internal CLI / automation
Why first:
- common adoption lane;
- manageable complexity;
- direct payoff for crate-choice paralysis;
- clear canonical surfaces.

### 2. Conservative HTTP/service baseline
Why second:
- strategically important;
- exercises runtime and middleware consequences honestly;
- likely to become accidental folklore unless bounded.

### 3. Existing polyglot workspace component
Why third:
- extremely real in practice;
- forces workspace, boundary, and packaging assumptions into view;
- keeps local overlays honest.

### 4. Script / repro / tiny utility
Why fourth:
- important because `cargo script` is active,
- but too easy to over-generalize into a full-project answer.

### 5. Safety-tilted / regulated baseline
Why fifth:
- strategically vital,
- but dangerous to publish casually without stronger evidence imports.

## What this framework should eliminate
This framework should help the archive eliminate:
- defaults that exist only because one crate is fashionable;
- defaults that lack canonical references;
- defaults that hide runtime or host lock-in;
- defaults that cannot survive renewal;
- defaults that are really org-local overlays in disguise;
- defaults that are actually starter-template decisions, not lane decisions.

## Practical archive consequence
When future revisions research “what Rust is missing”, they should not only mint new epic seams.
They should also ask:
- which recurring project classes now deserve a concrete default card,
- which existing default cards should be renewed or demoted,
- and which buildable companion-tool ideas would help maintain that corpus.

That is the practical path from abstract navigation theory to a worthy ecosystem contribution.
