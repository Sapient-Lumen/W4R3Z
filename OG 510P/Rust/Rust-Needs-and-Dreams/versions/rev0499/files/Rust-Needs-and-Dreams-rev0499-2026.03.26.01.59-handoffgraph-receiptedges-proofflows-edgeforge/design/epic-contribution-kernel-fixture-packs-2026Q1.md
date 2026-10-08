# Epic contribution kernel fixture packs (2026 Q1)

## Why this layer is now missing
The repo already knows:
- which Rust ecosystem contributions are strongest,
- what verdict they deserve now,
- what a bounded v0 should contain,
- what lands first inside that v0,
- what contract0 surface the first implementation should honor,
- and what example outputs should exist when that surface is exercised.

What it still did **not** know concretely enough was:
> what **input scenarios, command recipes, and expected checks** should drive those outputs so future revisions stop treating witness files as free-floating illustrations?

That missing layer is a **kernel fixture pack** layer.
A fixture pack is not a live telemetry corpus, not a benchmark contest, and not a universal integration test standard.
It is a bounded replayable input bundle that binds together:
- one proving-ground scenario,
- one command recipe,
- one small set of input assumptions,
- one expected artifact family,
- and one explicit negative-state or caveat posture.

It exists to keep the top kernels replayable instead of merely well-described.

## Why this is justified by current Rust signals
Fresh official Rust signals still point toward **replayable, machine-facing seams** with explicit compatibility posture rather than giant platform launches:
- Cargo's external-tools guidance still centers `cargo metadata`, `--message-format=json`, and custom subcommands, and it explicitly says callers should pass `--format-version` to future-proof `cargo metadata`. That rewards fixture packs with concrete command recipes and versioned expectations.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo/rustc JSON output remains line-oriented and partial by nature. The docs explicitly warn that `--message-format=json` only controls Cargo/rustc output, not arbitrary tool stdout. That means replay fixtures need mixed-stream and partial-capture expectations, not just happy-path JSON optimism.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
  https://doc.rust-lang.org/beta/rustc/json.html
- The March 2026 build-dir-layout-v2 testing call still says many downstream tools rely on unspecified internals and asks people to test real workflows with `-Zbuild-dir-new-layout`. That argues for fixture packs that preserve **stable-only** and **nightly-caveated** lanes separately.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build analysis is still prototype work around recorded metadata and unstable `cargo report *` subcommands. That makes fixture packs more valuable than more abstract design prose because they can show what a stable-only proving run should expect before optional unstable imports are present.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The libtest JSON goal exists because people had come to rely on programmatic output and the toolchain still needs a principled machine-readable testing surface. That is a strong ecosystem signal that **fixture-driven machine-facing contracts** are worth first-class archive space.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- The 2026 debugging survey still frames Rust debugging as a cross-debugger, cross-OS, async, visualizer, and expression-evaluation problem. That is not just a witness problem; it is a fixture problem, because tuple cards and replay results need representative input cases.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- crates.io's January 2026 update and the March 2026 Cargo advisory still make supply-chain posture route-specific. That means intake review needs replayable route fixtures, not one universal trust story.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The January 2026 safety-critical writeup still points toward evidence cards, dependency-lifecycle playbooks, async-runtime requirements, and shared ownership. Those all become more honest when bound to small scenario fixtures instead of badge language.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Maintenance work in Rust explicitly includes CI failures, security incidents, documentation upkeep, and dependency updates. That reinforces that fixture packs are not optional gloss; they are part of the upkeep burden of any serious new commons.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

## What a kernel fixture pack should contain
Each fixture pack should bind together five things:
1. **one scenario identity** from the proving-grounds matrix,
2. **one command recipe** on the endorsed contract surface,
3. **one bounded input assumption set**,
4. **one expected artifact family** tied to a witness bundle,
5. **one explicit negative-state or caveat expectation**.

