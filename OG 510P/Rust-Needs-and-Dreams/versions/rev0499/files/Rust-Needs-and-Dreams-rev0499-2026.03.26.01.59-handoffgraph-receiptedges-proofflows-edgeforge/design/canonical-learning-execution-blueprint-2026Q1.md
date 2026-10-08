# Design: Canonical Learning execution blueprint 2026Q1

## Why this note exists now
The archive already had the right ingredients for **Canonical Learning**:
- `design/canonical-learning-stack.md`
- `design/canonical-learning-lane-map.md`
- `design/canonical-learning-pilot-program.md`
- `design/canonical-learning-consumer-pilot-program.md`
- `design/docproof-kit.md`
- `design/compile-guidance-kit.md`
- `proposals/epic-canonical-learning-stack.md`

What it still lacked was the same thing Build-State Evidence, Feedback Loop, Async Capability Commons, Safety-Critical Readiness Commons, Cargo Artifact Contract, Distribution Contract, Workspace Environment, Publisher & Source Identity, Reviewable Edit, Toolchain Productization, and Support Envelope now have:

> one direct answer to **what the worthy contribution should actually ship in theory and practice**.

That absence matters because the current ecosystem pressure is no longer only “docs are important” or “assistants are getting popular”.
It is that serious Rust teams increasingly need to answer **what exactly is canonical learning truth, what is merely rendered or derived, what evidence says the teaching surface still works, what consumer may import it, and what an editor/assistant/docs host must never silently rewrite or over-claim**.

The archive should therefore stop treating Canonical Learning as only a stack, lane map, and pilot ladder.
It should describe a real contribution shape.

## Fresh signals that force the seam into focus
Primary sources now line up around the same missing middle:
- The 2025 State of Rust survey says online documentation remains the preferred canonical reference, while open answers and tooling usage suggest some learning traffic is shifting toward LLM tooling and editors with agentic support.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s December 2025 vision writeup says crates still lack good tools for building **supportive** abstractions and explicitly argues for better diagnostics and guidance from crates.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- docs.rs already exposes build-shaping metadata such as `features`, `all-features`, `no-default-features`, `default-target`, `targets`, and `rustdoc-args`, which means public documentation posture is already partly machine-declared.
  https://docs.rs/about/metadata
- docs.rs also documents host-specific build behavior and caveats: `#[cfg(docsrs)]` can diverge from local builds, and maintainers are encouraged to test docs.rs-oriented builds in CI.
  https://docs.rs/about/builds
- docs.rs now hosts rustdoc JSON, which gives downstream tools a structured documentation import surface instead of forcing HTML scraping.
  https://docs.rs/about/rustdoc-json
- rustdoc already treats documentation examples as executable tests, and the 2024 Edition changed doctest execution to combine many tests into a single binary to reduce overhead. That is evidence that executable teaching is a first-class Rust surface, not documentation decoration.
  https://doc.rust-lang.org/rustdoc/documentation-tests.html
  https://doc.rust-lang.org/edition-guide/rust-2024/rustdoc-doctests.html
- mdBook has a first-class `test` command for Rust snippets in books, so long-form guide/tutorial teaching already has a native validation lane.
  https://rust-lang.github.io/mdBook/cli/test.html
- rustc already emits structured JSON diagnostics, Cargo can surface JSON diagnostics and build artifacts to external tools, `cargo fix` already consumes compiler suggestions, and the Rust Reference documents stable diagnostic attributes like `must_use`, `deprecated`, and `diagnostic::on_unimplemented` as part of the public language surface.
  https://doc.rust-lang.org/beta/rustc/json.html
  https://doc.rust-lang.org/cargo/reference/external-tools.html
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
  https://doc.rust-lang.org/reference/attributes/diagnostics.html

Taken together, those signals say the missing contribution is not another docs portal and not a universal AI context blob.
It is a **reviewable canonical-learning layer**.

## Headline answer
If one serious team wants to build the archive's clearest remaining teaching-truth contribution, the answer should now be:

