# Design: Process Surface Lane Map (direct exec, shell-shaped composition, pipe topology, async child lifecycle, tree control, and PTY interaction)

## Goal
Make the archive more precise about **what kind of subprocess claim is actually being made**.

Rust’s process story is strong, but the ecosystem still talks too often as if one phrase — “process support” — names one coherent thing.
It does not.
A direct `std::process::Command` spawn, an explicit shell command, an `xshell` command that deliberately does **not** use the shell directly, a `duct` pipeline expression, a Tokio child with best-effort background reaping, an `async-process` child with `reap_on_drop`, a process-group/job-object wrapper, and a PTY-backed interactive session are **different but connected** lanes.

The worthy contribution here is therefore not another shell helper, task runner, or universal supervisor.
It is a **portable lane map and evidence boundary** that lets tools say which process lane they are using, what semantics actually attach to it, where adapters are lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/process-surface-kit.md`](./process-surface-kit.md)
- [`design/process-surface-pilot-program.md`](./process-surface-pilot-program.md)
- [`design/command-surface-kit.md`](./command-surface-kit.md)
- [`design/filesystem-surface-kit.md`](./filesystem-surface-kit.md)
- [`proposals/epic-process-surface-kit.md`](../proposals/epic-process-surface-kit.md)

## Why this note is needed now
The current standard and ecosystem signals line up around one conclusion: Rust needs a better **process-surface contract**, not just more subprocess helpers.

- Std `Command` in current docs still keeps the baseline lane deliberately sharp: no shell by default, OS-defined path lookup, explicit environment/current-dir/stdio settings, and a specific warning that relative program paths plus `current_dir` are platform-specific and unstable.
  https://doc.rust-lang.org/std/process/struct.Command.html
- Std `Child` still has no `Drop`, and std docs still warn that exited-but-unwaited children may remain as zombies on Unix. That means cleanup/reaping posture is public process semantics, not implementation trivia.
  https://doc.rust-lang.org/std/process/struct.Child.html
- `std::io::pipe`, stabilized in 1.87, makes explicit pipe topology and cross-process writer/reader sharing part of ordinary std process orchestration rather than a crate-only trick.
  https://doc.rust-lang.org/std/io/fn.pipe.html
- Tokio’s current process docs intentionally preserve std’s default “drop does not cancel” behavior, add `kill_on_drop`, and only promise best-effort background reaping on Unix. That is already a distinct child-lifecycle lane.
  https://docs.rs/tokio/latest/tokio/process/index.html
  https://docs.rs/tokio/latest/tokio/process/struct.Command.html
  https://docs.rs/tokio/latest/tokio/process/struct.Child.html
- `async-process` explicitly grew `reap_on_drop` and `kill_on_drop`, which is direct evidence that async subprocess lifecycle is still an active design seam rather than a settled clone of std.
  https://docs.rs/async-process
  https://docs.rs/crate/async-process/2.5.0/source/CHANGELOG.md
- `xshell` and `duct` prove that “shell-like ergonomics” are not one thing: `xshell` explicitly says it does **not** use the shell directly, while `duct` explicitly frames itself as shell-like pipeline/redirection ergonomics with checked non-zero exits by default.
  https://docs.rs/xshell/latest/src/xshell/lib.rs.html
  https://docs.rs/duct/latest/duct/
- `process-wrap`, `command-group`, `shared_child`, and Unix `CommandExt::process_group` show that process-tree scope, concurrent wait/kill control, and descendant cleanup are still separate lanes above raw spawn.
  https://docs.rs/process-wrap/latest/process_wrap/
  https://docs.rs/shared_child/latest/shared_child/
  https://doc.rust-lang.org/std/os/unix/process/trait.CommandExt.html
- `portable-pty` proves PTY-backed interaction is a first-class lane with its own command builder, controlling-terminal assumptions, resize behavior, and even serial-TTY caveats.
  https://docs.rs/portable-pty/latest/portable_pty/

There is also a useful lesson from the past: the older `tokio-process` crate made dropped children terminate by default because the child itself was the future. Current Tokio explicitly does not do that. That historical swing is exactly why the archive should preserve child-lifecycle lanes explicitly instead of narrating one async process story as timeless truth.
https://docs.rs/tokio-process/latest/tokio_process/

## The lane map

### Lane 1 — Direct-exec builder lane
**What it is**
- `std::process::Command` and near-clones that keep the direct-exec baseline.
- Literal argv, explicit env/cwd/stdio configuration, and OS-defined program lookup.

**Why it matters**
- This is the baseline lane most other wrappers start from.
- It is the cleanest place to record exact spawn subject, env/cwd posture, and stdio defaults.

**What the archive should preserve**
- direct exec versus shell posture,
- path lookup posture,
- relative-program-path + `current_dir` caveat,
- inherited versus cleared/filtered environment,
- and ordinary stdin/stdout/stderr defaults for `spawn`, `status`, and `output`.

**What it should not pretend**
- that direct exec is the same as shell execution,
- that env/cwd state is a minor detail,
- or that a direct-exec lane automatically says anything about process-tree cleanup.

### Lane 2 — Shell-shaped composition lane
**What it is**
- Shell-like ergonomics, scripting DSLs, and pipeline helpers.
- Includes both explicit shell execution and shell-shaped helpers that intentionally avoid invoking the shell directly.

**Why it matters**
- This is where the ecosystem most often flattens real differences.
- `xshell` and `duct` solve similar ergonomic pain while making different semantic commitments.

**What the archive should preserve**
- actual shell invocation versus shell-free interpolation,
- default exit-check posture,
- pipeline composition semantics,
- environment/cwd statefulness,
- and where helper syntax changes quoting/threat assumptions.

**What it should not pretend**
- that every shell-like API is an actual shell,
- that pipelines are just stdio toggles,
- or that a convenient DSL erases platform process differences.

### Lane 3 — Pipe-topology lane
**What it is**
- Explicit pipes, pipeline graphs, fan-in/fan-out topologies, and bridge points between process outputs and new child `Stdio` inputs.

**Why it matters**
- `std::io::pipe` and Tokio’s child-stdout to `Stdio` conversions make topology itself part of the public surface.
- Read/write blocking, interleaving, and EOF behavior are part of the contract.

**What the archive should preserve**
- whether the surface uses `Stdio::piped`, `std::io::pipe`, helper-owned pipelines, or PTYs instead,
- capture versus streaming posture,
- blocking/interleaving caveats,
- and deadlock/EOF assumptions.

**What it should not pretend**
- that pipe topology is interchangeable with PTY interaction,
- that capture and streaming are the same claim,
- or that pipeline edges can always be reconstructed later from logs.

### Lane 4 — Async child-lifecycle lane
**What it is**
- Child lifetime, drop behavior, kill behavior, wait behavior, and reaping guarantees for async process APIs.

**Why it matters**
- Async users are especially vulnerable to “drop means cancel” intuition.
- Tokio, `async-process`, and older Tokio lineage show that this lane is historically unstable enough to deserve explicit review.

**What the archive should preserve**
- default drop behavior,
- `kill_on_drop` / `reap_on_drop` posture,
- whether `kill` also waits,
- whether reaping is explicit, background, or best-effort,
- and what guarantees remain platform-specific.

**What it should not pretend**
- that every async child behaves like a dropped future,
- that background reaping equals deterministic cleanup,
- or that one async crate’s lifecycle rules generalize to the whole ecosystem.

### Lane 5 — Tree-control and concurrent-control lane
**What it is**
- Process groups, sessions, job objects, descendant cleanup wrappers, and concurrent wait/kill control.

**Why it matters**
- Lone-child control and process-tree control are not the same lane.
- Shared wait/kill semantics are awkward enough that focused crates exist purely to model them honestly.

**What the archive should preserve**
- child-only versus group/session/job-object scope,
- descendant cleanup guarantees versus best effort,
- concurrent wait/kill posture,
- wrapper ordering and adapter dependencies,
- and explicit platform gaps.

**What it should not pretend**
- that “kill” means the same thing across child, tree, session, and job lanes,
- that Unix and Windows tree control are one story,
- or that a wrapper crate magically upgrades std semantics without new caveats.

### Lane 6 — PTY / interactive lane
**What it is**
- PTY-backed interactive execution, controlling-terminal behavior, resize/signals, and transcript-oriented interaction.

**Why it matters**
- PTYs change prompts, buffering, terminal control, and signal expectations.
- `portable-pty` even includes a serial-TTY lane that cannot spawn arbitrary commands the same way.

**What the archive should preserve**
- PTY allocation versus plain pipes,
- controlling-terminal posture,
- resize and interactive buffering expectations,
- transcript capture and replay posture,
- and serial/remote caveats.

**What it should not pretend**
- that PTY is just another `stdout` mode,
- that interactive behavior can be inferred from pipe recordings,
- or that shell/process-tree semantics automatically carry over unchanged once a PTY is involved.

## Adapter rules
A lane map becomes useful only if it names **lossy boundaries**.
The archive should therefore treat these as first-class adapter classes:

1. **direct exec ↔ shell-shaped helper**
   - can change quoting, exit checking, environment defaults, and user-input risk posture.
2. **direct exec / helper ↔ explicit pipe topology**
   - can change buffering, EOF, ownership, and deadlock behavior.
3. **sync child ↔ async child wrapper**
   - can change drop/reap guarantees and kill/wait orchestration.
4. **lone child ↔ tree wrapper**
   - can change kill scope, descendant cleanup, and signal routing.
5. **pipe ↔ PTY**
   - can change prompts, buffering, terminal control, and transcript meaning.

Adapters should report not just “supported” or “unsupported”, but what semantics changed.

## What this changes in the archive
This note sharpens the Process Surface Kit in one important way:

- the archive should stop treating **actual shell execution**, **shell-like but shell-free helpers**, **pipe topology**, **async lifecycle/reaping**, **tree-control wrappers**, and **PTY interaction** as one bucket;
- pilot programs should prove those lanes separately before speaking about “Rust subprocess support” in general;
- downstream consumers should import only the lane facts they can honestly reuse.

The worthy contribution here is therefore a thin `cargo procsurf` / `process-pack/v0` layer whose lane profiles, adapter reports, vector reports, and consumer handoffs make subprocess truth reviewable without forcing one universal process abstraction.
