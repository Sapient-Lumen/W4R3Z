# Gap: process surfaces, subprocess semantics, pipelines, PTY/TTY behavior, and reviewable supervision contracts

## What is missing

Revision note (rev0325): the archive should now preserve a sharper lane split inside this gap: **direct exec, actual shell execution, shell-like but shell-free helpers, explicit pipe topology, async child lifecycle/reaping, tree-control wrappers, and PTY interaction**. The missing contribution is not one “better Command API” but a portable way to publish which of those lanes a public surface actually occupies.
Rust has good child-process primitives, but the ecosystem still lacks a **portable way to publish what a subprocess surface actually means**.

Today there is no standard way to say:
- whether a program is spawned by direct exec, by an explicit shell, or through a script/pipeline helper,
- whether argv is treated as literal arguments, raw Windows command-line text, or shell syntax,
- whether environment and current-directory inheritance are preserved, filtered, or cleared,
- whether stdio is inherited, piped, nulled, tee’d, fan-out/fan-in piped, or attached to a PTY,
- whether a child is a lone process, a process-group/session leader, a Windows job-object member, or part of a larger tree with kill/reap expectations,
- whether dropping a handle leaves the child running, kills it best-effort, kills and waits, or only affects the leader and not descendants,
- whether exit checking is strict-by-default, opt-in, stream-first, output-buffering, or pipeline-aggregate,
- whether signal handling and shutdown are parent-driven, runtime-driven, or intentionally left to callers,
- and what evidence actually ran: argv-quoting vectors, pipeline/pipe-topology vectors, orphan/zombie vectors, process-group kill vectors, PTY-interactive vectors, or platform-matrix probes.

That gap matters because Rust’s process ecosystem is not one thing.
Std `process` gives a sharp but low-level builder with literal argv semantics, environment/current-dir controls, explicit stdio wiring, and no `Drop` cleanup for `Child`. `xshell` explicitly offers shell-like ergonomics without using the shell directly, while `duct` offers shell-like pipeline composition with checked exits by default, which is exactly why “shell helper” is not one semantic lane. Tokio and `async-process` add async interaction but with different cleanup/reaping stories, and the older `tokio-process` crate is a useful historical reminder that async child-drop semantics have already shifted meaningfully over time. `duct` and `xshell` offer safer shelling-out/pipeline ergonomics. `command-group`, `process-wrap`, `shared_child`, `portable-pty`, `signal-hook`, and runtime-specific signal modules each solve sharp slices of supervision, PTY, or signal complexity. But there is no shared artifact family that records which slice a public surface actually chose.

So the missing contribution is not another shell helper, task runner, or process wrapper.
It is a **reviewable process-surface layer** for publishing spawn model, argv/env/cwd posture, stdio/pipeline topology, supervision and signal semantics, PTY posture, and evidence honestly.

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
- https://docs.rs/portable-pty/latest/portable_pty/cmdbuilder/struct.CommandBuilder.html
- https://docs.rs/command-group
- https://docs.rs/process-wrap
- https://docs.rs/shared_child
- https://docs.rs/signal-hook

## The current seam is awkward
Rust already has several real subprocess subcultures, but their semantics do not line up cleanly:
- std `Command` does **not** invoke a shell by default, passes argv literally, warns that `cmd.exe` and `.bat` files on Windows use non-standard decoding, and documents that a relative program path together with `current_dir` is platform-specific and unstable;
- std `Child` has no `Drop`, so dropped handles leave children running, and un-waited exited children can remain as zombies on Unix;
- std `wait`/`wait_with_output` close stdin before waiting to help avoid deadlock, while `try_wait` explicitly does not;
- Tokio intentionally keeps the “dropping a child handle does not imply cancellation” behavior by default, but adds `kill_on_drop`, documents only best-effort background reaping, and makes `Child::kill` different from std by killing **and then waiting**;
- `async-process` uses a dedicated background thread to reap exited children and explicitly contrasts itself with std’s drop/leak behavior;
- std now has `std::io::pipe`, while pipeline helpers such as `duct` and scripting helpers such as `xshell` operate at a higher semantic level around composition and exit-checking;
- Unix `CommandExt` exposes `process_group`/`setsid`, but cross-platform tree control is still fragmented enough that crates such as `command-group` and `process-wrap` exist to model process groups, sessions, job objects, and kill-on-drop wrappers;
- PTY handling is different again: `portable-pty` exposes a cross-platform PTY API with its own command builder and controlling-terminal posture;
- `shared_child` exists because std `Child` requires `&mut self` for `wait` and `kill`, partly to avoid a Unix `waitpid`/PID-reuse race when kill and wait happen concurrently;
- and both `signal-hook` and Tokio’s signal docs say signal handling is tricky and should be treated carefully.