> Build a **Canonical Learning reference layer** that captures maintainer-authored learning lanes, docs-host posture, executable-learning evidence, compile-guidance evidence, consumer-import boundaries, and bounded downstream handoffs; emit reusable reports and packs; and prove the shape across API docs, guide books, negative-teaching diagnostics, docs hosts, editors, assistants, and review consumers.

That answer is deliberately narrower than “solve documentation UX for Rust”.
It is also deliberately stronger than “improve docs.rs search” or “teach LLMs Rust better”.

## What this contribution should be in theory

### Core thesis
A canonical-learning system becomes real ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact learning subject is under discussion** — crate, workspace, package family, release, feature/target/toolchain slice, or docs host variant;
2. **what learning lanes are maintainer-authored canon** — API-doc/reference, guide/tutorial, executable-example proof, compile-guidance/negative-teaching, docs-host posture, structured machine-import attachments;
3. **what evidence exists for each lane** — declared only, rendered, doctested, book-tested, compile-fail checked, imported from compiler diagnostics, or manually reviewed;
4. **what a consumer actually imported** — docs host, CI, editor, assistant, atlas, support-review, or release-review consumers should say what they imported, normalized, omitted, or cached;
5. **what remained derived rather than canonical** — overlays, summaries, grouping, search indexes, quick-fix panels, or assistant explanations;
6. **what downstream consumers may honestly conclude** — support/release/policy/mutation consumers should be able to import selected facts without silently promoting derived overlays into source-of-truth status.

If a project cannot answer those questions without mixing README prose, docs.rs settings, book-testing scripts, stderr fixtures, and assistant memory by hand, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable canonical-learning truth and handoff**.

It should include:
- learning subject and lane identity;
- docs-host and build posture;
- executable-example and compile-guidance evidence;
- consumer import reports and authority boundaries;
- bounded diffs and handoffs.

It should not become:
- the new universal docs host;
- an assistant-memory warehouse;
- a documentation-quality leaderboard;
- a replacement for rustdoc, docs.rs, mdBook, `trybuild`, Cargo, or editors;
- or a mutation system that rewrites docs/code because a consumer inferred better wording.

### Separation rule
A worthy contribution here must preserve at least six distinct truth classes:
- **subject truth** — which crate/workspace/release/lane slice the learning record describes;
- **canonical-lane truth** — which reference, guide, example, compile-guidance, and docs-host surfaces are maintainer-authored canon;
- **evidence truth** — what was actually checked or imported for each lane;
- **consumer-import truth** — what a specific downstream tool imported, skipped, or normalized;
- **derived-overlay truth** — what was summarized, re-grouped, highlighted, or suggested downstream;
- **consumer-handoff truth** — what a support/release/editor/assistant/archive consumer is allowed to claim.

Without that separation, a docs.rs page, one editor panel, or one assistant answer silently becomes “the docs”, and the whole layer stops being honest.

### Shape rule
The primary contribution shape should now be:
- **reference layer + report/pack command + consumer/import corpus**.

Why this shape fits:
- **reference layer** because the seam is really about lane identity, authority boundaries, and non-collapse rules;
- **report/pack command** because the missing piece is a portable output that maintainers can publish, diff, and attach to releases/CI/docs hosts;
- **consumer/import corpus** because real value comes from proving that different consumers can reuse canonical learning truth without silently becoming the canon.

