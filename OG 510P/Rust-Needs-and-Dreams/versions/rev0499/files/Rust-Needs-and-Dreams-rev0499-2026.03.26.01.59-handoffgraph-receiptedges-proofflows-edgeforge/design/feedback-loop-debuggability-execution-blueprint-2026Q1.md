# Design: Feedback Loop / Debuggability Acceptance execution blueprint (2026 Q1)

## Goal
Turn the archive's clearest **under-ranked missing middle** into a sharper **buildable program**.

The missing contribution is not another debugger fork, another IDE-only integration, another hosted DX portal, or another assistant that claims it understands local state.
It is a disciplined companion layer that makes Rust's **build → diagnose → inspect → explain → hand off** loop reviewable across local workstations, CI, support, and future assistant/editor consumers.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team wants to build the archive's current best “missing middle” contribution, what should that project actually ship in theory and practice?

Read with:
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/feedback-loop-stack.md`
- `design/debuggability-stack.md`
- `design/feedback-loop-pilot-program.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `proposals/epic-feedback-loop-stack.md`

## Why this note is needed now
The archive already knew that **Feedback Loop / Debuggability Acceptance** mattered.
What it still lacked was a crisper answer to **what the missing contribution should look like**.

Fresh official signals sharpen that answer:
- Rust's 2025 State of Rust survey says resource usage remains one of the biggest non-trivial productivity problems, the debugging story remains a major problem, online docs are still the preferred canonical reference, and more users are learning through editor/LLM-mediated flows.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The compiler-performance survey says workflow differences matter, more than 35% of respondents consider IDE and Cargo blocking one another to be a big problem, and full debug info in dev builds increases disk usage and slows compilation and linking.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The Cargo build-analysis goal is explicitly about recording build metadata across invocations, exposing rebuild reasons, and enabling richer `cargo report` analysis.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The **Relink don't Rebuild** goal says many harmless edits still rebuild reverse dependencies today, which means the feedback loop needs a place to keep **observed rebuild pain** distinct from **future avoidable rebuild opportunities**.
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- The build-dir-layout goal and the March 2026 testing call make editor/CLI coexistence, finer-grained locking, target-dir GC, and layout honesty first-class concerns rather than hidden local folklore.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The 2026 debugging survey says “truly stellar” support would require multiple debugger versions across OSes, quality visualizers, first-class async debugging, and Rust expression evaluation, and says Rust is not there yet.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The production-ready Cranelift backend goal says a production-ready local-dev backend still lacks one major feature: debug info. That is direct evidence that debuggability is not just a docs problem or editor problem; it shapes compilation strategy too.
  https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html
- The 2026 goals page continues to emphasize **Just Add Async** and broader higher-level ergonomics, which means async-capable inspection and better loop ergonomics are not optional side quests if ideal Rust is meant to feel operable in practice.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

Taken together, those signals say the archive should stop describing the missing middle only as a theme.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's strongest under-ranked contribution, the answer should now be:

> Build a **Feedback Loop / Debuggability Acceptance layer** that imports build-state evidence, records debugger/runtime-inspection tuple truth, carries an acceptance corpus for visualizers and async/native scenarios, and emits reviewable packs and handoffs for humans, support, CI, and later assistant/editor consumers.

That answer is deliberately narrower than “fix Rust debugging”.
It is also deliberately stronger than “show logs and debugger notes”.

## What this contribution should be in theory

### Core thesis
A feedback-loop system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what subject and session were under review;**
2. **what build-state facts existed for that session;**
3. **what diagnostic / debugger / runtime-inspection lane actually ran;**
4. **what tuple, profile, and visualizer assumptions those observations depended on;**
5. **what gaps remained unsupported, partial, or merely watch-listed;**
6. **what downstream consumer may honestly conclude from the evidence.**

If a project cannot answer those questions without shell history, IDE state, debugger tribal knowledge, and issue-thread archaeology, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable feedback-loop acceptance**.

It should include:
- session and subject capture;
- imports from Build-State Evidence;
- diagnostic/rendering/debugger/runtime-inspection receipts;
- debugger-tuple and visualizer acceptance facts;
- async/native/split-debug scenario coverage;
- consumer-specific summaries.