So the ecosystem is not missing *subprocess primitives*.
It is missing the **artifact family that records which spawn, argv, stdio, supervision, PTY, and signal semantics a public surface actually chose, and what evidence checked those claims**.

Sources:
- https://doc.rust-lang.org/std/process/struct.Command.html
- https://doc.rust-lang.org/std/process/struct.Child.html
- https://doc.rust-lang.org/std/os/unix/process/trait.CommandExt.html
- https://doc.rust-lang.org/std/io/fn.pipe.html
- https://docs.rs/tokio/latest/tokio/process/struct.Command.html
- https://docs.rs/tokio/latest/tokio/process/struct.Child.html
- https://docs.rs/tokio/latest/tokio/signal/index.html
- https://docs.rs/async-process
- https://docs.rs/duct
- https://docs.rs/xshell
- https://docs.rs/portable-pty/latest/portable_pty/cmdbuilder/struct.CommandBuilder.html
- https://docs.rs/command-group
- https://docs.rs/process-wrap
- https://docs.rs/shared_child
- https://docs.rs/signal-hook

## Why this matters
This gap matters because subprocess semantics cut across many high-value Rust systems at once:
1. **build tools and developer tooling** — wrappers, compilers, linters, formatters, and test runners all spawn external tools, and bad env/cwd/stdio/signal choices become reliability bugs;
2. **services and supervisors** — long-running systems need honest process-tree, kill, reap, and shutdown behavior rather than “best effort” folklore;
3. **agentic and automation workflows** — once tools start shelling out recursively, pipeline behavior, PTY use, and descendant cleanup become security and correctness boundaries;
4. **CLI scripting and orchestration** — users care whether whitespace/shell syntax is interpreted, whether failures are checked, and how pipelines propagate output and exit status;
5. **interactive tools and terminals** — PTY versus pipe semantics change prompts, buffering, terminal control, and signal delivery;
6. **cross-platform support** — Windows quoting, job objects, `.bat` semantics, Unix process groups, and signal differences leak into product claims quickly.

A worthy contribution here is therefore not another shell DSL or child-process facade.
It is a way to treat **process surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://doc.rust-lang.org/std/process/struct.Command.html
- https://doc.rust-lang.org/std/process/struct.Child.html
- https://doc.rust-lang.org/std/os/unix/process/trait.CommandExt.html
- https://docs.rs/tokio/latest/tokio/process/struct.Command.html
- https://docs.rs/tokio/latest/tokio/process/struct.Child.html
- https://docs.rs/async-process
- https://docs.rs/duct
- https://docs.rs/xshell
- https://docs.rs/portable-pty
- https://docs.rs/process-wrap

## What “good” looks like
A worthy contribution here is **not** one fake universal process badge.
It is a shared process-surface boundary:
- one `process-surface/v0` describing the top-level subprocess family and intended use,
- one `spawn-model-profile/v0` describing direct-exec vs shell-driven vs helper/wrapper posture, program-path assumptions, and exit-check defaults,
- one `argv-env-cwd-profile/v0` describing argument encoding/escaping rules, environment inheritance/filtering, working-directory semantics, and platform caveats,
- one `stdio-topology-profile/v0` describing stdin/stdout/stderr inheritance, pipes, tee/fan-out, stream capture, buffering, and pipeline topology,
- one `supervision-termination-profile/v0` describing lone-child vs tree/group/session/job-object posture, kill/wait/reap expectations, drop semantics, and shutdown/signal handling,
- one `tty-pty-profile/v0` describing PTY allocation, controlling-terminal posture, interactive expectations, resize/signal caveats, and container/remote caveats,
- one `process-adapter-profile/v0` describing bridges between std, Tokio/async-process, pipeline/scripting helpers, PTY stacks, and group/session wrappers,
- one `process-vector-set/v0` describing argv-quoting, relative-path/current-dir, env-filtering, pipe/deadlock, orphan/zombie, process-tree kill, PTY-interactive, and signal-shutdown vectors,
- one `process-check-report/v0` recording which vectors actually ran,
- and one `process-pack/v0` bundle for docs, CI, transcripts, logs, fixtures, and archaeology.

That would let Rust teams reason about subprocess choices with **explicit artifacts** instead of a brittle mix of helper APIs, runtime caveats, and platform bug folklore.

## Non-goals
This gap should not be used to:
- replace std `process`, Tokio, `async-process`, pipeline helpers, or PTY crates,
- define one canonical pipeline DSL or one canonical supervisor,
- collapse argv/env/cwd semantics, stdio topology, supervision, PTY behavior, and signal handling into one fake manifest,
- or pretend that “process support” can be solved by a single abstraction layer.

The job is smaller and sharper:
**make subprocess surfaces legible, honest, and checkable across spawn model, arguments, stdio, supervision, PTY/TTY behavior, and evidence.**
