---
id: P-0104
title: Deterministic Simulation Kit — simulation profiles, backend receipts, and replayable async failure bundles
status: idea
domains: [testing, determinism, distributed-systems, async, devtools]
last_reviewed: 2026-03-09
evidence:
  - https://docs.rs/tokio/latest/tokio/time/fn.pause.html
  - https://github.com/tokio-rs/simulation
  - https://docs.rs/turmoil/latest/turmoil/
  - https://docs.rs/madsim/latest/madsim/
  - https://docs.rs/shuttle/latest/shuttle/
  - https://docs.rs/loom/latest/loom/
  - https://rust-lang.github.io/rust-project-goals/2025h1/async.html
  - https://www.polarsignals.com/blog/posts/2025/07/08/dst-rust
---

# P-0104 — Deterministic Simulation Kit

**Codename:** `simkit`

**Canonical artifact:** `*.simrun.zip`, ideally as a `simrun@1` profile on top of **P-0256 Evidence Bundle Core Kit**.

**Primary surface:** a crate workspace plus `cargo sim`.

## Problem

Rust no longer lacks *all* substrate for deterministic testing of async and distributed systems.
It now has a fragmented but increasingly real stack:

- Tokio already supports **paused/mock time** on a `current_thread` runtime, with explicit `start_paused` support and auto-advance behavior.
- `tokio-rs/simulation` still captures an important design idea: deterministic analogues to time, scheduling, and network I/O for FoundationDB-style simulation testing.
- `turmoil` provides deterministic multi-host execution inside one thread, plus seeded network hardship and optional filesystem lanes.
- `madsim` shows that a tokio-like deterministic runtime can work in practice, but it also demonstrates the cost of runtime replacement and dependency patching when a project wants deep control.
- `shuttle` and `loom` show that schedule exploration and deterministic replay are already valuable in Rust, but they target different parts of the problem space: shared-memory concurrency and intrusive scheduler exploration rather than a general async multi-host simulation workflow.

That combination changes the shape of the missing value.
The missing crate is **not** “invent deterministic testing from scratch”.
It is also **not** “pick one runtime and make everyone rewrite their code”.

The missing crate is a **boring coordination kit** above today’s substrate:

- one simulation profile,
- one backend capability receipt,
- one portable fault/scenario contract,
- one comparable transcript/report format,
- one replay/minimization workflow,
- and one honest bundle another person can inspect.

## Main judgment

A worthy crate contribution here would give other people one honest answer to:

> which ingredients of nondeterminism were actually under control, which backend or adapter produced the run, what schedule/time/fault decisions materially shaped the outcome, and can another reviewer replay or minimize the failure?

That answer should stay useful even when different teams choose different deterministic backends.

## What the crate should provide other people

### 1. A small simulation profile
The first missing deliverable is not an executor.
It is a compact `sim-profile.toml` that freezes the receiver-facing contract for a run:

- subject/workspace identity,
- backend adapter (`tokio-paused`, `turmoil`, `madsim`, `shuttle`, `custom`),
- time model,
- randomness model,
- fault lanes in scope,
- transport/network abstraction in scope,
- replay strictness,
- redaction defaults,
- and comparability policy.

This keeps the product focused on **portable runs and artifacts**, not “replace the world with one runtime”.

### 2. Explicit ingredient lanes
The proposal should make the main simulation ingredients explicit instead of hiding them in one fake “deterministic mode” flag.

A good first lane model is:

1. **scheduler lane** — how task/thread interleavings are chosen and replayed,
2. **time lane** — paused/virtual time semantics and auto-advance behavior,
3. **randomness lane** — seed identity and controlled RNG surfaces,
4. **fault lane** — injected delay/drop/reorder/partition/crash/clock effects,
5. **external-I/O lane** — whether the run used simulated I/O, real I/O, cassettes, or unsupported live edges.

This matters because today’s substrate covers these lanes unevenly.
A run with deterministic scheduling but live sockets is not the same claim as a run with simulated networking and deterministic time.

### 3. Backend capability receipts
The crate should emit one `backend-capability.receipt.json` that says what the chosen backend can and cannot honestly guarantee.

