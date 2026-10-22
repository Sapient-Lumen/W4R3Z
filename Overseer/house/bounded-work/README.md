# Bounded work with a return path

[The house](../README.md) · [The Overseer](../../README.md)

The house was not only a way back into one conversation. Its finite-loop machinery gave another worker a named job, a turn budget and a place to return its result. This made room for work alongside the primary conversation without treating every continuing task as an indefinitely running agent.

## Give the work an address

The [spawn script](scripts/spawn_finite_loop.py) joins the steps: create a job through the [registry](scripts/finite_loop_registry.py), optionally attach it to a group, invoke the executor, and retain the result. The record carries the task, class, mission, remaining turns, session policy and lineage. A worker therefore has more than a prompt: its work has a place that can be reopened and inspected.

The [audit launcher](scripts/spawn_audit_loop.py) makes the purpose concrete. It writes a mission, names documents to inspect, and provides a destination for severity-ordered findings. It asks for contradictions, weak assumptions and missing tests, without repair by default. Another worker can contribute skeptical attention rather than merely add more construction. The mission is an instruction to the worker, not a filesystem prohibition on editing.

## Make the next turn depend on the last

The [executor](scripts/finite_loop_executor.py) asks each turn for structured JSON: an outcome, summary, resume hint, possible next prompt, task state, human-intervention flag, confidence and evidence paths. Continuing, completing, being blocked, failing and cancelling are distinct reported outcomes. The response helps determine the next step rather than leaving continuation to an unchanging command sent blindly.

A successful turn consumes a turn from the ledger. If its reported outcome asks to continue but no budget remains, the executor records blocked, unfinished work rather than completion. A recognized capacity refusal leaves a planned job with an explicit capacity hold and no turn consumed. Lower-level runner metadata is retained alongside the higher-level task result, so the account of what happened does not depend only on the worker's prose.

Those records organize evidence; they do not certify the worker's conclusions. An evidence path is a place to inspect, and a confidence label is part of the returned report. Neither is an independent check that the task was done correctly.

## Steer at a real boundary

A [control note](loop-control.md) can cancel before another turn, request a stop or hold after a returned turn, focus the next turn, or persist as information. The [writer](scripts/write_loop_control_note.py) maintains one active note and a readable mirror. This is steering between turns, not live keyboard intervention into a running non-interactive turn, and not a queue of independently acknowledged instructions.

The registry's recovery packet gathers the paths needed to reopen the job. An [explicit successor](scripts/spawn_followup_loop.py) records where its task came from and links it into a lineage. [Group reconstruction](scripts/loop_group_registry.py) can follow that lineage toward its later member without silently rewriting the group's attached membership. A group organizes the account of work; labels such as serial or parallel do not themselves implement a scheduler.

The [observability compiler](scripts/compile_loop_observability_brief.py) combines these records with runtime and checkpoint signals to make recent running, held, failed and completed work easier to find. This lets a returning reader choose which job needs a closer look instead of opening every run directory.

## Separate state is not a sandbox

The [runtime preparer](scripts/prepare_loop_runtime.py) creates per-loop Codex state and, for Git-backed work, a detached worktree. These reduce accidental sharing between jobs. Outside Git, it creates a task directory but still executes in the original shared workspace. That distinction matters when reading the original documents' shorter phrase “fallback task directory.”

The [power model](delegation-power-model.md) distinguishes assigned authority from technical capability. Same-family workers deliberately retain broad host reach; the [runner](scripts/codex_exec_with_load_balancer.py) bypasses its original CLI's approvals and sandbox. A mission, worktree and turn budget are different controls, not interchangeable kinds of confinement.

Continuation also needs its own reading. A successor receives a new budget, so a finite job does not establish a cumulative limit for the whole lineage. The generic follow-up path retains history but does not pass the original loop class or mission path into creation; it must not be described as automatically inheriting the same mission authority.

## Read the state, not just its label

A per-invocation turn limit can stop an executor invocation while its job remains marked running with budget left. Runtime and checkpoint signals are therefore needed beside that label. The normal failure handlers also do not cover every exception: malformed JSON can escape the structured-output handler that catches `SystemExit`. These are limits visible in the source, not newly reproduced failure results.

The included [executor tests](tests/test_finite_loop_executor.py) use substituted runner, registry and runtime components; the [group tests](tests/test_loop_group_registry.py) make reconstruction expectations inspectable. The original documents also narrate historical concurrency trials, whose cited per-run receipts are not carried in this selection. A test source and a historical claim remain different kinds of evidence.

The construction is nevertheless substantial: work had an address, a budget, a way to be steered, a recoverable history and a return path for its result. The original [finite-loop account](finite-loops.md), [group design](loop-groups.md) and [observability design](loop-observability.md) preserve how that working world was understood from inside the project.