It should not become:
- a replacement Cargo;
- a replacement debugger;
- a universal IDE backend;
- a local daemon empire;
- or a hosted debugging analytics product.

### Separation rule
The contribution must preserve at least five distinct truth classes:
- **session truth** — what subject, workflow lane, profile, toolchain, target-dir/build-dir policy, and intent were under review;
- **build-state truth** — what Cargo/build evidence actually said;
- **inspection truth** — what diagnostics, debugger actions, traces, or runtime-side tools actually ran;
- **acceptance truth** — what debugger tuple, visualizer, async inspection, or expression-evaluation capability was proven, partial, or unsupported;
- **consumer truth** — what docs/support/CI/assistant exports may conclude, with what lossiness.

This is the largest theory/practice guardrail in the design.
Without it, every loop summary becomes a confidence soup.

### Shape rule
This contribution should begin as a **capability commons + acceptance corpus + report/pack command**.
That means:
- a **commons** for reusable capability vocabulary and scenario IDs;
- an **acceptance corpus** for debugger tuples, visualizers, and async/native scenarios;
- and a thin **command / pack layer** that imports build and debug evidence instead of replacing it.

It should not begin as a service, ranking site, or “one debugger story” brand.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo innerloop session`
- `cargo innerloop attach-build`
- `cargo innerloop attach-debug`
- `cargo innerloop accept`
- `cargo innerloop diff`
- `cargo innerloop doctor`
- `cargo innerloop export --consumer <issue|support|docs|ci|assistant|editor>`
- `cargo innerloop pack`

The tool should **import** first-party or established companion surfaces when available rather than replace them.

### Public artifact spine

#### Imported/internal families
- `build-state-pack/v0`
- `impact-pack/v0`
- `diagnostic-pack/v0`
- `debug-pack/v0`
- `obs-pack/v0`
- `debuggability-pack/v0`
- optional replay / incident / test attachments

#### Public review families
- `feedback-loop-session/v0`
- `debugger-tuple-profile/v0`
- `debug-acceptance-scenario/v0`
- `visualizer-acceptance-report/v0`
- `async-debug-acceptance-report/v0`
- `feedback-loop-acceptance-brief/v0`
- `feedback-loop-pack/v0`
- `feedback-loop-handoff/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — workspace/package/target/profile/features/toolchain, workflow lane, OS/target/debugger family, and intent class;
- **authority posture** — observed locally, imported from Cargo-native reports, imported from debugger/runtime-inspection receipts, or inferred;
- **coverage / completeness** — exact, partial, fallback-only, unsupported, stale, or mixed;
- **tuple anchors** — debugger version, OS, architecture, toolchain channel, debug-info posture, and visualizer set;
- **scenario anchors** — sync, async, `!Send`, split-debug-info, optimized-dev, native-edge, cross-target, or CI-repro lanes;
- **raw attachments** — transcripts, traces, timing reports, minimized repros, pretty-printer logs, screenshots, or recording pointers when present;
- **reason-coded conclusions** — supported / partial / watch / unsupported / inconclusive with explicit ambiguity;
- **consumer limits** — what issue/support/docs/assistant/editor consumers may and may not claim.

### Commands and what they should emit

#### `cargo innerloop session`
Purpose:
- capture one loop session;
- record subject, workflow, profile, target-dir/build-dir posture, and intended inspection lane;
- emit `feedback-loop-session/v0`.

Important rule:
- if change provenance is missing, say it is missing instead of inventing a semantic diff.

#### `cargo innerloop attach-build`
Purpose:
- import Build-State Evidence and keep session/build anchors linked;
- make rebuild pain, lock contention, duplication, and debug-info posture part of the loop record.

Important rule:
- observed build facts and hypothetical relink opportunities must stay distinct.

#### `cargo innerloop attach-debug`
Purpose:
- attach diagnostics, debugger receipts, traces, or runtime-side inspection evidence;
- preserve which inspection lane actually ran.

Important rule:
- runtime-side inspection is not debugger parity and must not be rendered as such.

#### `cargo innerloop accept`
Purpose:
- emit debugger tuple and visualizer acceptance results for one or more shared scenarios;
- produce `debugger-tuple-profile/v0`, `visualizer-acceptance-report/v0`, and `async-debug-acceptance-report/v0` as appropriate.