Wrong shapes to refuse first:
- one giant learning schema that absorbs support, policy, and mutation;
- a universal docs search portal pretending to own canon;
- an assistant-only export format;
- or a docs-score service that cannot explain which lane it actually validated.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo learncanon inspect`
- `cargo learncanon lanes`
- `cargo learncanon check`
- `cargo learncanon import --from <rustdoc|mdbook|rustc|cargo|docsrs>`
- `cargo learncanon diff`
- `cargo learncanon handoff --to <docs-host|ci|editor|assistant|atlas|support|release>`
- `cargo learncanon pack`
- `cargo learncanon doctor`

The tool should **import** rustdoc, docs.rs, mdBook, Cargo, and compiler facts where possible rather than replacing them.

### Public artifact spine
A credible public artifact family would keep the current stack ideas but make the review spine explicit:
- `learning-lane-catalog/v0`
- `canonical-learning-brief/v0`
- `canonical-learning-sources/v0`
- `canonical-learning-check-report/v0`
- `canonical-learning-import-report/v0`
- `canonical-learning-overlay-report/v0`
- `canonical-learning-authority-boundary/v0`
- `canonical-learning-handoff/v0`
- `canonical-learning-pack/v0`
- `canonical-learning-diff/v0`

The pack should import, not replace:
- `doc-pack/v0`
- `guidance-pack/v0`
- docs.rs metadata and docs-host posture
- rustdoc JSON pointers
- doctest/book-test/compile-fail evidence lanes

### First proving lanes
A credible rollout should rank proving lanes instead of pretending every learning consumer lands at once.

#### Lane 1 — API-doc/reference + docs-host lane
Start where current Rust says canon already lives.
This lane proves that maintainers can declare canonical reference/doc-host posture and attach validation evidence without pretending that rendered docs or host defaults are the whole story.

What to prove:
- import docs.rs metadata and host caveats honestly;
- bind canonical reference surfaces to a clear subject and lane catalog;
- attach doctest/render/build evidence without turning “rendered once” into “fully taught”.

#### Lane 2 — guide/tutorial / book lane
Long-form learning matters, but it has different structure and different failure modes than API docs.
This lane proves that guide books and tutorials can stay canonical without being flattened into reference docs.

What to prove:
- import mdBook-backed guide lanes and test results;
- preserve book/guide scope separately from API reference scope;
- surface omissions, untested prose, and feature/target caveats explicitly.

#### Lane 3 — compile-guidance / negative-teaching lane
This is where Rust’s “supportive abstractions” ambition becomes operational rather than rhetorical.
This lane proves that compiler-facing guidance and compile-fail teaching belong inside canonical learning instead of living only in stderr and fixture lore.

What to prove:
- import structured diagnostic roots and compile-guidance attachments honestly;
- preserve negative-teaching examples and lint/help posture distinctly from positive examples;
- keep weaker or unstable consumer imports clearly marked.

#### Lane 4 — consumer-import / overlay lane
Only after canonical authoring lanes are solid should the ecosystem prove downstream overlays.
This is where docs hosts, CI, editors, and assistants stop scraping and start declaring imports.

What to prove:
- publish import reports, omissions, normalization rules, and freshness markers;
- keep overlays visibly derived and linked back to canonical lane IDs;
- forbid silent policy/support/mutation claims that exceed the imported learning facts.

#### Lane 5 — support/release/atlas/archive handoff lane
Only after the earlier lanes work should canonical learning become a broader handoff substrate.
This lane proves the archive’s cross-stack story stays modular.

What to prove:
- support/release/adoption/archive consumers can import learning facts without pretending learning artifacts alone prove support or release quality;
- archive-side summaries, editor hints, and assistant slices remain explicitly downstream;
- canonical learning can travel with release/review materials without losing source-of-truth boundaries.

## What to refuse
A worthy contribution here must refuse the most tempting wrong shapes:
- a universal “smart docs” platform;
- assistant-owned canonical summaries;
- a docs score that erases lane differences;
- a release/support gate that infers too much from docs checks alone;
- or a schema that makes docs hosts, editors, assistants, and release tooling look like equal authorities.

## Ranking and repo consequence
This revision does **not** rewrite the broad ladder.
It does **not** outrank **Build-State Evidence** overall.
It does **not** displace **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked day-to-day missing middle.

What it does do is make one repeatedly promoted seam explicit:
- **Canonical Learning** is now the clearest remaining **teaching-truth / consumer-import / authority-boundary execution blueprint** in the archive;
- its primary shape is **reference layer + report/pack command + consumer/import corpus**;
- **DocProof Kit** and **Compile Guidance Kit** remain the two key maintainer-authored leaf layers beneath it, but neither alone is the whole answer;
- and future docs-host, editor, assistant, atlas, support, release, and archive-summary workflows should be understood as downstream consumers of this layer, not its replacement.

That gives the archive a better answer to a question that is only getting more central:
How should Rust let humans, CI, docs hosts, editors, assistants, and this archive itself reuse learning truth **without** smearing canon, evidence, and derived overlays into one opaque knowledge blob?
