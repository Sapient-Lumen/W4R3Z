# Design: Public API execution blueprint 2026Q1

## Why this note exists now
The archive already had the right ingredients for **Public API**:
- `design/public-api-contract-2026Q1.md`
- `design/public-api-kit.md`
- `design/public-api-pilot-program.md`
- `gaps/public-api-boundaries-exposure-diffs-semver-and-msrv-handoffs.md`
- `proposals/epic-public-api-kit.md`
- `design/migration-public-api-execution-blueprint-2026Q1.md`

What it still lacked was the same thing Build-State Evidence, Feedback Loop, Async Capability Commons, Safety-Critical Readiness Commons, Cargo Artifact Contract, Distribution Contract, Workspace Environment, Publisher & Source Identity, Reviewable Edit, Toolchain Productization, Support Envelope, and Canonical Learning now have:

> one direct answer to **what the worthy contribution should actually ship in theory and practice**.

That absence matters because the current ecosystem pressure is no longer only “semver is hard” or “API diff tools exist”.
It is that serious Rust teams increasingly need to answer **what exact public boundary changed, what foreign items or public dependencies were exposed, what evidence is structural versus witness-backed, what feature/target/MSRV/toolchain bounds applied, and what later publish/migration/docs/policy/downstream consumers may honestly conclude**.

The archive should therefore stop treating Public API as only a contract, kit, and pilot ladder.
It should describe a real contribution shape.

## Fresh signals that force the seam into focus
Primary sources now line up around the same missing middle:
- Rust’s 2026 flagship slate still puts **public/private dependencies** and **SBOM support** in the top supply-chain band, alongside breaking-change detection. That means public-boundary truth is not just library hygiene anymore; it is an officially named ecosystem capability area.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The accepted public/private-dependencies goal says the feature should help users catch ways they unexpectedly expose implementation details and help tooling identify what constitutes an API. That is almost a direct statement that exposure truth needs a better review surface.
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- The current `cargo-semver-checks` goal says accidental SemVer violations are relatively common, Cargo wants eventual publish-time integration, and the hardest blockers still include **cross-crate items** and **type-sensitive checking**. It also says the current plan for stronger type checks is witness-program generation checked by `cargo check`.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- The 2025 GSoC results say witness generation is key to the `cargo-semver-checks` roadmap for 2026 and beyond. That makes witness-backed evidence real enough to plan around, but not finished enough to treat as the whole story.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s unstable-feature docs still say `public-dependency` is nightly-only and exists to pass extra information to rustc so `exported_private_dependencies` can function properly. That means declared exposure truth is still not a boring stable substrate yet.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo’s SemVer chapter still reads as guidance with major / minor / possibly-breaking classes rather than one final mechanically authoritative verdict. That makes evidence packaging and waiver posture more important than a single yes/no result.
  https://doc.rust-lang.org/cargo/reference/semver.html
- docs.rs now hosts rustdoc JSON, but it warns consumers to check `format_version` and notes that coverage only exists for releases rebuilt after rustdoc-JSON support began. That makes structured API import possible, but still bounded and versioned.
  https://docs.rs/about/rustdoc-json
- `cargo-public-api` continues to prove the lane is real, but its current docs still say it relies on building rustdoc JSON and needs a recent nightly installed. That is exactly the kind of useful-but-not-yet-boring substrate that a higher review layer should wrap without erasing provenance.
  https://docs.rs/crate/cargo-public-api/latest

Taken together, those signals say the missing contribution is not another diff viewer and not a one-number semver score.
It is a **reviewable public-API layer**.

## Headline answer
If one serious team wants to build the archive’s clearest remaining release-boundary contribution, the answer should now be:

> Build a **Public API reference layer** that captures public-boundary subject identity, declared and inferred exposure, structural diffs, witness-backed escalations, bounded verification posture, and downstream handoffs; emit reusable reports and packs; and prove the shape across library release review, workspace families, migration planning, publish-time checks, and downstream intake.

That answer is deliberately narrower than “solve semver for Rust”.
It is also deliberately stronger than “improve cargo-semver-checks” or “make `cargo public-api` prettier”.

## What this contribution should be in theory

### Core thesis
A public-API system becomes real ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact public boundary is under discussion** — crate, package, workspace member, baseline/new version pair, feature/target/toolchain slice;
2. **what exposure route matters** — declared public dependencies, inferred exposure through signatures/reexports/trait bounds/associated items, and unresolved foreign-item provenance;
3. **what changed structurally** — additions, removals, signature/trait/visibility shifts, newly exposed or no-longer-exposed items, and change classes;
4. **what stronger evidence exists** — heuristic suspicion versus witness-backed, compiler-checked evidence for type-sensitive or cross-crate cases;
5. **what bounded the claim** — rustdoc JSON format/version, MSRV, selected features, cfgs, targets, toolchains, waivers, and unsupported residue;
6. **what downstream consumers may honestly conclude** — publish, migration, distro, docs, policy, assistant, and archive consumers should be able to import selected facts without silently promoting them into broader claims.

If a project cannot answer those questions without combining CI logs, changelog prose, rustdoc JSON dumps, semver-check output, and maintainer memory by hand, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable public-boundary truth and handoff**.

It should include:
- public-boundary subject identity;
- declared and inferred exposure truth;
- structural-diff truth;
- witness / stronger-proof imports;
- bounded verification posture;
- consumer exports and redactions.

It should not become:
- the new universal release platform;
- a Cargo-only monopoly that erases tool provenance;
- a hosted semver-score service;
- a docs.rs mirror mistaken for API truth;
- or a migration engine that silently turns evidence into edits.