Examples:

- **Tokio paused-time lane:** single-threaded time control, but not a general network/fault simulator by itself.
- **Turmoil lane:** deterministic single-thread multi-host execution and seeded network hardship, but still backend-specific and not yet opinionated on application structure.
- **MadSim lane:** broader deterministic runtime surface, but may require runtime replacement and patched dependencies.
- **Shuttle lane:** replayable schedule exploration, but primarily for shared-memory/concurrency testing with adapted primitives rather than message-network simulation.
- **Loom lane:** exhaustive/permuted concurrency checking for small concurrent units, not a drop-in distributed-system simulator.

This receipt is one of the most missing artifacts in the current ecosystem.
People can often run these tools, but they rarely export a compact statement of **what exactly this backend controlled**.

### 4. Fault/scenario contracts
The crate should define one backend-neutral scenario/fault surface with concepts like:

- node/actor topology,
- allowed external inputs,
- partitions,
- link delay/reorder/drop,
- timer perturbation,
- crash/restart points,
- manual checkpoints,
- and shrink/minimization hints.

The design goal is not to flatten all backends into one fake common denominator.
It is to let a project say:

- which parts of the scenario are portable,
- which are backend-specific,
- and where a replay on another backend is only partially comparable.

### 5. Schedule/time transcripts
The output should include one transcript/report lane that another maintainer can actually inspect.
A useful `schedule-transcript.report.json` should preserve at least:

- seed identity,
- scheduler decisions or schedule token,
- time-advance events,
- message/fault injections,
- major task/host lifecycle events,
- assertion / failure location,
- and whether the transcript is exact, summarized, or redacted.

This is the day-to-day artifact missing from many “we have deterministic tests” stories.
The run happened, but another person cannot see the shape of it without reading logs or rerunning with custom tracing.

### 6. Replay and minimization reports
A worthy kit should not stop at “here is a seed”.
It should also ship:

- one replay command contract,
- one `minimization.report.json` saying what scenario complexity was reduced,
- and one conservative comparability statement saying whether the minimized run is semantically equivalent, partially equivalent, or manual-review-only.

This is especially important because different backends preserve different amounts of schedule information.

### 7. One honest 0.1 golden path
The MVP should ship one boring, supportable first story:

- **Tokio-first** project ergonomics,
- **single-thread deterministic core** as the default claim,
- **import/export adapters** for `turmoil`, `madsim`, and `shuttle`,
- and a small reference message-passing example that proves the bundle/replay/minimization workflow end to end.

The key strategic move is to start with **artifact compatibility above backend diversity**, not with a new universal runtime.
That is much more likely to become ecosystem infrastructure.

### 8. One portable `simrun` bundle
The main receiver-facing output should be `*.simrun.zip`, ideally using the shared bundle substrate from **P-0256**.
A first profile should include:

- bundle manifest,
- sim profile,
- backend capability receipt,
- fault plan,
- schedule transcript,
- minimization report,
- environment/toolchain summary,
- and optional redacted application trace lanes.

That is what this crate should hand to other people.

## Persona / who it’s for

- maintainers of async/distributed Rust services
- teams debugging rare timing and fault bugs
- library authors who want one portable deterministic-testing artifact instead of backend-specific story files
- CI owners who need replayable failure bundles
- researchers comparing scenario outcomes across implementations or backends

## Users & user stories

- **Distributed-systems maintainer:** “A failing seed should become a small bundle I can replay, shrink, and send to another maintainer.”
- **App team:** “We use Tokio today; help us adopt deterministic failure testing without a total runtime rewrite.”
- **Infra engineer:** “Tell me whether this run was really deterministic, or only deterministic with respect to time and scheduling but not external I/O.”
- **Reviewer:** “Show me whether two failing runs are actually comparable or only superficially similar.”
- **Tool author:** “I want to plug my backend into one shared artifact format instead of inventing yet another replay story.”

## Prior art scan (and why it’s insufficient)

### Tokio time control is substrate, not a full workflow
Tokio’s paused time support is real and useful.
It already gives Rust a credible time-control lane for tests.
But it does not by itself define:

