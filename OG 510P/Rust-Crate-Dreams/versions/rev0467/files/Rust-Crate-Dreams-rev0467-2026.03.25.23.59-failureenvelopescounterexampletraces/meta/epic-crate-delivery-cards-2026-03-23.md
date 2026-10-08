# Epic crate delivery cards (2026-03-23)

This note answers the planning question the archive now has to answer more often:

> For a top-ranked proposal, what should the crate actually provide other people?

Each card is intentionally compact.
If a future proposal cannot be reduced to a card like this, it is probably not ready for promotion.

## Card schema

Every serious crate should be describable in terms of:

- **users** — who needs it,
- **promise** — what boring answer it gives them,
- **`0.1` outputs** — what files/reports/commands exist on day one,
- **workflows shortened** — what repeated pain it removes,
- **refusal boundaries** — what it must not pretend to prove.

---

## P-0509 — Crate Ecosystem Pathfinder & Decision-Pack Kit

**Users:** teams choosing foundational crates under time pressure; consultants and staff engineers writing starter recommendations; reviewers inheriting old choices.

**Promise:** one replayable answer to “why these crates, under which constraints, and what would reopen the choice later?”

**`0.1` outputs:**
- `starter-set.bundle.json`
- `candidate-elimination.receipt.json`
- `candidate-reentry.policy.json`
- `decision-timebox.receipt.json`
- `as-of-replay.report.json`

**Workflows shortened:** dependency evaluation, starter-kit docs, architecture review, re-checking whether a previously rejected option should return.

**Refusal boundaries:** must not claim universal “best crate” authority, permanent correctness of rankings, or timeless advice detached from frozen constraints.

---

## P-0486 — Debuggability Support Contract Kit

**Users:** library maintainers supporting bug reports; teams debugging across OSes and debuggers; organizations needing realistic debug posture claims.

**Promise:** one honest answer to “what debugging is actually supported here, in which session family, with what evidence?”

**`0.1` outputs:**
- `session-scope.receipt.json`
- `capability-witness.report.json`
- `claim-ceiling.report.json`
- `debug-support-bundle.manifest.json`

**Workflows shortened:** debugger support docs, issue triage, support escalation, release-note truthfulness around async/visualizer/expression-evaluation claims.

**Refusal boundaries:** must not emit one fake support score, must not treat one debugger/backend/OS success as universal truth, and must not claim async inspection or Rust-expression evaluation without task-level evidence.

---

## P-0472 — Docs.rs Build Parity & Evidence Kit

**Users:** crate maintainers fighting docs.rs failures; tool authors importing docs.rs output; reviewers checking hosted-vs-local documentation drift.

**Promise:** one answer to “how did the hosted docs build differ from local assumptions, and what is the smallest honest parity issue bundle?”

**`0.1` outputs:**
- `build-surface.receipt.json`
- `parity-gap.report.json`
- `issue-bundle.manifest.json`
- `hosted-assumption.note.md`

**Workflows shortened:** docs.rs incident reports, target/feature drift diagnosis, rustdoc JSON consumer checks, CI preflight for docs changes.

**Refusal boundaries:** must not claim exact reproduction of docs.rs when the environment differs, and must not flatten target-sensitive docs into one universal support story.

---

## P-0489 — Cargo Build-Dir Consumer Transition Kit

**Users:** tool authors and CI/release maintainers relying on build-dir internals; maintainers repairing target-dir path inference.

**Promise:** one answer to “what consumer assumption broke, what stable replacement exists, and do we need dual-support or an upstream block?”

**`0.1` outputs:**
- `consumer-inventory.manifest.json`
- `adapter-plan.json`
- `path-contract.json`
- `dual-support-window.report.json`

**Workflows shortened:** build-dir migration planning, internal path reliance audits, release process repair, library ecosystem adaptation.

**Refusal boundaries:** must not pretend Cargo internals are public contract, and must not convert one local workaround into false ecosystem-wide guidance.

---

## P-0046 — Buildscript UX Kit

**Users:** developers blocked by opaque `build.rs` failures; CI maintainers; crate maintainers tired of asking for whole logs.

**Promise:** one boring answer to “what mattered in this build-script run and what should I try next?”

**`0.1` outputs:**
- `buildscript-report.json`
- `buildscript-summary.txt`
- `policy-gate.report.json`
- optional `support-snapshot.redacted.txt`

**Workflows shortened:** install/debug support, CI failure triage, maintainer issue templates, redaction-aware bug reports.

**Refusal boundaries:** must not pretend Cargo exposes perfect causality, and must not require whole raw logs to get value.

---

## P-0058 — Native Deps Kit

**Users:** `-sys` maintainers; downstream teams with pkg-config/vcpkg/vendored confusion; enterprise and air-gapped build owners.

**Promise:** one answer to “what native contract was declared, what probe path ran, what ABI/package-manager assumptions were used, and how do I satisfy or override them?”

**`0.1` outputs:**
- `native-contract.toml`
- `native-resolution.report.json`
- `backend-attempts.receipt.json`
- `abi-provenance.report.json`
- `consumer-doctor.txt`

**Workflows shortened:** native dependency diagnosis, Windows/MSVC setup, vendored-vs-system review, FFI support docs, offline CI preparation.

