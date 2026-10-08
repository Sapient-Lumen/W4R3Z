# Design: Process Surface Kit (`cargo procsurf`, `process-pack/v0`)

Read this together with:
- [`design/process-surface-lane-map.md`](./process-surface-lane-map.md)
- [`design/process-surface-pilot-program.md`](./process-surface-pilot-program.md)
- [`proposals/epic-process-surface-kit.md`](../proposals/epic-process-surface-kit.md)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **process surfaces** in Rust: spawn model, argv/env/cwd posture, stdio and pipeline topology, supervision and termination semantics, PTY/TTY behavior, and the evidence that those claims were actually checked.

This should help answer questions like:
- does this surface spawn directly or through a shell,
- are argv strings literal, raw-encoded, or shell-escaped,
- does it inherit or clear environment/current-directory state,
- does it expose pipes, buffered capture, streaming, tees, or PTYs,
- does dropping a handle leak the child, kill the leader, kill the process group, or wait for cleanup,
- does shutdown use signals, Ctrl-C forwarding, process groups, job objects, or explicit cooperative protocols,
- and which of those claims were actually tested on which platforms.

The kit should make subprocess behavior reviewable without flattening all process libraries into one facade.

The key refinement in this revision is that the kit should now be read through an explicit **lane map**: direct exec, shell-shaped composition, pipe topology, async child lifecycle/reaping, tree-control/concurrent-control wrappers, and PTY interaction are distinct but connected lanes. The kit should export lane truth and adapter lossiness rather than treating them as one subprocess score.

## Non-goals
The Process Surface Kit should **not**:
- replace `std::process`, Tokio, `async-process`, `duct`, `xshell`, PTY crates, or supervisor crates,
- invent a universal shell DSL,
- erase platform differences between Unix groups/sessions/signals and Windows job objects/command-line rules,
- or decide that one spawn/supervision strategy is “the Rust way”.

The goal is explicit contracts and evidence, not convergence on one implementation.

## Core artifact family

### 1) `process-surface/v0`
Top-level declaration for a subprocess-facing library or application boundary.

Fields:
- `surface_id`
- `purpose` (`tool-wrapper`, `pipeline-runner`, `supervisor`, `interactive-terminal`, `test-harness`, `agent-tool-runner`, `other`)
- `spawn_profiles`
- `argv_env_cwd_profiles`
- `stdio_profiles`
- `supervision_profiles`
- `tty_profiles`
- `adapter_profiles`
- `vector_sets`
- `check_reports`

### 2) `spawn-model-profile/v0`
How programs are located and launched.

Fields:
- `spawn_mode` (`direct_exec`, `shell`, `helper_wrapper`, `runtime_spawn`, `remote_like`, `mixed`)
- `program_resolution` (`path_lookup`, `absolute_only`, `caller_supplied_absolute_preferred`, `platform_specific_relative_warning`)
- `exit_check_default` (`unchecked`, `checked_nonzero`, `pipeline_defined`, `caller_managed`)
- `windows_raw_arg_support`
- `shell_interpretation_scope`
- `msrv_channel_notes`

### 3) `argv-env-cwd-profile/v0`
Arguments, environment, and working-directory posture.

Fields:
- `argv_encoding_mode` (`literal_os_strings`, `raw_windows_cmdline`, `shell_escaped_text`, `mixed`)
- `untrusted_input_policy`
- `env_inheritance` (`inherit`, `clear_then_add`, `filtered_allowlist`, `filtered_denylist`, `caller_managed`)
- `cwd_policy` (`inherit`, `explicit_override`, `scoped_shell_like`, `platform_specific_relative_program_caveat`)
- `arg0_policy`
- `platform_notes`

### 4) `stdio-topology-profile/v0`
How stdin/stdout/stderr and pipes are wired.

Fields:
- `stdin_mode`, `stdout_mode`, `stderr_mode` (`inherit`, `null`, `piped`, `captured`, `pty`, `tee`, `custom`)
- `pipe_topology` (`single_child`, `linear_pipeline`, `fan_out`, `fan_in`, `cross_runtime_bridge`, `custom`)
- `capture_strategy` (`buffered_output`, `streaming`, `streaming_plus_capture`, `reader_handle`, `caller_managed`)
- `deadlock_avoidance_notes`
- `pipe_api_dependencies` (`stdio_piped`, `std_io_pipe`, `os_pipe`, `runtime_specific`, `custom`)

### 5) `supervision-termination-profile/v0`
How child lifetime, process trees, and shutdown behave.

Fields:
- `child_scope` (`single_process`, `process_group`, `session`, `job_object`, `tree_best_effort`, `unknown_descendants`)
- `drop_behavior` (`leave_running`, `kill_best_effort`, `kill_and_wait`, `runtime_best_effort_reap`, `caller_must_wait`)
- `termination_api` (`kill_leader`, `kill_group`, `signal_then_wait`, `cooperative_then_force`, `runtime_defined`)
- `reap_guarantee` (`explicit_wait_required`, `best_effort_runtime`, `background_reaper`, `wrapper_enforced`, `platform_specific`)
- `signal_strategy` (`none`, `signal_hook`, `runtime_signal_stream`, `ctrl_c_forwarding`, `custom`)
- `descendant_policy`

### 6) `tty-pty-profile/v0`
Interactive-terminal posture.

Fields:
- `interactive_mode` (`plain_pipes`, `pty`, `serial_tty`, `mixed`)
- `controlling_terminal_policy`
- `resize_and_signal_support`
- `prompt_buffering_expectations`
- `container_remote_caveats`
- `transcript_capture_mode`

