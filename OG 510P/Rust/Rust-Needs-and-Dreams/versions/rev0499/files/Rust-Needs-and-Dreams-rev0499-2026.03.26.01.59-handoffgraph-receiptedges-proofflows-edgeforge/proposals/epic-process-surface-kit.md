# Epic proposal: Process Surface Kit

## Thesis
One of the more worthy ecosystem contributions in Rust now would be a **portable review layer for process surfaces**.

Rust programs constantly cross boundaries between direct exec and shell execution, literal argv and raw Windows command lines, inherited and filtered environments, pipes and PTYs, lone-child and process-tree supervision, strict exit checking and stream-first ergonomics. But today those semantics are usually published only through helper choice, runtime caveats, and scattered bug lore.

Rust does not need one more shell helper crate nearly as much as it needs a boring, explicit `process-pack/v0`.

The concrete refinement from this revision is that the pack should now export **lane-family truth**: direct exec, actual shell execution, shell-shaped but shell-free helpers, explicit pipe topology, async child lifecycle/reaping, tree-control/concurrent-control wrappers, and PTY interaction should be comparable without being flattened.

## Why now
The timing is good:
- std `Command` explicitly documents literal argv semantics, Windows quoting hazards for `cmd.exe`/`.bat`, and the ambiguous interaction between relative program paths and `current_dir`;
- std `Child` explicitly has no `Drop`, documents zombie risk on Unix, and distinguishes `wait`, `try_wait`, and `kill` sharply;
- std `io::pipe` now exists, which makes explicit pipe topology a more ordinary part of process orchestration rather than a crate-only trick;
- Tokio’s process docs preserve std’s default “drop does not cancel” behavior, add `kill_on_drop`, and document only best-effort background reaping, while Tokio signal docs openly say signal handling is tricky;
- `async-process` already proves there is demand for a different reaping story;
- `duct` and `xshell` show persistent demand for safer shelling-out and pipeline composition;
- `process-wrap`, `command-group`, and `shared_child` show that process-group/session/tree and concurrent-wait/kill behavior are still awkward enough to need focused wrappers;
- `portable-pty` shows that PTY-driven execution is a separate first-class lane, not a minor stdio toggle.

That means the next major subprocess seam is visible before it has converged.
This is exactly when a reviewable contract is more valuable than another helper facade.

Read this together with [`design/process-surface-lane-map.md`](../design/process-surface-lane-map.md) and [`design/process-surface-pilot-program.md`](../design/process-surface-pilot-program.md).

Sources:
- https://doc.rust-lang.org/std/process/struct.Command.html
- https://doc.rust-lang.org/std/process/struct.Child.html
- https://doc.rust-lang.org/std/process/struct.Stdio.html
- https://doc.rust-lang.org/std/os/unix/process/trait.CommandExt.html
- https://doc.rust-lang.org/std/io/fn.pipe.html
- https://docs.rs/tokio/latest/tokio/process/struct.Command.html
- https://docs.rs/tokio/latest/tokio/process/struct.Child.html
- https://docs.rs/tokio/latest/tokio/signal/index.html
- https://docs.rs/async-process
- https://docs.rs/duct
- https://docs.rs/xshell
- https://docs.rs/portable-pty
- https://docs.rs/command-group
- https://docs.rs/process-wrap
- https://docs.rs/shared_child
- https://docs.rs/signal-hook

## What should be built
A first credible version should ship:
1. `process-surface/v0`, `spawn-model-profile/v0`, `argv-env-cwd-profile/v0`, `stdio-topology-profile/v0`, `supervision-termination-profile/v0`, `tty-pty-profile/v0`, `process-adapter-profile/v0`, `process-vector-set/v0`, `process-check-report/v0`, and `process-pack/v0`
2. one std pilot distinguishing direct exec, env/cwd filtering, and explicit stdio topology
3. one async pilot distinguishing Tokio versus `async-process` cleanup/reaping behavior
4. one pipeline pilot using `duct` or equivalent to publish topology and exit-check defaults
5. one group/session/job-object pilot using wrappers such as `command-group` or `process-wrap`
6. one PTY pilot covering controlling-terminal and interactive-transcript posture
7. docs and CI that make Windows argv hazards, orphan/zombie risk, process-tree kill limits, and PTY differences visible

The winning version is compact, semantic, and boundary-aware.
It should make subprocess behavior legible together rather than canonizing one helper stack.

## Initial pilots
- **Tool-wrapper lane** — direct exec with explicit env/cwd and checked exit status
- **Async-supervisor lane** — compare Tokio kill/wait/drop semantics with alternative reaping models
- **Pipeline lane** — publish pipe topology, stderr/stdout capture, and aggregate exit semantics honestly
- **Process-tree lane** — publish group/session/job-object kill scope and descendant cleanup posture
- **Interactive lane** — publish PTY allocation, controlling-terminal posture, and transcript expectations

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document spawn, argv/env/cwd, stdio, supervision, PTY, and evidence vocabulary
2. **v0.2 std + async pilots**
   - ship one std tool-wrapper pilot and one async/supervisor pilot
   - show where drop, kill, wait, and reap semantics diverge
3. **v0.3 pipeline + PTY depth**
   - add pipeline topology and PTY evidence
   - capture Windows argv and interactive caveats explicitly
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical process stack

## Success metrics
- Library authors can review spawn, argv/env/cwd, stdio, supervision, and PTY behavior without reconstructing them from helper choice and issue threads.
- Applications can distinguish direct exec from shelling out, lone-child kill from process-tree cleanup, and pipe-based capture from PTY interaction.
- Security reviews can tell raw Windows argv, shell interpretation, and inherited-environment posture apart.
- Tooling stacks can publish whether dropped handles leak children, whether reaping is explicit or best-effort, and whether interactive behavior depends on PTYs.
- Migrations between std, Tokio, pipeline helpers, PTY wrappers, and process-group wrappers become diffable instead of surprising.

## Archive fit
This proposal fills a real gap in the archive:
- **Command Surface Kit** handles a tool’s own CLI UX,
- **Runtime Capability Kit** handles whether process authority exists,
- **Background Work Kit** handles durable jobs/workflows,
- **Filesystem Surface Kit** handles path/traversal/durability semantics,
- **Synchronization Surface Kit** and **Async Lifecycle Kit** handle in-process coordination and task lifetime.

But none of those is the portable contract for **spawn model, argv/env/cwd posture, stdio/pipeline topology, supervision/termination semantics, PTY behavior, and attachable subprocess evidence**.
Process Surface Kit is the missing substrate above Rust’s already powerful and already fragmented process ecosystem.
