# Epic crate adoption contracts — 2026-03-25

This note sharpens the archive’s working definition of a worthy contribution.

The key shift is:

**a worthy missing crate should export an adoption contract, not just an implementation trick.**

That means the crate should help another team adopt, review, or operate something with less tacit lore than before.

## What an adoption contract includes

A strong crate plan should be able to answer all of these.

### 1. Named receiver
Who gets value first?

Examples:
- platform engineers choosing a starter stack,
- maintainers trying to explain docs.rs differences,
- release engineers trying to prove target/toolchain posture,
- support engineers trying to know what debugging a release actually supports,
- regulated adopters trying to manage dependency drift.

If the answer is only “the Rust ecosystem”, the plan is still too vague.

### 2. Repeated workflow
What repeated pain becomes easier?

Examples:
- choosing among plausible crates for a task,
- freezing what evidence a recommendation was based on,
- explaining why hosted docs differ from local docs,
- stating what targets are truly supported,
- reopening a crate decision after a trust or lifecycle trigger.

If the crate only makes a one-off demo nicer, it is weaker.

### 3. Portable artifact family
What durable output does another team receive?

Examples:
- `decision-pack.report.json`
- `starter-set.lock.json`
- `review-packet.manifest.json`
- `target-support.report.json`
- `debugger-compatibility.report.json`
- `decision-revalidation.report.json`

If the answer is only “an API” or “a dashboard”, the contract is underspecified.

### 4. Imported substrate
Which real Rust surfaces does the crate stand on?

Today the archive should strongly prefer crates that import official or already-real substrate such as:
- crates.io security/trust surfaces,
- docs.rs build conditions, downloads, and rustdoc JSON,
- Cargo metadata and build/report work,
- CI matrices and `rust-toolchain.toml`,
- release/package contents,
- official target/support guidance,
- or future stable compiler/tooling surfaces like StableMIR or libtest/Cargo reporting.

If the crate invents fantasy substrate when real substrate exists, it is weaker.

### 5. First useful release
What can `0.1` honestly do?

A strong answer names:
- supported lanes or scenarios,
- supported inputs,
- explicit outputs,
- and what is manual-review-only.

If the plan needs every domain, every target, or every semantic edge case before it is useful, it is weaker.

### 6. Refusal boundary
What does the crate refuse to claim?

Examples:
- not a universal recommender,
- not a security oracle,
- not a replacement for docs.rs,
- not a universal debugger,
- not a whole async semantics prover.

If the refusal boundary is missing, later passes will overinflate the lane.

### 7. Drift / recheck story
How does the answer age?

A worthy crate should be able to say:
- what was frozen,
- what triggers re-open review,
- and what artifact records the changed posture.

Without that, the crate may help choose once but not operate over time.

## The top frontier through this lens

### Tier A — strongest adoption-contract front

#### P-0509 — Crate Ecosystem Pathfinder
Why it stays first:
- receiver is obvious,
- workflow is repeated,
- output can be reviewed,
- and current ecosystem substrate makes a narrow honest release plausible.

What it should provide:
- a compact answer to “what stack fits this task under these constraints?”,
- runner-up visibility,
- explicit policy handling,
- and a lock/recheck story.

#### P-0536 — Crate Knowledge Pack Kit
Why it stays paired with P-0509:
- pathfinder answers are much stronger when they sit on a replayable cited basis,
- current docs.rs/package surfaces make this unusually tractable,
- and both humans and tools benefit.

What it should provide:
- the cited, pinned bundle underneath a decision,
- build surface and target notes,
- and citation re-entry for later review.

### Tier B — the ground-truth import ring

#### P-0472 — Docs.rs Build Parity & Evidence Kit
What it should provide:
- preflight and diff artifacts for hosted/local documentation reality,
- target/default-target visibility,
- and portable issue/support bundles.

#### P-0484 — Toolchain & Target Support Contract Kit
What it should provide:
- tested vs claimed vs unknown target/toolchain posture,
- component requirements,
- and release-to-release diffable support statements.

#### P-0535 — Dependency Lifecycle Transition Kit
What it should provide:
- trigger intake,
- revalidation,
- replacement/internalization planning,
- and a durable difference between “old answer” and “new pressure”.

These lanes are especially strengthened by current official signals around docs.rs behavior, crates.io trust/security posture, safety-critical lifecycle concerns, Rust-for-Linux tooling constraints, and semver/public API work.

### Tier C — high-need but higher-ceiling lanes

#### P-0486 — Debuggability Support Contract Kit
The need is obvious.
The adoption contract is also strong.
But the first release should remain bounded:
- export support posture,
- symbol/debug sidecar truth,
- debugger/version notes,
- and async/debug claim ceilings.

#### P-0537 — Compile Iteration Feedback Kit
This lane grows stronger as Cargo build-analysis substrate matures.
Its adoption contract is promising, but it should not pretend today’s substrate already solves the whole workflow.

#### P-0538 — Concurrency Contract Kit
This remains highly salient, but it is still the hardest lane to overclaim.
A good first release likely needs scenario labs and bounded receipts around specific primitives or runtimes rather than a giant universal semantic truth engine.

## Receiver-leverage board

This pass keeps the archive’s practical receiver-leverage order roughly as:

1. **P-0509 + P-0536**
2. **P-0472 + P-0484 + P-0535**
3. **P-0486**
4. **P-0431 + P-0496**
5. **P-0537**
6. **P-0538**

Why:
- the first group helps teams choose and freeze;
- the second group helps them know what they really got;
- the third helps them support what they shipped;
- and the later groups matter, but either need more substrate or have a higher semantic claim ceiling.

## Anti-patterns

Do not promote a proposal just because it:
- sounds foundational,
- spans many domains,
- wraps a large ecosystem,
- or would make a good talk title.

A crate contribution becomes worthy when it helps another team do one of these things with less lore:
- choose,
- freeze,
- explain,
- support,
- transition,
- or interoperate.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://www.arewewebyet.org/
- https://areweguiyet.com/
- https://arewegameyet.rs/
- https://georust.org/
- https://github.com/automerge/automerge