### Separation rule
A worthy contribution here must preserve at least six distinct truth classes:
- **subject truth** — which boundary and comparison the record describes;
- **exposure truth** — what dependencies and foreign items are part of the public story, declared or inferred;
- **structural-diff truth** — what changed in the visible boundary;
- **witness/proof truth** — what got stronger evidence and how;
- **bounded-verification truth** — which matrix, MSRV, cfg, target, format, or waiver limits apply;
- **consumer-handoff truth** — what later consumers may import and what they must not over-claim.

Without that separation, one rustdoc JSON export, one semver lint run, or one “safe to upgrade” summary silently becomes the whole story.

### Shape rule
The primary contribution shape should now be:
- **reference layer + report/pack command + witness/import corpus**.

Why this shape fits:
- **reference layer** because the seam is really about boundary identity, evidence vocabulary, and non-collapse rules;
- **report/pack command** because the missing piece is a portable output that teams can diff, publish, attach to releases, and import elsewhere;
- **witness/import corpus** because the hard cases are exactly the ones where structural, declared, inferred, and compiler-backed lanes diverge and need reviewable comparison.

Wrong shapes to refuse first:
- one more HTML diff report without portable handoff;
- one single semver verdict badge;
- a publish-time gate that hides what evidence was or was not imported;
- or an assistant-facing summary format that cannot point back to source evidence.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo apitruth inspect`
- `cargo apitruth exposure`
- `cargo apitruth diff`
- `cargo apitruth witness`
- `cargo apitruth verify`
- `cargo apitruth handoff --to <publish|migration|docs|policy|assistant|archive>`
- `cargo apitruth pack`
- `cargo apitruth doctor`

The tool should **import** rustdoc, docs.rs, Cargo, and semver-check / witness facts where possible rather than replacing them.

### Public artifact spine
A credible public artifact family would keep the current contract ideas but make the review spine explicit:
- `api-boundary-subject/v0`
- `api-exposure-report/v0`
- `api-diff-report/v0`
- `api-witness-report/v0`
- `api-verification-report/v0`
- `api-waiver/v0`
- `api-handoff/v0`
- `api-pack/v0`
- `api-diff-bundle/v0`

The pack should import, not replace:
- rustdoc JSON pointers and format-version posture;
- `cargo-semver-checks` findings and reason codes;
- declared public/private dependency posture where available;
- cargo-public-api-style structural views;
- MSRV / feature / cfg / target / toolchain attachments.

### First proving lanes
A credible rollout should rank proving lanes instead of pretending every public-boundary question lands at once.

#### Lane 1 — single-crate release review lane
Start where the pain is clearest: a published library comparing one release to the next.

What to prove:
- separate structural diff from final semver summary;
- attach matrix bounds and unsupported residue;
- record whether witness-backed checks ran or only structural checks did;
- keep “inconclusive but reviewable” as a first-class outcome.

#### Lane 2 — cross-crate / foreign-item exposure lane
This lane proves the archive can stay honest where current tooling is weakest.

What to prove:
- preserve declared public-dependency posture when available;
- preserve inferred exposure when foreign items appear through signatures or reexports;
- record unresolved provenance rather than hiding it;
- keep exposure truth separate from downstream compatibility claims.

#### Lane 3 — workspace-family API lane
This lane proves that family releases are not just several single crates stapled together.

What to prove:
- per-member subject truth stays visible;
- shared utility crates and reexports do not vanish into one family summary;
- feature/cfg/target differences remain attached to the affected members;
- diff bundles stay reviewable across multiple release candidates.

#### Lane 4 — migration / publish / downstream intake import lane
Only after the earlier lanes work should the pack become a shared import layer.

What to prove:
- migration planning can import API evidence without claiming it authored the verdict;
- publish-time review can import API evidence without hiding waivers and unsupported cases;
- downstream intake or distro review can consume API drift without rerunning bespoke local logic;
- docs or archive summaries can render bounded explanations without replacing the pack.

#### Lane 5 — bounded assistive / archive-consumer lane
This lane proves the archive’s LLM/editor hygiene matters here too.

What to prove:
- assistant/editor/archive consumers can summarize boundary drift while preserving subject, evidence source, and bounded confidence;
- derived summaries remain visibly derived;
- no generated summary can silently upgrade structural hints into witness-backed proof or policy approval.

## What to refuse
A worthy contribution here must refuse the most tempting wrong shapes:
- another API diff snapshot format with no handoff layer;
- a universal “semver-safe” badge;
- treating docs.rs rustdoc JSON availability as equivalent to complete, stable public-boundary truth;
- treating declared public dependencies as the whole exposure story;
- treating witness generation as if it already removes all structural ambiguity;
- or making the pack depend on one CI provider, one registry, one docs host, or one consumer.

## Ranking and repo consequence
This revision does **not** rewrite the broad ladder.
It does **not** outrank **Build-State Evidence** overall.
It does **not** displace **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked day-to-day missing middle.

What it does do is make one repeatedly promoted seam explicit:
- **Migration/Public API** remains the broader release / upgrade composition answer in the archive;
- **Public API** is now the clearest **release-boundary / exposure / semver-evidence execution blueprint** beneath that broader band;
- its primary shape is now **reference layer + report/pack command + witness/import corpus**;
- **Publisher & Source Identity**, **Support Envelope**, **Canonical Learning**, and **Migration Truth** remain adjacent import/consumer layers rather than the same thing;
- and future release, publish, migration, distro-intake, docs, policy, and archive-summary work should import this layer rather than rediscovering public-boundary truth privately.

That gives the archive a better answer to a pressure cluster that keeps surfacing in official Rust reality:
How should Rust let teams describe **what boundary changed, how exposed it was, how strong the evidence is, and what consumers may honestly conclude** without flattening all of that into one semver label?