The fixture file itself should say:
- what scenario is being exercised,
- what tools and versions are assumed,
- what command or small command sequence is in scope,
- which artifact families must appear,
- which unsupported or caveated state must remain visible,
- what checks count as pass/fail,
- and what larger claim is still refused.

## Why fixture packs matter after witness packs
A witness pack can still fail in practice when:
- the example output is plausible but no scenario says when to emit it,
- the command names look clear but the required setup is implicit,
- stable and experimental lanes both exist but no fixture says which checks belong to which lane,
- route-specific or tuple-specific negative states exist in prose but not in replay inputs,
- or future editors quietly widen the meaning of an example artifact without binding it to a proving-ground case.

A fixture pack is the thinnest layer that prevents that drift.

## What belongs in the first fixture corpus
Only kernels that already have:
- a live packet,
- a kernel brief,
- a slice-0 note,
- a contract0 note,
- and a witness bundle.

That means the first fixture corpus should cover:
1. **Build-State Pack**
2. **Debug Acceptance Matrix**
3. **Package Intake Review Kit**
4. **Safety-Critical Readiness Cards**

Still excluded:
- **Navigation / Defaults / Claims Commons**

Why navigation/defaults stays excluded:
- it is still `hold`;
- its blocker is stewardship and renewal burden;
- and fixture packs would create fake implementation momentum before the editorial-renewal problem is solved.

## The first fixture family
### 1) Build-State Pack fixtures
Needed lanes:
- one stable inner-loop workspace fixture,
- one nightly build-dir-layout caveat fixture.

What the fixtures should teach:
- stable-only capture/diff/doctor is enough to be useful;
- unstable build-dir or `cargo report` posture must remain labeled as optional;
- and path/layout drift belongs in expected checks, not cleanup folklore.

### 2) Debug Acceptance Matrix fixtures
Needed lanes:
- one async-heavy tuple fixture,
- optionally later one visualizer-heavy or expression-eval-heavy fixture.

What the fixtures should teach:
- tuple identity is first-class;
- replay inputs matter more than “best debugger” rhetoric;
- and yellow/red states are expected outputs, not embarrassing exceptions.

### 3) Package Intake Review Kit fixtures
Needed lanes:
- one crates.io trusted-publishing intake fixture,
- one alternate-registry uncertainty or quarantine fixture.

What the fixtures should teach:
- local receipts are the real product;
- route-specific uncertainty must survive the happy path;
- and waivers/quarantines are core product surfaces, not afterthoughts.

### 4) Safety-Critical Readiness Cards fixtures
Needed lanes:
- one evidence-card bootstrap fixture,
- one stale-card or missing-evidence diff fixture.

What the fixtures should teach:
- owner/freshness/evidence/do-not-prove fields are the honesty spine;
- stale or incomplete evidence is part of the product;
- and institutional review happens over time, so diff posture matters.

## What fixture packs are allowed to do
Allowed:
- bind witness files to replayable proving-ground cases,
- encode thin pass/fail expectations for early kernels,
- keep stable-only and unstable-enhanced lanes visibly separate,
- and make future implementations comparable without pretending they are the same implementation.

## What fixture packs are not allowed to do
Not allowed:
- pretend to be complete integration test suites,
- smuggle hosted telemetry or dashboard requirements into the first build,
- act like one passed fixture proves ecosystem default readiness,
- replace live packets, kernels, slices, contracts, or witnesses,
- or create kernel momentum for `hold` candidates.

## Default interpretation for future revisions
Until the portfolio changes materially:
- the broad ladder is unchanged;
- the missing new layer is **kernel fixture packs / replayable input scenarios**, not another ranking rewrite;
- live packets still govern verdict posture;
- kernels still govern first repo shape;
- slices still govern what lands first;
- contracts still govern the first machine-facing surface;
- witness packs still govern what the surface should look like when exercised;
- and fixture packs now govern **what scenarios and checks should drive those exercised outputs honestly**.
