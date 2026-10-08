# Design: Process Surface Pilot Program

## Goal
Turn Process Surface Kit from a good conceptual map into a **ranked execution plan**.

Rust already has enough subprocess machinery to prove the gap is real.
The next step is not more helper accumulation.
It is a pilot sequence that shows Rust projects can publish **reviewable process-surface truth** across direct exec, shell-shaped composition, pipe topology, async lifecycle, tree control, and PTY interaction without pretending those lanes have already converged.

Read this together with:
- [`design/process-surface-kit.md`](./process-surface-kit.md)
- [`design/process-surface-lane-map.md`](./process-surface-lane-map.md)
- [`design/command-surface-kit.md`](./command-surface-kit.md)
- [`design/filesystem-surface-kit.md`](./filesystem-surface-kit.md)
- [`proposals/epic-process-surface-kit.md`](../proposals/epic-process-surface-kit.md)

## Why this needs its own design layer
The Process Surface Kit already defines the artifact family: surface/profile/vector/check/pack artifacts.

What it did **not** yet answer clearly enough is:
- which subprocess lanes should be piloted first,
- which distinctions are worth locking in early,
- how to keep shell-like helpers separate from actual shell execution,
- how to preserve lifecycle and cleanup differences across std and async crates,
- and what counts as pilot success versus another subprocess demo.

Without that layer, process-surface work risks two bad outcomes:
1. **helper flattening** — the archive starts implying all process libraries differ only in ergonomics;
2. **abstraction theater** — a wrapper or DSL gets narrated as if it solved spawn, tree control, and PTY semantics all at once.

## Design principles
1. **Start from exact lane identity.** Every pilot should say which process lane it is proving.
2. **Separate actual shell from shell-shaped ergonomics.** Helper syntax is not enough to infer shell semantics.
3. **Treat cleanup/reaping as public contract.** Drop, kill, wait, and reap behavior are part of the surface.
4. **Treat tree control as its own lane.** Lone-child control is not process-tree control.
5. **Treat PTY as a mode shift, not a stdio toggle.** PTYs alter interaction semantics materially.
6. **Prefer vectors that reveal lossiness.** Relative-path/current-dir, EOF, deadlock, dropped-child, descendant cleanup, and PTY prompt vectors matter more than broad feature matrices.
7. **Consumer handoffs must stay bounded.** A CI reviewer, migration tool, or agent runner should only claim the lane facts actually exported.
8. **Historical lessons count.** Older Tokio child-drop semantics should remain visible as a caution against narrating one lifecycle lane as permanent Rust truth.

## Artifact family
### 1. `process-pilot-brief/v0`
Why this process lane is being piloted.

Should record:
- pilot id and summary
- lane family (`direct-exec`, `shell-shaped`, `pipe-topology`, `async-lifecycle`, `tree-control`, `pty-interactive`)
- why the lane matters now
- intended consumer(s)
- why the lane is tractable now

### 2. `process-lane-profile/v0`
The declared contract for the lane.

Should record:
- allowed spawn modes
- allowed env/cwd/path assumptions
- stdio or PTY posture
- lifecycle/cleanup rules if relevant
- platform limits
- adapter/lossiness notes
- explicit unsupported areas

### 3. `process-query-budget/v0`
The bounded questions the pilot must answer.

Should record:
- named semantic questions in scope
- required answer fields
- required uncertainty classes
- mandatory vector coverage
- explicit out-of-scope questions

### 4. `process-consumer-handoff/v0`
How a downstream consumer may reuse the pilot.

Should record:
- consumer class (`tool-wrapper`, `orchestrator`, `ci-review`, `migration`, `interactive-app`, `agent-runner`)
- which artifacts are consumed directly
- which claims remain advisory only
- what the consumer must still verify independently

### 5. `process-pilot-scorecard/v0`
Decides whether widening is justified.

Should ask:
- did the pilot preserve lane identity honestly?
- did it make lossy adapters explicit?
- did it attach concrete vectors and reports?
- did at least one real consumer import it?
- did it avoid claiming universal subprocess support?