**Refusal boundaries:** must not become a package manager, must not hide vendoring behind feature magic, and must not imply ABI certainty it cannot prove.

---

## P-0535 — Dependency Lifecycle Transition Kit

**Users:** teams replacing or off-ramping dependencies; regulated adopters; maintainers planning long-lived support posture.

**Promise:** one answer to “what keeps today’s selection stable, what breaks on fresh resolve, and what transition seam is reviewable?”

**`0.1` outputs:**
- `selection-anchor.receipt.json`
- `reresolution-risk.report.json`
- `offramp-bundle.manifest.json`
- `override-authority.receipt.json`

**Workflows shortened:** dependency replacement planning, lockfile/yank review, compatibility exception tracking, support-lifetime docs.

**Refusal boundaries:** must not pretend locks are forever, must not confuse local patches with portable solutions, and must not erase MSRV and source provenance from lifecycle decisions.

---

## P-0484 — Toolchain & Target Support Contract Kit

**Users:** platform engineers, embedded/kernel/Wasm maintainers, reviewers checking support claims.

**Promise:** one answer to “what part of support is actually true here: target tier, host route, std/no_std posture, exercised environment, or external prerequisite?”

**`0.1` outputs:**
- `target-support.receipt.json`
- `host-target-route.report.json`
- `external-prerequisite.report.json`
- `support-bundle.manifest.json`

**Workflows shortened:** support matrices, release documentation, CI target audits, cross-build debugging.

**Refusal boundaries:** must not collapse target availability, docs presence, and tested support into one fake yes/no badge.

---

## P-0536 — Crate Knowledge Pack Kit

**Users:** human maintainers, support engineers, documentation tools, assistants retrieving crate knowledge.

**Promise:** one pinned, target-aware, cited answer pack for recurring crate questions.

**`0.1` outputs:**
- `assistant-context.pack.json`
- `query-support.matrix.json`
- `claim-trace.report.json`
- `citation-locator.receipt.json`
- `citation-capability.report.json`

**Workflows shortened:** support docs, internal knowledge handoff, assistant retrieval, common question playbooks.

**Refusal boundaries:** must not cite unpinned “latest” surfaces as if they were stable, and must not answer beyond its evidence class.

---

## P-0537 — Compile Iteration Feedback Kit

**Users:** developers optimizing edit-build-run loops; teams comparing reload strategies; maintainers documenting fast-path claims.

**Promise:** one answer to “what fast path applied, what blocked it, what code generation is live, and what degraded mode or restart is now required?”

**`0.1` outputs:**
- `edit-scope.receipt.json`
- `fast-path-barrier.report.json`
- `generation-witness.report.json`
- `live-update-outcome.report.json`
- `degraded-iteration-mode.report.json`

**Workflows shortened:** reload/hotpatch support docs, dev-loop experimentation, issue triage around stale code and mixed-generation risks.

**Refusal boundaries:** must not use one visible UI update as proof that the whole process is updated, drained, or homogeneous.

---

## P-0538 — Concurrency Contract Kit

**Users:** runtime/library authors, teams comparing channels/locks/notify surfaces, reviewers trying to avoid folklore.

**Promise:** one answer to “what are the real semantics here around delivery, fairness, cancellation, locality, late join, and evidence of receipt?”

**`0.1` outputs:**
- `progress-fairness.report.json`
- `wait-cancellation.report.json`
- `delivery-order.report.json`
- `gap-visibility.report.json`
- `mobility-affinity.report.json`
- `driver-liveness.report.json`

**Workflows shortened:** concurrency API docs, primitive comparison, migration between runtimes or channel families, async support review.

**Refusal boundaries:** must not flatten many distinct semantics into one “concurrency-safe” claim.

---

## P-0011 — Crate Health Contract Kit

**Users:** adopters evaluating long-lived dependencies; maintainers signaling support posture; organizations reviewing continuity risk.

**Promise:** one answer to “what maintenance and response posture exists here, who owns it, and what continuity backstops are visible?”

**`0.1` outputs:**
- `maintenance-coverage.matrix.json`
- `routing-continuity.report.json`
- `artifact-completeness.report.json`
- `health-contract.bundle.json`

**Workflows shortened:** dependency intake review, succession planning, support channel routing, issue response expectations.

**Refusal boundaries:** must not equate recent commits with sustainable maintenance.

---

## What the cards change in practice

A future pass should now be able to say, for any promoted crate:

- what file bundle appears on disk,
- what command or API creates it,
- what boring work it replaces,
- and where honesty requires a refusal or a manual-review boundary.

That should be treated as part of the archive’s quality bar.

## Sources

- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build scripts reference — https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ (“Why is Cargo rebuilding my code?”) — https://doc.rust-lang.org/cargo/faq.html
- docs.rs builds — https://docs.rs/about/builds
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- What does it take to ship Rust in safety-critical? — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- system-deps docs — https://docs.rs/system-deps/latest/system_deps/
- `system-deps` standardization discussion — https://github.com/gdesmott/system-deps/issues/97
- vcpkg docs — https://docs.rs/vcpkg/latest/vcpkg/
