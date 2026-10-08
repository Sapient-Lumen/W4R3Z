# Design: Migration/Public API execution blueprint (2026 Q1)

## Goal
Turn the archive's clearest remaining **portfolio element** into a sharper **buildable program**.

The missing contribution is not another semver linter, another dependency-bump bot, another release checklist, or another fixer wrapper.
It is a thin composition layer that lets Rust teams carry **public-boundary truth and upgrade-program truth together** without flattening them into one opaque “versioning status” blob.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team or funder wants to build the archive's **Migration/Public API** portfolio answer in practice, what exact artifact families, commands, pilot lanes, and anti-goals should that contribution have?

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/public-api-contract-2026Q1.md`
- `design/migration-truth-contract-2026Q1.md`
- `design/public-api-pilot-program.md`
- `design/migration-truth-stack.md`

## Why this note is needed now
The archive already knew that **Migration/Public API** belonged in the strongest multi-project portfolio.
What it still lacked was a crisper answer to **what that release / upgrade contribution should actually look like**.

Fresh official signals sharpen that answer:
- Rust's 2026 flagship slate makes **control over public API dependencies** and **breaking change detection** explicit supply-chain priorities rather than niche library-maintainer concerns.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The accepted public/private-dependencies goal says the feature should help users catch unexpected exposure of implementation details and help tooling identify what constitutes an API.
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- The `cargo-semver-checks` integration goal says the tool is on the critical path toward `cargo publish`, that accidental SemVer violations remain common, and that cross-crate items plus precise type information are still major blockers.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- That same goal says `cargo-semver-checks` currently only sees the target package's rustdoc JSON, which causes many real false positives/negatives when public APIs expose foreign items, and the tool wants more stable public interfaces on its road toward Cargo.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- GSoC 2025 witness-generation work established a concrete compiler-backed path for type-related SemVer breakage checking.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- docs.rs now hosts rustdoc JSON directly, but its docs warn consumers to check `format_version` and note that historical coverage is still being filled in.
  https://docs.rs/about/rustdoc-json
- Cargo's SemVer chapter still presents compatibility as guidelines with **major**, **minor**, and **possibly-breaking** categories, not as one final mechanical bit.
  https://doc.rust-lang.org/cargo/reference/semver.html
- Edition migration still requires repeated passes across features and targets for many projects, and advanced migrations remain explicitly configuration-sensitive and often incremental.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Rust 1.85 / Rust 2024 says `cargo fix` output is conservative and “should not be considered a recommendation”.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Cargo's `rust-version` docs say mixed workspace policies complicate verification because dependencies are unified across semver-compatible versions.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- `cargo update --breaking` exists only as a nightly unstable option, which is a good sign that semver-aware upgrade orchestration is still fragmented rather than solved.
  https://doc.rust-lang.org/cargo/commands/cargo-update.html
- The Relink-don't-Rebuild goal sharpens the long-term payoff of cleaner public-boundary truth: only changes that affect a crate's public interface should force downstream rebuilds.
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- The 2025 State of Rust survey says docs remain the canonical reference even as editor/LLM-mediated learning rises, which increases the value of durable release/upgrade packs that survive past one terminal session.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, those signals say the archive should stop leaving **Migration/Public API** only as a portfolio phrase.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's release / upgrade contribution, the answer should now be:

> Build a **Migration/Public API bridge** (working label: **Version Bridge**) that imports public-boundary evidence, records upgrade intent and applied changes separately, verifies bounded slices explicitly, and emits reusable packs and handoffs for release review, upgrade guides, CI, distros, and assistants.

That answer is deliberately narrower than “solve Rust versioning”.
It is also deliberately stronger than “wire `cargo-semver-checks` to `cargo fix`”.

## What this contribution should be in theory

### Core thesis
A release / upgrade system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact subject and baseline were examined;**
2. **what public-boundary / exposure / proof changes were observed;**
3. **what destination policy or migration intent was being pursued;**
4. **which changes were only suggested, which were actually applied, and which stayed manual or deferred;**
5. **which verification lanes were run, with what bounds and residue;**
6. **what later consumers may honestly claim** from the result.

If a project cannot answer those questions without opening CI logs, shell history, release PRs, and rustdoc artifacts side by side, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable release-boundary and upgrade review**.

It should include:
- baseline and comparison subject identity;
- imported public API / semver / witness evidence;
- explicit upgrade intent and slice selection;
- suggested-vs-applied-vs-deferred change truth;
- bounded verification and outcome truth;
- consumer-specific handoffs.

It should not become:
- a replacement for `cargo publish`, `cargo fix`, or `cargo update`;
- a universal dependency governance platform;
- a hosted “Rust release health” dashboard empire;
- or a semver oracle that silently hides its assumptions.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **release-boundary subject truth** — what crate/workspace, baseline, target release, features, cfgs, targets, toolchain, and resolver posture were under review;
- **exposure / proof truth** — what public-surface diff, public/private dependency posture, witness evidence, and MSRV or type-sensitive proof was actually imported;
- **migration-intent truth** — what edition / `rust-version` / dependency / feature / support change was intended and why;
- **change-application truth** — what was only suggested, what was applied mechanically, what was edited manually, and what was deferred or waived;
- **bounded verification / outcome truth** — what semver, docs, tests, MSRV, downstream, or policy-sensitive lanes actually ran and where the evidence stayed partial;
- **consumer-handoff truth** — what release reviewers, upgrade-guide authors, distros, CI, support engineers, or assistants may honestly import next.

This is the biggest theory/practice guardrail in the whole design.
Without it, every release / upgrade report becomes a confidence soup.

### Composition rule
A worthy v0 should **compose imported artifacts** instead of replacing them.

It should import, not erase:
- `api-pack/v0`
- `semver-report/v0`
- optional `api-witness-report/v0`
- optional `msrv-report/v0`
- `migration-plan/v0`
- `migration-run-report/v0`
- `migration-outcome-report/v0`
- optional `semctx-pack/v0`
- optional compatibility/docs/downstream evidence packs

And then it should emit one thinner **bridge family** above those imports.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo version-bridge capture-api`
- `cargo version-bridge plan`
- `cargo version-bridge apply-report`
- `cargo version-bridge verify`
- `cargo version-bridge brief`
- `cargo version-bridge handoff --to <publish|upgrade-guide|ci|distro|support|assistant>`
- `cargo version-bridge pack`