### 7) `process-adapter-profile/v0`
How one lane maps to another.

Examples:
- std `Command` → Tokio `Command`
- std/Tokio child → group/session/job-object wrapper
- pipe-based child → PTY child
- std pipes ↔ `std::io::pipe`
- `duct`/`xshell` expressions ↔ lower-level `Command` plans

Fields:
- `source_lane`
- `destination_lane`
- `lossiness`
- `behavior_deltas`
- `required_platform_features`
- `review_notes`

### 8) `process-vector-set/v0`
Named vectors and fixtures.

Examples:
- Windows argv quoting / `.bat` / `cmd.exe` vectors
- relative-program-path + `current_dir` vectors
- env-clear / env-remove / filtered-env vectors
- `wait`/`try_wait`/stdin-close deadlock vectors
- dropped-child orphan/zombie vectors
- group/session/job-object kill vectors
- PTY prompt/interactive vectors
- signal-forwarding / Ctrl-C / shutdown vectors

### 9) `process-check-report/v0`
Machine-readable outcomes.

Fields:
- `vector_id`
- `platform`
- `toolchain`
- `runtime`
- `result`
- `behavior_observed`
- `attachments`

### 10) `process-pack/v0`
Bundle format containing:
- one `process-surface/v0`
- one or more profiles of each relevant type
- one `process-vector-set/v0`
- one or more `process-check-report/v0`
- transcripts / logs / PTY recordings / CI notes / migration notes

## Reference UX: `cargo procsurf`
- `cargo procsurf inspect`
  - discover likely spawn modes, shell usage, env/cwd controls, stdio wiring, PTY usage, runtime/process wrappers, and shutdown assumptions
- `cargo procsurf check`
  - run declared vectors and emit `process-check-report/v0`
- `cargo procsurf diff <A> <B>`
  - compare two packs or versions and explain semantic drift
- `cargo procsurf doctor`
  - explain likely ambiguity points: shell interpretation, Windows argv hazards, dropped-child cleanup, group/session mismatch, PTY expectations
- `cargo procsurf pack`
  - bundle a `process-pack/v0`

`cargo procsurf` should begin as an orchestrator / validator / packer. It should avoid becoming a new shell, supervisor, PTY implementation, or runtime.

## Default policy
- **Direct exec versus shell spawn must be explicit.**
- **Argument and quoting posture must be explicit, especially on Windows.**
- **Environment inheritance and current-directory behavior must be explicit.**
- **Pipe topology and capture strategy must be explicit.**
- **Drop behavior, kill scope, and reap guarantees must be explicit.**
- **PTY use must be modeled separately from pipe-based interaction.**
- **Best-effort and platform-dependent outcomes are valid outcomes.**

## What the kit should provide to others
- **Application authors:** a way to state what their tool runner, supervisor, or agent process surface actually supports.
- **Library authors:** a way to publish spawn, env, stdio, PTY, and cleanup semantics honestly.
- **Tooling authors:** a way to compare std/Tokio/helper-wrapper behavior without flattening them.
- **Security reviewers:** a way to tell direct exec, shell, raw Windows argv, and process-tree cleanup choices apart.
- **Migration work:** a way to compare std, Tokio, `async-process`, `duct`, PTY wrappers, and process-group wrappers without pretending they are interchangeable.

## Overlap boundaries
- **Not Command Surface Kit:** that kit owns the application’s own CLI flags/help/transcripts; Process Surface Kit owns what happens when code *spawns other programs*.
- **Not Runtime Capability Kit:** that kit owns whether process-spawn authority exists and how it is delegated; this kit owns the semantics after spawning is allowed.
- **Not Background Work Kit:** that kit owns durable jobs/workflows and scheduling; this kit owns subprocess semantics beneath those systems.
- **Not Filesystem Surface Kit:** that kit owns path/traversal/durability semantics; this kit only touches cwd/env/path lookup insofar as they affect spawn behavior.
- **Not Synchronization or Async Lifecycle Kits:** those kits own in-process coordination and task lifetime; this kit owns OS-process lifetime and supervision semantics.

## Hard problems (explicitly scoped)
1. **Dropping is not cancellation**
   - std and Tokio both preserve child execution by default after handle drop; the kit must model that honestly instead of assuming future-style cancellation.
2. **Process-tree semantics are platform-shaped**
   - Unix groups/sessions/signals and Windows job objects/command-line rules should remain explicit lanes, not hidden implementation details.
3. **PTY changes behavior fundamentally**
   - prompts, buffering, signal delivery, and terminal control are materially different from pipes.
4. **Shelling out is not just argv**
   - quoting, raw command-line encoding, and helper DSLs change the threat and correctness model.
5. **Signal handling stays tricky**
   - the kit should record strategy and caveats, not promise one magical safe signal layer.

## Evaluation plan
Pilot on:
1. one std-based tool wrapper using `Command` and explicit env/cwd controls,
2. one Tokio service or supervisor using async child processes,
3. one shell/pipeline helper lane using `duct` or `xshell`,
4. one PTY-driven interactive tool,
5. one process-group/session or job-object wrapper lane.

Success bar:
- projects can publish subprocess assumptions without inventing their own schema,
- reviewers can tell spawn, argv/env/cwd, stdio/pipeline, supervision, and PTY behavior apart,
- kill/reap/orphan surprises become visible before production,
- and the ecosystem gets a reusable boundary above today’s fragmented process stack without flattening meaningful differences.