- a portable simulation profile,
- a fault plan,
- a schedule transcript,
- a replay bundle,
- or a comparability contract.

### tokio-rs/simulation captures the right architecture, but not the boring product
The Simulation project still captures the design idea of deterministic time, scheduling, and network analogues.
But it is not today’s broadly adopted default crate workflow.
That reinforces the archive’s judgment that the missing value is now the **boring kit and artifact contract above substrate**, not just one more low-level runtime experiment.

### Turmoil is powerful but backend-shaped
Turmoil already provides deterministic multi-host execution with controllable network hardship.
That is serious substrate.
What it does not yet provide is a backend-neutral bundle/replay/minimization surface that multiple Rust projects can share.

### MadSim proves depth, but also ecosystem cost
MadSim shows that deterministic simulation can go much deeper when a project is willing to replace runtime and networking surfaces.
Its docs also make clear that this often means crate replacement and patches.
That is useful evidence for why a missing crate should start from **portable artifacts and adapters** rather than requiring one universal runtime bet.

### Shuttle and Loom matter, but they are different layers
Shuttle and Loom are strong evidence that deterministic schedule exploration and replay are valuable.
But they operate on different boundaries:

- Loom explores concurrent executions for small concurrent programs under a memory-model-focused testing lens.
- Shuttle explores and replays schedules for concurrent Rust code with adapted primitives.

A good P-0104 crate should compose with those tools where useful, while staying honest that they are not the same thing as multi-host async simulation with explicit fault/network lanes.

## Design goals

- Prefer **artifact compatibility** over pretending backends are identical.
- Preserve which deterministic ingredients were actually controlled.
- Keep **not comparable** and **manual-review-required** as first-class outputs.
- Start with **single-thread deterministic-core claims** before broader promises.
- Make replay/minimization first-class because that is what makes failures operationally useful.
- Compose with existing Rust testing stacks instead of replacing them all.

## Non-goals

- Not a universal async runtime replacement.
- Not a full record/replay debugger for arbitrary live production executions; that remains closer to **P-0073 Async Replay Debugger Kit**.
- Not a game-specific rollback state-hashing kit; that remains closer to **P-0066 Determinism Sim Kit**.
- Not a standards corpus or protocol-specific hardship suite by itself; those belong in domain kits or in **P-0114 Distributed Systems Hardship Harness Kit**.
- Not a promise of exact determinism across uncontrolled external I/O from day 1.

## MVP sketch

### 0.1 — receipt spine
- `sim-profile.toml`
- `backend-capability.receipt.json`
- `fault-plan.json`
- `schedule-transcript.report.json`
- `minimization.report.json`
- `cargo sim replay`

### 0.2 — backend adapters
- import/export adapters for `turmoil`, `madsim`, and `shuttle`
- one Tokio-first reference harness
- one cross-backend comparability report

### 0.3 — redaction and shared bundles
- `simrun@1` profile on top of **P-0256**
- transcript redaction support
- signed/diffable support-bundle workflows

## Adoption plan

- Start with one reference workspace that proves the bundle shape on a real async example.
- Treat backend adapters as separate crates so one unstable backend does not stall the whole kit.
- Ship domain-agnostic examples first, then let protocol/distributed crates layer scenario corpora on top.
- Publish guidance for “what claims you are and are not allowed to make” based on the backend capability receipt.

## Why now

Async Rust remains strategically important to the language and ecosystem, and the Rust project has explicitly framed async ergonomics and reliability as an area where users still encounter sharp edges.
At the same time, the substrate for deterministic testing is no longer hypothetical.
What is missing is a shared, boring, reviewable contract that turns that substrate into something ordinary teams can adopt.

## Sources

- https://docs.rs/tokio/latest/tokio/time/fn.pause.html
- https://github.com/tokio-rs/simulation
- https://docs.rs/turmoil/latest/turmoil/
- https://docs.rs/madsim/latest/madsim/
- https://docs.rs/shuttle/latest/shuttle/
- https://docs.rs/loom/latest/loom/
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://www.polarsignals.com/blog/posts/2025/07/08/dst-rust