The tool should **import** Cargo-native and companion-tool surfaces when available rather than replacing them.

### Public artifact spine

#### Imported families
- `api-pack/v0`
- `semver-report/v0`
- `api-witness-report/v0`
- `msrv-report/v0`
- `migration-plan/v0`
- `migration-run-report/v0`
- `migration-outcome-report/v0`

#### Public bridge families
- `version-bridge-subject/v0`
- `version-bridge-change-report/v0`
- `version-bridge-application-report/v0`
- `version-bridge-verification-report/v0`
- `version-bridge-brief/v0`
- `version-bridge-handoff/v0`
- `version-bridge-pack/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — crate/workspace members, baseline tag/version, target tag/version, selected packages, features, cfgs, targets, toolchain, resolver, lockfile posture;
- **authority posture** — observed locally, imported from trusted companion pack, imported from public release cache, or inferred;
- **why-change markers** — edition change, `rust-version` ratchet, dependency major update, public/private dependency correction, feature re-scope, MSRV/support policy, docs/support refresh;
- **imported evidence refs** — API diff IDs, semver reports, witness reports, migration runs, docs/test/downstream reports;
- **application classes** — suggested, applied-mechanical, applied-manual, deferred, rejected, waived;
- **coverage / completeness** — exact, partial, mixed, stale, policy-limited, unsupported;
- **consumer limits** — what publish/release/distro/support/assistant consumers may and may not claim;
- **raw attachments** — rustdoc JSON URLs/digests, diffs, fix logs, CI links, notes, or downstream reports when present;
- **reason-coded ambiguity** — explicit why for every partial or unsupported answer.

### Commands and what they should emit

#### `cargo version-bridge capture-api`
Purpose:
- capture the release-boundary subject;
- import public API / exposure / semver / witness evidence when available;
- emit `version-bridge-subject/v0` plus `version-bridge-change-report/v0`.

Important rule:
- if only weaker API evidence is available, emit a **weaker bridge report** instead of pretending final SemVer certainty.

#### `cargo version-bridge plan`
Purpose:
- record destination intent and why the change is happening;
- preserve package / feature / target / edition / `rust-version` slices explicitly;
- emit an application-neutral bridge plan.

Important rule:
- do **not** infer intent only from observed code changes.

#### `cargo version-bridge apply-report`
Purpose:
- record what `cargo fix`, manifest edits, dependency updates, or manual patches were suggested and what was actually applied;
- preserve manual follow-up and deferred residue;
- emit `version-bridge-application-report/v0`.

#### `cargo version-bridge verify`
Purpose:
- run or import bounded checks: semver/API, witness/type-proof, MSRV, docs/examples, selected tests, downstream or policy-sensitive checks;
- emit `version-bridge-verification-report/v0`.

Important rule:
- verification must stay **slice-aware**.
One green run may not cover every feature, target, or workspace policy.

#### `cargo version-bridge brief`
Purpose:
- tell a human what changed at the public boundary, why the upgrade happened, what was applied, what remains manual, and what claims are justified;
- render the same pack at different depths without inventing new facts.

#### `cargo version-bridge handoff`
Purpose:
- emit smaller downstream exports for release review, upgrade guides, distros, CI, support, or assistants without making those slices canonical by themselves.

#### `cargo version-bridge pack`
Purpose:
- assemble the bridge subject, changes, applications, verification results, and imported evidence refs into one reviewable `version-bridge-pack/v0`.

## Ranked feature set

### P0 — required for a worthy v0
- exact baseline/target subject capture;
- imported public API / semver evidence with explicit public/private-dependency posture when available;
- explicit migration intent with slice selection;
- suggested-vs-applied-vs-manual-vs-deferred change tracking;
- bounded verification that can combine semver/API lanes with migration-sensitive lanes;
- one portable brief plus one portable pack;
- honest `partial`, `policy-limited`, `stale`, `unsupported`, and `waived` states.

### P1 — strong near-term extensions
- workspace mixed-`rust-version` and mixed-edition support;
- upgrade-guide and distro handoffs;
- explicit docs/support consequence imports;
- nightly `cargo update --breaking` experiment capture where teams choose to use it;
- downstream-impact or relink-sensitive hints that say when public-boundary change likely matters to dependents.

### P2 — do later or fold elsewhere
- automatic code-rewrite empires;
- universal dependency approval workflows;
- hosted badge/status portals;
- one-bit migration or semver “health scores”;
- pretending that every release can or should be reduced to a deterministic auto-fix story.

## Pilot lanes that best prove the idea

### 1) Ordinary library minor-release lane
Prove:
- baseline vs target public-boundary truth;
- imported semver/API evidence;
- explicit “possibly-breaking” residue where the SemVer guide leaves judgment to maintainers;
- one reviewable release brief.

This lane matters because the Cargo SemVer chapter is intentionally guidance-heavy rather than purely binary.

### 2) Edition migration with public-API guardrails
Prove:
- repeated `cargo fix --edition` / feature / target passes are recorded as slices;
- conservative tool output stays separate from actual recommendations;
- public API consequences remain visible before release claims are made.

This lane matters because edition migration is still configuration-sensitive and staged.

### 3) Workspace `rust-version` ratchet lane
Prove:
- mixed workspace policies are visible;
- shared dependency unification complications are preserved;
- final claims are bounded to the packages and policies actually exercised.

This lane matters because workspace support floors are a live release / upgrade pain rather than trivia.

### 4) Dependency major-upgrade lane
Prove:
- one dependency moves across a semver boundary;
- public/private dependency exposure is reviewed rather than assumed;
- the bridge can record manual edits, deferred fallout, and unstable helper lanes honestly.

This lane matters because upgrade intent is often real before a project has perfect first-party tooling.

### 5) Downstream / distro handoff lane
Prove:
- release reviewers, downstream packagers, and support engineers can consume one bounded pack;
- consumers can import the same truth without scraping bespoke CI and changelog prose;
- assistants remain downstream summarizers rather than canonical evidence owners.

## Failure modes to avoid

### 1) The semver-oracle trap
If the bridge starts pretending every API change has one final automatic answer, it will either lie or hide maintainer judgment.

### 2) The fixer-bot trap
If the bridge becomes mostly an edit engine, it will erase why the change happened and what release boundary was at stake.

### 3) The one-config illusion
If one feature set, one target, or one workspace member silently stands in for the whole subject, the pack will over-claim.

### 4) The collapse trap
If public API evidence, migration intent, and applied edits are flattened into one report, archaeology and review both get worse.

### 5) The consumer-overclaim trap
If release notes, distros, CI, or assistants can say more than the pack actually proved, the contribution becomes presentation theater instead of infrastructure.

## Why this is the right deepening now
The archive already had the two adjacent contracts.
What it still lacked was the build-program note that says:

- do **not** treat Public API and Migration Truth as disconnected empires;
- do **not** collapse them into one new mega-contract either;
- build the **composition / bridge layer** that lets serious teams carry release-boundary truth into upgrade-program truth and back out into bounded downstream consumers.

That is the cleanest way to deepen the current portfolio without forcing another promotion.

## Ranking impact
This does **not** promote a new frontier and it does **not** change the archive's top band.

It does make one portfolio fact more concrete:
- **Build-State Evidence** remains the strongest one-project answer.
- **Native Edge Contract** remains the active specialist frontier.
- **Package Intake Gateway** remains the most underappreciated operational seam.
- **Semantic Context Contract** remains the key hidden multiplier.
- **Migration/Public API** now has an explicit execution blueprint for the release / upgrade quadrant of the portfolio.

That means the archive's clearest multi-project answer is still:

> **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**

But the remaining unblueprinted quadrant is no longer just a phrase.
It now has a practical reference shape.

## What not to build
Do **not** build:
- another standalone semver-only checker with no upgrade story;
- another upgrade bot that hides public-boundary consequences;
- a release checklist that swallows suggested-vs-applied change truth;
- or an assistant-friendly summary layer that cannot point to bounded imported evidence.

The winning contribution is thinner and more durable:
**publish explicit release-boundary truth, explicit upgrade-intent truth, explicit suggested-vs-applied change truth, explicit bounded verification truth, and hand that off honestly to multiple consumers without flattening unlike changes into one story.**