### 6. `process-pilot-pack/v0`
Bundle of:
- pilot brief
- lane profile
- query budget
- consumer handoff
- process-surface artifacts from the base kit
- scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Direct-exec truth lane
**Why first**
- It is the baseline lane other wrappers start from.
- Current std docs already expose enough sharp semantics to justify a pack immediately: no shell by default, OS path lookup, relative-program-path + `current_dir` ambiguity, explicit env clear/filter posture, and different stdio defaults for `spawn` versus `output`.

**Primary artifacts**
- `process-surface/v0`
- `spawn-model-profile/v0`
- `argv-env-cwd-profile/v0`
- `stdio-topology-profile/v0`
- vectors for relative path + `current_dir`, env clearing/filtering, and ordinary stdio defaults

**Primary consumers**
- tool wrappers
- build/test harnesses
- CI reviewers

### 2) Shell-shaped composition lane
**Why second**
- The ecosystem is already using `xshell` and `duct`, but their semantics are easy to flatten.
- This lane proves the archive can distinguish actual shell execution from shell-free interpolation and pipeline composition.

**Primary artifacts**
- `spawn-model-profile/v0` with explicit shell posture
- `stdio-topology-profile/v0` for pipeline graphs
- `process-adapter-profile/v0` for helper→direct-exec lowering
- vectors for quoting, exit-check defaults, pipeline aggregation, and environment/cwd statefulness

**Primary consumers**
- script-like tool authors
- xtask-style repos
- orchestration/migration reviewers

### 3) Async child-lifecycle lane
**Why third**
- This is where user intuition is most often wrong.
- Tokio, `async-process`, and older `tokio-process` are strong enough evidence that drop/kill/reap semantics must be piloted explicitly.

**Primary artifacts**
- `supervision-termination-profile/v0`
- `process-adapter-profile/v0` for std↔Tokio↔`async-process`
- vectors for dropped-child cleanup, `kill_on_drop`, explicit wait, and zombie-risk posture
- scorecard entries that distinguish deterministic, best-effort, and unsupported cleanup claims

**Primary consumers**
- async services
- supervisors
- agent/tool runners

### 4) Tree-control and concurrent-control lane
**Why fourth**
- `process_group`, `process-wrap`, `command-group`, and `shared_child` already show that child-only control is insufficient for some real workloads.
- This lane proves the archive can model group/session/job-object scope and concurrent wait/kill control without pretending they are universal defaults.

**Primary artifacts**
- `supervision-termination-profile/v0`
- `process-adapter-profile/v0`
- vectors for descendant cleanup, Ctrl-C/process-group behavior, concurrent wait+kill, and wrapper-ordering caveats

**Primary consumers**
- supervisors
- dev tools that spawn trees
- operator-facing services

### 5) PTY / interactive lane
**Why fifth**
- PTY behavior is meaningfully different, but should arrive only after pipe and lifecycle lanes are already explicit.
- `portable-pty` is strong enough to pilot now, but PTY should not become the default narrative for all process work.

**Primary artifacts**
- `tty-pty-profile/v0`
- `stdio-topology-profile/v0` with PTY exclusion notes
- vectors for prompts, buffering, resize, transcript capture, and serial-TTY caveats

**Primary consumers**
- interactive CLIs
- terminal apps
- transcript/testing consumers

## Graduation criteria
A process-surface pilot should graduate only when it has:
1. an explicit pilot brief;
2. a lane profile naming the subprocess lane under review;
3. a bounded query budget with named vectors;
4. at least one consumer-handoff artifact;
5. concrete check reports or attached evidence;
6. a scorecard showing the pilot remained lane-specific and did not claim universal subprocess truth.

## Anti-goals
- one giant process manifest that erases shell, pipe, tree, and PTY differences;
- narrating every helper crate as a semantic superset of std;
- treating best-effort background reaping as deterministic cleanup;
- treating PTY behavior as recoverable from ordinary pipe logs;
- widening to remote execution / workflow scheduling / agent frameworks before the subprocess lanes are stable.

## Why this is an ecosystem contribution
Rust already has strong process crates.
What it still lacks is a compact, reviewable way to say **which subprocess lane a public surface actually occupies, what evidence checked it, and how much downstream consumers may safely infer**.

A good Process Surface Pilot Program would give the ecosystem that missing middle layer.
It would make subprocess design more boring, comparable, and honest without forcing one universal process abstraction.