Important rule:
- unsupported or flaky capability claims are first-class results, not embarrassing footnotes.

#### `cargo innerloop diff`
Purpose:
- compare two packs while preserving the distinction between:
  - changed build evidence,
  - changed debugger tuple posture,
  - changed visualizer quality,
  - changed async/native acceptance,
  - and changed consumer claims.

#### `cargo innerloop doctor`
Purpose:
- attach bounded next-step suggestions such as “separate target dir to avoid contention”, “debug info/profile mismatch blocks tuple parity”, “visualizer missing for core type family”, or “async scenario not yet covered by acceptance corpus”.

Important rule:
- suggestions should always point back to the fact basis.

#### `cargo innerloop export`
Purpose:
- emit smaller issue/support/docs/CI/assistant/editor slices without making those slices canonical by themselves.

## Ranked feature set

### P0 — required for a worthy v0
- explicit session capture;
- imports from Build-State Evidence rather than log scraping;
- debugger-tuple profiles with OS/version/toolchain anchors;
- visualizer acceptance for a small representative corpus of common Rust types;
- one async-debug acceptance lane with honest unsupported states;
- one native/split-debug-info lane with explicit caveats;
- one portable brief plus one portable pack;
- lossiness-visible exports for issue/support/docs consumers.

### P1 — strong near-term extensions
- CI repro packs and minimized reproduction linkage;
- expression-evaluation posture tracking where available;
- richer async lane coverage (`!Send`, runtime-specific, task-local, timer-heavy cases);
- editor-facing slices once the human-facing pack is stable;
- release-note / compatibility handoffs for debugger tuple changes.

### P2 — do later or fold elsewhere
- hosted team dashboards;
- debugger orchestration SaaS;
- universal log/trace schema empires;
- assistant-first auto-debugging agents;
- organization-wide scores that flatten evidence quality.

## Pilot lanes that best prove the idea

### 1) Session + build/debug handoff lane
Prove:
- one real loop session can link Cargo evidence and inspection evidence without guesswork;
- target-dir/build-dir/debug-info posture remains visible;
- observed build pain and observed debugger pain are separable but linked.

### 2) Debugger tuple / visualizer acceptance lane
Prove:
- a small shared type corpus can be exercised across a handful of debugger tuples;
- quality, unsupported states, and regressions can be named explicitly;
- the result is more useful than vague “Rust debugging works here” prose.

### 3) Async inspection lane
Prove:
- async support is modeled as an acceptance problem, not a yes/no slogan;
- the pack can distinguish native debugger support from runtime-side inspection and tracing;
- unsupported or partial results remain part of the output.

### 4) Native-edge / split-debug-info lane
Prove:
- non-default compilation/debug-info setups can still produce honest loop evidence;
- the stack can document when compiler/backend/debug-info choices narrow debugger quality.

### 5) Issue / support / docs consumer lane
Prove:
- the pack can drive bounded human-facing handoffs before any assistant/editor widening happens.

## What should count as success overall
The stack is working when a maintainer or downstream consumer can answer:
- what exact loop session is under review;
- what Cargo/build evidence exists for it;
- what inspection lane actually ran;
- which debugger tuple or runtime-side lane the result depends on;
- what remains unsupported or partial;
- and what the resulting issue/support/docs/assistant slice may safely summarize,

without scraping shell history, IDE state, debugger folklore, or CI archaeology.

## Failure modes to avoid
- starting from a giant IDE platform;
- pretending runtime-side inspection equals debugger parity;
- flattening build-state evidence and debug-acceptance evidence into one score;
- widening to assistant-first experiences before human-readable packs are stable;
- hiding unsupported tuple/scenario results because the narrative sounds nicer.

## Archive implications
Treat this note as the sharper execution answer for the archive's “under-ranked missing middle”.

The strongest current formulation is now:
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** is the clearest next contribution that ideal Rust still needs in ordinary daily practice;
- its primary shape is **capability commons + acceptance corpus + report/pack layer**;
- it should import Build-State Evidence rather than replace it;
- and later assistant/editor/service overlays should remain consumers, not the canonical truth source.
